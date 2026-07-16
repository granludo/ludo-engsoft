<!-- =============================================================================================================== -->
<!-- Universitat Politècnica de Catalunya (UPC) -->
<!-- =============================================================================================================== -->

# 📚 Explorador de context

Una demostració interactiva senzilla per visualitzar com funciona el context LLM.

## El que veureu

- **Pila de context** – Tots els missatges de la conversa
- **Sol·licitud a l'API** – El JSON exacte que s'envia a OpenAI
- **API Resposta** – Què retorna OpenAI (incloent l'ús de token)

## Configuració

```bash
cd context-explorer
uv venv
source .venv/bin/activate
uv sync
```

Crea un fitxer amb el nom `.env`:

```bash
# Required
OPENAI_API_KEY=your-key-here

# Optional: choose model (default: gpt-4.1-mini)
MODEL=gpt-4.1-mini

# Optional: use alternative OpenAI-compatible API endpoint
# OPENAI_ENDPOINT=http://localhost:11434/v1  # Ollama
# OPENAI_ENDPOINT=https://your-azure-endpoint.openai.azure.com/v1
```

## Correr

```bash
uv run context_explorer.py
```

## Conceptes clau

1. **Missatge del sistema** – Defineix el comportament de l'assistent (índex 0)
2. **Missatges dels usuaris** – Les vostres aportacions es afegeixen al context.
3. **Missatges d'assistència** – Les respostes s'afegeixen al context.
4. **Creixement del context** – Cada interacció afegeix 2 missatges.
5. **Token Ús** - Vegeu quant de tokens utilitza cada sol·licitud.

## 📖 Llicència

This repository is licensed under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](LICENSE) (`CC BY-NC-SA 4.0`).

## 👤 Autor

[@granludo](https://github.com/granludo) – Marc Alier, Universitat Politècnica de Catalunya (UPC)


---

© 2026 **Marc Alier i Forment** (Universitat Politècnica de Catalunya) · <https://wasabi.essi.upc.edu/ludo> · <https://lamb-project.org>
Curs per a agents de BSC — *Transformers, LLMs, RAG i Agents: Des del teòric a la pràctica*.
Licensed under [Creative Commons BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/): reuse must credit the author, no commercial use, derivatives under the same license.
