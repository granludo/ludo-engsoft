# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# Curs per a agents de BSC — Transformers, LLMs, RAG i Agents: Des del teòric fins a la pràctica
# Amb llicència Creative Commons BY-NC-SA 4.0 – és obligatori citar l'autor, no es pot fer ús comercial, i les obres derivades han de tenir la mateixa llicència.

"""Dinàmica senzilla RAG – un sistema de "trucs" senzill, amb una base de dades al darrere.

Misma forma que RAG: un prompt de plantilla amb {context} i {usuari}, amb històries sense estructura, el model basat en la informació que li proporcionem. UNA cosa ha canviat: l'origen del context. En comptes de copiar tot el fitxer cada vegada:

  1. utilitzeu la {user_input} com a consulta.
  2. consultar la col·lecció: els K elements més similars, superant el límit de similitud, chunks.
  3. formateu-los (en format Markdown, amb les metadades originals).
  4. Insereix-ho al model prompt, pregunta i respon.

El coneixement pot ser tan gran com vulgueu – cinquanta documents, mil – i cada vegada només s'extreuen unes quantes dades rellevants chunks. Primer, utilitzeu el fitxer `ingest.py` per importar els documents. Poseu una línia en blanc per finalitzar.
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
THRESHOLD = float(os.environ.get("THRESHOLD", "0.4"))   # similaritat del cosinus mínim

col = create_collection(os.environ.get("COLLECTION", "handbook"),
                        metric="cosine",
                        persist_path=os.environ.get("PERSIST_PATH", "./collections-store"))

SYSTEM = "Answer using only the context. If it is not there, say so."
TEMPLATE = "Context:\n----\n{context}\n----\n\nQuestion: {user_input}"


def format_context(hits: list[dict]) -> str:
    """Formateu les dades recuperades (chunks) en format Markdown, incloent la seva procedència."""
    blocks = []
    for h in hits:
        m = h["metadata"]
        blocks.append(f"[{m['title']} · chunk {m['chunk_number']} · {m['md_url']} "
                      f"· similarity {h['similarity']:.3f}]\n{h['chunk']}")
    return "\n\n".join(blocks)


print(f"Simple dynamic RAG · model={MODEL} · collection={col.name} ({col.count()} chunks) "
      f"· top-{TOP_K} over {THRESHOLD}")
print("Pregunte sobre els documents ingerits. Línia en blanc per sortir.")

history = []  # El joc BARE només crea peces – cada ronda, chunks peces es creen de nou, però no s'emmagatzemen.

while True:
    user_input = input("tu").strip()
    if not user_input:
        break

    # Augmentació dinàmica: la entrada de l'usuari és la consulta.
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
