#!/usr/bin/env bash
# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# BSC Agents Course — Transformers, LLMs, RAG and Agents: From Theory to Production
# Licensed under Creative Commons BY-NC-SA 4.0 — reuse must credit the author, no commercial use, derivatives under the same license.

# Chat Completions API — the classic OpenAI-compatible endpoint.
# No SDK. Just HTTP. JSON in, JSON out.
# OPENAI_ENDPOINT / MODEL come from your .env; defaults below hit OpenAI.
ENDPOINT="${OPENAI_ENDPOINT:-https://api.openai.com/v1}"
MODEL="${MODEL:-gpt-4.1-mini}"

curl "$ENDPOINT/chat/completions" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "'"$MODEL"'",
    "messages": [
      {"role": "system", "content": "You are a terse assistant."},
      {"role": "user",   "content": "Say hello in one sentence."}
    ],
    "temperature": 0.7
  }'
