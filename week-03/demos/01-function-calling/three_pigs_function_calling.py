# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# Curs per a agents de BSC — Transformers, LLMs, RAG i Agents: Des del teòric fins a la pràctica
# Amb llicència Creative Commons BY-NC-SA 4.0 – és obligatori citar l'autor, no es pot fer ús comercial, i les obres derivades han de tenir la mateixa llicència.

"""
🐷 OpenAI Function Calling Demostració: Els tres petits conills 🐺

Una demostració interactiva on TU et poses al lloc del llop! Comença a comparar com reacciona la gallina amb i sense function calling.

Requisits: instaleu els paquets necessaris amb `pip install -r requirements.txt`

Ús:
    1. Crea un fitxer ".env" amb la teva clau API.
    2. python three_pigs_function_calling.py
"""

import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Llibreta extensa per a crear una interfície d'usuari atractiva per a terminals.
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text
from rich.live import Live
from rich.spinner import Spinner
from rich.table import Table
from rich import box

# Cargar les variables d'entorn des del fitxer ".env"
load_dotenv()

# Inicialitzar la consola Ric
console = Console()

# Inicialitzar el client OpenAI
client = None

# Configuració des del fitxer .env
MODEL = os.getenv("MODEL", "gpt-4.1-mini")
OPENAI_ENDPOINT = os.getenv("OPENAI_ENDPOINT")  # Opcional: per a alternatives API endpoints

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
# Definició de funcions per a LLM
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
    """Simula la situació d'enviar un missatge de sol·licitud d'ajuda al caçador."""
    responses = {
        "low": "The hunter received your message and will check on you later.",
        "medium": "The hunter is on his way, should arrive in 10 minutes.",
        "high": "The hunter grabbed his shotgun and is running to your house!",
        "emergency": "The hunter is sprinting to your location with backup and heavy weapons! Hold on!"
    }
    return responses.get(urgency, "The hunter received your call.")


# ============================================================================
# FUNCIONS D'ASSISTÈNCIA PER A LA INTERFÀCIA D'USUARI
# ============================================================================

def create_message_panel(role: str, content: str) -> Panel:
    """Crea un panell estilificat per a un missatge de xat."""
    styles = {
        "user": ("bright_white on blue", "blue", "🐺 You (The Wolf)"),
        "assistant": ("bright_white on dark_green", "green", "🐷 Pig"),
        "system": ("bright_white on purple4", "magenta", "⚙️ System"),
        "tool": ("black on yellow", "yellow", "🔧 Tool Result")
    }
    
    text_style, border_color, title = styles.get(role, ("bright_white on grey23", "white", role))
    
    return Panel(
        Text(content, style=text_style),
        title=title,
        title_align="a l'esquerra",
        border_style=border_color,
        padding=(0, 1)
    )


def show_context_stack(messages: list, tools_available: bool) -> Panel:
    """Mostra l'estat actual de la pila de converses."""
    table = Table(
        box=box.SIMPLE,
        show_header=True,
        header_style="bold bright_white on grey23",
        style="on grey23"
    )
    table.add_column("#", style="bright_cyan on grey23", width=3)
    table.add_column("Role", style="bright_magenta on grey23", width=12)
    table.add_column("Content Preview", style="bright_white on grey23")
    
    for i, msg in enumerate(messages):
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        if content:
            preview = content.replace("\n", " ")
        else:
            preview = "(tool_calls)"
        table.add_row(str(i), role, preview)
    
    tools_text = "✅ Tools: [call_hunter]" if tools_available else "❌ No Tools"
    
    return Panel(
        table,
        title=f"📚 Context Stack ({len(messages)} messages) | {tools_text}",
        border_style="magenta",
        style="en gris 23",
        padding=(0, 1)
    )


def show_api_request(request_data: dict) -> Panel:
    """Mostra la sol·licitud original API."""
    json_str = json.dumps(request_data, indent=2, ensure_ascii=False)
    syntax = Syntax(json_str, "json", theme="monocai", background_color="gris23", word_wrap=True)
    
    return Panel(
        syntax,
        title="📤 API Request (sent to OpenAI)",
        border_style="groc",
        style="en gris 23",
        padding=(0, 1)
    )


def show_api_response(response_data: dict) -> Panel:
    """Mostra la resposta original API."""
    json_str = json.dumps(response_data, indent=2, ensure_ascii=False)
    syntax = Syntax(json_str, "json", theme="monocai", background_color="gris23", word_wrap=True)
    
    return Panel(
        syntax,
        title="📥 API Response (from OpenAI)",
        border_style="cian",
        style="en gris 23",
        padding=(0, 1)
    )


def wait_for_llm():
    """Mostra un indicador de progrés mentre s'espera la LLM."""
    return Live(
        Panel(
            Spinner("dots", text=Text("Esperant la resposta LLM.", style="negre gros sobre fons groc")),
            border_style="groc",
            style="en groc",
            padding=(0, 1)
        ),
        console=console,
        refresh_per_second=10
    )


# ============================================================================
# FUNTIONS DE MISSATGE
# ============================================================================

def run_chat(use_tools: bool):
    """Organitzar una sessió de xat interactiva."""
    
    scenario_name = "WITH Function Calling" if use_tools else "WITHOUT Function Calling"
    scenario_color = "green" if use_tools else "red"
    
    console.print()
    console.print(Panel(
        Text(f"Scenario: {scenario_name}\n\nYou are the wolf! Type your messages.\nPress Enter with empty message to end.", 
             style=f"bold bright_white on dark_{scenario_color}"),
        title=f"🎭 Starting Chat",
        border_style=scenario_color,
        style=f"on dark_{scenario_color}",
        padding=(1, 2)
    ))
    
    if use_tools:
        console.print()
        console.print(Panel(
            Syntax(json.dumps(AVAILABLE_TOOLS, indent=2), "json", theme="monocai", background_color="gris23", word_wrap=True),
            title="🔧 Tools Available to the Pig",
            border_style="cian",
            style="en gris 23",
            padding=(0, 1)
        ))
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Mostrar el context inicial
    console.print()
    console.print(show_context_stack(messages, use_tools))
    
    while True:
        # Obtenir la entrada de l'usuari
        console.print()
        user_input = console.input("[bold blue]🐺 You (wolf): [/bold blue]")
        
        # Entrada buida = finalitzar la conversa
        if not user_input.strip():
            console.print()
            console.print(Panel(
                Text("La conversa ha finalitzat. Tornant al menú...", style="negre intens i blanc brillant sobre gris clar"),
                border_style="dim",
                style="en gris 23"
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
        
        # Trucar al API
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
        
        # Verificar les crides a les eines.
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
        
        # Mostrar la resposta original API
        console.print()
        console.print(show_api_response(response_data))
        
        # Si hi ha eines de process, es indiquen aquí.
        if assistant_message.tool_calls:
            # Afegir un missatge d'ajuda amb les crides a les eines.
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
                    Text(f"🔧 FUNCTION CALLED: {function_name}(\n   urgency=\"{function_args.get('urgency')}\",\n   message=\"{function_args.get('message')}\"\n)", 
                         style="negre gros sobre fons groc"),
                    border_style="groc",
                    style="en groc",
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
# MÉS INFORMACIÓ
# ============================================================================

def show_menu():
    """Mostrar el menú principal."""
    console.print()
    console.print(Panel(
        Text.from_markup(
            "[bold bright_white]🐷 OpenAI Function Calling Demo 🐺[/bold bright_white]\n\n"
            "[bright_cyan]The Three Little Pigs Edition[/bright_cyan]\n\n"
            "[bright_white]You play as the wolf. Try both scenarios\n"
            "and see how function calling changes behavior![/bright_white]"
        ),
        title="🏠 Menu 🏠",
        title_align="centre",
        border_style="magenta brillant",
        style="en gris 23",
        padding=(1, 4)
    ))
    
    console.print()
    menu_table = Table(box=box.ROUNDED, show_header=False, style="on grey23", border_style="cyan")
    menu_table.add_column("Option", style="bold bright_cyan on grey23", width=5)
    menu_table.add_column("Description", style="bright_white on grey23")
    menu_table.add_row("1", "Scenario 1: Chat WITHOUT function calling (pig can only talk)")
    menu_table.add_row("2", "Scenario 2: Chat WITH function calling (pig can call hunter)")
    menu_table.add_row("q", "Quit")
    console.print(Panel(menu_table, border_style="cian", style="en gris 23", padding=(0, 1)))


def main():
    """Funció principal."""
    global client
    
    console.clear()
    
    # Verificar si existeix la clau API.
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        console.print(Panel(
            Text("La clau API d'OPENAI no s'ha trobat!\\n\\nCreeu un fitxer \".env\" amb el següent contingut:\\nOPENAI_API_KEY=la-seva-clau",
                 style="negre i brillant, blanc sobre vermell fosc"),
            title="❌ Error",
            border_style="vermell",
            style="en vermell fosc"
        ))
        return
    
    # Inicialitzar el client amb opcions personalitzades endpoint (opcional)
    if OPENAI_ENDPOINT:
        client = OpenAI(api_key=api_key, base_url=OPENAI_ENDPOINT)
    else:
        client = OpenAI(api_key=api_key)
    
    # Configuració
    console.print(Panel(
        Text(f"Model: {MODEL}\nEndpoint: {OPENAI_ENDPOINT or 'https://api.openai.com/v1'}", 
             style="blanc clar sobre gris 23"),
        title="⚙️ Configuration",
        border_style="cian",
        style="en gris 23"
    ))
    
    while True:
        show_menu()
        
        console.print()
        choice = console.input("[bold cyan]Choose option (1/2/q): [/bold cyan]").strip().lower()
        
        if choice == "1":
            run_chat(use_tools=False)
        elif choice == "2":
            run_chat(use_tools=True)
        elif choice == "q":
            console.print()
            console.print(Panel(
                Text("Goodbye! 🐷👋", style="bold bright_white on grey23"),
                border_style="magenta",
                style="en gris 23"
            ))
            break
        else:
            console.print()
            console.print(Panel(
                Text("Opció no vàlida. Si us plau, trieu l'opció 1, 2 o 'q'.", style="negre gros sobre fons groc"),
                border_style="groc",
                style="en groc"
            ))


if __name__ == "__main__":
    main()
