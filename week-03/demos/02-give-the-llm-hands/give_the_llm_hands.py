# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# Curs per a agents de BSC — Transformers, LLMs, RAG i Agents: Des del teòric fins a la pràctica
# Amb llicència Creative Commons BY-NC-SA 4.0 – és obligatori citar l'autor, no es pot fer ús comercial, i les obres derivades han de tenir la mateixa llicència.

# =============================================================================================================== #
# Universitat Politècnica de Catalunya (UPC)                                                                      #
# =============================================================================================================== #

"""
Dóna les LLM mans – una estructura amb eines.

Li donem al model dues eines (wget + execute\\_sql) i continuem cridant-lo fins que deixi de sol·licitar més eines. Sense cap estructura predefinida. Sense "màgia". Li assignem una tasca – no una pregunta – i observem com realitza els passos per si mateix.

Ollama-first: funciona contra un punt d'accés compatible amb OpenAI local, sense clau ni cost.

NOTA SOBRE MODELS: els models locals petits (qwen3: 1,7B) gestionen aquest bucle de manera desigual — obliden connectar les etapes, tenen arguments incorrectes per a la funció, o es detenen massa aviat. Això és una lliçó en si mateixa: el bucle és senzill; la intel·ligència que el controla és el model. Apunteu el fitxer ".env" cap a un model local més gran o cap al sistema "frontier / MareNostrum endpoint", i les mateixes sis línies funcionaran molt millor.

Ús: `uv run --with openai python give_the_llm_hands.py` i `uv run --with openai python give_the_llm_hands.py "el teu prompt"`
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

# --- Configuració: Ollama - Prioritat per defecte, variable d'entorn que es pot sobreescribir (a través de .env o l'entorn del terminal) -----------
BASE_URL = os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1")
API_KEY = os.getenv("OPENAI_API_KEY", "ollama")  # qualsevol cadena no buida per a Ollama
MODEL = os.getenv("MODEL", "qwen3:1.7b")

client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
DB_PATH = "database.db"

# --- Esquemes de eines exposats al model (OpenAI funció d'anomenació) ---------
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
    """GATE amb participació humana: la seguretat es troba en la infraestructura, no en el prompt."""
    cmd = f"wget -qO- {url}"
    print(f"\n⚠️  The LLM wants to run:\n    $ {cmd}")
    if input("Permet? (escriu \"sí\"):").strip().lower() != "y":
        return "USER DENIED: the user refused to execute this wget command. Do not retry."
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "give-the-llm-hands/1.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode("utf-8", errors="replace")
        return body[:12000] + ("\n... [truncated]" if len(body) > 12000 else "")
    except Exception as e:
        return f"ERROR fetching {url}: {e}"


def tool_execute_sql(query):
    """Crear/inserir/seleccionar/actualitzar/eliminar dades a la base de dades "database.db"."""
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
    while True:                                                       # 1. EL CÍCLO – pregunte fins que el model deixi d'interrogar.
        iteration += 1
        print(f"\n── LLM call #{iteration} ──")
        resp = client.chat.completions.create(                        # 2. Pregunteu al model i feu-li arribar les eines.
            model=MODEL, messages=messages, tools=TOOLS, temperature=0.2)
        msg = resp.choices[0].message
        if not msg.tool_calls:                                        # 3. No necessitat d'utilitzar eines → resposta final, ATUR
            print(f"\n✅ Final answer:\n{msg.content}")
            return msg.content
        messages.append(msg.model_dump(exclude_none=True))            # 4. Recordeu què demanava el model.
        for tc in msg.tool_calls:                                     # 5. Executar cada eina de la que es demani.
            args = json.loads(tc.function.arguments or "{}")
            result = DISPATCH.get(tc.function.name, lambda **_: "ERROR: unknown tool")(**args)
            print(f"📎 {tc.function.name} → {result[:200]}")
            messages.append({"role": "tool", "tool_call_id": tc.id,   # 6. Mostrar els resultats, i després tornar a començar (repetir el procés).
                             "name": tc.function.name, "content": result})
    # ^^^ Les línies 1 a 6 anteriors són el motor complet. Tot el que resta és la instal·lació de canonades.


def main():
    print(f"⚙️  model={MODEL}  endpoint={BASE_URL}  db={DB_PATH}")
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = ("Fetch https://jsonplaceholder.typicode.com/users , create a "
                  "table for the user id, name, email and city, insert every "
                  "row, then tell me how many users you stored.")
        print("(no prompt given — using the built-in demo prompt)")
    run_loop(prompt)


if __name__ == "__main__":
    main()
