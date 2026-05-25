# Week 1 — Foundations: LLMs, the API call, and the universal interface

Companion code for **BSC Agents Course · Week 1**. The lectures lay the theory; the exercises here are where you touch it.

## What Week 1 covers

- **Tokenization** — what the model actually sees, and why your bill is in tokens not words.
- **Base vs. aligned** — GPT-2 (a base model, never RLHF'd) vs. Qwen3-1.7B (aligned). The same prompt produces a quiz on one side and an answer on the other. The alignment stack from Lecture 2 is the difference.
- **The API call** — JSON in, JSON out, over HTTP. Universal wire format across providers (OpenAI, Anthropic via OpenRouter, Mistral, …) and local servers (Ollama, vLLM, LM Studio). See [`../context-explorer/`](../context-explorer/) at the repo root.

## Exercises

| # | What you do | Folder |
|---|---|---|
| **1 — Tokenize** | Load a tokenizer locally, count tokens, measure the multilingual penalty, compare two tokenizers on four kinds of input. | [`ex-01-tokenise/`](ex-01-tokenise/) |
| **2 — Base vs. aligned** | Run GPT-2 (base, ~124M) and Qwen3-1.7B (aligned) side by side. Ask both the same four prompts; observe the gap. | [`ex-02-base-vs-aligned/`](ex-02-base-vs-aligned/) |
| **3 — Call an LLM** | Use [`../context-explorer/`](../context-explorer/) (at the repo root) against a local Ollama-served Qwen3-1.7B. Same model as Exercise 2, this time wrapped in the OpenAI wire format. No API key, no money. | [`../context-explorer/`](../context-explorer/) |

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

If you don't have a working Python 3.10+ environment, the canonical course VM build is at [`../vm/SETUP.md`](../vm/SETUP.md) (VirtualBox + Ubuntu Server, OVA image distributed by the course).

## License

[CC BY-NC-SA 4.0](../LICENSE) — share + adapt for non-commercial use, with attribution and same-license redistribution.
