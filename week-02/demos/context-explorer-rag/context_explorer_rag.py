# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# BSC Agents Course — Transformers, LLMs, RAG and Agents: From Theory to Production
# Licensed under Creative Commons BY-NC-SA 4.0 — reuse must credit the author, no commercial use, derivatives under the same license.

# =============================================================================================================== #
# Universitat Politècnica de Catalunya (UPC)                                                                      #
# =============================================================================================================== #

"""
📚 Context Explorer — single-file RAG: what the app stores vs. what the LLM receives.

Single-file RAG is the crudest thing that earns the name: paste a whole file into
the prompt as context and ask. This explorer shows the part everyone gets wrong —
the difference between the conversation the CHAT UI keeps and the call the LLM
actually receives. They are not the same, and the gap is the lesson.

THREE LAYERS (the same shape as serving an assistant over an OpenAI-compatible API,
e.g. LAMB):

    🖥️  CHAT UI        sends:  history (bare) + your latest message
                                  |   history = what you see; no system prompt, no augmentation
                                  v
    🛠️  ASSISTANT ENDPOINT  (STATELESS; the model id selects system prompt + template + RAG)
            builds:  [system] + [history] + [ template(your message, RAG augmentation) ]
                                  |   rebuilt every call — it has no state to keep it in
                                  v
    🧠  LLM            returns:  the response only
                                  ^
    🖥️  CHAT UI        appends (your message, response) to history   ✗ augmentation NOT saved

Because the endpoint is stateless, the augmentation is built fresh every turn and
thrown away. The UI history stays bare. To KEEP the augmentation you would have to
store augmented history and make the chat stateful — try `/stateful` to see what
that costs.

TWO PLACEMENT MODES (switch live with /mode):
- user-augment    (default) — the file is injected into the USER message every turn.
                              Volatile: it rides in the tail of the prompt, re-sent and
                              re-billed every call, never cacheable.
- system-grounding          — the file is placed in the SYSTEM prompt ONCE (part of the
                              assistant's config). Retrieve once, at the start. The
                              conversation stays "pure" (bare Q&A), and the file sits in
                              the stable, cacheable prefix (KV cache).

Usage:
    1. Copy .env.example to .env and fill in your values
    2. uv run context_explorer_rag.py
    3. (optional) RAG_MODE=system-grounding  KNOWLEDGE_FILE=mynotes.txt  uv run context_explorer_rag.py

In-chat commands:
    /mode user-augment | system-grounding   switch placement (resets the conversation)
    /stateful                                toggle storing augmented history (the stateful alternative)
    /file <path>                             load a different knowledge file
    /context                                 print the loaded knowledge file
    (empty line)                             quit
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
OPENAI_ENDPOINT = os.getenv("OPENAI_ENDPOINT")  # Optional: alternative OpenAI-compatible endpoint
KNOWLEDGE_FILE = os.getenv("KNOWLEDGE_FILE", "knowledge.txt")

MODE_USER_AUGMENT = "user-augment"
MODE_SYSTEM_GROUNDING = "system-grounding"
RAG_MODE = os.getenv("RAG_MODE", MODE_USER_AUGMENT)

# Grounding instruction: answer from the context, admit it when the answer is not there.
SYSTEM_PROMPT_BASE = "Answer using only the context provided. If the answer is not in the context, say you don't know."

# The RAG prompt template — the shape students reuse all week.
PROMPT_TEMPLATE = "Context:\n----\n{context}\n----\n\nQuestion: {question}"


# =============================================================================================================== #
# Retrieval — the one part that changes between single-file RAG and embeddings RAG.                               #
# =============================================================================================================== #

class WholeFileRetriever:
    """Single-file RAG: ignore the question, return the WHOLE file. Cheating at solitaire.

    No chunking, no embeddings, no vector store. The "retrieval" step is `open().read()`.
    Later in the course this is swapped for an EmbeddingsRetriever that returns only the
    top-k nearest chunks — and nothing else in this program changes. That is the point.
    """

    def __init__(self, path: str):
        self.path = path
        with open(path, encoding="utf-8") as f:
            self.text = f.read()

    def retrieve(self, question: str) -> str:
        return self.text  # the whole file — the question is ignored on purpose

    def describe(self) -> str:
        return f"WholeFileRetriever · {os.path.basename(self.path)} · whole file"


# =============================================================================================================== #
# The two layers that matter — and the boundary between them.                                                    #
# =============================================================================================================== #

class AssistantEndpoint:
    """A STATELESS RAG endpoint — the same shape as serving an assistant over an
    OpenAI-compatible API (this is what LAMB does).

    It holds NO conversation state. On every call it receives the bare history + the
    latest user message from the UI, looks up its configuration (system prompt, prompt
    template, RAG source — here fixed at construction, in production keyed by model id),
    and BUILDS the real LLM call from scratch:

        user-augment      → [system] + history + [user: template(retrieve(msg), msg)]
        system-grounding  → [system + file] + history + [user: msg]   (bare; file is in system)

    The augmentation it builds is never returned and never stored. Next call it builds again.
    """

    def __init__(self, retriever: WholeFileRetriever, mode: str):
        self.retriever = retriever
        self.mode = mode
        if mode == MODE_SYSTEM_GROUNDING:
            # Retrieve ONCE, at setup: the file becomes part of the assistant's system prompt.
            grounding = retriever.retrieve("")  # whole file; query ignored
            self.system_prompt = (
                SYSTEM_PROMPT_BASE
                + "\n\nContext:\n----\n" + grounding + "\n----"
            )
            self.retrieved_at_setup = True
        else:
            self.system_prompt = SYSTEM_PROMPT_BASE
            self.retrieved_at_setup = False

    def build(self, history: list, user_message: str) -> dict:
        """Build the LLM call from the bare history + the latest user message.

        Returns a dict describing the build so the explorer can render the boundary:
          messages          — the actual list sent to the LLM
          augmented_index   — index of the message the endpoint augmented (or None)
          retrieval         — what retrieval did this turn (string), or None
        """
        messages = [{"role": "system", "content": self.system_prompt}]
        messages += history  # passed straight through from the UI — still bare

        if self.mode == MODE_SYSTEM_GROUNDING:
            # File already lives in the system prompt. The user turn is bare. No retrieval now.
            messages.append({"role": "user", "content": user_message})
            return {"messages": messages, "augmented_index": None,
                    "retrieval": "none this turn — the file is in the system prompt (retrieved once, at setup)"}

        # user-augment: retrieve now and inject the file into THIS user message.
        context = self.retriever.retrieve(user_message)
        built = PROMPT_TEMPLATE.format(context=context, question=user_message)
        messages.append({"role": "user", "content": built})
        return {"messages": messages, "augmented_index": len(messages) - 1,
                "retrieval": f"retrieved {len(context)} chars (~{_approx_tokens(context)} tokens) and injected into THIS user message"}

    def complete(self, history: list, user_message: str) -> dict:
        """Build → call the LLM → return the response. The endpoint keeps nothing."""
        build = self.build(history, user_message)
        with wait_spinner():
            response = client.chat.completions.create(
                model=MODEL, messages=build["messages"], temperature=0.7
            )
        build["response"] = response
        return build


class ChatUI:
    """The chat UI. It holds the conversation the USER sees — bare turns only.
    No system prompt, no augmentation: those live behind the endpoint."""

    def __init__(self, stateful_augment: bool = False):
        self.history = []
        # If True, the UI stores the AUGMENTED user message instead of the bare one —
        # the "make the chat stateful" alternative. Off by default (the realistic model).
        self.stateful_augment = stateful_augment

    def outgoing(self, user_message: str) -> list:
        """What the UI sends to the endpoint: its history + the new message (all bare)."""
        return self.history + [{"role": "user", "content": user_message}]

    def record(self, user_message: str, assistant_message: str, augmented_user: str = None):
        stored_user = augmented_user if (self.stateful_augment and augmented_user) else user_message
        self.history.append({"role": "user", "content": stored_user})
        self.history.append({"role": "assistant", "content": assistant_message})


# =============================================================================================================== #
# Panels                                                                                                          #
# =============================================================================================================== #

def _approx_tokens(text: str) -> int:
    """Rough estimate before the API answers (≈ 4 chars/token). The real number is usage.prompt_tokens."""
    return max(1, len(text) // 4)


def _truncate(text: str, width: int = 88) -> str:
    one_line = text.replace("\n", " ")
    if len(one_line) <= width:
        return one_line
    return one_line[:width] + f"… [+{len(one_line) - width} chars]"


def show_flow(mode: str, stateful: bool) -> Panel:
    """The three-layer boundary diagram — shown at start and on mode/stateful switch."""
    aug = "store AUGMENTED history (stateful)" if stateful else "augmentation NOT saved (stateless)"
    body = Text()
    body.append("🖥️  CHAT UI", style="bold bright_blue on grey23")
    body.append("        sends:  history (bare) + your latest message\n", style="bright_white on grey23")
    body.append("                       │  history = what you see; no system, no augmentation\n", style="grey70 on grey23")
    body.append("                       ▼\n", style="grey70 on grey23")
    body.append("🛠️  ASSISTANT ENDPOINT", style="bold bright_yellow on grey23")
    body.append(f"  (STATELESS; mode = {mode})\n", style="bright_white on grey23")
    body.append("        builds:  [system] + [history] + [ this turn's user content ]\n", style="bright_white on grey23")
    body.append("                       │  rebuilt every call — no state to keep it in\n", style="grey70 on grey23")
    body.append("                       ▼\n", style="grey70 on grey23")
    body.append("🧠  LLM", style="bold bright_green on grey23")
    body.append("            returns:  the response only\n", style="bright_white on grey23")
    body.append("                       ▲\n", style="grey70 on grey23")
    body.append("🖥️  CHAT UI", style="bold bright_blue on grey23")
    body.append(f"        appends (your message, response) → history   ✗ {aug}", style="bright_white on grey23")
    return Panel(body, title="🔁 The three layers", border_style="bright_magenta", style="on grey23", padding=(1, 2))


def show_ui_send(outgoing: list) -> Panel:
    """What the Chat UI sends to the endpoint — bare history + the new message."""
    table = Table(box=box.SIMPLE, show_header=True, header_style="bold bright_white on grey23", style="on grey23")
    table.add_column("#", style="bright_cyan on grey23", width=3)
    table.add_column("Role", style="bright_blue on grey23", width=10)
    table.add_column("Content (bare — no system, no augmentation)", style="bright_white on grey23")
    for i, m in enumerate(outgoing):
        table.add_row(str(i), m["role"], _truncate(m["content"]))
    return Panel(table, title="🖥️ → 🛠️  Chat UI sends to the endpoint", border_style="blue", style="on grey23", padding=(0, 1))


def show_endpoint_build(build: dict, mode: str) -> Panel:
    """What the stateless endpoint builds for the LLM — system + history + this turn's user content."""
    messages = build["messages"]
    aug_idx = build["augmented_index"]
    table = Table(box=box.SIMPLE, show_header=True, header_style="bold bright_white on grey23", style="on grey23")
    table.add_column("#", style="bright_cyan on grey23", width=3)
    table.add_column("Role", style="bright_magenta on grey23", width=10)
    table.add_column("Source / lifetime", style="bright_yellow on grey23", width=22)
    table.add_column("Content", style="bright_white on grey23")
    last = len(messages) - 1
    for i, m in enumerate(messages):
        if m["role"] == "system":
            src = "assistant config · static"
        elif i == aug_idx:
            src = "★ built here · discarded"
        elif i == last:
            src = "from UI (bare) · this turn"
        else:
            src = "from UI · passed through"
        table.add_row(str(i), m["role"], src, _truncate(m["content"]))
    note = Text(f"\nretrieval: {build['retrieval']}", style="italic bright_yellow on grey23")
    grid = Table.grid()
    grid.add_row(table)
    grid.add_row(note)
    if aug_idx is not None:
        grid.add_row(Text("★ the augmented message is built fresh now and thrown away — it never returns to the UI",
                          style="italic bright_red on grey23"))
    return Panel(grid, title="🛠️ → 🧠  Endpoint builds the LLM call (stateless)", border_style="yellow", style="on grey23", padding=(0, 1))


def show_api_request(messages: list) -> Panel:
    json_str = json.dumps({"model": MODEL, "messages": messages, "temperature": 0.7}, indent=2, ensure_ascii=False)
    syntax = Syntax(json_str, "json", theme="monokai", background_color="grey23", word_wrap=True)
    return Panel(syntax, title="📤 The actual request to the LLM", border_style="yellow", style="on grey23", padding=(0, 1))


def show_api_response(response_data: dict) -> Panel:
    json_str = json.dumps(response_data, indent=2, ensure_ascii=False)
    syntax = Syntax(json_str, "json", theme="monokai", background_color="grey23", word_wrap=True)
    return Panel(syntax, title="📥 LLM response", border_style="cyan", style="on grey23", padding=(0, 1))


def show_ui_history(history: list, stateful: bool) -> Panel:
    """What the Chat UI keeps after the turn — what the user sees / what gets stored."""
    table = Table(box=box.SIMPLE, show_header=True, header_style="bold bright_white on grey23", style="on grey23")
    table.add_column("#", style="bright_cyan on grey23", width=3)
    table.add_column("Role", style="bright_blue on grey23", width=10)
    table.add_column("Content", style="bright_white on grey23")
    for i, m in enumerate(history):
        table.add_row(str(i), m["role"], _truncate(m["content"]))
    if stateful:
        cap = "STATEFUL: augmented user turns ARE stored — the file now rides in history too"
        style = "italic bright_red on grey23"
    else:
        cap = "no system prompt · no augmentation · just the turns the user saw"
        style = "italic grey70 on grey23"
    grid = Table.grid()
    grid.add_row(table)
    grid.add_row(Text(cap, style=style))
    return Panel(grid, title="🖥️  Chat UI history (what the user sees / what is stored)", border_style="blue", style="on grey23", padding=(0, 1))


def show_cost(history_tokens: list) -> Panel:
    table = Table(box=box.SIMPLE, show_header=True, header_style="bold bright_white on grey23", style="on grey23")
    table.add_column("Turn", style="bright_cyan on grey23", width=5)
    table.add_column("prompt_tokens", style="bright_yellow on grey23", width=14)
    table.add_column("cached", style="bright_green on grey23", width=8)
    table.add_column("", style="bright_red on grey23")
    peak = max((t[0] for t in history_tokens), default=1) or 1
    for i, (pt, cached) in enumerate(history_tokens, start=1):
        bar = "█" * max(1, int(26 * pt / peak))
        table.add_row(str(i), str(pt), ("—" if cached is None else str(cached)), bar)
    return Panel(table, title="💸 Token cost per turn (prompt_tokens · cached)", border_style="red", style="on grey23", padding=(0, 1))


def show_message(role: str, content: str) -> Panel:
    styles = {
        "user": ("bright_white on blue", "blue", "👤 You"),
        "assistant": ("bright_white on dark_green", "green", "🤖 Assistant"),
    }
    text_style, border, title = styles.get(role, ("bright_white on grey23", "white", role))
    return Panel(Text(content, style=text_style), title=title, border_style=border, padding=(0, 1))


def wait_spinner():
    return Live(
        Panel(Spinner("dots", text=Text(" Waiting for the LLM...", style="bold black on yellow")),
              border_style="yellow", style="on yellow", padding=(0, 1)),
        console=console, refresh_per_second=10
    )


# =============================================================================================================== #
# Chat loop                                                                                                       #
# =============================================================================================================== #

def run_chat(retriever: WholeFileRetriever, mode: str):
    ui = ChatUI(stateful_augment=False)
    endpoint = AssistantEndpoint(retriever, mode)
    token_history = []

    console.print()
    console.print(Panel(
        Text("Ask about the knowledge file. Each turn shows the gap between what the\n"
             "CHAT UI keeps (bare turns) and what the stateless ENDPOINT builds for the LLM.\n\n"
             "/mode user-augment | system-grounding   ·   /stateful   ·   /file <path>   ·   /context   ·   (empty = quit)",
             style="bright_white on grey23"),
        title="📚 Context Explorer — single-file RAG", border_style="bright_magenta", style="on grey23", padding=(1, 2)))
    console.print()
    console.print(show_flow(mode, ui.stateful_augment))

    while True:
        console.print()
        user_input = console.input("[bold blue]👤 You: [/bold blue]")
        cmd = user_input.strip()

        if not cmd:
            console.print(Panel(Text("Goodbye!", style="bright_white on grey23"), border_style="dim"))
            break
        if cmd == "/context":
            console.print(Panel(Text(retriever.text, style="grey70 on grey23"),
                                title=f"📄 {os.path.basename(retriever.path)}", border_style="green", style="on grey23"))
            continue
        if cmd == "/stateful":
            ui.stateful_augment = not ui.stateful_augment
            ui.history = []
            console.print(Panel(Text(f"stateful_augment = {ui.stateful_augment} · conversation reset.",
                                     style="bright_white on grey23"), border_style="green", style="on grey23"))
            console.print(show_flow(mode, ui.stateful_augment))
            continue
        if cmd.startswith("/mode "):
            new_mode = cmd[len("/mode "):].strip()
            if new_mode not in (MODE_USER_AUGMENT, MODE_SYSTEM_GROUNDING):
                console.print(Panel(Text(f"unknown mode '{new_mode}'. Use: {MODE_USER_AUGMENT} | {MODE_SYSTEM_GROUNDING}",
                                         style="bold bright_white on dark_red"), border_style="red", style="on dark_red"))
                continue
            mode = new_mode
            endpoint = AssistantEndpoint(retriever, mode)
            ui.history = []
            token_history = []
            console.print(Panel(Text(f"mode = {mode} · conversation reset.", style="bright_white on grey23"),
                                border_style="green", style="on grey23"))
            console.print(show_flow(mode, ui.stateful_augment))
            continue
        if cmd.startswith("/file "):
            new_path = cmd[len("/file "):].strip()
            try:
                retriever = WholeFileRetriever(new_path)
                endpoint = AssistantEndpoint(retriever, mode)
                ui.history = []
                token_history = []
                console.print(Panel(Text(f"Loaded {new_path} ({len(retriever.text)} chars) · conversation reset.",
                                         style="bright_white on grey23"), border_style="green", style="on grey23"))
            except OSError as exc:
                console.print(Panel(Text(f"Could not load {new_path}: {exc}", style="bold bright_white on dark_red"),
                                    border_style="red", style="on dark_red"))
            continue

        # 1) The UI sends its bare history + the new message to the endpoint.
        outgoing = ui.outgoing(user_input)
        console.print()
        console.print(show_message("user", user_input))
        console.print()
        console.print(show_ui_send(outgoing))

        # 2) The stateless endpoint builds the real LLM call and runs it.
        build = endpoint.complete(ui.history, user_input)
        console.print()
        console.print(show_endpoint_build(build, mode))
        console.print()
        console.print(show_api_request(build["messages"]))

        response = build["response"]
        assistant_content = response.choices[0].message.content
        usage = response.usage
        cached = getattr(getattr(usage, "prompt_tokens_details", None), "cached_tokens", None)
        response_data = {
            "id": response.id, "model": response.model,
            "finish_reason": response.choices[0].finish_reason,
            "message": {"role": "assistant", "content": assistant_content},
            "usage": {"prompt_tokens": usage.prompt_tokens, "completion_tokens": usage.completion_tokens,
                      "total_tokens": usage.total_tokens, **({"cached_tokens": cached} if cached is not None else {})},
        }
        console.print()
        console.print(show_api_response(response_data))
        console.print()
        console.print(show_message("assistant", assistant_content))

        # 3) The response flows back to the UI; only the bare turn + reply are stored.
        augmented_user = build["messages"][build["augmented_index"]]["content"] if build["augmented_index"] is not None else None
        ui.record(user_input, assistant_content, augmented_user=augmented_user)
        console.print()
        console.print(show_ui_history(ui.history, ui.stateful_augment))

        token_history.append((usage.prompt_tokens, cached))
        console.print()
        console.print(show_cost(token_history))


def main():
    global client
    console.clear()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        console.print(Panel(Text("OPENAI_API_KEY not found!\n\nCopy .env.example to .env and fill it in.",
                                 style="bold bright_white on dark_red"), title="❌ Error", border_style="red", style="on dark_red"))
        return

    if RAG_MODE not in (MODE_USER_AUGMENT, MODE_SYSTEM_GROUNDING):
        console.print(Panel(Text(f"Unknown RAG_MODE '{RAG_MODE}'. Use {MODE_USER_AUGMENT} or {MODE_SYSTEM_GROUNDING}.",
                                 style="bold bright_white on dark_red"), title="❌ Error", border_style="red", style="on dark_red"))
        return

    knowledge_path = KNOWLEDGE_FILE
    if not os.path.isabs(knowledge_path):
        knowledge_path = os.path.join(os.path.dirname(__file__), knowledge_path)
    try:
        retriever = WholeFileRetriever(knowledge_path)
    except OSError as exc:
        console.print(Panel(Text(f"Could not load knowledge file '{knowledge_path}':\n{exc}",
                                 style="bold bright_white on dark_red"), title="❌ Error", border_style="red", style="on dark_red"))
        return

    client = OpenAI(api_key=api_key, base_url=OPENAI_ENDPOINT) if OPENAI_ENDPOINT else OpenAI(api_key=api_key)

    console.print(Panel(
        Text(f"Model     : {MODEL}\n"
             f"Endpoint  : {OPENAI_ENDPOINT or 'https://api.openai.com/v1'}\n"
             f"Knowledge : {os.path.basename(knowledge_path)} ({len(retriever.text)} chars, ~{_approx_tokens(retriever.text)} tokens)\n"
             f"Mode      : {RAG_MODE}",
             style="bright_white on grey23"),
        title="⚙️ Configuration", border_style="cyan", style="on grey23"))

    run_chat(retriever, RAG_MODE)


if __name__ == "__main__":
    main()
