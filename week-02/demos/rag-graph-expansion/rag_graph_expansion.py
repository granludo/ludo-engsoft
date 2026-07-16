"""Expansió de grafs + RRF – recuperar per connexió, i després fusionar.

El vector RAG troba chunks que *sembla* ser la pregunta. Falleix quan la resposta és una cadena de documents i el pont chunk no comparteix paraules amb la pregunta. Aquí: "Quina velocitat té el robot creat per l'empresa que va adquirir Acme?", necessita Acme -> Northwind -> Pallet Pup -> 2,1 m/s, però el pont ("Northwind crea el Pallet Pup") mai es menciona "Acme" o "ràpid", de manera que el cosinus la classifica com a baixa.

La solució consisteix en una segona execució de recuperació, paral·lel a la primera: extreu les entitats de la pregunta, recorre un graf de coneixement amb un o dos passos sobre relacions tipificades, i recopila els chunks que trobes. Després, combina les dues llistes classificades mitjançant Reciprocal Rank Fusion. El graf arriba al pont per connexió; RRF permet que arribi a la posició K sense desplaçar el que ja ha trobat la cerca vectorial.

Números relacionats amb aquesta idea: TFG d'Adrià Guilera Bernabé (FIB-UPC, 2026) — una capa de graf sobre el servidor kb de LAMB, mesurada a HotPotQA / MuSiQue / 2WikiMultihopQA.

Executar: `uv venv && source .venv/bin/activate && uv sync && python rag_graph_expansion.py`
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

TOP_K = 4              # chunks Ara ens centrem en el model. La cadena de respostes aquí consta de 3 documents (Acme -> Northwind -> Pallet Pup) + espai per a noves aportacions.
RRF_K = 20             # Constanta de reducció del rang (el paper "Rank-Damping" fa servir un valor de 60; Adrià fa servir un valor de 20)
GRAPH_WEIGHT = 0.85    # Quant les llistes de grafs i les llistes de vectors tenen elements?

# --- El conjunt de dades: dissenyat perquè el pont chunk (d1) sigui lèxicament diferent de la pregunta ---
DOCS = {
    "d0": "Acme Robotics was a Barcelona startup founded in 2019. In 2024 it was acquired by Northwind Industries.",
    "d1": "Northwind Industries is a logistics-automation firm. Its flagship product is the Pallet Pup, an autonomous warehouse robot.",  # el pont
    "d2": "The Pallet Pup has a top speed of 2.1 m/s and an eight-hour battery.",  # la resposta
    "d3": "Acme Robotics' early prototypes were shelf-scanning drones, not ground robots.",  # Atrair: Acme + robot
    "d4": "Warehouse robots typically move between 1 and 3 meters per second depending on payload.",  # Atrair: robot + velocitat
    "d5": "Northwind Industries reported strong revenue growth in its 2025 annual report.",  # element que distrae l'atenció
}

# Relacions tipades a partir de les quals es construeix el graf. En l'ús real, s'extreuen a
# consumit per un LLM (veure el fitxer README – els sistemes de NER clàssics només donen informació sobre la coexistència, no
# relacions tipades); les enviem ja extretes, de manera que la demostració és determinista.
TRIPLES = [
    ("Acme Robotics", "acquired_by", "Northwind Industries"),
    ("Northwind Industries", "builds", "Pallet Pup"),
    ("Pallet Pup", "has_spec", "top speed"),
]
ENTITIES = ["Acme Robotics", "Northwind Industries", "Pallet Pup"]


def embed(texts):
    return [d.embedding for d in client.embeddings.create(model=EMBED_MODEL, input=texts).data]


# Indexar el chunks a Chroma (el sistema de recuperació vectorial) ------------------------------
collection = chromadb.Client().create_collection("acme-graph")
ids = list(DOCS)
collection.add(ids=ids, documents=[DOCS[i] for i in ids], embeddings=embed([DOCS[i] for i in ids]))

# que chunks indica quina entitat (el vincle entre el graf i el text, creat durant la incorporació) ---
mentions = {e: [cid for cid, t in DOCS.items() if e.lower() in t.lower()] for e in ENTITIES}
# proximitat: entitat -> les entitats a les quals fa referència
adj = {}
for h, _rel, t in TRIPLES:
    adj.setdefault(h, []).append(t)


def walk(seeds, max_hops=2):
    """Algoritme de BFS sobre el graf a partir dels elements de la pregunta; retornar els elements trobats, en ordre."""
    found, frontier = list(seeds), list(seeds)
    for _ in range(max_hops):
        nxt = [t for e in frontier for t in adj.get(e, []) if t not in found]
        found += nxt
        frontier = nxt
    return found


def rrf_merge(rankings, weights, k=RRF_K):
    """Classificació per fusió: puntuació(id) = suma(pes / (k + rang)). Reordenar per puntuació."""
    scores = {}
    for ranking, w in zip(rankings, weights):
        for rank, cid in enumerate(ranking):
            scores[cid] = scores.get(cid, 0.0) + w / (k + rank)
    return sorted(scores, key=scores.get, reverse=True)


question = "How fast is the robot built by the company that acquired Acme Robotics?"

# 1) Recollidor de vectors – el punt de partida, classificat per similaritat
vec_hits = collection.query(query_embeddings=embed([question]), n_results=len(DOCS))
vector_ranking = vec_hits["ids"][0]

# 2) Recollidor de grafs – Començar amb les entitats de la pregunta, fer un recorregut i recollir chunks
seeds = [e for e in ENTITIES if e.lower() in question.lower()]   # {Robòtica Acme}
path = walk(seeds, max_hops=2)                                   # Acme -> Northwind -> Pallet Pup
graph_ranking = []
for ent in reversed(path):              # l'entitat més fonamental per primera – la resposta és el final de la cadena
    for cid in mentions.get(ent, []):
        if cid not in graph_ranking:
            graph_ranking.append(cid)

# 3) fusó
fused = rrf_merge([vector_ranking, graph_ranking], weights=[1.0, GRAPH_WEIGHT])

print(f"question: {question}\n")
print(f"vector-only top-{TOP_K}: {vector_ranking[:TOP_K]}   (bridge d1? answer d2?)")
print(f"graph hop from {seeds}: {' -> '.join(path)}")
print(f"graph ranking:        {graph_ranking}")
print(f"KG-RAG fused top-{TOP_K}: {fused[:TOP_K]}   (bridge + answer recovered)\n")

context = "\n".join(f"- {DOCS[c]}" for c in fused[:TOP_K])
resp = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "Answer using only the context. If it is not there, say so."},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
    ],
)
print(resp.choices[0].message.content)
