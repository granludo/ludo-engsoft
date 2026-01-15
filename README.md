<!-- =============================================================================================================== -->
<!-- Plan de Generación de Talento Digital 2025 - INTIA/UEx                                                          -->
<!-- Actividad financiada por la Consejería de Economía, Empleo y Transformación Digital de la Junta de Extremadura  -->
<!-- Dirección General de Digitalización Regional de la Junta de Extremadura                                         -->
<!-- =============================================================================================================== -->

# 🎓 Software Engineering Educational Demos

A collection of interactive demos for teaching software engineering concepts, focusing on LLM APIs and AI integration.

## 📚 Available Demos

### 1. [Context Explorer](./context-explorer/)

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

### 2. [Function Calling Demo](./function-calling/)

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

Public Domain

## 👤 Author

[@granludo](https://github.com/granludo) - Marc Alier
