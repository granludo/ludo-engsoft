# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# BSC Agents Course — Transformers, LLMs, RAG and Agents: From Theory to Production
# Licensed under Creative Commons BY-NC-SA 4.0 — reuse must credit the author, no commercial use, derivatives under the same license.

"""
Streaming a chat completion — get the tokens as they are produced, instead of
waiting for the whole answer.

A normal call blocks until the model has produced every token, then returns the
finished string. With `stream=True` the API instead sends back a sequence of
small *chunks*, one (or a few) tokens at a time, as the model decodes them. You
print each chunk the moment it arrives — that is the typewriter effect you see
in ChatGPT. Nothing about the model changes; only how the bytes reach you.

Run it:
    cp ../.env.example .env   # set OPENAI_ENDPOINT / OPENAI_API_KEY / MODEL
    uv run --with openai python stream.py
"""

import os

from openai import OpenAI

client = OpenAI(
    base_url=os.environ.get("OPENAI_ENDPOINT", "https://api.openai.com/v1"),
    api_key=os.environ.get("OPENAI_API_KEY"),
)
model = os.environ.get("MODEL", "gpt-4.1-mini")

# stream=True turns the response into an iterator of chunks.
# stream_options asks the server to send a final chunk carrying the usage record
# (a normal streamed response does not include usage otherwise).
stream = client.chat.completions.create(
    model=model,
    messages=[{"role": "user", "content": "Write a short paragraph about why streaming feels faster, even when total time is the same."}],
    stream=True,
    stream_options={"include_usage": True},
)

usage = None
for chunk in stream:
    # Most chunks carry a delta with a little more text. Print it immediately,
    # with flush=True so it shows up now and not when the buffer fills.
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
    # The very last chunk (because of include_usage) has empty choices and the
    # token usage for the whole response.
    if chunk.usage:
        usage = chunk.usage

print()  # newline after the streamed text
if usage:
    print("\nusage:", usage)
