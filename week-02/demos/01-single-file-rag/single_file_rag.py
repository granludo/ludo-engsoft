# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# Curs per a agents de BSC — Transformers, LLMs, RAG i Agents: Des del teòric fins a la pràctica
# Amb llicència Creative Commons BY-NC-SA 4.0 – és obligatori citar l'autor, no es pot fer ús comercial, i les obres derivades han de tenir la mateixa llicència.

"""RAG en fila sol – una manera de jugar a "solitaire" de forma estratègica, com si fos un programa de xat.

No chunking, sense índex, sense recuperació. Llegiu tot el fitxer de coneixement i feu-ho copiar a la prompt en cada ocasió, i converseu amb ell. El model "sabeix" perquè la resposta està al seu context. L'adéu — i la lliçona principal — és que heu d'enviar TOT el fitxer en cada ocasió: observeu com augmenta el nombre de tokens de consulta mentre les vostres preguntes romanen curtes.

Línia en blanc per sortir. Sense persistència – la conversa es manté en memòria durant aquesta sessió.
"""
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url=os.environ.get("OPENAI_ENDPOINT", "http://localhost:11434/v1"),
    api_key=os.environ.get("OPENAI_API_KEY", "ollama"),
)
MODEL = os.environ.get("MODEL", "qwen3:1.7b")

# Tot el fitxer esdevé el context. Sense seleccions – tot s'inclou, cada pas.
context = open(os.path.join(os.path.dirname(__file__), "knowledge.txt")).read()
SYSTEM = "Answer using only the context. If it is not there, say so."

history = []  # La conversa fins ara – només les funcions bàsiques (com una interfície de conversa real hauria de tenir)
print(f"Single-file RAG chat · model={MODEL} · knowledge.txt ({len(context)} chars)")
print("Pregunte sobre el document. Línia en blanc per sortir.")

while True:
    question = input("tu").strip()
    if not question:
        break

    # Naïvi RAG: copia l'arxiu complet al costat de la pregunta – reconstruint-lo a cada pas.
    augmented = f"Context:\n----\n{context}\n----\n\nQuestion: {question}"
    messages = [{"role": "system", "content": SYSTEM}] + history + [{"role": "user", "content": augmented}]

    resp = client.chat.completions.create(model=MODEL, messages=messages)
    answer = resp.choices[0].message.content
    print(f"bot> {answer}")
    print(f"     [{resp.usage.prompt_tokens} prompt tokens — the whole file rode along again]\n")

    # Recordeu només les parts bàsiques, no el missatge ampliat – per tant, el fitxer NO és…
    # acumulats al llarg de la història; es tornen a injectar frescos en el següent cop.
    history += [{"role": "user", "content": question},
                {"role": "assistant", "content": answer}]
