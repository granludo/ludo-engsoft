<!-- =============================================================================================================== -->
<!-- Universitat Politècnica de Catalunya (UPC)                                                                      -->
<!-- =============================================================================================================== -->

# 🔎 Simple Embeddings RAG (with Chroma)

The single-file demo pasted the **whole** knowledge file into the prompt on every turn.
That is fine for one small file and hopeless for a real corpus — `prompt_tokens` grows
with the size of your knowledge, not with the question.

This demo does retrieval properly. It **chunks** the knowledge, **embeds** each chunk
into a vector, **stores** the vectors in **Chroma** (a vector database), and then, for
each question, **retrieves** only the few nearest chunks and injects those. You send what
is *relevant*, not what is *there*.

The one idea from the embeddings lesson, now doing work: **meaning is geometry, so
"relevant" is "nearby."** Watch two things — the question and the chunk that answers it
often share almost no words, and `prompt_tokens` stays small and flat no matter how big
`knowledge.txt` gets.

## The pipeline

```
knowledge.txt ──chunk──► pieces ──embed──► vectors ──store──► Chroma
                                                                 │
question ──embed──► query vector ──► nearest-neighbour search ───┘──► top-K chunks ──inject──► LLM answer
```

Two models do two jobs: an **embeddings model** (`nomic-embed-text`) turns text into
vectors, and a **chat model** writes the answer. Both are reached through the same
OpenAI-compatible endpoint — only the configuration changes.

## Setup

```bash
cd simple-embeddings-rag
uv venv && source .venv/bin/activate && uv sync
```

Copy `.env.example` to `.env`. The default is **local Ollama** — no key, no cost. Pull
both models first:

```bash
ollama serve
ollama pull nomic-embed-text
ollama pull qwen3:1.7b
```

## Run

```bash
uv run simple_embeddings_rag.py
```

Ask about Acme Robotics and the Pallet Pup. Empty line to quit.

## The knobs (and the trade-offs)

Set these in `.env` (or leave the defaults) and feel what they do:

| Knob | Default | Trade-off |
|---|---|---|
| `CHUNK_SIZE` | 320 | Bigger keeps facts together but pulls in noise; smaller is precise but can cut a fact in two. |
| `CHUNK_OVERLAP` | 40 | A shared margin so a fact split at a boundary still survives whole in one chunk. |
| `TOP_K` | 3 | How many nearest chunks to retrieve and inject per question. |

## The thing to notice

Ask **"how quick is the delivery robot?"** — words the document never uses (it says *top
speed*, not *how quick*; *Pallet Pup*, not *delivery robot*). It still retrieves the right
chunk, because retrieval is by meaning. Then compare the `prompt_tokens` line here with the
one from `single-file-rag`: there the whole file rode along every turn; here only a few
chunks do. Add ten more paragraphs to `knowledge.txt` and the number barely moves.

There is no persistence: the index is rebuilt in memory each run.

## 📖 License

Licensed under [Creative Commons BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) (`CC BY-NC-SA 4.0`).

## 👤 Author

[@granludo](https://github.com/granludo) — Marc Alier, Universitat Politècnica de Catalunya (UPC)
