# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# Curs per a agents de BSC — Transformers, LLMs, RAG i Agents: Des del teòric fins a la pràctica
# Amb llicència Creative Commons BY-NC-SA 4.0 – és obligatori citar l'autor, no es pot fer ús comercial, i les obres derivades han de tenir la mateixa llicència.

"""
Streaming d'una chat completion: obtén els tokens a mesura que es generen, en comptes
d'esperar tota la resposta.

Una crida normal es bloqueja fins que el model ha generat tots els tokens i llavors
retorna la cadena final. Amb `stream=True`, en canvi, l'API envia una seqüència de
petits *chunks*, un (o uns quants) tokens cada cop, a mesura que el model els
descodifica. Imprimeixes cada chunk tan bon punt arriba: és l'efecte de màquina
d'escriure que veus a ChatGPT. El model no canvia gens; només canvia la manera com
t'arriben les dades.

Executa-ho:
    cp ../.env.example .env   # defineix OPENAI_ENDPOINT, OPENAI_API_KEY i MODEL
    uv run --with openai --with python-dotenv python stream.py
"""

import os

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # llegeix `OPENAI_ENDPOINT`, `OPENAI_API_KEY` i `MODEL` d'un fitxer `.env` local

client = OpenAI(
    base_url=os.environ.get("OPENAI_ENDPOINT", "https://api.openai.com/v1"),
    api_key=os.environ.get("OPENAI_API_KEY"),
)
model = os.environ.get("MODEL", "gpt-4.1-mini")

# `stream=True` converteix la resposta en un iterador de chunks.
# `stream_options` demana al servidor que enviï un últim chunk amb el registre d'ús
# (una resposta en streaming normal, altrament, no inclou l'ús).
stream = client.chat.completions.create(
    model=model,
    messages=[{"role": "user", "content": "Write a short paragraph about why streaming feels faster, even when total time is the same."}],
    stream=True,
    stream_options={"include_usage": True},
)

usage = None
for chunk in stream:
    # La majoria de chunks porten una delta amb una mica més de text. Imprimeix-la a
    # l'instant, amb `flush=True` perquè es mostri de seguida i no quan s'ompli el búfer.
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
    # L'últim chunk de tots (a causa d'include_usage) té les choices buides i
    # l'ús de tokens de tota la resposta.
    if chunk.usage:
        usage = chunk.usage

print()  # salt de línia després del text emès en streaming
if usage:
    print("\nús:", usage)
