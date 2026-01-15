<!-- =============================================================================================================== -->
<!-- Plan de Generación de Talento Digital 2025 - INTIA/UEx                                                          -->
<!-- Actividad financiada por la Consejería de Economía, Empleo y Transformación Digital de la Junta de Extremadura  -->
<!-- Dirección General de Digitalización Regional de la Junta de Extremadura                                         -->
<!-- =============================================================================================================== -->

# 🐷 OpenAI Function Calling Demo: The Three Little Pigs 🐺

A didactic Python script that demonstrates the difference between a regular LLM conversation and one with **function calling** capabilities, using the classic Three Little Pigs tale.

## 📚 What You'll Learn

- How to define **tools/functions** for the OpenAI API
- How the LLM **decides when** to call functions based on context
- How to **process function calls** and feed results back to the LLM
- The difference between an LLM that can only talk vs. one that can **take action**

## 🎭 The Demo

The script runs two scenarios with the same conversation:

| Scenario | Tools Available | What Happens |
|----------|----------------|--------------|
| **Scenario 1** | ❌ None | The pig can only *talk* about calling for help |
| **Scenario 2** | ✅ `call_hunter()` | The pig can *actually* call the hunter! |

### The Conversation

1. **User:** "knock knock..."
2. **Pig:** *(cautiously asks who's there)*
3. **User:** "I am the wolf! Open the door or I will blow away your house!"
4. **Pig:** *(In Scenario 2, calls the hunter for help!)*

## 🚀 Setup & Run

### Prerequisites

- Python 3.10 or higher
- An OpenAI API key ([get one here](https://platform.openai.com/api-keys))
- `uv` package manager ([install uv](https://docs.astral.sh/uv/getting-started/installation/))

### Step 1: Create and activate the virtual environment

```bash
cd function-calling
uv venv
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate     # On Windows
```

### Step 2: Install dependencies

```bash
uv sync
```

### Step 3: Configure your API key

Create a `.env` file in the `function-calling` folder:

```bash
# Required
OPENAI_API_KEY=your-api-key-here

# Optional: choose model (default: gpt-4.1-mini)
MODEL=gpt-4.1-mini

# Optional: use alternative OpenAI-compatible API endpoint
# OPENAI_API_ENDPOINT=http://localhost:11434/v1  # Ollama
# OPENAI_API_ENDPOINT=https://your-azure-endpoint.openai.azure.com/v1
```

> ⚠️ **Never commit your `.env` file!** It's already in `.gitignore`.

### Step 4: Run the demo

```bash
python three_pigs_function_calling.py
```

## 🔧 How Function Calling Works

### 1. Define the Tool

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

### 2. Pass Tools to the API

```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    tools=AVAILABLE_TOOLS  # 🔑 This enables function calling!
)
```

### 3. Check if the LLM Wants to Call a Function

```python
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        # Execute the function and return results to the LLM
```

## 💡 Key Takeaway

> **Function calling transforms LLMs from chatbots into agents that can take real-world actions!**

Without function calling, the pig can only *say* "I'll call the hunter." With function calling, the pig can *actually* call the hunter and get a response.

## 📖 Further Reading

- [OpenAI Function Calling Documentation](https://platform.openai.com/docs/guides/function-calling)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)

# Licensed under public domain 

@granludo Marc Alier 

