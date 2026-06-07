<!-- =============================================================================================================== -->
<!-- Universitat Politècnica de Catalunya (UPC)                                                                      -->
<!-- =============================================================================================================== -->

# 📚 Context Explorer

A simple interactive demo to visualize how LLM context works.

## What You'll See

- **Context Stack** - All messages in the conversation
- **API Request** - The exact JSON sent to OpenAI
- **API Response** - What OpenAI returns (including token usage)

## Setup

```bash
cd context-explorer
uv venv
source .venv/bin/activate
uv sync
```

Create a `.env` file:

```bash
# Required
OPENAI_API_KEY=your-key-here

# Optional: choose model (default: gpt-4.1-mini)
MODEL=gpt-4.1-mini

# Optional: use alternative OpenAI-compatible API endpoint
# OPENAI_ENDPOINT=http://localhost:11434/v1  # Ollama
# OPENAI_ENDPOINT=https://your-azure-endpoint.openai.azure.com/v1
```

## Run

```bash
uv run context_explorer.py
```

## Key Concepts

1. **System Message** - Sets the assistant's behavior (index 0)
2. **User Messages** - Your inputs get added to context
3. **Assistant Messages** - Responses get added to context
4. **Context Growth** - Each exchange adds 2 messages
5. **Token Usage** - See how many tokens each request uses

## 📖 License

This repository is licensed under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](LICENSE) (`CC BY-NC-SA 4.0`).

## 👤 Author

[@granludo](https://github.com/granludo) - Marc Alier, Universitat Politècnica de Catalunya (UPC)


---

© 2026 **Marc Alier i Forment** (Universitat Politècnica de Catalunya) · <https://wasabi.essi.upc.edu/ludo> · <https://lamb-project.org>
BSC Agents Course — *Transformers, LLMs, RAG and Agents: From Theory to Production*.
Licensed under [Creative Commons BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/): reuse must credit the author, no commercial use, derivatives under the same license.
