# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# Curs d'agents de BSC — Transformers, LLMs, RAG i Agents: de la teoria a la producció
# Amb llicència Creative Commons BY-NC-SA 4.0 – és obligatori citar l'autor, no es pot fer ús comercial, i les obres derivades han de tenir la mateixa llicència.

# =============================================================================================================== #
# Universitat Politècnica de Catalunya (UPC)                                                                      #
# =============================================================================================================== #

"""
🔌🤖 El bucle d'agent fet a mà, ara cridant un servidor MCP.

Aquest és el cicle d'anada i tornada que funciona perquè has construït les dues meitats: el bucle (de «donar mans a l'LLM») i el servidor (server.py). En connectar-se, el client demana al servidor el seu REGISTRE d'eines —nom + descripció + esquema JSON de cadascuna— i les passa directament al model com a llista d'eines. Quan el model demana una eina, el bucle encamina la crida per JSON-RPC cap al servidor MCP i en retorna el resultat.

El bucle no ha canviat. Només ha canviat d'on venen les eines: en lloc d'escriure-les a mà al client, es DESCOBREIXEN des del servidor.

    uv run agent_with_mcp.py "quina és la velocitat màxima del Pallet Pup?"
"""
import asyncio
import json
import os
import sys

from openai import OpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

client = OpenAI(
    base_url=os.environ.get("OPENAI_BASE_URL", "http://localhost:11434/v1"),
    api_key=os.environ.get("OPENAI_API_KEY", "ollama"),
)
MODEL = os.environ.get("MODEL", "qwen3:1.7b")
SERVER = StdioServerParameters(command=sys.executable, args=["server.py"])


def to_openai_tool(t):
    """L'entrada de registre d'una eina MCP JA ÉS un esquema d'eina d'OpenAI, gairebé al peu de la lletra."""
    return {"type": "function", "function": {
        "name": t.name, "description": t.description or "", "parameters": t.inputSchema}}


async def main(user_prompt):
    async with stdio_client(SERVER) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 1. Descobrir el registre que anuncia el servidor
            listing = await session.list_tools()
            tools = [to_openai_tool(t) for t in listing.tools]
            print("── el registre MCP que rep el model ──")
            for t in tools:
                print(f"  eina: {t['function']['name']}  —  {t['function']['description']}")
            print()

            messages = [{"role": "user", "content": user_prompt}]
            while True:  # el MATEIX bucle que «donar mans a l'LLM»: només ha canviat la font de les eines
                resp = client.chat.completions.create(model=MODEL, messages=messages, tools=tools)
                print(f"  prompt_tokens: {resp.usage.prompt_tokens}")   # el registre s'inclou en cada petició
                msg = resp.choices[0].message
                messages.append(msg.model_dump(exclude_none=True))
                if not msg.tool_calls:
                    print(f"✅ {msg.content}")
                    return
                for tc in msg.tool_calls:
                    args = json.loads(tc.function.arguments or "{}")
                    print(f"  → crida MCP: {tc.function.name}({args})")
                    result = await session.call_tool(tc.function.name, args)   # anada i tornada per JSON-RPC
                    text = "".join(getattr(c, "text", "") for c in result.content)
                    print(f"  ← resultat MCP: {text}")
                    messages.append({"role": "tool", "tool_call_id": tc.id, "content": text})


if __name__ == "__main__":
    prompt = " ".join(sys.argv[1:]) or "What is the top speed of the Pallet Pup, and who is Acme's CEO?"
    asyncio.run(main(prompt))
