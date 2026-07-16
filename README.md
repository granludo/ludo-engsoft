# 🎓 Software Engineering Demostracions educatives

Una col·lecció de demostracions interactives i materials per a cursos d'ensenyament dels conceptes de la enginyeria del software, amb un enfoc prim en les API d'LLM i la integració de l'IA.

Aquest és el **repositori principal per als estudiants**, destinat a les assignatures [Curs per a agents de BSC](https://www.bsc.es/) (UPC × BSC AI Factory) i [IA augmentada Software Engineering](https://github.com/granludo/). Les eines individuals del repositori es reutilitzen en diverses setmanes i assignatures; els exercicis específics de cada assignatura es troben dins de les carpetes `week-NN/`.

## 📚 Materials del curs

| Carpeta | Què hi ha allà? |
|---|---|
| [`week-01/`](./week-01/) | **Setmana 1 – Transformadors i models de llenguatge grans (LLM).** Tokenització, comparació entre models base i alineats (GPT-2 vs Qwen3-1.7B), i la primera crida a l'API mitjançant el [`context-explorer`](./week-01/demos/02-context-explorer/) demo. |
| [`week-02/`](./week-02/) | **Setmana 2 — RAG.** La escala de demostració, des d'una fila única RAG fins a l'explorador embeddings-RAG, juntament amb les eines proporcionades: [`collections-manager`](./week-02/collections-manager/) i [`simple-dynamic-rag`](./week-02/simple-dynamic-rag/). |
| [`week-03/`](./week-03/) | **Setmana 3 – Agents.** Function calling (la demostració dels tres porcs), el bucle de l'agent que consta d'unes 30 línies de codi, i un servidor mínim MCP. |
| [`pre-course/`](./pre-course/) | **Abans de començar:** El [Guia d'instal·lació de VM](./pre-course/vm-setup.md) (Ubuntu Server 24.04 + la base de codi del BSC: uv, `llm`, transformers, torch-CPU, opencode, gh) i un [guia de comandaments](./pre-course/cheatsheet.md). |

A mesura que avança el curs, s'afegiran més setmanes.

## Vídeos demonstratius

### Explorador de context — [`week-01/demos/02-context-explorer/`](./week-01/demos/02-context-explorer/)

Una demostració interactiva senzilla per visualitzar com funciona el context de conversa d'un model lingüístic gran (LLM).

**Aprende:**
- Com s'acumulen els missatges en el context.
- Què s'envia a la API en cada sol·licitud
- Token ús i costos

```bash
cd week-01/demos/02-context-explorer
uv venv && source .venv/bin/activate && uv sync
python context_explorer.py
```

### Function Calling Versió de demostració — [`week-03/demos/01-function-calling/`](./week-03/demos/01-function-calling/)

Els tres porcs petits 🐷🐺 - Una demostració interactiva que mostra la diferència entre LLMs amb i sense function calling.

**Aprende:**
- Com definir eines/funcions per a LLMs
- Quan i com LLMs decidirà utilitzar eines?
- La diferència entre "parlar sobre accions" i "prendre accions"

```bash
cd week-03/demos/01-function-calling
uv venv && source .venv/bin/activate && uv sync
python three_pigs_function_calling.py
```

## ⚙️ Configuració

Totes les demostracions utilitzen un fitxer de configuració (`.env`).

```bash
# Required
OPENAI_API_KEY=your-api-key-here

# Optional: choose model (default: gpt-4.1-mini)
MODEL=gpt-4.1-mini

# Optional: use alternative OpenAI-compatible API endpoint
OPENAI_ENDPOINT=http://localhost:11434/v1  # Ollama
# OPENAI_ENDPOINT=https://your-azure-endpoint.openai.azure.com/v1
```

### Compatible Endpoints

Aquestes demostracions funcionen amb qualsevol OpenAI compatible amb API:
- **OpenAI** - Valor per defecte
- **Ollama** - Models locals (`http://localhost:11434/v1`)
- **Azure OpenAI** - Empresa
- **LM Studio** - Models locals
- **Together AI, Groq, etc.**

## 🛠️ Requisits

- Python 3.10 o superior
- gestor de paquets [uv](https://docs.astral.sh/uv/)
- OpenAI API clau (o compatible endpoint)

## 📖 Llicència

This repository is licensed under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](LICENSE) (`CC BY-NC-SA 4.0`).

## 👤 Autor

[@granludo](https://github.com/granludo) – Marc Alier


---

© 2026 **Marc Alier i Forment** (Universitat Politècnica de Catalunya) · <https://wasabi.essi.upc.edu/ludo> · <https://lamb-project.org>
Curs per a agents de BSC — *Transformers, LLMs, RAG i Agents: Des del teòric a la pràctica*.
Licensed under [Creative Commons BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/): reuse must credit the author, no commercial use, derivatives under the same license.
