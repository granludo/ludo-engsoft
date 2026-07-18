# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# Curs per a agents de BSC — Transformers, LLMs, RAG i Agents: Des del teòric fins a la pràctica
# Amb llicència Creative Commons BY-NC-SA 4.0 – és obligatori citar l'autor, no es pot fer ús comercial, i les obres derivades han de tenir la mateixa llicència.

"""
Envia una imatge a la Chat Completions API.

Un model multimodal pot llegir imatges igual que text. El wire format és la mateixa
crida de chat-completions que ja coneixes: l'única diferència és la forma del
`content` d'un missatge: en lloc d'una cadena simple, passa a ser una *llista* de
parts, i una d'aquestes parts és una imatge (indicada com un URL públic, o
incrustada com una URI `data:` en base64). Tota la resta —l'endpoint, l'SDK, el
registre d'ús— és idèntica.

Necessites un model amb capacitat de visió (per exemple, gpt-4.1-mini, gpt-4o). Un
model local diminut normalment no pot veure imatges.

Executa-ho:
    cp ../.env.example .env          # defineix un MODEL de visió + la teva clau
    uv run --with openai --with python-dotenv python send_image.py                  # la Great A'Tuin inclosa
    uv run --with openai --with python-dotenv python send_image.py path/to/photo.jpg
    uv run --with openai --with python-dotenv python send_image.py https://example.com/photo.jpg
"""

import base64
import os
import sys

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # llegeix `OPENAI_ENDPOINT`, `OPENAI_API_KEY` i `MODEL` d'un fitxer `.env` local

client = OpenAI(
    base_url=os.environ.get("OPENAI_ENDPOINT", "https://api.openai.com/v1"),
    api_key=os.environ.get("OPENAI_API_KEY"),
)
model = os.environ.get("MODEL", "gpt-4.1-mini")  # ha de poder veure imatges

# Sense cap argument, enviem la imatge de la Great A'Tuin inclosa (tortugues fins al
# fons de tot). Passa el teu propi fitxer d'imatge o URL com a primer argument per fer-lo servir.
default_img = os.path.join(os.path.dirname(__file__), "great-atuin.png")
image = sys.argv[1] if len(sys.argv) > 1 else default_img

# Una imatge entra al missatge com un URL que el servidor pot obtenir, o bé com una
# URI de dades en base64 que incrustes directament (útil per a fitxers locals o imatges privades).
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
            # el contingut ara és una LLISTA de parts, no una simple cadena:
            "content": [
                {"type": "text", "text": "Describe this image. What is holding up the world — and what is holding up that?"},
                {"type": "image_url", "image_url": {"url": image_url}},
            ],
        }
    ],
)

print(resp.choices[0].message.content)
print("\nús:", resp.usage)
