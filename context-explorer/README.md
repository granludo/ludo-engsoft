<!-- =============================================================================================================== -->
<!-- Plan de Generación de Talento Digital 2025 - INTIA/UEx                                                          -->
<!-- Actividad financiada por la Consejería de Economía, Empleo y Transformación Digital de la Junta de Extremadura  -->
<!-- Dirección General de Digitalización Regional de la Junta de Extremadura                                         -->
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
# OPENAI_API_ENDPOINT=http://localhost:11434/v1  # Ollama
# OPENAI_API_ENDPOINT=https://your-azure-endpoint.openai.azure.com/v1
```

## Run

```bash
python context_explorer.py
```

## Key Concepts

1. **System Message** - Sets the assistant's behavior (index 0)
2. **User Messages** - Your inputs get added to context
3. **Assistant Messages** - Responses get added to context
4. **Context Growth** - Each exchange adds 2 messages
5. **Token Usage** - See how many tokens each request uses

## 📖 License

Public Domain

## 👤 Author

[@granludo](https://github.com/granludo) - Marc Alier