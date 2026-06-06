# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# BSC Agents Course — Transformers, LLMs, RAG and Agents: From Theory to Production
# Licensed under Creative Commons BY-NC-SA 4.0 — reuse must credit the author, no commercial use, derivatives under the same license.

"""Responses API — OpenAI's newer endpoint, via the openai SDK."""
from openai import OpenAI

client = OpenAI()  # reads OPENAI_API_KEY from the environment

resp = client.responses.create(
    model="gpt-4.1-mini",
    instructions="You are a terse assistant.",
    input="Say hello in one sentence.",
)

print(resp.output_text)
print(resp.usage)  # input / output / total tokens
