# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# BSC Agents Course — Transformers, LLMs, RAG and Agents: From Theory to Production
# Licensed under Creative Commons BY-NC-SA 4.0 — reuse must credit the author, no commercial use, derivatives under the same license.

# =============================================================================================================== #
# Universitat Politècnica de Catalunya (UPC)                                                                      #
# =============================================================================================================== #

"""
📚 Context Explorer — RAG edition: watch the context grow when you cheat at solitaire.

This is the Context Explorer from week 1, with one thing added: retrieval.

Before each call, a Retriever reads a knowledge file and pastes it into the
prompt. The single-file retriever does the most trivial thing possible — it
returns the WHOLE file, every turn, ignoring your question. That is single-file
RAG. It works. The catch is visible here: the file rides in the prompt on every
turn, so prompt_tokens climbs and never comes back down.

Watch four things each turn:
- 📥 Retrieval   — what the retriever pulled in (here: the whole file)
- 📤 API Request — the prompt the model actually receives (context + question)
- 📚 Context     — the message stack, growing
- 💸 Token cost  — prompt_tokens per turn, climbing

Later in the course we swap the WholeFileRetriever for an EmbeddingsRetriever.
The loop below does not change — only the Retriever does. That is the whole point.

Usage:
    1. Copy .env.example to .env and fill in your values
    2. uv run context_explorer_rag.py
    3. (optional) point it at your own file:  KNOWLEDGE_FILE=mynotes.txt uv run context_explorer_rag.py

In-chat commands:
    /file <path>   load a different knowledge file
    /context       print the loaded knowledge file
    (empty line)   quit
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
OPENAI_ENDPOINT = os.getenv("OPENAI_ENDPOINT")  # Optional: for alternative API endpoints
KNOWLEDGE_FILE = os.getenv("KNOWLEDGE_FILE", "knowledge.txt")

# Grounding instruction: answer from the context, admit it when the answer is not there.
# This is what lets you SEE that the model reads the context and not its training data —
# ask something off-corpus and it should say so instead of confabulating.
SYSTEM_PROMPT = "Answer using only the context below. If the answer is not in the context, say you don't know."

# The RAG prompt template — students reuse this shape all week.
PROMPT_TEMPLATE = "Context:\n----\n{context}\n----\n\nQuestion: {question}"


# =============================================================================================================== #
# Retrieval — the one part that changes between simple RAG and embeddings RAG.                                    #
# =============================================================================================================== #

class Retriever:
    """The retrieval interface. Given a question, return the context to inject.

    Everything else in this program — the chat loop, the panels, the token
    accounting — stays the same no matter how retrieval works. Swap the
    Retriever and you have a different RAG system.
    """

    def retrieve(self, question: str) -> str:
        raise NotImplementedError


class WholeFileRetriever(Retriever):
    """Single-file RAG: ignore the question, return the WHOLE file. Cheating at solitaire.

    No chunking, no embeddings, no vector store. The "retrieval" step is `open().read()`.
    The question is not even looked at — the model gets the entire file every time and
    finds the answer itself. This is the simplest thing that earns the name RAG.
    """

    def __init__(self, path: str):
        self.path = path
        with open(path, encoding="utf-8") as f:
            self.text = f.read()

    def retrieve(self, question: str) -> str:
        return self.text  # the whole file — the question is ignored on purpose

    def describe(self) -> str:
        return f"WholeFileRetriever · {os.path.basename(self.path)} · whole file, every turn"


# Later in the course:
#
#     class EmbeddingsRetriever(Retriever):
#         """Chunk the file, embed the chunks, embed the question, return the top-k nearest."""
#         def retrieve(self, question: str) -> str:
#             q = embed(question)
#             top = nearest(q, self.chunks, k=4)
#             return "\n\n".join(top)
#
# The chat loop below does not change. Only this class does.


# =============================================================================================================== #
# Panels                                                                                                          #
# =============================================================================================================== #

def _approx_tokens(text: str) -> int:
    """Rough estimate before the API answers (≈ 4 chars per token). The real number
    comes back in usage.prompt_tokens — this is just for the retrieval preview."""
    return max(1, len(text) // 4)


def _truncate(text: str, width: int = 90) -> str:
    one_line = text.replace("\n", " ")
    if len(one_line) <= width:
        return one_line
    return one_line[:width] + f"… [+{len(one_line) - width} chars]"


def show_retrieval(retriever: "WholeFileRetriever", context: str) -> Panel:
    """Show what retrieval pulled in for this turn."""
    body = Text()
    body.append(f"retriever : {retriever.describe()}\n", style="bright_white on grey23")
    body.append(f"pulled in : {len(context)} chars  (~{_approx_tokens(context)} tokens)\n", style="bright_yellow on grey23")
    body.append("preview   : ", style="bright_white on grey23")
    body.append(_truncate(context, 120) + "\n", style="grey70 on grey23")
    body.append("→ this whole block is pasted into the prompt, every turn", style="italic bright_red on grey23")
    return Panel(body, title="📥 Retrieval", border_style="green", style="on grey23", padding=(0, 1))


def show_context(messages: list) -> Panel:
    """Show the current conversation context. Long content is truncated so the
    stack stays readable — the [+N chars] badge is where the cost hides."""
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
        table.add_row(str(i), role, _truncate(msg.get("content", "")))

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


def show_cost(history: list) -> Panel:
    """Show prompt_tokens per turn as a little bar chart — the climb is the lesson."""
    table = Table(box=box.SIMPLE, show_header=True, header_style="bold bright_white on grey23", style="on grey23")
    table.add_column("Turn", style="bright_cyan on grey23", width=5)
    table.add_column("prompt_tokens", style="bright_yellow on grey23", width=14)
    table.add_column("", style="bright_red on grey23")

    peak = max(history) if history else 1
    for i, pt in enumerate(history, start=1):
        bar = "█" * max(1, int(28 * pt / peak))
        table.add_row(str(i), str(pt), bar)

    note = "every turn re-sends the whole file → prompt_tokens only goes up"
    body = Table.grid()
    body.add_row(table)
    body.add_row(Text(note, style="italic bright_red on grey23"))
    return Panel(body, title="💸 Token cost (prompt_tokens per turn)", border_style="red", style="on grey23", padding=(0, 1))


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


# =============================================================================================================== #
# Chat loop                                                                                                       #
# =============================================================================================================== #

def run_chat(retriever: WholeFileRetriever):
    """Run the chat loop. Each turn: retrieve → wrap → send → watch the stack grow."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    prompt_token_history = []

    console.print()
    console.print(Panel(
        Text(
            "Ask about the knowledge file and watch the context grow.\n"
            "Try a question the file answers, then one it does NOT — a grounded\n"
            "model should admit it doesn't know.\n\n"
            "Commands:  /file <path>   /context   (empty line = quit)",
            style="bright_white on grey23"
        ),
        title="📚 Context Explorer — RAG edition",
        border_style="bright_magenta",
        style="on grey23",
        padding=(1, 2)
    ))

    console.print()
    console.print(show_context(messages))

    while True:
        console.print()
        user_input = console.input("[bold blue]👤 You: [/bold blue]")

        if not user_input.strip():
            console.print(Panel(Text("Goodbye!", style="bright_white on grey23"), border_style="dim"))
            break

        # In-chat commands so students can play.
        if user_input.strip() == "/context":
            console.print(Panel(Text(retriever.text, style="grey70 on grey23"),
                                title=f"📄 {os.path.basename(retriever.path)}",
                                border_style="green", style="on grey23", padding=(0, 1)))
            continue
        if user_input.strip().startswith("/file "):
            new_path = user_input.strip()[len("/file "):].strip()
            try:
                retriever = WholeFileRetriever(new_path)
                console.print(Panel(Text(f"Loaded {new_path} ({len(retriever.text)} chars).",
                                         style="bright_white on grey23"),
                                    border_style="green", style="on grey23"))
            except OSError as exc:
                console.print(Panel(Text(f"Could not load {new_path}: {exc}",
                                         style="bold bright_white on dark_red"),
                                    border_style="red", style="on dark_red"))
            continue

        # 1) RETRIEVE — pull the context. (Here: the whole file, ignoring the question.)
        context = retriever.retrieve(user_input)
        console.print()
        console.print(show_retrieval(retriever, context))

        # 2) AUGMENT — paste the context into the prompt template, then add to the stack.
        #    The wrapped prompt (context + question) is what goes into the context — so the
        #    file rides in EVERY user turn we keep. That is exactly where the cost comes from.
        wrapped = PROMPT_TEMPLATE.format(context=context, question=user_input)
        messages.append({"role": "user", "content": wrapped})
        console.print(show_message("user", user_input))  # show the bare question to the human

        # Build and show the request.
        request_data = {"model": MODEL, "messages": messages, "temperature": 0.7}
        if OPENAI_ENDPOINT:
            request_data["_endpoint"] = OPENAI_ENDPOINT
        console.print()
        console.print(show_api_request(request_data))

        # 3) GENERATE — call the model.
        with wait_spinner():
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=0.7
            )

        assistant_content = response.choices[0].message.content

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
            "message": {"role": "assistant", "content": assistant_content},
            "usage": usage_data
        }
        console.print()
        console.print(show_api_response(response_data))

        messages.append({"role": "assistant", "content": assistant_content})

        console.print()
        console.print(show_message("assistant", assistant_content))

        # The two payoffs: the growing stack, and the climbing bill.
        console.print()
        console.print(show_context(messages))

        prompt_token_history.append(response.usage.prompt_tokens)
        console.print()
        console.print(show_cost(prompt_token_history))


def main():
    global client

    console.clear()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        console.print(Panel(
            Text("OPENAI_API_KEY not found!\n\nCopy .env.example to .env and fill it in.",
                 style="bold bright_white on dark_red"),
            title="❌ Error", border_style="red", style="on dark_red"
        ))
        return

    # Load the knowledge file. Resolve relative to this script so it runs from anywhere.
    knowledge_path = KNOWLEDGE_FILE
    if not os.path.isabs(knowledge_path):
        knowledge_path = os.path.join(os.path.dirname(__file__), knowledge_path)
    try:
        retriever = WholeFileRetriever(knowledge_path)
    except OSError as exc:
        console.print(Panel(
            Text(f"Could not load knowledge file '{knowledge_path}':\n{exc}\n\n"
                 "Set KNOWLEDGE_FILE in .env or pass /file <path> once running.",
                 style="bold bright_white on dark_red"),
            title="❌ Error", border_style="red", style="on dark_red"
        ))
        return

    # Initialize client with optional custom endpoint.
    if OPENAI_ENDPOINT:
        client = OpenAI(api_key=api_key, base_url=OPENAI_ENDPOINT)
    else:
        client = OpenAI(api_key=api_key)

    console.print(Panel(
        Text(
            f"Model     : {MODEL}\n"
            f"Endpoint  : {OPENAI_ENDPOINT or 'https://api.openai.com/v1'}\n"
            f"Knowledge : {os.path.basename(knowledge_path)} ({len(retriever.text)} chars, "
            f"~{_approx_tokens(retriever.text)} tokens)\n"
            f"Retriever : {retriever.describe()}",
            style="bright_white on grey23"
        ),
        title="⚙️ Configuration",
        border_style="cyan",
        style="on grey23"
    ))

    run_chat(retriever)


if __name__ == "__main__":
    main()
