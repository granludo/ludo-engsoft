<!-- =============================================================================================================== -->
<!-- Universitat Politècnica de Catalunya (UPC)                                                                      -->
<!-- =============================================================================================================== -->

# 📐 Embeddings Explorer

The companion to the context explorer, for the embeddings lesson. Type a sentence; the demo
**embeds it** (turns it into a list of numbers), **shows the vector**, and then shows **how
close it is to every sentence you entered before** — measured two ways at once, in a table
sorted nearest-first.

The lesson is the one idea behind all of dynamic RAG: **meaning becomes geometry.** Once a
sentence is a point in space, "similar" is just "near", and you can put a number on it.

## The two metrics

| Metric | What it measures | Reading |
|---|---|---|
| **cosine similarity** | the angle between the two vectors | `1.0` = same direction · `0.0` = unrelated · **higher = closer** |
| **Euclidean distance** | the straight-line gap between the two points | `0.0` = identical · **lower = closer** |

These models return **unit-length** vectors (norm ≈ 1.0 — the demo shows it). For unit
vectors the two metrics are the same ranking, because `distance² = 2·(1 − cosine)`. So you
get two names for one geometry, and you can watch them agree.

## Setup

```bash
cd embeddings-explorer
uv venv && source .venv/bin/activate && uv sync
```

Copy `.env.example` to `.env`. The default is **local Ollama + `nomic-embed-text`** — no key,
no cost. Pull the model first:

```bash
ollama serve
ollama pull nomic-embed-text
```

```bash
OPENAI_API_KEY=ollama
MODEL=nomic-embed-text
OPENAI_ENDPOINT=http://localhost:11434/v1
```

To use OpenAI's paid embeddings instead, point `.env` at `https://api.openai.com/v1` with a
real key and `MODEL=text-embedding-3-small`. The code does not change — only the configuration.

## Run

```bash
uv run embeddings_explorer.py
```

In-chat commands:

| Command | What it does |
|---|---|
| *(type any sentence)* | embed it, show the vector, compare it to the earlier ones |
| `/seed` | load a few example sentences so the distances land immediately |
| `/list` | list the sentences entered so far |
| `/clear` | forget everything and start over |
| *(empty line)* | quit |

## The thing to notice

Run `/seed`, then enter **"how quick is the warehouse robot?"**. It has almost no words in
common with *"The warehouse robot's top speed is 2.4 metres per second"* — yet it lands
**closest**, by both metrics. The numbers track **meaning**, not shared words. Then enter a
recipe and watch it fall to the bottom. There is no persistence: close the program and the
space is gone.

## 📖 License

Licensed under [Creative Commons BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) (`CC BY-NC-SA 4.0`).

## 👤 Author

[@granludo](https://github.com/granludo) — Marc Alier, Universitat Politècnica de Catalunya (UPC)

---

© 2026 **Marc Alier i Forment** (Universitat Politècnica de Catalunya) · <https://wasabi.essi.upc.edu/ludo> · <https://lamb-project.org>
BSC Agents Course — *Transformers, LLMs, RAG and Agents: From Theory to Production*.
