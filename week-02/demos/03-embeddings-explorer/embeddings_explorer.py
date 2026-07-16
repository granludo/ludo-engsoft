# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# Curs per a agents de BSC — Transformers, LLMs, RAG i Agents: Des del teòric fins a la pràctica
# Amb llicència Creative Commons BY-NC-SA 4.0 – és obligatori citar l'autor, no es pot fer ús comercial, i les obres derivades han de tenir la mateixa llicència.

# =============================================================================================================== #
# Universitat Politècnica de Catalunya (UPC)                                                                      #
# =============================================================================================================== #

"""
📐 Embeddings Explorador — visualitza el significat en coordenades i mesura-ho de dues maneres.

Escriu una frase. La demostració la inclou (la transforma en una llista de números), mostra el vector, i després mostra quina distància té respecte a cada frase que has introduit abans – mesurada tant per la similaritat de cosí com per la distància euclidiana, en una taula ordenada per proximitat.

La lliçó: el significat és la geometria. La paraula "proper" té més d'una definició, però per als vectors d'UNITAT-LONGITUD que retornen aquests models, les dues definicions donen EL MATEIX classificació (distància² = 2·(1 − cosinus)). Dos punts de vista del mateix concepte.

Sense persistència – tot es guarda en la memòria només per a la sessió actual.

Backend: compatible amb OpenAI /embeddings endpoint. Valor per defecte: local Ollama + nomic-embed-text (sense clau, sense cost). Modifiqueu el fitxer .env per apuntar a OpenAI o a un altre proveïdor.

Comandes en el chat: /seed - carregar algunes frases d'exemple perquè les distàncies es mostrin immediatament /list - llistar totes les frases que s'han introduit fins ara /clear - oblidar tot i començar de nou (línia buida) sortir
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

# Tema de contrast elevat – es correspon amb l'estil de disseny de la "casa d'exploració del context".
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
# Les dues coses que són importants: transformar el text en un vector i mesurar la proximitat de dues maneres. #
# =============================================================================================================== #

def embed(text: str) -> np.ndarray:
    """Entrada de text, sortida vectorial. La idea completa d'un embedding, en una única API."""
    resp = client.embeddings.create(model=MODEL, input=text)
    return np.array(resp.data[0].embedding, dtype=float)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Angle entre els vectors: 1.0 = mateixa direcció, 0.0 = sense relació. Un angle més gran indica una major proximitat."""
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def euclidean_distance(a: np.ndarray, b: np.ndarray) -> float:
    """Distància en línia recta entre els punts. Menor valor = més proper."""
    return float(np.linalg.norm(a - b))


# =============================================================================================================== #
# Panells
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
                        border_style="groc", style=ON_BG, padding=(0, 1)))


def show_table(new_vec: np.ndarray, entries: list) -> None:
    rows = []
    for text, vec in entries:
        rows.append((cosine_similarity(new_vec, vec), euclidean_distance(new_vec, vec), text))
    rows.sort(key=lambda r: r[0], reverse=True)  # el més proper (amb el màxim cosinus)

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
# Cicle
# =============================================================================================================== #

def add_text(text: str, entries: list) -> None:
    """Incorporeu-lo, mostreu el vector, compareu-lo amb les entrades anteriors, i després recordeu-lo."""
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
    entries: list = []  # (text, vector) – només en memòria, sense persistència
    console.print()
    show_intro()

    while True:
        console.print()
        raw = console.input(INPUT_PROMPT)
        cmd = raw.strip()

        if not cmd:
            console.print(Panel(Text("Adéu!", style=TEXT), border_style="dim"))
            break
        if cmd == "/clear":
            entries.clear()
            console.print(Panel(Text("forgotten everything · start over.", style=TEXT), border_style="green", style=ON_BG))
            continue
        if cmd == "/list":
            if not entries:
                console.print(Panel(Text("Cap cosa ha entrat fins ara.", style=TEXT_DIM), border_style="dim", style=ON_BG))
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
                                 style="negre i brillant, blanc sobre vermell fosc"), title="❌ Error", border_style="red"))
        return
    try:
        run()
    except Exception as exc:  # noqa: BLE001 — surface backend errors plainly to a learner
        console.print(Panel(Text(f"{type(exc).__name__}: {exc}\n\n"
                                 f"Is the endpoint up and the model pulled?\n"
                                 f"  endpoint = {OPENAI_ENDPOINT}\n  model = {MODEL}\n"
                                 f"  (Ollama: `ollama pull {MODEL}`)",
                                 style="negre i brillant, blanc sobre vermell fosc"), title="❌ Backend error", border_style="red"))


if __name__ == "__main__":
    main()
