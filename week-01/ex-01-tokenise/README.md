# Week 1 · Exercise 1 — Tokenize, locally

Load a tokenizer with the Hugging Face `transformers` library and count tokens by hand. See what the model actually sees. Measure the multilingual penalty. Compare two tokenizer families on code-ish inputs.

## Run it

```bash
uv venv && source .venv/bin/activate
uv sync
python ex_01_tokenise.py
```

The first run downloads two small tokenizers from Hugging Face (a few hundred KB each). No model weights, no GPU, no API key.

## What you may edit

- `PARAGRAPH_EN` / `PARAGRAPH_MINE` at the top of `ex_01_tokenise.py` — replace `PARAGRAPH_MINE` with your own language to compute *your* multilingual penalty.
- `TOKENIZER_A` / `TOKENIZER_B` — any Hugging Face tokenizer id works (`gpt2`, `bert-base-uncased`, `bert-base-multilingual-cased`, …).



---

© 2026 **Marc Alier i Forment** (Universitat Politècnica de Catalunya) · <https://wasabi.essi.upc.edu/ludo> · <https://lamb-project.org>
BSC Agents Course — *Transformers, LLMs, RAG and Agents: From Theory to Production*.
Licensed under [Creative Commons BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/): reuse must credit the author, no commercial use, derivatives under the same license.
