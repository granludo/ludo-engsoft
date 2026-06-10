<!-- =============================================================================================================== -->
<!-- Universitat Politècnica de Catalunya (UPC)                                                                      -->
<!-- =============================================================================================================== -->

# 📚 Context Explorer — RAG edition

The [Context Explorer](../../../week-01/demos/context-explorer/) from week 1, with one
thing added: **retrieval**.

Before every call, a `Retriever` reads a knowledge file and pastes it into the
prompt. The single-file retriever does the most trivial thing that earns the name
RAG — it returns the **whole file, every turn, ignoring your question**. The model
answers because the answer is sitting in its context window. This is *cheating at
our own solitaire*: you already hold the answer card, so you slide it where the
model can see it.

It works. The catch is made visible here.

## What you'll see each turn

- **📥 Retrieval** — what the retriever pulled in (here: the whole file)
- **📤 API Request** — the prompt the model actually receives (context + question)
- **📥 API Response** — the answer plus `usage` (token counts)
- **📚 Context** — the message stack, growing
- **💸 Token cost** — `prompt_tokens` per turn, as a bar chart, climbing

The whole file rides in the prompt on **every turn**, so `prompt_tokens` only goes
up. That is the cost of single-file RAG. We come back to it later in the course —
for now, just watch the number.

## The thing to notice

1. Ask a question the file answers (e.g. *"Where is Acme Robotics headquartered?"*) →
   correct, grounded in the context.
2. Ask one the file does **not** answer (e.g. *"Who is the CEO of Tesla?"*) → a
   grounded model says it doesn't know. That refusal is the proof: the model is
   reading the context, not its training data.

## Setup

```bash
cd context-explorer-rag
uv venv
source .venv/bin/activate
uv sync
```

Copy `.env.example` to `.env` and fill it in:

```bash
OPENAI_API_KEY=your-key-here
MODEL=gpt-4.1-mini
OPENAI_ENDPOINT=https://api.openai.com/v1
KNOWLEDGE_FILE=knowledge.txt
```

Ollama-first option (no key, no money, no internet):

```bash
OPENAI_ENDPOINT=http://localhost:11434/v1
MODEL=qwen3:1.7b
```

## Run

```bash
uv run context_explorer_rag.py
```

In-chat commands:

| Command | What it does |
|---|---|
| `/file <path>` | load a different knowledge file (try your own notes) |
| `/context` | print the loaded knowledge file |
| *(empty line)* | quit |

## How embeddings RAG slots in later

The retrieval step is one class, `WholeFileRetriever`. Everything else — the chat
loop, the panels, the token accounting — is independent of how retrieval works.
Later in the course we replace it with an `EmbeddingsRetriever` that embeds your
question, finds the nearest chunks, and returns only those. **The loop does not
change. Only the retriever does.** That is the whole architecture of RAG in one
swap.

```python
class Retriever:
    def retrieve(self, question: str) -> str: ...

class WholeFileRetriever(Retriever):   # this lecture: the whole file, every turn
    def retrieve(self, question): return self.text

class EmbeddingsRetriever(Retriever):  # later: top-k nearest chunks
    def retrieve(self, question): return nearest(embed(question), self.chunks, k=4)
```

## 📖 License

This repository is licensed under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](../../../week-01/demos/context-explorer/LICENSE) (`CC BY-NC-SA 4.0`).

## 👤 Author

[@granludo](https://github.com/granludo) - Marc Alier, Universitat Politècnica de Catalunya (UPC)

---

© 2026 **Marc Alier i Forment** (Universitat Politècnica de Catalunya) · <https://wasabi.essi.upc.edu/ludo> · <https://lamb-project.org>
BSC Agents Course — *Transformers, LLMs, RAG and Agents: From Theory to Production*.
Licensed under [Creative Commons BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/): reuse must credit the author, no commercial use, derivatives under the same license.
