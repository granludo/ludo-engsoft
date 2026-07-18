"""Expansió de graf + RRF — recupera per connexió i, després, fusiona.

El RAG vectorial troba chunks que *semblen* la pregunta. Falla quan la resposta és una
cadena a través de diversos documents i el chunk pont no comparteix cap paraula amb la
pregunta. Aquí: «How fast is the robot built by the company that acquired Acme?»
necessita Acme -> Northwind -> Pallet Pup -> 2.1 m/s, però el pont («Northwind builds
the Pallet Pup») no esmenta mai «Acme» ni «fast», així que el cosinus el classifica avall.

La solució és una SEGONA passada de recuperació en paral·lel a la vectorial: extreu les
entitats de la pregunta, recorre un graf de coneixement un o dos salts per relacions
tipades i recull els chunks on caus. Després fusiona les dues llistes ordenades amb
Reciprocal Rank Fusion. El graf arriba al pont per connexió; el RRF li permet enfilar-se
fins al top-K sense desplaçar el que la cerca vectorial ja ha encertat.

Els números darrere d'aquesta idea: el TFG d'Adrià Guilera Bernabé (FIB-UPC, 2026) — una
capa de graf sobre el kb-server de LAMB, mesurada amb HotPotQA / MuSiQue / 2WikiMultihopQA.

Executa:  uv venv && source .venv/bin/activate && uv sync && python rag_graph_expansion.py
"""
import os
import chromadb
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url=os.environ.get("OPENAI_BASE_URL", "http://localhost:11434/v1"),
    api_key=os.environ.get("OPENAI_API_KEY", "ollama"),
)
MODEL = os.environ.get("MODEL", "qwen3:1.7b")
EMBED_MODEL = os.environ.get("EMBED_MODEL", "nomic-embed-text")

TOP_K = 4              # chunks que passem al model — la cadena de resposta aquí són 3 docs (Acme -> Northwind -> Pallet Pup) + marge
RRF_K = 20             # constant d'esmorteïment del rang (el paper de RRF fa servir 60; l'Adrià, 20)
GRAPH_WEIGHT = 0.85    # quant compta la llista del graf respecte a la del vector

# --- el corpus: dissenyat perquè el chunk PONT (d1) sigui lèxicament diferent de la pregunta ---
DOCS = {
    "d0": "Acme Robotics was a Barcelona startup founded in 2019. In 2024 it was acquired by Northwind Industries.",
    "d1": "Northwind Industries is a logistics-automation firm. Its flagship product is the Pallet Pup, an autonomous warehouse robot.",  # el pont
    "d2": "The Pallet Pup has a top speed of 2.1 m/s and an eight-hour battery.",  # la resposta
    "d3": "Acme Robotics' early prototypes were shelf-scanning drones, not ground robots.",  # esquer: Acme + robot
    "d4": "Warehouse robots typically move between 1 and 3 meters per second depending on payload.",  # esquer: robot + velocitat
    "d5": "Northwind Industries reported strong revenue growth in its 2025 annual report.",  # distractor
}

# Relacions tipades a partir de les quals es construeix el graf. En producció s'extreuen
# durant la ingesta amb un LLM (mira el README — el NER clàssic només dóna co-ocurrència, no
# relacions tipades); nosaltres les enviem ja extretes perquè la demostració sigui determinista.
TRIPLES = [
    ("Acme Robotics", "acquired_by", "Northwind Industries"),
    ("Northwind Industries", "builds", "Pallet Pup"),
    ("Pallet Pup", "has_spec", "top speed"),
]
ENTITIES = ["Acme Robotics", "Northwind Industries", "Pallet Pup"]


def embed(texts):
    return [d.embedding for d in client.embeddings.create(model=EMBED_MODEL, input=texts).data]


# indexa els chunks a Chroma (el recuperador vectorial) ------------------------------
collection = chromadb.Client().create_collection("acme-graph")
ids = list(DOCS)
collection.add(ids=ids, documents=[DOCS[i] for i in ids], embeddings=embed([DOCS[i] for i in ids]))

# quins chunks esmenten quina entitat (el vincle graf<->text, creat durant la ingesta) ---
mentions = {e: [cid for cid, t in DOCS.items() if e.lower() in t.lower()] for e in ENTITIES}
# adjacència: entitat -> entitats a què apunta
adj = {}
for h, _rel, t in TRIPLES:
    adj.setdefault(h, []).append(t)


def walk(seeds, max_hops=2):
    """BFS sobre el graf a partir de les entitats de la pregunta; retorna les entitats trobades, en ordre."""
    found, frontier = list(seeds), list(seeds)
    for _ in range(max_hops):
        nxt = [t for e in frontier for t in adj.get(e, []) if t not in found]
        found += nxt
        frontier = nxt
    return found


def rrf_merge(rankings, weights, k=RRF_K):
    """Fusiona llistes ordenades: score(id) = suma(pes / (k + rang)). Reordena per puntuació."""
    scores = {}
    for ranking, w in zip(rankings, weights):
        for rank, cid in enumerate(ranking):
            scores[cid] = scores.get(cid, 0.0) + w / (k + rank)
    return sorted(scores, key=scores.get, reverse=True)


question = "How fast is the robot built by the company that acquired Acme Robotics?"

# 1) recuperador vectorial — la base de referència, ordenat per similitud
vec_hits = collection.query(query_embeddings=embed([question]), n_results=len(DOCS))
vector_ranking = vec_hits["ids"][0]

# 2) recuperador de graf — sembra amb les entitats de la pregunta, recorre-les i recull chunks
seeds = [e for e in ENTITIES if e.lower() in question.lower()]   # {Acme Robotics}
path = walk(seeds, max_hops=2)                                   # Acme -> Northwind -> Pallet Pup
graph_ranking = []
for ent in reversed(path):              # l'entitat més profunda primer — l'extrem de la cadena on hi ha la resposta
    for cid in mentions.get(ent, []):
        if cid not in graph_ranking:
            graph_ranking.append(cid)

# 3) fusiona
fused = rrf_merge([vector_ranking, graph_ranking], weights=[1.0, GRAPH_WEIGHT])

print(f"pregunta: {question}\n")
print(f"només vector top-{TOP_K}: {vector_ranking[:TOP_K]}   (pont d1? resposta d2?)")
print(f"salt de graf des de {seeds}: {' -> '.join(path)}")
print(f"rànquing de graf:        {graph_ranking}")
print(f"KG-RAG fusionat top-{TOP_K}: {fused[:TOP_K]}   (pont + resposta recuperats)\n")

context = "\n".join(f"- {DOCS[c]}" for c in fused[:TOP_K])
resp = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "Answer using only the context. If it is not there, say so."},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
    ],
)
print(resp.choices[0].message.content)
