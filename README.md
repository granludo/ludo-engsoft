# 🎓 Demostracions educatives d'enginyeria del software

Una col·lecció de demostracions interactives i materials de curs per ensenyar conceptes d'enginyeria del software, centrats en les API d'LLM i la integració amb la IA.

Aquest és el **repositori públic de referència per als estudiants** del [Curs d'Agents del BSC](https://www.bsc.es/) (UPC × BSC AI Factory) i del curs [Enginyeria del Software Augmentada amb IA](https://github.com/granludo/). Les eines independents que hi ha a l'arrel del repositori es reutilitzen entre diverses setmanes i cursos; els exercicis específics de cada curs viuen dins de les carpetes `week-NN/`.

## 🗂️ Materials del curs

| Carpeta | Què hi trobaràs |
|---|---|
| [`week-01/`](./week-01/) | **Setmana 1 — Transformers i LLM.** Tokenització, comparació entre un base model i un aligned model (GPT-2 vs Qwen3-1.7B) i la primera crida a l'API amb la demostració [`context-explorer`](./week-01/demos/02-context-explorer/). |
| [`week-02/`](./week-02/) | **Setmana 2 — RAG.** L'escala de demostracions, des del RAG d'un sol fitxer fins a l'explorador d'embeddings-RAG, més les eines que et proporcionem: [`collections-manager`](./week-02/collections-manager/) i [`simple-dynamic-rag`](./week-02/simple-dynamic-rag/). |
| [`week-03/`](./week-03/) | **Setmana 3 — Agents.** Function calling (la demostració dels tres porquets), el bucle d'agent d'unes 30 línies i un servidor MCP mínim. |
| [`pre-course/`](./pre-course/) | **Abans de començar.** La [guia d'instal·lació de la VM](./pre-course/vm-setup.md) (Ubuntu Server 24.04 + la base d'eines del BSC: uv, `llm`, transformers, torch-CPU, opencode, gh) i una [guia ràpida de comandes](./pre-course/cheatsheet.md). |

A mesura que avanci el curs, hi anirem afegint més setmanes.

## 🧰 Demostracions

### Explorador de context — [`week-01/demos/02-context-explorer/`](./week-01/demos/02-context-explorer/)

Una demostració interactiva i senzilla per visualitzar com funciona el context d'una conversa amb un LLM.

**Aprèn:**
- Com s'acumulen els missatges dins del context.
- Què s'envia a l'API en cada sol·licitud.
- L'ús de tokens i els costos.

```bash
cd week-01/demos/02-context-explorer
uv venv && source .venv/bin/activate && uv sync
python context_explorer.py
```

### Demostració de function calling — [`week-03/demos/01-function-calling/`](./week-03/demos/01-function-calling/)

Els tres porquets 🐷🐺: una demostració interactiva que mostra la diferència entre un LLM amb function calling i un sense.

**Aprèn:**
- Com definir eines i funcions per a un LLM.
- Quan i com un LLM decideix fer servir les eines.
- La diferència entre «parlar d'accions» i «executar accions».

```bash
cd week-03/demos/01-function-calling
uv venv && source .venv/bin/activate && uv sync
python three_pigs_function_calling.py
```

## ⚙️ Configuració

Totes les demostracions es configuren amb un fitxer `.env`:

```bash
# Required
OPENAI_API_KEY=your-api-key-here

# Optional: choose model (default: gpt-4.1-mini)
MODEL=gpt-4.1-mini

# Optional: use alternative OpenAI-compatible API endpoint
OPENAI_ENDPOINT=http://localhost:11434/v1  # Ollama
# OPENAI_ENDPOINT=https://your-azure-endpoint.openai.azure.com/v1
```

### Endpoints compatibles

Aquestes demostracions funcionen amb qualsevol API compatible amb OpenAI:
- **OpenAI** — l'opció per defecte.
- **Ollama** — models locals (`http://localhost:11434/v1`).
- **Azure OpenAI** — per a entorns empresarials.
- **LM Studio** — models locals.
- **Together AI**, **Groq**, etc.

## 🛠️ Requisits

- Python 3.10 o superior.
- El gestor de paquets [uv](https://docs.astral.sh/uv/).
- Una clau d'API d'OpenAI (o un endpoint compatible).

## 📖 Llicència

This repository is licensed under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](LICENSE) (`CC BY-NC-SA 4.0`).

## 👤 Autor

[@granludo](https://github.com/granludo) — Marc Alier


---

© 2026 **Marc Alier i Forment** (Universitat Politècnica de Catalunya) · <https://wasabi.essi.upc.edu/ludo> · <https://lamb-project.org>
Curs d'Agents del BSC — *Transformers, LLMs, RAG i Agents: de la teoria a la producció*.
Licensed under [Creative Commons BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/): reuse must credit the author, no commercial use, derivatives under the same license.
