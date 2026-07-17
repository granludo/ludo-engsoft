# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# Curs d'agents de BSC — Transformers, LLMs, RAG i Agents: de la teoria a la producció
# Amb llicència Creative Commons BY-NC-SA 4.0 – és obligatori citar l'autor, no es pot fer ús comercial, i les obres derivades han de tenir la mateixa llicència.

"""
Un agent mínim de línia d'ordres (CLI) — agents el 2026, tot en un sol fitxer.

Tres carpetes donen una identitat a l'agent:
    agent.md   — qui és i què ha de fer (a l'inici del system prompt)
    memory/    — fitxers Markdown, carregats sencers a l'arrencada (memòria fixa)
    skills/    — una carpeta per habilitat; a l'arrencada només se'n carrega la
                 PRIMERA LÍNIA de cada skill.md; el text complet es llegeix SOTA DEMANDA

Dues eines li donen mans:
    run_command — una ordre de shell, que s'imprimeix i es bloqueja amb la porta «y» abans d'executar-se
    read_skill  — obté les instruccions completes d'una habilitat pel seu nom

El motor és el mateix bucle de sis línies de «donar mans a l'LLM».

Ús:
    uv run minimal_cli_agent.py "fes-me un informe en Word de l'espai de treball"
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


# --- El "jo": agent.md + memòria, carregats sencers; habilitats, llistades per la primera línia --
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
    """La porta «y»: la seguretat viu aquí, en l'entramat de suport — mai en el prompt."""
    print(f"\n⚠️  L'agent vol executar:\n    $ {command}")
    if input("    Permet-ho? (escriu \"y\"): ").strip().lower() != "y":
        return "USER DENIED: the user refused this command. Do not retry it."
    r = subprocess.run(command, shell=True, capture_output=True, text=True,
                       timeout=120, cwd=HOME)
    out = (r.stdout + r.stderr)[:12000]
    return f"exit={r.returncode}\n{out}"


def tool_read_skill(name):
    f = HOME / "skills" / name / "skill.md"
    return f.read_text() if f.is_file() else f"ERROR: no skill named '{name}'."


DISPATCH = {"run_command": tool_run_command, "read_skill": tool_read_skill}


# --- El motor: les mateixes sis línies ---------------------------------------------
def run(user_prompt):
    messages = [{"role": "system", "content": build_system()},
                {"role": "user", "content": user_prompt}]
    while True:                                                # 1. el bucle
        resp = client.chat.completions.create(                 # 2. pregunta, amb eines
            model=MODEL, messages=messages, tools=TOOLS)
        print(f"  prompt_tokens: {resp.usage.prompt_tokens}")
        msg = resp.choices[0].message
        messages.append(msg.model_dump(exclude_none=True))
        if not msg.tool_calls:                                 # 3. resposta → atura
            print(f"\n✅ {msg.content}")
            return msg.content
        for tc in msg.tool_calls:                              # 4-5. executa el que ha demanat
            args = json.loads(tc.function.arguments or "{}")
            print(f"  → {tc.function.name}({args})")
            result = DISPATCH.get(tc.function.name,
                                  lambda **_: "ERROR: unknown tool")(**args)
            messages.append({"role": "tool", "tool_call_id": tc.id,  # 6. retorna els resultats
                             "content": result})


if __name__ == "__main__":
    prompt = " ".join(sys.argv[1:]) or "Introduce yourself: who are you, what do you remember, and what can you do?"
    print(f"⚙️  model={MODEL}  endpoint={client.base_url}")
    run(prompt)
