# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# Curs d'agents de BSC — Transformers, LLMs, RAG i Agents: de la teoria a la producció
# Amb llicència Creative Commons BY-NC-SA 4.0 – és obligatori citar l'autor, no es pot fer ús comercial, i les obres derivades han de tenir la mateixa llicència.

"""
🐷 Demostració de function calling amb OpenAI: els tres porquets 🐺

Demostració interactiva on el llop ets TU!
Compara com respon el porquet amb i sense function calling.

Requisits:
    pip install -r requirements.txt

Ús:
    1. Crea un fitxer .env amb la teva clau API.
    2. python three_pigs_function_calling.py
"""

import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Biblioteca Rich per a una interfície de terminal atractiva
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text
from rich.live import Live
from rich.spinner import Spinner
from rich.table import Table
from rich import box

# Carregar les variables d'entorn del fitxer .env
load_dotenv()

# Inicialitzar la consola de Rich
console = Console()

# Inicialitzar el client d'OpenAI
client = None

# Configuració des del fitxer .env
MODEL = os.getenv("MODEL", "gpt-4.1-mini")
OPENAI_ENDPOINT = os.getenv("OPENAI_ENDPOINT")  # Opcional: per a endpoints d'API alternatius

# ============================================================================
# CONFIGURACIÓ
# ============================================================================

SYSTEM_PROMPT = """
You are one of the three little pigs from the classic children's tale.
You live in a sturdy brick house and you are very scared of the Big Bad Wolf.

Your personality:
- You speak with a slight oink and are very nervous when danger is near
- You are protective of your house and your brothers
- You remember that the wolf destroyed your brothers' houses (straw and sticks)
- You are clever and resourceful

When someone knocks at your door, you are cautious and ask who it is.
When threatened by the wolf, you become very scared but try to be brave.

IMPORTANT: If you have access to tools and you are in danger, USE THEM!
Call the hunter immediately if the wolf threatens you!

Keep your responses short and in character (2-3 sentences max).
"""

# ============================================================================
# DEFINICIÓ DE FUNCIONS PER A L'LLM
# ============================================================================

AVAILABLE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "call_hunter",
            "description": "Call the hunter to come help protect the pig from the wolf. The hunter lives nearby and can scare away the wolf with his presence.",
            "parameters": {
                "type": "object",
                "properties": {
                    "urgency": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "emergency"],
                        "description": "How urgent is the situation?"
                    },
                    "message": {
                        "type": "string",
                        "description": "A brief message to tell the hunter about the situation"
                    }
                },
                "required": ["urgency", "message"]
            }
        }
    }
]


def call_hunter(urgency: str, message: str) -> str:
    """Simula la crida al caçador per demanar ajuda."""
    responses = {
        "low": "The hunter received your message and will check on you later.",
        "medium": "The hunter is on his way, should arrive in 10 minutes.",
        "high": "The hunter grabbed his shotgun and is running to your house!",
        "emergency": "The hunter is sprinting to your location with backup and heavy weapons! Hold on!"
    }
    return responses.get(urgency, "The hunter received your call.")


# ============================================================================
# FUNCIONS AUXILIARS DE LA INTERFÍCIE D'USUARI
# ============================================================================

def create_message_panel(role: str, content: str) -> Panel:
    """Crea un panell amb estil per a un missatge de xat."""
    styles = {
        "user": ("bright_white on blue", "blue", "🐺 Tu (El Llop)"),
        "assistant": ("bright_white on dark_green", "green", "🐷 Porquet"),
        "system": ("bright_white on purple4", "magenta", "⚙️ Sistema"),
        "tool": ("black on yellow", "yellow", "🔧 Resultat de l'eina")
    }
    
    text_style, border_color, title = styles.get(role, ("bright_white on grey23", "white", role))
    
    return Panel(
        Text(content, style=text_style),
        title=title,
        title_align="left",
        border_style=border_color,
        padding=(0, 1)
    )


def show_context_stack(messages: list, tools_available: bool) -> Panel:
    """Mostra la pila de context actual de la conversa."""
    table = Table(
        box=box.SIMPLE,
        show_header=True,
        header_style="bold bright_white on grey23",
        style="on grey23"
    )
    table.add_column("#", style="bright_cyan on grey23", width=3)
    table.add_column("Rol", style="bright_magenta on grey23", width=12)
    table.add_column("Vista prèvia del contingut", style="bright_white on grey23")
    
    for i, msg in enumerate(messages):
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        if content:
            preview = content.replace("\n", " ")
        else:
            preview = "(tool_calls)"
        table.add_row(str(i), role, preview)
    
    tools_text = "✅ Eines: [call_hunter]" if tools_available else "❌ Sense eines"

    return Panel(
        table,
        title=f"📚 Pila de context ({len(messages)} missatges) | {tools_text}",
        border_style="magenta",
        style="on grey23",
        padding=(0, 1)
    )


def show_api_request(request_data: dict) -> Panel:
    """Mostra la sol·licitud API en brut."""
    json_str = json.dumps(request_data, indent=2, ensure_ascii=False)
    syntax = Syntax(json_str, "json", theme="monokai", background_color="grey23", word_wrap=True)
    
    return Panel(
        syntax,
        title="📤 Petició a l'API (enviada a OpenAI)",
        border_style="yellow",
        style="on grey23",
        padding=(0, 1)
    )


def show_api_response(response_data: dict) -> Panel:
    """Mostra la resposta API en brut."""
    json_str = json.dumps(response_data, indent=2, ensure_ascii=False)
    syntax = Syntax(json_str, "json", theme="monokai", background_color="grey23", word_wrap=True)
    
    return Panel(
        syntax,
        title="📥 Resposta de l'API (d'OpenAI)",
        border_style="cyan",
        style="on grey23",
        padding=(0, 1)
    )


def wait_for_llm():
    """Mostra un indicador giratori mentre s'espera l'LLM."""
    return Live(
        Panel(
            Spinner("dots", text=Text("Esperant la resposta de l'LLM...", style="bold black on yellow")),
            border_style="yellow",
            style="on yellow",
            padding=(0, 1)
        ),
        console=console,
        refresh_per_second=10
    )


# ============================================================================
# FUNCIÓ DE XAT
# ============================================================================

def run_chat(use_tools: bool):
    """Executa una sessió de xat interactiva."""
    
    scenario_name = "AMB Function Calling" if use_tools else "SENSE Function Calling"
    scenario_color = "green" if use_tools else "red"

    console.print()
    console.print(Panel(
        Text(f"Escenari: {scenario_name}\n\nEts el llop! Escriu els teus missatges.\nPrem Enter amb un missatge buit per acabar.",
             style=f"bold bright_white on dark_{scenario_color}"),
        title=f"🎭 Comença el xat",
        border_style=scenario_color,
        style=f"on dark_{scenario_color}",
        padding=(1, 2)
    ))
    
    if use_tools:
        console.print()
        console.print(Panel(
            Syntax(json.dumps(AVAILABLE_TOOLS, indent=2), "json", theme="monokai", background_color="grey23", word_wrap=True),
            title="🔧 Eines disponibles per al porquet",
            border_style="cyan",
            style="on grey23",
            padding=(0, 1)
        ))
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Mostrar el context inicial
    console.print()
    console.print(show_context_stack(messages, use_tools))
    
    while True:
        # Obtenir l'entrada de l'usuari
        console.print()
        user_input = console.input("[bold blue]🐺 Tu (llop): [/bold blue]")
        
        # Entrada buida = finalitzar la conversa
        if not user_input.strip():
            console.print()
            console.print(Panel(
                Text("S'ha acabat la conversa. Es torna al menú...", style="bold bright_white on grey23"),
                border_style="dim",
                style="on grey23"
            ))
            break
        
        # Afegir missatge de l'usuari
        messages.append({"role": "user", "content": user_input})
        console.print(create_message_panel("user", user_input))
        
        # Dades de sol·licitud per mostrar-les
        request_data = {
            "model": MODEL,
            "messages": messages,
            "temperature": 0.7
        }
        if use_tools:
            request_data["tools"] = AVAILABLE_TOOLS
        if OPENAI_ENDPOINT:
            request_data["_endpoint"] = OPENAI_ENDPOINT
        
        # Mostrar la sol·licitud
        console.print()
        console.print(show_api_request(request_data))
        
        # Cridar l'API
        with wait_for_llm():
            if use_tools:
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                    tools=AVAILABLE_TOOLS,
                    temperature=0.7
                )
            else:
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                    temperature=0.7
                )
        
        assistant_message = response.choices[0].message
        
        # Generar dades de resposta per a mostrar-les
        response_data = {
            "id": response.id,
            "model": response.model,
            "finish_reason": response.choices[0].finish_reason,
            "message": {
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": None
            }
        }
        
        # Comprovar si hi ha crides a eines
        if assistant_message.tool_calls:
            response_data["message"]["tool_calls"] = [
                {
                    "id": tc.id,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in assistant_message.tool_calls
            ]
        
        # Mostrar la resposta API en brut
        console.print()
        console.print(show_api_response(response_data))
        
        # Processar les crides a eines, si n'hi ha
        if assistant_message.tool_calls:
            # Afegir el missatge de l'assistent amb les crides a eines
            messages.append({
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in assistant_message.tool_calls
                ]
            })
            
            if assistant_message.content:
                console.print()
                console.print(create_message_panel("assistant", assistant_message.content))
            
            # Executar cada crida a la funció corresponent.
            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                console.print()
                console.print(Panel(
                    Text(f"🔧 FUNCIÓ CRIDADA: {function_name}(\n   urgency=\"{function_args.get('urgency')}\",\n   message=\"{function_args.get('message')}\"\n)",
                         style="bold black on yellow"),
                    border_style="yellow",
                    style="on yellow",
                    padding=(0, 1)
                ))
                
                # Executar la funció
                result = call_hunter(**function_args)
                
                # Afegir el resultat de l'eina als missatges
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": result
                })
                
                console.print()
                console.print(create_message_panel("tool", result))
            
            # Mostrar sol·licitud de seguiment
            follow_request = {
                "model": MODEL,
                "messages": messages,
                "tools": AVAILABLE_TOOLS,
                "temperature": 0.7
            }
            if OPENAI_ENDPOINT:
                follow_request["_endpoint"] = OPENAI_ENDPOINT
            console.print()
            console.print(show_api_request(follow_request))
            
            # Obtenir una resposta de seguiment
            with wait_for_llm():
                follow_up = client.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                    tools=AVAILABLE_TOOLS,
                    temperature=0.7
                )
            
            follow_up_content = follow_up.choices[0].message.content
            messages.append({"role": "assistant", "content": follow_up_content})
            
            console.print()
            console.print(show_api_response({
                "id": follow_up.id,
                "model": follow_up.model,
                "finish_reason": follow_up.choices[0].finish_reason,
                "message": {"role": "assistant", "content": follow_up_content}
            }))
            
            console.print()
            console.print(create_message_panel("assistant", follow_up_content))
        else:
            # Sense crides a eines – només una resposta normal.
            messages.append({"role": "assistant", "content": assistant_message.content})
            console.print()
            console.print(create_message_panel("assistant", assistant_message.content))
        
        # Mostrar el context actualitzat
        console.print()
        console.print(show_context_stack(messages, use_tools))


# ============================================================================
# MENÚ PRINCIPAL
# ============================================================================

def show_menu():
    """Mostra el menú principal."""
    console.print()
    console.print(Panel(
        Text.from_markup(
            "[bold bright_white]🐷 Demo de Function Calling amb OpenAI 🐺[/bold bright_white]\n\n"
            "[bright_cyan]Edició dels Tres Porquets[/bright_cyan]\n\n"
            "[bright_white]Fas de llop. Prova els dos escenaris\n"
            "i mira com el function calling canvia el comportament![/bright_white]"
        ),
        title="🏠 Menú 🏠",
        title_align="center",
        border_style="bright_magenta",
        style="on grey23",
        padding=(1, 4)
    ))
    
    console.print()
    menu_table = Table(box=box.ROUNDED, show_header=False, style="on grey23", border_style="cyan")
    menu_table.add_column("Opció", style="bold bright_cyan on grey23", width=5)
    menu_table.add_column("Descripció", style="bright_white on grey23")
    menu_table.add_row("1", "Escenari 1: Xat SENSE function calling (el porquet només pot parlar)")
    menu_table.add_row("2", "Escenari 2: Xat AMB function calling (el porquet pot cridar el caçador)")
    menu_table.add_row("q", "Surt")
    console.print(Panel(menu_table, border_style="cyan", style="on grey23", padding=(0, 1)))


def main():
    """Funció principal."""
    global client
    
    console.clear()
    
    # Comprovar si existeix la clau API
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        console.print(Panel(
            Text("No s'ha trobat OPENAI_API_KEY!\n\nCrea un fitxer \".env\" amb:\nOPENAI_API_KEY=la-teva-clau",
                 style="bold bright_white on dark_red"),
            title="❌ Error",
            border_style="red",
            style="on dark_red"
        ))
        return
    
    # Inicialitzar el client amb opcions personalitzades endpoint (opcional)
    if OPENAI_ENDPOINT:
        client = OpenAI(api_key=api_key, base_url=OPENAI_ENDPOINT)
    else:
        client = OpenAI(api_key=api_key)
    
    # Mostrar la configuració
    console.print(Panel(
        Text(f"Model: {MODEL}\nEndpoint: {OPENAI_ENDPOINT or 'https://api.openai.com/v1'}", 
             style="bright_white on grey23"),
        title="⚙️ Configuració",
        border_style="cyan",
        style="on grey23"
    ))
    
    while True:
        show_menu()
        
        console.print()
        choice = console.input("[bold cyan]Tria una opció (1/2/q): [/bold cyan]").strip().lower()
        
        if choice == "1":
            run_chat(use_tools=False)
        elif choice == "2":
            run_chat(use_tools=True)
        elif choice == "q":
            console.print()
            console.print(Panel(
                Text("Adéu! 🐷👋", style="bold bright_white on grey23"),
                border_style="magenta",
                style="on grey23"
            ))
            break
        else:
            console.print()
            console.print(Panel(
                Text("Opció no vàlida. Tria 1, 2 o q.", style="bold black on yellow"),
                border_style="yellow",
                style="on yellow"
            ))


if __name__ == "__main__":
    main()
