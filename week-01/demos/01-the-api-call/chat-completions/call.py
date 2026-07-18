# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# Curs per a agents de BSC — Transformers, LLMs, RAG i Agents: Des del teòric fins a la pràctica
# Amb llicència Creative Commons BY-NC-SA 4.0 – és obligatori citar l'autor, no es pot fer ús comercial, i les obres derivades han de tenir la mateixa llicència.

"""Chat Completions API — l'endpoint clàssic, a través de l'SDK d'OpenAI."""
import os

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # llegeix `OPENAI_ENDPOINT`, `OPENAI_API_KEY` i `MODEL` d'un fitxer `.env` local

# `OPENAI_ENDPOINT` orienta l'SDK cap a qualsevol API compatible amb OpenAI (OpenAI,
# OpenRouter, Groq, un Ollama local, ...); `MODEL` tria el model. Tots dos surten de
# .env — els valors per defecte de sota apunten a OpenAI mateix.
client = OpenAI(
    base_url=os.environ.get("OPENAI_ENDPOINT", "https://api.openai.com/v1"),
    api_key=os.environ.get("OPENAI_API_KEY"),
)
model = os.environ.get("MODEL", "gpt-4.1-mini")

resp = client.chat.completions.create(
    model=model,
    messages=[
        {"role": "system", "content": "You are a terse assistant."},
        {"role": "user",   "content": "Say hello in one sentence."},
    ],
    temperature=0.7,
)

print(resp.choices[0].message.content)
print(resp.usage)  # tokens de prompt / de compleció / totals
