# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# Curs d'agents de BSC — Transformers, LLMs, RAG i Agents: de la teoria a la producció
# Amb llicència Creative Commons BY-NC-SA 4.0 – és obligatori citar l'autor, no es pot fer ús comercial, i les obres derivades han de tenir la mateixa llicència.

# =============================================================================================================== #
# Universitat Politècnica de Catalunya (UPC)                                                                      #
# =============================================================================================================== #

"""
Dóna mans a l'LLM — un bucle amb eines.

Donem dues eines al model (wget + execute_sql) i el continuem cridant fins que deixa de demanar-ne. Sense frameworks. Sense màgia. Li donem una tasca —no una pregunta— i mirem com encadena els passos ell sol.

Ollama-first: s'executa contra un endpoint local compatible amb OpenAI, sense clau ni cost.

NOTA SOBRE MODELS: els models locals petits (qwen3:1.7b) recorren aquest bucle de manera IRREGULAR: obliden encadenar els passos, generen arguments d'eina mal formats o s'aturen massa aviat. Això ja és una lliçó: el bucle és trivial; la intel·ligència que el guia és el model. Apunta .env cap a un model local més gran o cap a un endpoint frontier / MareNostrum i les mateixes sis línies funcionaran molt millor.

Ús:
    uv run --with openai python give_the_llm_hands.py
    uv run --with openai python give_the_llm_hands.py "el teu prompt"
"""

import json
import os
import sqlite3
import subprocess
import sys
import urllib.request

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# --- Config: Ollama per defecte, sobreescrivible per entorn (.env o entorn del terminal) -----------
BASE_URL = os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1")
API_KEY = os.getenv("OPENAI_API_KEY", "ollama")  # qualsevol cadena no buida per a Ollama
MODEL = os.getenv("MODEL", "qwen3:1.7b")

client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
DB_PATH = "database.db"

# --- Esquemes d'eines exposats al model (function calling d'OpenAI) ---------
TOOLS = [
    {"type": "function", "function": {
        "name": "wget", "description": "Fetch the content of a URL.",
        "parameters": {"type": "object", "properties": {
            "url": {"type": "string", "description": "URL to fetch."},
            "flags": {"type": "string", "description": "Ignored; kept for compatibility."}},
            "required": ["url"]}}},
    {"type": "function", "function": {
        "name": "execute_sql",
        "description": "Run one SQL statement against local SQLite db (database.db). "
                       "SELECT returns rows; CREATE/INSERT/UPDATE/DELETE return affected-row count.",
        "parameters": {"type": "object", "properties": {
            "query": {"type": "string", "description": "The SQL statement."}},
            "required": ["query"]}}},
]


def tool_wget(url, flags=""):
    """GATE amb humà al circuit: la seguretat viu en l'entramat, no en el prompt."""
    cmd = f"wget -qO- {url}"
    print(f"\n⚠️  L'LLM vol executar:\n    $ {cmd}")
    if input("    Permet-ho? (escriu \"y\"): ").strip().lower() != "y":
        return "USER DENIED: the user refused to execute this wget command. Do not retry."
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "give-the-llm-hands/1.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode("utf-8", errors="replace")
        return body[:12000] + ("\n... [truncated]" if len(body) > 12000 else "")
    except Exception as e:
        return f"ERROR fetching {url}: {e}"


def tool_execute_sql(query):
    """CREATE/INSERT/SELECT/UPDATE/DELETE contra database.db."""
    print(f"\n🗄️  SQL: {query}")
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(query)
        if query.strip().upper().startswith("SELECT"):
            cols = [d[0] for d in cur.description] if cur.description else []
            rows = cur.fetchall()
            conn.close()
            return json.dumps({"columns": cols, "rows": rows}, default=str)
        conn.commit()
        n = cur.rowcount
        conn.close()
        return f"OK — {n} row(s) affected."
    except Exception as e:
        return f"SQL ERROR: {e}"


DISPATCH = {"wget": tool_wget, "execute_sql": tool_execute_sql}

SYSTEM = ("You are a data-collection assistant. Use wget to fetch URLs and "
          "execute_sql to store data in SQLite (database.db). Work step by step: "
          "fetch, create a table, insert rows, then answer in plain text.")


def run_loop(user_prompt):
    messages = [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": user_prompt}]
    iteration = 0
    while True:                                                       # 1. EL BUCLE — pregunta fins que el model deixa de demanar
        iteration += 1
        print(f"\n── crida a l'LLM #{iteration} ──")
        resp = client.chat.completions.create(                        # 2. pregunta al model i posa-li les eines a la mà
            model=MODEL, messages=messages, tools=TOOLS, temperature=0.2)
        msg = resp.choices[0].message
        if not msg.tool_calls:                                        # 3. cap crida a eines → resposta final, ATURA
            print(f"\n✅ Resposta final:\n{msg.content}")
            return msg.content
        messages.append(msg.model_dump(exclude_none=True))            # 4. recorda què ha demanat el model
        for tc in msg.tool_calls:                                     # 5. executa cada eina demanada
            args = json.loads(tc.function.arguments or "{}")
            result = DISPATCH.get(tc.function.name, lambda **_: "ERROR: unknown tool")(**args)
            print(f"📎 {tc.function.name} → {result[:200]}")
            messages.append({"role": "tool", "tool_call_id": tc.id,   # 6. retorna els resultats i torna a començar el BUCLE
                             "name": tc.function.name, "content": result})
    # ^^^ Les línies 1-6 de dalt són tot el motor. La resta són canonades.


def main():
    print(f"⚙️  model={MODEL}  endpoint={BASE_URL}  db={DB_PATH}")
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = ("Fetch https://jsonplaceholder.typicode.com/users , create a "
                  "table for the user id, name, email and city, insert every "
                  "row, then tell me how many users you stored.")
        print("(no s'ha indicat cap prompt — es fa servir el prompt de demostració integrat)")
    run_loop(prompt)


if __name__ == "__main__":
    main()
