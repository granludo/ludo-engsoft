# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# Curs per a agents de BSC — Transformers, LLMs, RAG i Agents: Des del teòric fins a la pràctica
# Amb llicència Creative Commons BY-NC-SA 4.0 – és obligatori citar l'autor, no es pot fer ús comercial, i les obres derivades han de tenir la mateixa llicència.

"""
Un agent mínim per a la línia de comanda (CLI) – agents en 2026, tot en un fitxer.

Tres carpetes proporcionen a l'agent una identitat pròpia: agent.md — que és i què ha de fer (arxivat a system prompt) memòria/ — fitxers Markdown, carregats completament al començament (memòria fixa) habilitats/ — una carpeta per a cada habilitat; només la PRIMERA LÍNIA de cada fitxer habil.md es carrega al començament — el text complet es llegeix DEMANAD

Dos eines permeten executar-les: `run_command` – un comandament de la línia d'ordres, que s'imprimeix i es bloqueja abans d'executar-se; i `read_skill` – per obtenir les instruccions completes d'una habilitat pel seu nom.

El motor és el mateix bucle de sis línies del programa "dóna les LLM mans".

Ús: `uv` executa el fitxer `minimal_cli_agent.py` amb l'argument `"crea un informe de paraules sobre l'espai de treball"`
"""

import json
import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(base_url=os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1"),
                api_key=os.getenv("OPENAI_API_KEY", "ollama"))
MODEL = os.getenv("MODEL", "qwen3:1.7b")
HOME = Path(__file__).resolve().parent


# --- El "jo": fitxer agent.md + memòria, carregat complet; habilitats, listades per la primera línia --
def build_system():
    parts = [(HOME / "agent.md").read_text()]

    memory = sorted((HOME / "memory").glob("*.md"))
    if memory:
        parts.append("## Memory\n\n" + "\n\n".join(f.read_text() for f in memory))

    skills = sorted(d for d in (HOME / "skills").iterdir()
                    if (d / "skill.md").is_file())
    if skills:
        index = [f"- {d.name}: {(d / 'skill.md').read_text().splitlines()[0].lstrip('# ')}"
                 for d in skills]
        parts.append("## Skills available\n"
                     "Read a skill with read_skill BEFORE using it — the index "
                     "below is only the first line of each.\n\n" + "\n".join(index))
    return "\n\n".join(parts)


# --- Les mans ---------------------------------------------------------------
TOOLS = [
    {"type": "function", "function": {
        "name": "run_command",
        "description": "Run ONE shell command on the user's machine. The user "
                       "sees the exact command and must approve it.",
        "parameters": {"type": "object", "properties": {
            "command": {"type": "string", "description": "The shell command."}},
            "required": ["command"]}}},
    {"type": "function", "function": {
        "name": "read_skill",
        "description": "Read the full instructions of an available skill.",
        "parameters": {"type": "object", "properties": {
            "name": {"type": "string", "description": "Skill folder name."}},
            "required": ["name"]}}},
]


def tool_run_command(command):
    """La porta "y": la seguretat es troba aquí, a les estructures de suport – mai en el prompt."""
    print(f"\n⚠️  The agent wants to run:\n    $ {command}")
    if input("Permet? (escriu \"sí\"):").strip().lower() != "y":
        return "USER DENIED: the user refused this command. Do not retry it."
    r = subprocess.run(command, shell=True, capture_output=True, text=True,
                       timeout=120, cwd=HOME)
    out = (r.stdout + r.stderr)[:12000]
    return f"exit={r.returncode}\n{out}"


def tool_read_skill(name):
    f = HOME / "skills" / name / "skill.md"
    return f.read_text() if f.is_file() else f"ERROR: no skill named '{name}'."


DISPATCH = {"run_command": tool_run_command, "read_skill": tool_read_skill}


# --- El motor: els mateixos sis cilindres ------------------------------------------
def run(user_prompt):
    messages = [{"role": "system", "content": build_system()},
                {"role": "user", "content": user_prompt}]
    while True:                                                # 1. El bucle
        resp = client.chat.completions.create(                 # 2. Preguntar, utilitzant eines.
            model=MODEL, messages=messages, tools=TOOLS)
        print(f"  prompt_tokens: {resp.usage.prompt_tokens}")
        msg = resp.choices[0].message
        messages.append(msg.model_dump(exclude_none=True))
        if not msg.tool_calls:                                 # 3 resposta → atura
            print(f"\n✅ {msg.content}")
            return msg.content
        for tc in msg.tool_calls:                              # 4-5: executar les demandes que es van fer
            args = json.loads(tc.function.arguments or "{}")
            print(f"  → {tc.function.name}({args})")
            result = DISPATCH.get(tc.function.name,
                                  lambda **_: "ERROR: unknown tool")(**args)
            messages.append({"role": "tool", "tool_call_id": tc.id,  # 6 comentaris/opinions
                             "content": result})


if __name__ == "__main__":
    prompt = " ".join(sys.argv[1:]) or "Introduce yourself: who are you, what do you remember, and what can you do?"
    print(f"⚙️  model={MODEL}  endpoint={client.base_url}")
    run(prompt)
