# Week 1 — Foundations: LLMs, the API call, and the universal interface

Companion code for **BSC Agents Course · Week 1**. The lectures lay the theory; the exercises here are where you touch it.

## What Week 1 covers

- **Tokenization** — what the model actually sees, and why your bill is in tokens not words.
- **Base vs. aligned** — GPT-2 (a base model, never RLHF'd) vs. Qwen3-1.7B (aligned). The same prompt produces a quiz on one side and an answer on the other. The alignment stack from Lecture 2 is the difference.
- **The API call** — JSON in, JSON out, over HTTP. Universal wire format across providers (OpenAI, Anthropic via OpenRouter, Mistral, …) and local servers (Ollama, vLLM, LM Studio). See [`demos/context-explorer/`](./demos/context-explorer/) and [`demos/the-api-call/`](./demos/the-api-call/) — the bare call in `curl` and via the SDK, with chat-completions and the newer Responses API side by side.

## Exercises

| # | What you do | Folder |
|---|---|---|
| **1 — Tokenize** | Load a tokenizer locally, count tokens, measure the multilingual penalty, compare two tokenizers on four kinds of input. | [`ex-01-tokenise/`](ex-01-tokenise/) |
| **2 — Base vs. aligned** | Run GPT-2 (base, ~124M) and Qwen3-1.7B (aligned) side by side. Ask both the same four prompts; observe the gap. | [`ex-02-base-vs-aligned/`](ex-02-base-vs-aligned/) |
| **3 — Call an LLM** | Use [`demos/context-explorer/`](./demos/context-explorer/) against a local Ollama-served Qwen3-1.7B. Same model as Exercise 2, this time wrapped in the OpenAI wire format. No API key, no money. | [`demos/context-explorer/`](./demos/context-explorer/) |
| **4 — Call the LLM from code** | The bare call: `curl` and a short Python script against your own Ollama, on the model you can run. Same wire format that reaches a frontier model — only the `.env` changes. | [`ex-04-call-the-llm/`](ex-04-call-the-llm/) |

## How to run anything in this folder

Each exercise sub-folder is independent — its own `pyproject.toml`, its own `.venv`. Standard pattern:

```bash
cd week-01/ex-01-tokenise
uv venv && source .venv/bin/activate
uv sync
python ex_01_tokenise.py
```

`.venv/` and `.env` are gitignored everywhere — never commit them.

## Course VM

If you don't have a working Python 3.10+ environment, the canonical course VM build is at [`../pre-course/vm-setup.md`](../pre-course/vm-setup.md) (VirtualBox + Ubuntu Server, OVA image distributed by the course); the [`../pre-course/cheatsheet.md`](../pre-course/cheatsheet.md) has the day-one commands.

## License

[CC BY-NC-SA 4.0](../LICENSE) — share + adapt for non-commercial use, with attribution and same-license redistribution.


---

© 2026 **Marc Alier i Forment** (Universitat Politècnica de Catalunya) · <https://wasabi.essi.upc.edu/ludo> · <https://lamb-project.org>
BSC Agents Course — *Transformers, LLMs, RAG and Agents: From Theory to Production*.
Licensed under [Creative Commons BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/): reuse must credit the author, no commercial use, derivatives under the same license.
