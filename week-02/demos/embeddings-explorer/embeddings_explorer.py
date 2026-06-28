# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# BSC Agents Course — Transformers, LLMs, RAG and Agents: From Theory to Production
# Licensed under Creative Commons BY-NC-SA 4.0 — reuse must credit the author, no commercial use, derivatives under the same license.

# =============================================================================================================== #
# Universitat Politècnica de Catalunya (UPC)                                                                      #
# =============================================================================================================== #

"""
📐 Embeddings Explorer — watch meaning become coordinates, and measure it two ways.

Type a sentence. The demo embeds it (turns it into a list of numbers), shows the vector,
and then shows how close it is to every sentence you entered before — measured by BOTH
cosine similarity AND Euclidean distance, in a table sorted nearest-first.

The lesson: meaning is geometry. "Close" has more than one definition — but for the
UNIT-LENGTH vectors these models return, the two definitions give the SAME ranking
(distance² = 2·(1 − cosine)). Two views of the same thing.

No persistence — everything lives in memory for the session only.

Backend: any OpenAI-compatible /embeddings endpoint. Default = local Ollama + nomic-embed-text
(no key, no cost). Edit .env to point at OpenAI or another provider.

In-chat commands:
    /seed        load a few example sentences so the distances land immediately
    /list        list the sentences entered so far
    /clear       forget everything and start over
    (empty line) quit
"""
import os
from dotenv import load_dotenv
import numpy as np
from openai import OpenAI

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

load_dotenv()

# High-contrast theme — matches the context-explorer house style.
BG = "grey23"
ON_BG = f"on {BG}"
TEXT = f"bright_white {ON_BG}"
TEXT_DIM = f"grey84 {ON_BG}"
ACCENT = f"bold cyan1 {ON_BG}"
NUM = f"bright_yellow {ON_BG}"
GOOD = f"bright_green {ON_BG}"
COST = f"orange1 {ON_BG}"
BORDER = "bright_cyan"
INPUT_PROMPT = "[bold bright_cyan]📝 text: [/bold bright_cyan]"

MODEL = os.getenv("MODEL", "nomic-embed-text")
OPENAI_ENDPOINT = os.getenv("OPENAI_ENDPOINT", "http://localhost:11434/v1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "ollama")

console = Console()
client = OpenAI(base_url=OPENAI_ENDPOINT, api_key=OPENAI_API_KEY)

SEED = [
    "The warehouse robot's top speed is 2.4 metres per second.",
    "How fast does the robot go?",
    "Acme Robotics was founded in 2019 in Girona.",
    "The recipe needs two eggs and a cup of flour.",
]


# =============================================================================================================== #
# The two things that matter: turning text into a vector, and measuring closeness two ways.                       #
# =============================================================================================================== #

def embed(text: str) -> np.ndarray:
    """Text in, vector out. The whole idea of an embedding, in one API call."""
    resp = client.embeddings.create(model=MODEL, input=text)
    return np.array(resp.data[0].embedding, dtype=float)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Angle between the vectors: 1.0 = same direction, 0.0 = unrelated. Higher = closer."""
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def euclidean_distance(a: np.ndarray, b: np.ndarray) -> float:
    """Straight-line distance between the points. Lower = closer."""
    return float(np.linalg.norm(a - b))


# =============================================================================================================== #
# Panels                                                                                                          #
# =============================================================================================================== #

def _truncate(text: str, width: int = 60) -> str:
    one = text.replace("\n", " ")
    return one if len(one) <= width else one[: width - 1] + "…"


def show_intro() -> None:
    body = Text()
    body.append("An ", style=TEXT)
    body.append("embedding", style=ACCENT)
    body.append(" turns a piece of text into a list of numbers — a point in space — so that\n", style=TEXT)
    body.append("texts that MEAN similar things land near each other.\n\n", style=TEXT)
    body.append("Type a sentence. You'll see its vector, then how close it is to everything you\n", style=TEXT)
    body.append("typed before, measured two ways:\n", style=TEXT)
    body.append("  • cosine similarity", style=ACCENT)
    body.append("  — the angle between the vectors. ", style=TEXT)
    body.append("higher = closer", style=GOOD)
    body.append(" (1.0 = same direction).\n", style=TEXT)
    body.append("  • Euclidean distance", style=ACCENT)
    body.append(" — the straight-line gap between the points. ", style=TEXT)
    body.append("lower = closer", style=GOOD)
    body.append(".\n\n", style=TEXT)
    body.append("These models return unit-length vectors, so the two metrics give the SAME ranking\n", style=TEXT_DIM)
    body.append("(distance² = 2·(1 − cosine)). Two names for one geometry — watch them agree.\n\n", style=TEXT_DIM)
    body.append("/seed  load examples   ·   /list   ·   /clear   ·   (empty line = quit)", style=TEXT_DIM)
    console.print(Panel(body, title="📐 Embeddings Explorer", border_style="bright_magenta",
                        style=ON_BG, padding=(1, 2)))
    console.print(Panel(Text(f"model: {MODEL}   ·   endpoint: {OPENAI_ENDPOINT}", style=TEXT_DIM),
                        title="⚙️ Configuration", border_style=BORDER, style=ON_BG, padding=(0, 1)))


def show_embedding(text: str, vec: np.ndarray) -> None:
    n = len(vec)
    norm = float(np.linalg.norm(vec))
    head = ", ".join(f"{v:+.4f}" for v in vec[:12])
    g = Table.grid(padding=(0, 0))
    g.add_row(Text(f'"{text}"', style=TEXT))
    g.add_row(Text(f"{MODEL}  ·  {n} dimensions  ·  norm = {norm:.4f}"
                   + ("  (unit length)" if abs(norm - 1.0) < 0.02 else ""), style=NUM))
    g.add_row(Text(f"[ {head}, … ]   (first 12 of {n})", style=TEXT_DIM))
    console.print(Panel(g, title="📐 The embedding — meaning as coordinates",
                        border_style="yellow", style=ON_BG, padding=(0, 1)))


def show_table(new_vec: np.ndarray, entries: list) -> None:
    rows = []
    for text, vec in entries:
        rows.append((cosine_similarity(new_vec, vec), euclidean_distance(new_vec, vec), text))
    rows.sort(key=lambda r: r[0], reverse=True)  # nearest first (highest cosine)

    table = Table(box=box.SIMPLE, show_header=True, header_style=f"bold {TEXT}", style=ON_BG)
    table.add_column("#", style=f"bright_cyan {ON_BG}", width=3)
    table.add_column("cosine ↑", style=GOOD, width=9)
    table.add_column("distance ↓", style=COST, width=11)
    table.add_column("earlier text", style=TEXT)
    for i, (cos, dist, text) in enumerate(rows, 1):
        table.add_row(str(i), f"{cos:.3f}", f"{dist:.3f}", _truncate(text))
    note = Text("nearest first · cosine high = close, distance low = close — "
                "same order, because the vectors are unit length", style=TEXT_DIM)
    grid = Table.grid()
    grid.add_row(table)
    grid.add_row(note)
    console.print(Panel(grid, title="📊 Closeness to the texts you entered before",
                        border_style=BORDER, style=ON_BG, padding=(0, 1)))


# =============================================================================================================== #
# Loop                                                                                                            #
# =============================================================================================================== #

def add_text(text: str, entries: list) -> None:
    """Embed, show the vector, compare against earlier entries, then remember it."""
    with console.status("[bold yellow]embedding…", spinner="dots"):
        vec = embed(text)
    console.print()
    show_embedding(text, vec)
    if entries:
        console.print()
        show_table(vec, entries)
    else:
        console.print(Panel(Text("nothing to compare against yet — add another sentence.", style=TEXT_DIM),
                            border_style="dim", style=ON_BG))
    entries.append((text, vec))


def run() -> None:
    entries: list = []  # (text, vector) — in memory only, no persistence
    console.print()
    show_intro()

    while True:
        console.print()
        raw = console.input(INPUT_PROMPT)
        cmd = raw.strip()

        if not cmd:
            console.print(Panel(Text("Goodbye!", style=TEXT), border_style="dim"))
            break
        if cmd == "/clear":
            entries.clear()
            console.print(Panel(Text("forgotten everything · start over.", style=TEXT), border_style="green", style=ON_BG))
            continue
        if cmd == "/list":
            if not entries:
                console.print(Panel(Text("nothing entered yet.", style=TEXT_DIM), border_style="dim", style=ON_BG))
            else:
                t = Table(box=box.SIMPLE, show_header=False, style=ON_BG)
                t.add_column("#", style=f"bright_cyan {ON_BG}", width=3)
                t.add_column("text", style=TEXT)
                for i, (text, _) in enumerate(entries, 1):
                    t.add_row(str(i), _truncate(text, 80))
                console.print(Panel(t, title="📋 Texts so far", border_style=BORDER, style=ON_BG, padding=(0, 1)))
            continue
        if cmd == "/seed":
            console.print(Panel(Text("loading example sentences…", style=TEXT_DIM), border_style="green", style=ON_BG))
            for s in SEED:
                add_text(s, entries)
            continue

        add_text(cmd, entries)


def main() -> None:
    console.clear()
    if not OPENAI_API_KEY:
        console.print(Panel(Text("OPENAI_API_KEY not set. Copy .env.example to .env.\n"
                                 "(For local Ollama any non-empty string works.)",
                                 style="bold bright_white on dark_red"), title="❌ Error", border_style="red"))
        return
    try:
        run()
    except Exception as exc:  # noqa: BLE001 — surface backend errors plainly to a learner
        console.print(Panel(Text(f"{type(exc).__name__}: {exc}\n\n"
                                 f"Is the endpoint up and the model pulled?\n"
                                 f"  endpoint = {OPENAI_ENDPOINT}\n  model = {MODEL}\n"
                                 f"  (Ollama: `ollama pull {MODEL}`)",
                                 style="bold bright_white on dark_red"), title="❌ Backend error", border_style="red"))


if __name__ == "__main__":
    main()
