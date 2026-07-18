
# 🐷 Demostració de function calling amb OpenAI: els tres porquets 🐺

Un script de Python didàctic que mostra la diferència entre una conversa normal amb un LLM i una que fa servir **function calling**, a partir del conte clàssic dels tres porquets.

## 📚 Què aprendràs

- Com definir **eines/funcions** per a l'API d'OpenAI.
- Com **decideix** l'LLM **quan** cridar funcions segons el context.
- Com **processar les crides a funcions** i retornar-ne els resultats a l'LLM.
- La diferència entre un LLM que només pot parlar i un que pot **actuar**.

## 🎭 La demostració

L'script executa dos escenaris amb la mateixa conversa:

| Escenari | Eines disponibles | Què passa |
|----------|----------------|--------------|
| **Escenari 1** | ❌ Cap | El porquet només pot *parlar* de demanar ajuda. |
| **Escenari 2** | ✅ `call_hunter()` | El porquet pot cridar el caçador *de debò*! |

### La conversa

1. **Usuari:** «Toc, toc…»
2. **Porquet:** *(pregunta amb cautela qui hi ha)*
3. **Usuari:** «Sóc el llop! Obre la porta o t'esbufegaré la casa!»
4. **Porquet:** *(a l'Escenari 2, crida el caçador perquè l'ajudi!)*

## 🚀 Configuració i execució

### Requisits previs

- Python 3.10 o superior
- Una clau API d'OpenAI ([aconsegueix-ne una aquí](https://platform.openai.com/api-keys))
- El gestor de paquets `uv` ([instal·la uv](https://docs.astral.sh/uv/getting-started/installation/))

### Pas 1: Crea i activa l'entorn virtual

```bash
cd week-03/demos/01-function-calling
uv venv
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate     # On Windows
```

### Pas 2: Instal·la les dependències

```bash
uv sync
```

### Pas 3: Configura la teva clau API

Crea un fitxer `.env` dins d'aquesta carpeta:

```bash
# Required
OPENAI_API_KEY=your-api-key-here

# Optional: choose model (default: gpt-4.1-mini)
MODEL=gpt-4.1-mini

# Optional: use alternative OpenAI-compatible API endpoint
# OPENAI_ENDPOINT=http://localhost:11434/v1  # Ollama
# OPENAI_ENDPOINT=https://your-azure-endpoint.openai.azure.com/v1
```

> ⚠️ **Mai no commitis el fitxer `.env`!** Ja està present a `.gitignore`.

### Pas 4: Executa la demostració

```bash
python three_pigs_function_calling.py
```

## 🔧 Com funciona Function Calling

### 1. Defineix l'eina

```python
AVAILABLE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "call_hunter",
            "description": "Call the hunter to help protect the pig from the wolf",
            "parameters": {
                "type": "object",
                "properties": {
                    "urgency": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "emergency"]
                    },
                    "message": {
                        "type": "string",
                        "description": "Message for the hunter"
                    }
                },
                "required": ["urgency", "message"]
            }
        }
    }
]
```

### 2. Passa les eines a l'API

```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    tools=AVAILABLE_TOOLS  # 🔑 This enables function calling!
)
```

### 3. Comprova si l'LLM vol cridar una funció

```python
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        # Execute the function and return results to the LLM
```

## 💡 La idea clau

> **El function calling converteix els LLM de simples chatbots en agents capaços de dur a terme accions reals al món!**

Sense function calling, el porquet només pot *dir* «trucaré al caçador». Amb function calling, el porquet pot cridar el caçador de debò i rebre'n una resposta.

## 📚 Per aprofundir

- [Documentació de function calling d'OpenAI](https://platform.openai.com/docs/guides/function-calling)
- [Referència de l'API d'OpenAI](https://platform.openai.com/docs/api-reference)

## 📖 Llicència

This repository is licensed under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](../../../LICENSE) (`CC BY-NC-SA 4.0`).

## 👤 Autor

[@granludo](https://github.com/granludo) — Marc Alier



---

© 2026 **Marc Alier i Forment** (Universitat Politècnica de Catalunya) · <https://wasabi.essi.upc.edu/ludo> · <https://lamb-project.org>
Curs d'agents del BSC — *Transformers, LLMs, RAG i Agents: De la teoria a la producció*.
Licensed under [Creative Commons BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/): reuse must credit the author, no commercial use, derivatives under the same license.
