# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# Curs per a agents de BSC — Transformers, LLMs, RAG i Agents: Des del teòric fins a la pràctica
# Amb llicència Creative Commons BY-NC-SA 4.0 – és obligatori citar l'autor, no es pot fer ús comercial, i les obres derivades han de tenir la mateixa llicència.

"""
Transmetre la finalització d'un missatge de chat: obtenir els tokens a mesura que es generen, en comptes d'esperar a que s'acabi la resposta completa.

Una crida normal es bloqueja fins que el model ha generat cada token, i després retorna la cadena final. Amb `stream=True`, en canvi, el API envia una seqüència de petits *chunks*, un (o alguns) tokens alhora, mentre el model els descodifica. Imprimeix cada chunk tan aviat com arriba — aquesta és l'efecte del tipografador que veieu a ChatGPT. No hi ha cap canvi en el model; només en la manera de rebre les dades.

Executa'u: `cp ../.env.example .env` # Defineix les variables OPENAI_ENDPOINT, OPENAI_API_KEY i MODEL amb els valors corresponents. Després executa: `python stream.py --with openai --with python-dotenv`
"""

import os

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # extreure la variable `OPENAI_ENDPOINT`, `OPENAI_API_KEY` i `MODEL` d'un fitxer `.env` local.

client = OpenAI(
    base_url=os.environ.get("OPENAI_ENDPOINT", "https://api.openai.com/v1"),
    api_key=os.environ.get("OPENAI_API_KEY"),
)
model = os.environ.get("MODEL", "gpt-4.1-mini")

# `stream=True` transforma la resposta en un iterador que conté una llista amb un element: chunks.
# `stream_options` demana al servidor que enviï l'últim fragment que conté la informació d'ús.
# (una resposta normal no inclou l'ús, a menys que no sigui el cas).
stream = client.chat.completions.create(
    model=model,
    messages=[{"role": "user", "content": "Write a short paragraph about why streaming feels faster, even when total time is the same."}],
    stream=True,
    stream_options={"include_usage": True},
)

usage = None
for chunk in stream:
    # La majoria de les chunks tenen una delta amb una mica més de text. Imprimeu-la immediatament.
    # amb `flush=True`, per tal que s'mostri immediatment i no quan el búfer estigui ple.
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
    # L'últim element (chunk, per tal d'incloure l'ús) té opcions buides i el
    # token per a tot el contingut de la resposta.
    if chunk.usage:
        usage = chunk.usage

print()  # línia en blanc després del text transmesa
if usage:
    print("Ús:", usage)
