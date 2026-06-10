<!-- =============================================================================================================== -->
<!-- Universitat Politècnica de Catalunya (UPC)                                                                      -->
<!-- =============================================================================================================== -->

# 📚 Context Explorer — single-file RAG

Single-file RAG is the crudest thing that earns the name: paste a whole file into the
prompt as context and ask. This explorer shows the part everyone gets wrong — **the
difference between the conversation the chat UI keeps and the call the LLM actually
receives.** They are not the same, and the gap is the lesson.

## The three layers

This is the same shape as serving an assistant over an OpenAI-compatible API (e.g. LAMB):

```
🖥️  CHAT UI        sends:  history (bare) + your latest message
                       │   history = what you see; no system prompt, no augmentation
                       ▼
🛠️  ASSISTANT ENDPOINT  (STATELESS; the model id selects system prompt + template + RAG)
        builds:  [system] + [history] + [ template(your message, RAG augmentation) ]
                       │   rebuilt every call — it has no state to keep it in
                       ▼
🧠  LLM            returns:  the response only
                       ▲
🖥️  CHAT UI        appends (your message, response) → history   ✗ augmentation NOT saved
```

Because the endpoint is **stateless**, the augmentation is built fresh every turn and
thrown away. The UI history stays bare. The system prompt and the file the LLM sees are
**never** in the conversation the user sees. Watch the two panels each turn:

- **`🛠️ → 🧠 Endpoint builds the LLM call`** — system + history + this turn's augmented message
- **`🖥️ Chat UI history`** — just the bare turns

The gap between them — the system prompt and the augmentation — is exactly what the app
does not remember.

## Two placement modes (switch live with `/mode`)

| Mode | The file goes… | Per-turn user message | What it shows |
|---|---|---|---|
| **`user-augment`** *(default)* | into the **user message**, every turn | augmented (file + question) | the app-vs-LLM gap; the file rides the volatile tail, re-sent and re-billed every call |
| **`system-grounding`** | into the **system prompt**, **once** | bare question | retrieve once at the start → a "pure" conversation → the file sits in the stable, cacheable prefix (KV cache) |

Flip between them on camera and re-ask the same questions: in `user-augment` the file is
rebuilt into every call; in `system-grounding` it is retrieved once and the conversation
stays clean.

The counterfactual: to **keep** the augmentation you would have to store augmented history
and make the chat **stateful** — `/stateful` toggles that so you can see what it costs.

## Setup

```bash
cd context-explorer-rag
uv venv && source .venv/bin/activate && uv sync
```

Copy `.env.example` to `.env`:

```bash
OPENAI_API_KEY=your-key-here
MODEL=gpt-4.1-mini
OPENAI_ENDPOINT=https://api.openai.com/v1
KNOWLEDGE_FILE=knowledge.txt
RAG_MODE=user-augment            # or system-grounding
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
| `/mode user-augment` · `/mode system-grounding` | switch where the file goes (resets the conversation) |
| `/stateful` | toggle storing augmented history (the stateful alternative) |
| `/file <path>` | load a different knowledge file |
| `/context` | print the loaded knowledge file |
| *(empty line)* | quit |

## The thing to notice

1. Ask a question the file answers, then a follow-up. In `user-augment`, look at the
   endpoint build on turn 2: the *previous* turns are passed through **bare** — last turn's
   augmentation is gone. The file is re-injected only into the current message.
2. The UI history never contains the system prompt or the augmentation. The model reads a
   lot more than the app remembers.
3. Switch to `system-grounding`. Now the file is in the system prompt, the user turns are
   bare, and retrieval happens once — the conversation is "pure."

## How embeddings RAG slots in next

The retrieval step is one class, `WholeFileRetriever`. Everything else — the UI, the
stateless endpoint, the panels, the token accounting — is independent of how retrieval
works. The next rung swaps in an `EmbeddingsRetriever` that embeds the question, finds the
nearest chunks, and returns only those. **The loop does not change. Only the retriever
does.** That is the architecture of RAG in one swap.

## 📖 License

Licensed under [Creative Commons BY-NC-SA 4.0](../../../week-01/demos/context-explorer/LICENSE) (`CC BY-NC-SA 4.0`).

## 👤 Author

[@granludo](https://github.com/granludo) - Marc Alier, Universitat Politècnica de Catalunya (UPC)

---

© 2026 **Marc Alier i Forment** (Universitat Politècnica de Catalunya) · <https://wasabi.essi.upc.edu/ludo> · <https://lamb-project.org>
BSC Agents Course — *Transformers, LLMs, RAG and Agents: From Theory to Production*.
Licensed under [Creative Commons BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/): reuse must credit the author, no commercial use, derivatives under the same license.
