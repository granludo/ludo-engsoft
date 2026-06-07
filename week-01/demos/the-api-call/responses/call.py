# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# BSC Agents Course — Transformers, LLMs, RAG and Agents: From Theory to Production
# Licensed under Creative Commons BY-NC-SA 4.0 — reuse must credit the author, no commercial use, derivatives under the same license.

"""Responses API — OpenAI's newer endpoint, via the openai SDK."""
import os

from openai import OpenAI

# OPENAI_ENDPOINT + MODEL come from .env. Note: the Responses API is
# OpenAI-specific — most OpenAI-compatible providers (Ollama included) do not
# implement /v1/responses, so this one usually needs to point at OpenAI.
client = OpenAI(
    base_url=os.environ.get("OPENAI_ENDPOINT", "https://api.openai.com/v1"),
    api_key=os.environ.get("OPENAI_API_KEY"),
)
model = os.environ.get("MODEL", "gpt-4.1-mini")

resp = client.responses.create(
    model=model,
    instructions="You are a terse assistant.",
    input="Say hello in one sentence.",
)

print(resp.output_text)
print(resp.usage)  # input / output / total tokens
