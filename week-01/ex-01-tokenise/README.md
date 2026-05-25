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

## What to deliver

A short report (markdown or PDF, half a page is plenty) in your course repo at `week1/exercise1/`:

- The token count for the demo sentence (*"The model never sees the letters in strawberry."*).
- The multilingual penalty number for your language vs. English.
- For the four code-ish inputs: one sentence per row on where the two tokenizers disagree most and why you think that might be.
