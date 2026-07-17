# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# Curs per a agents de BSC — Transformers, LLMs, RAG i Agents: Des del teòric fins a la pràctica
# Amb llicència Creative Commons BY-NC-SA 4.0 – és obligatori citar l'autor, no es pot fer ús comercial, i les obres derivades han de tenir la mateixa llicència.

# =============================================================================================================== #
# Universitat Politècnica de Catalunya (UPC)                                                                      #
# =============================================================================================================== #

"""
📚 Explorador de context: mira com funciona el context d'un LLM

Una demostració interactiva senzilla per visualitzar:
- Els missatges enviats a l'API (el context)
- La sol·licitud i la resposta en brut de l'API

Ús:
    1. Crea un fitxer .env amb la teva clau d'API.
    2. python context_explorer.py
"""
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text
from rich.live import Live
from rich.spinner import Spinner
from rich.table import Table
from rich import box

load_dotenv()

console = Console()
client = None

# Configuració des del fitxer .env
MODEL = os.getenv("MODEL", "gpt-4.1-mini")
OPENAI_ENDPOINT = os.getenv("OPENAI_ENDPOINT")  # Opcional: per a endpoints d'API alternatius

SYSTEM_PROMPT = "You are a helpful assistant."


def show_context(messages: list) -> Panel:
    """Mostra el context actual de la conversa."""
    table = Table(
        box=box.SIMPLE,
        show_header=True,
        header_style="bold bright_white on grey23",
        style="on grey23"
    )
    table.add_column("#", style="bright_cyan on grey23", width=3)
    table.add_column("Rol", style="bright_magenta on grey23", width=12)
    table.add_column("Contingut", style="bright_white on grey23")
    
    for i, msg in enumerate(messages):
        role = msg.get("role", "unknown")
        content = msg.get("content", "").replace("\n", " ")
        table.add_row(str(i), role, content)
    
    return Panel(
        table,
        title=f"📚 Context ({len(messages)} missatges)",
        border_style="magenta",
        style="on grey23",
        padding=(0, 1)
    )


def show_api_request(request_data: dict) -> Panel:
    """Mostra la sol·licitud de l'API."""
    json_str = json.dumps(request_data, indent=2, ensure_ascii=False)
    syntax = Syntax(json_str, "json", theme="monokai", background_color="grey23", word_wrap=True)
    return Panel(syntax, title="📤 Sol·licitud de l'API", border_style="yellow", style="on grey23", padding=(0, 1))


def show_api_response(response_data: dict) -> Panel:
    """Mostra la resposta de l'API."""
    json_str = json.dumps(response_data, indent=2, ensure_ascii=False)
    syntax = Syntax(json_str, "json", theme="monokai", background_color="grey23", word_wrap=True)
    return Panel(syntax, title="📥 Resposta de l'API", border_style="cyan", style="on grey23", padding=(0, 1))


def show_message(role: str, content: str) -> Panel:
    """Mostra un missatge de xat."""
    styles = {
        "user": ("bright_white on blue", "blue", "👤 Tu"),
        "assistant": ("bright_white on dark_green", "green", "🤖 Assistent"),
        "system": ("bright_white on purple4", "magenta", "⚙️ Sistema")
    }
    text_style, border, title = styles.get(role, ("bright_white on grey23", "white", role))
    return Panel(Text(content, style=text_style), title=title, border_style=border, padding=(0, 1))


def wait_spinner():
    """Mostra un indicador d'espera."""
    return Live(
        Panel(
            Spinner("dots", text=Text("Esperant una resposta...", style="bold black on yellow")),
            border_style="yellow", style="on yellow", padding=(0, 1)
        ),
        console=console, refresh_per_second=10
    )


def run_chat():
    """Executa el bucle de xat."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    console.print()
    console.print(Panel(
        Text("Escriu els teus missatges. Missatge buit = sortir.\nObserva com creix el context a cada intercanvi!",
             style="bright_white on grey23"),
        title="📚 Explorador de context",
        border_style="bright_magenta",
        style="on grey23",
        padding=(1, 2)
    ))
    
    # Mostra el context inicial
    console.print()
    console.print(show_context(messages))
    
    while True:
        console.print()
        user_input = console.input("[bold blue]👤 Tu: [/bold blue]")
        
        if not user_input.strip():
            console.print(Panel(Text("Adéu!", style="bright_white on grey23"), border_style="dim"))
            break
        
        messages.append({"role": "user", "content": user_input})
        console.print(show_message("user", user_input))
        
        # Construeix i mostra la sol·licitud
        request_data = {
            "model": MODEL,
            "messages": messages,
            "temperature": 0.7
        }
        if OPENAI_ENDPOINT:
            request_data["_endpoint"] = OPENAI_ENDPOINT
        console.print()
        console.print(show_api_request(request_data))
        
        # Crida a l'API
        with wait_spinner():
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=0.7
            )
        
        assistant_content = response.choices[0].message.content
        
        # Mostra la resposta
        usage_data = {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens
        }
        prompt_tokens_details = getattr(response.usage, "prompt_tokens_details", None)
        cached_tokens = getattr(prompt_tokens_details, "cached_tokens", None)
        if cached_tokens is not None:
            usage_data["cached_tokens"] = cached_tokens

        response_data = {
            "id": response.id,
            "model": response.model,
            "finish_reason": response.choices[0].finish_reason,
            "message": {
                "role": "assistant",
                "content": assistant_content
            },
            "usage": usage_data
        }
        console.print()
        console.print(show_api_response(response_data))
        
        messages.append({"role": "assistant", "content": assistant_content})
        
        console.print()
        console.print(show_message("assistant", assistant_content))
        
        # Mostra el context actualitzat
        console.print()
        console.print(show_context(messages))


def main():
    global client
    
    console.clear()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        console.print(Panel(
            Text("No s'ha trobat OPENAI_API_KEY!\n\nCrea un fitxer .env amb:\nOPENAI_API_KEY=la-teva-clau",
                 style="bold bright_white on dark_red"),
            title="❌ Error", border_style="red", style="on dark_red"
        ))
        return
    
    # Inicialitza el client amb un endpoint personalitzat opcional
    if OPENAI_ENDPOINT:
        client = OpenAI(api_key=api_key, base_url=OPENAI_ENDPOINT)
    else:
        client = OpenAI(api_key=api_key)
    
    # Mostra la configuració
    console.print(Panel(
        Text(f"Model: {MODEL}\nEndpoint: {OPENAI_ENDPOINT or 'https://api.openai.com/v1'}",
             style="bright_white on grey23"),
        title="⚙️ Configuració",
        border_style="cyan",
        style="on grey23"
    ))
    
    run_chat()


if __name__ == "__main__":
    main()
