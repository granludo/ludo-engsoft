# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# BSC Agents Course — Transformers, LLMs, RAG and Agents: From Theory to Production
# Licensed under Creative Commons BY-NC-SA 4.0 — reuse must credit the author, no commercial use, derivatives under the same license.

"""
Send an image to the Chat Completions API.

A multimodal model can read images as well as text. The wire format is the same
chat-completions call you already know — the only change is the shape of a
message's `content`: instead of a plain string, it becomes a *list* of parts,
and one of the parts is an image (given as a public URL, or inlined as a
base64 `data:` URI). Everything else — the endpoint, the SDK, the usage record —
is identical.

You need a vision-capable model (e.g. gpt-4.1-mini, gpt-4o). A tiny local model
usually cannot see images.

Run it:
    cp ../.env.example .env          # set a vision MODEL + your key
    uv run --with openai python send_image.py                  # the bundled Great A'Tuin
    uv run --with openai python send_image.py path/to/photo.jpg
    uv run --with openai python send_image.py https://example.com/photo.jpg
"""

import base64
import os
import sys

from openai import OpenAI

client = OpenAI(
    base_url=os.environ.get("OPENAI_ENDPOINT", "https://api.openai.com/v1"),
    api_key=os.environ.get("OPENAI_API_KEY"),
)
model = os.environ.get("MODEL", "gpt-4.1-mini")  # must be able to see images

# With no argument we send the bundled Great A'Tuin image (turtles all the way
# down). Pass your own image file or URL as the first argument to use that.
default_img = os.path.join(os.path.dirname(__file__), "great-atuin.png")
image = sys.argv[1] if len(sys.argv) > 1 else default_img

# An image goes into the message either as a URL the server can fetch, or as a
# base64 data URI you inline (handy for local files / private images).
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
            # content is now a LIST of parts, not a plain string:
            "content": [
                {"type": "text", "text": "Describe this image. What is holding up the world — and what is holding up that?"},
                {"type": "image_url", "image_url": {"url": image_url}},
            ],
        }
    ],
)

print(resp.choices[0].message.content)
print("\nusage:", resp.usage)
