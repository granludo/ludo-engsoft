# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# Curs d'agents del BSC — Transformers, LLMs, RAG i Agents: de la teoria a la producció
# Amb llicència Creative Commons BY-NC-SA 4.0 – és obligatori citar l'autor, no es pot fer ús comercial, i les obres derivades han de tenir la mateixa llicència.

"""
Crida un LLM a través de l'API de Chat Completions compatible amb OpenAI.

Funciona SENSE CANVIS contra:
  - el teu Ollama local        (l'opció per defecte: sense clau, sense diners, sense Internet)
  - OpenAI / OpenRouter / Groq (defineix OPENAI_ENDPOINT i OPENAI_API_KEY al .env)

El wire format és el mateix a tot arreu. Només canvia el .env.
"""
import os

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # carrega OPENAI_ENDPOINT / OPENAI_API_KEY / MODEL d'un fitxer .env local

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
print("Ús:", resp.usage)             # tokens del prompt / de la resposta / totals
print("Motiu de finalització:", resp.choices[0].finish_reason)
