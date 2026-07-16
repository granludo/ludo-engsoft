
# 🐷 OpenAI Function Calling Demostració: Els tres petits conills 🐺

Un script de Python didàctic que demostra la diferència entre una conversa normal amb [LLM, i una altra amb [function calling, utilitzant la història clàssica dels tres porcs.

## 📚 Què aprendreш

- Com definir les **eines/funcions** per a OpenAI i API.
- Com decideix el LLM quan cridar funcions en funció del context.
- Com **processar les crides a funcions** i retornar els resultats al LLM.
- La diferència entre un model de llenguatge que només pot parlar i un que pot **prendre accions**.

## 🎭 La demostració

El guió presenta dos escenaris amb la mateixa conversa:

| Escenari | Eines disponibles | Què passa? |
|----------|----------------|--------------|
| **Escenari 1** | ❌ No hi ha cap | El porc només pot parlar sobre la necessitat de demanar ajuda. |
| **Escenari 2** | ✅ `call_hunter()` | En fet, el porc pot *realment* trucar al caçador! |

### La conversa

1. **Usuari:** "Què hi ha?"...
2. **Porc:** *(pregunta amb cautela qui és)*
3. **Usuari:** "¡Jo sóc el llop! Obriu la porta o destruiré la vostra casa!"
4. **Porc:** (En el Escenari 2, crida al caçador per ajudar-se!)

## 🚀 Configuració i execució

### Requisits previs

- Python 3.10 o superior
- Una clau OpenAI API ([trobeu-ne un aquí](https://platform.openai.com/api-keys))
- `uv` Gestor de paquets ([instal·lar UV](https://docs.astral.sh/uv/getting-started/installation/))

### Pas 1: Crear i activar l'entorn virtual

```bash
cd week-03/demos/01-function-calling
uv venv
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate     # On Windows
```

### Pas 2: Instal·lar les dependències.

```bash
uv sync
```

### Pas 3: Configureu la vostra clau API

Crea un fitxer anomenat "`.env`" dins aquest directori:

```bash
# Required
OPENAI_API_KEY=your-api-key-here

# Optional: choose model (default: gpt-4.1-mini)
MODEL=gpt-4.1-mini

# Optional: use alternative OpenAI-compatible API endpoint
# OPENAI_ENDPOINT=http://localhost:11434/v1  # Ollama
# OPENAI_ENDPOINT=https://your-azure-endpoint.openai.azure.com/v1
```

> ⚠️ **Mai no commiteu el fitxer `.env`!** Ja està present a `.gitignore`.

### Pas 4: Executar la demostració

```bash
python three_pigs_function_calling.py
```

## 🔧 Com funciona Function Calling

### 1. Definir l'eina

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

### 2. Transmetre les eines a la API

```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    tools=AVAILABLE_TOOLS  # 🔑 This enables function calling!
)
```

### 3. Comproveu si la funció LLM vol fer una crida.

```python
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        # Execute the function and return results to the LLM
```

## 💡 L'aspect més important

> **Function calling transforma LLMs de simples programes de conversació en agents que poden prendre accions reals!**

Sense function calling, el porc només pot dir: "Trucaré al caçador". Amb function calling, el porc pot realment trucar al caçador i rebre una resposta.

## 📚 Referències addicionals

- [OpenAI Function Calling Documentació](https://platform.openai.com/docs/guides/function-calling)
- [OpenAI API Referència](https://platform.openai.com/docs/api-reference)

## 📖 Llicència

This repository is licensed under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](../../../LICENSE) (`CC BY-NC-SA 4.0`).

## 👤 Autor

[@granludo](https://github.com/granludo) – Marc Alier



---

© 2026 **Marc Alier i Forment** (Universitat Politècnica de Catalunya) · <https://wasabi.essi.upc.edu/ludo> · <https://lamb-project.org>
Curs per a agents de BSC — *Transformers, LLMs, RAG i Agents: Des del teòric a la pràctica*.
Licensed under [Creative Commons BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/): reuse must credit the author, no commercial use, derivatives under the same license.
