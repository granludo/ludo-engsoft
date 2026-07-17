# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# Curs d'agents de BSC — Transformers, LLMs, RAG i Agents: De la teoria a la producció
# Amb llicència Creative Commons BY-NC-SA 4.0 – és obligatori citar l'autor, no es pot fer ús comercial, i les obres derivades han de tenir la mateixa llicència.

"""Simple dynamic RAG — el truc d'un sol fitxer, però amb una base de dades al darrere.

La mateixa forma que el RAG d'un sol fitxer: una plantilla de prompt amb {context} i {user_input},
només els torns nus a l'historial, el model fonamentat en el que li donem. UNA cosa ha canviat:
d'on ve el context. En comptes d'enganxar un fitxer sencer a cada torn:

  1. agafa el {user_input} i fes-lo servir com a CONSULTA,
  2. consulta la col·lecció: els top-K chunks que superen el llindar de similitud,
  3. formata'ls (markdown, amb les metadades del seu origen),
  4. insereix això a la plantilla de prompt, pregunta i respon.

Ara el coneixement pot ser tan gran com vulguis — cinquanta documents, mil — i cada torn continua
enviant només un grapat de chunks rellevants. Primer ingesta els documents amb ingest.py.
Línia en blanc per sortir.
"""
import os
from dotenv import load_dotenv
from openai import OpenAI

from collections_manager import create_collection, query

load_dotenv()

client = OpenAI(
    base_url=os.environ.get("OPENAI_ENDPOINT", "http://localhost:11434/v1"),
    api_key=os.environ.get("OPENAI_API_KEY", "ollama"),
)
MODEL = os.environ.get("MODEL", "qwen3:1.7b")
TOP_K = int(os.environ.get("TOP_K", "4"))
THRESHOLD = float(os.environ.get("THRESHOLD", "0.4"))   # similitud de cosinus mínima

col = create_collection(os.environ.get("COLLECTION", "handbook"),
                        metric="cosine",
                        persist_path=os.environ.get("PERSIST_PATH", "./collections-store"))

SYSTEM = "Answer using only the context. If it is not there, say so."
TEMPLATE = "Context:\n----\n{context}\n----\n\nQuestion: {user_input}"


def format_context(hits: list[dict]) -> str:
    """Formata els chunks recuperats com a markdown, cadascun amb la seva procedència."""
    blocks = []
    for h in hits:
        m = h["metadata"]
        blocks.append(f"[{m['title']} · chunk {m['chunk_number']} · {m['md_url']} "
                      f"· similarity {h['similarity']:.3f}]\n{h['chunk']}")
    return "\n\n".join(blocks)


print(f"Simple dynamic RAG · model={MODEL} · collection={col.name} ({col.count()} chunks) "
      f"· top-{TOP_K} over {THRESHOLD}")
print("Pregunta sobre els documents ingerits. Línia en blanc per sortir.\n")

history = []  # només torns nus — els chunks recuperats es reconstrueixen a cada torn, mai s'emmagatzemen

while True:
    user_input = input("tu> ").strip()
    if not user_input:
        break

    # Augmentació dinàmica: l'entrada de l'usuari ÉS la consulta.
    hits = query(col, user_input, top_k=TOP_K, threshold=THRESHOLD)
    if not hits:
        print(f"bot> (nothing in the collection passes similarity {THRESHOLD} — "
              f"ingest more documents, or lower THRESHOLD)\n")
        continue

    augmented = TEMPLATE.format(context=format_context(hits), user_input=user_input)
    messages = [{"role": "system", "content": SYSTEM}] + history + [{"role": "user", "content": augmented}]

    resp = client.chat.completions.create(model=MODEL, messages=messages)
    answer = resp.choices[0].message.content
    print(f"bot> {answer}")
    retrieved = ", ".join(f"{h['metadata']['source']}::{h['metadata']['chunk_number']}"
                          f"({h['similarity']:.2f})" for h in hits)
    print(f"     [retrieved {retrieved}]")
    print(f"     [{resp.usage.prompt_tokens} prompt tokens — {len(hits)} chunks rode along, "
          f"out of {col.count()} in the collection]\n")

    history += [{"role": "user", "content": user_input},
                {"role": "assistant", "content": answer}]
