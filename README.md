# 🎓 Software Engineering Educational Demos

A collection of interactive demos and course materials for teaching software engineering concepts, focusing on LLM APIs and AI integration.

This is the **public student-facing companion repo** for the [BSC Agents Course](https://www.bsc.es/) (UPC × BSC AI Factory) and the [AI-Augmented Software Engineering](https://github.com/granludo/) course. Standalone tools at the repo root are reused across multiple weeks and courses; course-specific exercises live under `week-NN/` folders.

## 🗂️ Course materials

| Folder | What's there |
|---|---|
| [`week-01/`](./week-01/) | **Week 1 — Foundations.** Tokenization, base-vs-aligned model comparison (GPT-2 vs Qwen3-1.7B), and the first API call via `context-explorer`. |
| [`vm/`](./vm/) | **Course VM setup.** Ubuntu Server 24.04 VirtualBox image with the BSC tool baseline (uv, `llm`, transformers, torch-CPU, opencode, gh). Instructors build the OVA; students import. |

More weeks land here as the course progresses.

## 🧰 Standalone demos (used across weeks)

### Context Explorer — [`./context-explorer/`](./context-explorer/)

A simple interactive demo to visualize how LLM conversation context works.

**Learn:**
- How messages accumulate in the context
- What gets sent to the API on each request
- Token usage and costs

```bash
cd context-explorer
uv venv && source .venv/bin/activate && uv sync
python context_explorer.py
```

### Function Calling Demo — [`./function-calling/`](./function-calling/)

The Three Little Pigs 🐷🐺 - An interactive demo showing the difference between LLMs with and without function calling.

**Learn:**
- How to define tools/functions for LLMs
- When and how LLMs decide to use tools
- The difference between "talking about actions" vs "taking actions"

```bash
cd function-calling
uv venv && source .venv/bin/activate && uv sync
python three_pigs_function_calling.py
```

## ⚙️ Configuration

All demos use a `.env` file for configuration:

```bash
# Required
OPENAI_API_KEY=your-api-key-here

# Optional: choose model (default: gpt-4.1-mini)
MODEL=gpt-4.1-mini

# Optional: use alternative OpenAI-compatible API endpoint
OPENAI_API_ENDPOINT=http://localhost:11434/v1  # Ollama
# OPENAI_API_ENDPOINT=https://your-azure-endpoint.openai.azure.com/v1
```

### Compatible Endpoints

These demos work with any OpenAI-compatible API:
- **OpenAI** - Default
- **Ollama** - Local models (`http://localhost:11434/v1`)
- **Azure OpenAI** - Enterprise
- **LM Studio** - Local models
- **Together AI**, **Groq**, etc.

## 🛠️ Requirements

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager
- OpenAI API key (or compatible endpoint)

## 📖 License

This repository is licensed under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](LICENSE) (`CC BY-NC-SA 4.0`).

## 👤 Author

[@granludo](https://github.com/granludo) - Marc Alier
