# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# Curs per a agents de BSC — Transformers, LLMs, RAG i Agents: Des del teòric fins a la pràctica
# Amb llicència Creative Commons BY-NC-SA 4.0 – és obligatori citar l'autor, no es pot fer ús comercial, i les obres derivades han de tenir la mateixa llicència.

"""RAG d'un sol fitxer — fer trampes al solitari, en forma de xat.

Sense chunking, sense índex, sense recuperació. Llegeix tot el fitxer de coneixement,
enganxa'l a la prompt a cada torn i conversa-hi. El model "sap" la resposta perquè la
té al context. El truc —i tota la lliçó— és que reenvies TOT el fitxer a cada torn:
mira com puja prompt_tokens mentre les teves preguntes es mantenen curtes.

Línia en blanc per sortir. Sense persistència — la conversa viu en memòria durant aquesta execució.
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

# Tot el fitxer esdevé el context. Sense selecció — tot hi entra, a cada torn.
context = open(os.path.join(os.path.dirname(__file__), "knowledge.txt")).read()
SYSTEM = "Answer using only the context. If it is not there, say so."

history = []  # la conversa fins ara — només els torns nus (el que guarda una interfície de xat real)
print(f"Xat RAG d'un sol fitxer · model={MODEL} · knowledge.txt ({len(context)} caràcters)")
print("Pregunta sobre el document. Línia en blanc per sortir.\n")

while True:
    question = input("tu> ").strip()
    if not question:
        break

    # RAG naïf: enganxa TOT el fitxer al costat de la pregunta — reconstruït a cada torn.
    augmented = f"Context:\n----\n{context}\n----\n\nQuestion: {question}"
    messages = [{"role": "system", "content": SYSTEM}] + history + [{"role": "user", "content": augmented}]

    resp = client.chat.completions.create(model=MODEL, messages=messages)
    answer = resp.choices[0].message.content
    print(f"bot> {answer}")
    print(f"     [{resp.usage.prompt_tokens} prompt tokens — el fitxer sencer hi ha tornat a viatjar]\n")

    # Recorda només els torns nus, no el missatge augmentat — així el fitxer NO
    # s'acumula a la història; es torna a injectar de nou al torn següent.
    history += [{"role": "user", "content": question},
                {"role": "assistant", "content": answer}]
