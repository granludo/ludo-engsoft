# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# BSC Agents Course — Transformers, LLMs, RAG and Agents: From Theory to Production
# Licensed under Creative Commons BY-NC-SA 4.0 — reuse must credit the author, no commercial use, derivatives under the same license.

"""Chat Completions API — the classic endpoint, via the openai SDK."""
import os

from openai import OpenAI

# OPENAI_ENDPOINT points the SDK at any OpenAI-compatible API (OpenAI,
# OpenRouter, Groq, a local Ollama, ...); MODEL picks the model. Both come from
# .env — the defaults below hit OpenAI itself.
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
print(resp.usage)  # prompt / completion / total tokens
