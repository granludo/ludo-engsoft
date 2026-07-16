# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# Curs per a agents de BSC — Transformers, LLMs, RAG i Agents: Des del teòric fins a la pràctica
# Amb llicència Creative Commons BY-NC-SA 4.0 – és obligatori citar l'autor, no es pot fer ús comercial, i les obres derivades han de tenir la mateixa llicència.

"""
Truqueu a través del LLM mitjançant un OpenAI compatible amb el Chat Completions, utilitzant el API.

Resultats sense canvi contra:
  - el vostre lloc local Ollama (l'opció per defecte – sense clau, sense diners, sense connexió a Internet)
  - OpenAI / OpenRouter / Groq (configureu les variables `OPENAI_ENDPOINT` i `OPENAI_API_KEY` al fitxer `.env`)

wire format és el mateix en tots els casos. Només el fitxer ".env" canvia.
"""
import os

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # extreure la variable `OPENAI_ENDPOINT`, `OPENAI_API_KEY` i `MODEL` d'un fitxer `.env` local.

client = OpenAI(
    base_url=os.environ.get("OPENAI_ENDPOINT", "http://localhost:11434/v1"),
    api_key=os.environ.get("OPENAI_API_KEY", "ollama"),  # Ollama ignora el valor
)
model = os.environ.get("MODEL", "ministral-3:8b")

resp = client.chat.completions.create(
    model=model,
    messages=[
        {"role": "system", "content": "You are a terse assistant."},
        {"role": "user",   "content": "Say hello in one sentence."},
    ],
    temperature=0.7,
)

print(resp.choices[0].message.content)
print("---")
print("Ús:", resp.usage)             # prompt / finalització / total tokens
print("Motiu per finalitzar:", resp.choices[0].finish_reason)
