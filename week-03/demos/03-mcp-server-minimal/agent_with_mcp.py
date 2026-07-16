# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# Curs per a agents de BSC — Transformers, LLMs, RAG i Agents: Des del teòric fins a la pràctica
# Amb llicència Creative Commons BY-NC-SA 4.0 – és obligatori citar l'autor, no es pot fer ús comercial, i les obres derivades han de tenir la mateixa llicència.

# =============================================================================================================== #
# Universitat Politècnica de Catalunya (UPC)                                                                      #
# =============================================================================================================== #

"""
🔌🤖 El bucle d'agent creat manualment, que ara crida a un servidor MCP.

Aquest és el circuit que funciona perquè has creat les dues parts: el bucle (des de "donar les LLM manes") i el servidor (server.py). Quan es connecta, el client sol·licita al servidor la seva llista d'eines — nom + descripció + JSON esquema per a cada una — i les passa directament al model com a la seva llista d'eines. Quan el model demana una eina, el bucle dirigeix la petició a través del JSON-RPC al MCP servidor i retorna el resultat.

El bucle no va canviar. Només el punt d'origen dels instruments ha canviat: en lloc de ser escrits a mà per al client, es TROBEN al servidor.

    Executar l'agent uv amb el fitxer agent\\_with\\_mcp.py amb l'ordre "Quina és la velocitat màxima del Pallet Pup?".
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
    """Una entrada de registre per a una eina MCP és essencialment un esquema d'eina d'OpenAI, gairebé idèntic."""
    return {"type": "function", "function": {
        "name": t.name, "description": t.description or "", "parameters": t.inputSchema}}


async def main(user_prompt):
    async with stdio_client(SERVER) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 1. Descobrir el registre que anuncia el servidor
            listing = await session.list_tools()
            tools = [to_openai_tool(t) for t in listing.tools]
            print("── the MCP registry the model receives ──")
            for t in tools:
                print(f"  tool: {t['function']['name']}  —  {t['function']['description']}")
            print()

            messages = [{"role": "user", "content": user_prompt}]
            while True:  # el mateix bucle que "donar les LLM mans" – però la font de l'eina ha canviat.
                resp = client.chat.completions.create(model=MODEL, messages=messages, tools=tools)
                print(f"  prompt_tokens: {resp.usage.prompt_tokens}")   # El registre es inclou en cada sol·licitud.
                msg = resp.choices[0].message
                messages.append(msg.model_dump(exclude_none=True))
                if not msg.tool_calls:
                    print(f"✅ {msg.content}")
                    return
                for tc in msg.tool_calls:
                    args = json.loads(tc.function.arguments or "{}")
                    print(f"  → MCP call: {tc.function.name}({args})")
                    result = await session.call_tool(tc.function.name, args)   # JSON - Temps de viatge de tornada (RPC)
                    text = "".join(getattr(c, "text", "") for c in result.content)
                    print(f"  ← MCP result: {text}")
                    messages.append({"role": "tool", "tool_call_id": tc.id, "content": text})


if __name__ == "__main__":
    prompt = " ".join(sys.argv[1:]) or "What is the top speed of the Pallet Pup, and who is Acme's CEO?"
    asyncio.run(main(prompt))
