# =============================================================================================================== #
# Plan de Generación de Talento Digital 2025 - INTIA/UEx                                                          #
# Actividad financiada por la Consejería de Economía, Empleo y Transformación Digital de la Junta de Extremadura  #
# Dirección General de Digitalización Regional de la Junta de Extremadura                                         #
# =============================================================================================================== #

"""
📚 Context Explorer: See How LLM Context Works

A simple interactive demo to visualize:
- The messages sent to the API (context)
- The raw API request and response

Usage:
    1. Create a .env file with your API key
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

# Configuration from .env
MODEL = os.getenv("MODEL", "gpt-4.1-mini")
OPENAI_API_ENDPOINT = os.getenv("OPENAI_API_ENDPOINT")  # Optional: for alternative API endpoints

SYSTEM_PROMPT = "You are a helpful assistant."


def show_context(messages: list) -> Panel:
    """Show the current conversation context."""
    table = Table(
        box=box.SIMPLE,
        show_header=True,
        header_style="bold bright_white on grey23",
        style="on grey23"
    )
    table.add_column("#", style="bright_cyan on grey23", width=3)
    table.add_column("Role", style="bright_magenta on grey23", width=12)
    table.add_column("Content", style="bright_white on grey23")
    
    for i, msg in enumerate(messages):
        role = msg.get("role", "unknown")
        content = msg.get("content", "").replace("\n", " ")
        table.add_row(str(i), role, content)
    
    return Panel(
        table,
        title=f"📚 Context ({len(messages)} messages)",
        border_style="magenta",
        style="on grey23",
        padding=(0, 1)
    )


def show_api_request(request_data: dict) -> Panel:
    """Show the API request."""
    json_str = json.dumps(request_data, indent=2, ensure_ascii=False)
    syntax = Syntax(json_str, "json", theme="monokai", background_color="grey23", word_wrap=True)
    return Panel(syntax, title="📤 API Request", border_style="yellow", style="on grey23", padding=(0, 1))


def show_api_response(response_data: dict) -> Panel:
    """Show the API response."""
    json_str = json.dumps(response_data, indent=2, ensure_ascii=False)
    syntax = Syntax(json_str, "json", theme="monokai", background_color="grey23", word_wrap=True)
    return Panel(syntax, title="📥 API Response", border_style="cyan", style="on grey23", padding=(0, 1))


def show_message(role: str, content: str) -> Panel:
    """Show a chat message."""
    styles = {
        "user": ("bright_white on blue", "blue", "👤 You"),
        "assistant": ("bright_white on dark_green", "green", "🤖 Assistant"),
        "system": ("bright_white on purple4", "magenta", "⚙️ System")
    }
    text_style, border, title = styles.get(role, ("bright_white on grey23", "white", role))
    return Panel(Text(content, style=text_style), title=title, border_style=border, padding=(0, 1))


def wait_spinner():
    """Show a waiting spinner."""
    return Live(
        Panel(
            Spinner("dots", text=Text(" Waiting for response...", style="bold black on yellow")),
            border_style="yellow", style="on yellow", padding=(0, 1)
        ),
        console=console, refresh_per_second=10
    )


def run_chat():
    """Run the chat loop."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    console.print()
    console.print(Panel(
        Text("Type your messages. Empty message = quit.\nWatch the context grow with each exchange!", 
             style="bright_white on grey23"),
        title="📚 Context Explorer",
        border_style="bright_magenta",
        style="on grey23",
        padding=(1, 2)
    ))
    
    # Show initial context
    console.print()
    console.print(show_context(messages))
    
    while True:
        console.print()
        user_input = console.input("[bold blue]👤 You: [/bold blue]")
        
        if not user_input.strip():
            console.print(Panel(Text("Goodbye!", style="bright_white on grey23"), border_style="dim"))
            break
        
        messages.append({"role": "user", "content": user_input})
        console.print(show_message("user", user_input))
        
        # Build and show request
        request_data = {
            "model": MODEL,
            "messages": messages,
            "temperature": 0.7
        }
        if OPENAI_API_ENDPOINT:
            request_data["_endpoint"] = OPENAI_API_ENDPOINT
        console.print()
        console.print(show_api_request(request_data))
        
        # Call API
        with wait_spinner():
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=0.7
            )
        
        assistant_content = response.choices[0].message.content
        
        # Show response
        response_data = {
            "id": response.id,
            "model": response.model,
            "finish_reason": response.choices[0].finish_reason,
            "message": {
                "role": "assistant",
                "content": assistant_content
            },
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }
        console.print()
        console.print(show_api_response(response_data))
        
        messages.append({"role": "assistant", "content": assistant_content})
        
        console.print()
        console.print(show_message("assistant", assistant_content))
        
        # Show updated context
        console.print()
        console.print(show_context(messages))


def main():
    global client
    
    console.clear()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        console.print(Panel(
            Text("OPENAI_API_KEY not found!\n\nCreate a .env file with:\nOPENAI_API_KEY=your-key-here",
                 style="bold bright_white on dark_red"),
            title="❌ Error", border_style="red", style="on dark_red"
        ))
        return
    
    # Initialize client with optional custom endpoint
    if OPENAI_API_ENDPOINT:
        client = OpenAI(api_key=api_key, base_url=OPENAI_API_ENDPOINT)
    else:
        client = OpenAI(api_key=api_key)
    
    # Show configuration
    console.print(Panel(
        Text(f"Model: {MODEL}\nEndpoint: {OPENAI_API_ENDPOINT or 'https://api.openai.com/v1'}", 
             style="bright_white on grey23"),
        title="⚙️ Configuration",
        border_style="cyan",
        style="on grey23"
    ))
    
    run_chat()


if __name__ == "__main__":
    main()
