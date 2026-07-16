# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# Curs per a agents de BSC — Transformers, LLMs, RAG i Agents: Des del teòric fins a la pràctica
# Amb llicència Creative Commons BY-NC-SA 4.0 – és obligatori citar l'autor, no es pot fer ús comercial, i les obres derivades han de tenir la mateixa llicència.

"""
Envieu una imatge a la Chat Completions i a la API.

Un model multimodal pot llegir imatges així com text. El format de cable és el mateix que les "llamades" de chat-completions que ja coneixeu: la única diferència és la forma del missatge `content`: en lloc d'una cadena senzilla, es converteix en una *llista* de parts, i una d'aquestes parts és una imatge (proporcionada a través d'un URL públic, o inclosa com una URI base64 `data:`). El que resta —l'endpoint, l'SDK, el registre d'ús— és idèntic.

Necessiteu un model amb capacitat de processament d'imatges (per exemple, gpt-4.1-mini, gpt-4o). Un petit model local normalment no pot processar imatges.

Executa-ho: cp ../.env.example .env          # defineix el MODEL de visió + la teva clau uv executa --amb openai --amb python-dotenv python send_image.py                  # l'aplicació Great A'Tuin executa --amb openai --amb python-dotenv python send_image.py path/to/photo.jpg executa --amb openai --amb python-dotenv python send_image.py https://example.com/photo.jpg
"""

import base64
import os
import sys

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # extreure la variable `OPENAI_ENDPOINT`, `OPENAI_API_KEY` i `MODEL` d'un fitxer `.env` local.

client = OpenAI(
    base_url=os.environ.get("OPENAI_ENDPOINT", "https://api.openai.com/v1"),
    api_key=os.environ.get("OPENAI_API_KEY"),
)
model = os.environ.get("MODEL", "gpt-4.1-mini")  # ha de poder veure imatges

# Sense cap dubte, enviem la imatge de Great A'Tuin completa (tartanes per tot arreu).
# (després). Passeu el vostre fitxer d'imatge o URL com a primer argument per utilitzar-lo.
default_img = os.path.join(os.path.dirname(__file__), "great-atuin.png")
image = sys.argv[1] if len(sys.argv) > 1 else default_img

# Una imatge es pot incloure en el missatge, ja sigui com a URL, que és una imatge que el servidor pot obtenir, o bé com a...
# URI de dades base64 que s'inclou directament (útil per a fitxers locals o imatges privades).
if image.startswith(("http://", "https://")):
    image_url = image
else:
    with open(image, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    ext = image.rsplit(".", 1)[-1].lower()
    image_url = f"data:image/{ext};base64,{b64}"

resp = client.chat.completions.create(
    model=model,
    messages=[
        {
            "role": "user",
            # El contingut ara és una llista de parts, no simplement una cadena de caràcters:
            "content": [
                {"type": "text", "text": "Describe this image. What is holding up the world — and what is holding up that?"},
                {"type": "image_url", "image_url": {"url": image_url}},
            ],
        }
    ],
)

print(resp.choices[0].message.content)
print("Ús:", resp.usage)
