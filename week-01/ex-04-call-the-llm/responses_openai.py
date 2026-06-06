# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# BSC Agents Course — Transformers, LLMs, RAG and Agents: From Theory to Production
# Licensed under Creative Commons BY-NC-SA 4.0 — reuse must credit the author, no commercial use, derivatives under the same license.

"""
The Responses API — OpenAI's newer endpoint.

NOTE: this one is OpenAI-specific. Ollama does NOT implement /v1/responses,
so this script only runs against OpenAI (or a provider that supports it).
That is the lesson: chat/completions is the portable wire format that runs
on your laptop; the Responses API is not (yet) universal.

Needs a real OPENAI_API_KEY (and OPENAI_BASE_URL unset or pointing at OpenAI).
"""
import os

from openai import OpenAI

client = OpenAI()  # reads OPENAI_API_KEY from the environment

resp = client.responses.create(
    model=os.environ.get("MODEL", "gpt-4.1-mini"),
    instructions="You are a terse assistant.",
    input="Say hello in one sentence.",
)

print(resp.output_text)
print("usage:", resp.usage)  # input / output / total tokens
