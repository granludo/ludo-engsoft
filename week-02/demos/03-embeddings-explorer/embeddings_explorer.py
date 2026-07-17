# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# Curs d'agents del BSC — Transformers, LLMs, RAG i Agents: de la teoria a la producció
# Amb llicència Creative Commons BY-NC-SA 4.0 – és obligatori citar l'autor, no es pot fer ús comercial, i les obres derivades han de tenir la mateixa llicència.

# =============================================================================================================== #
# Universitat Politècnica de Catalunya (UPC)                                                                      #
# =============================================================================================================== #

"""
📐 Embeddings Explorer — mira com el significat es converteix en coordenades i mesura'l de dues maneres.

Escriu una frase. La demostració en genera l'embedding (la converteix en una llista de números), en mostra el vector i, tot seguit, mostra com de propera és a cada frase que has introduït abans — mesurat TANT per la similitud de cosinus COM per la distància euclidiana, en una taula ordenada de més propera a menys.

La lliçó: el significat és geometria. «A prop» té més d'una definició, però per als vectors de LONGITUD UNITÀRIA que retornen aquests models totes dues definicions donen EL MATEIX ordre (distància² = 2·(1 − cosinus)). Dues visions d'una mateixa cosa.

Sense persistència — tot viu en memòria només durant la sessió.

Backend: qualsevol endpoint /embeddings compatible amb OpenAI. Per defecte = Ollama en local + nomic-embed-text (sense clau, sense cost). Edita .env per apuntar a OpenAI o a un altre proveïdor.

Comandes dins del xat:
    /seed        carrega unes quantes frases d'exemple perquè les distàncies apareguin de seguida
    /list        llista les frases introduïdes fins ara
    /clear       oblida-ho tot i torna a començar
    (línia buida) surt
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

# Tema d'alt contrast — coincideix amb l'estil visual de l'explorador de context.
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
# Les dues coses que importen: convertir el text en un vector i mesurar la proximitat de dues maneres.          #
# =============================================================================================================== #

def embed(text: str) -> np.ndarray:
    """Text a l'entrada, vector a la sortida. Tota la idea d'un embedding, en una sola crida a l'API."""
    resp = client.embeddings.create(model=MODEL, input=text)
    return np.array(resp.data[0].embedding, dtype=float)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Angle entre els vectors: 1.0 = mateixa direcció, 0.0 = sense relació. Més alt = més a prop."""
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def euclidean_distance(a: np.ndarray, b: np.ndarray) -> float:
    """Distància en línia recta entre els punts. Més baix = més a prop."""
    return float(np.linalg.norm(a - b))


# =============================================================================================================== #
# Panells
# =============================================================================================================== #

def _truncate(text: str, width: int = 60) -> str:
    one = text.replace("\n", " ")
    return one if len(one) <= width else one[: width - 1] + "…"


def show_intro() -> None:
    body = Text()
    body.append("Un ", style=TEXT)
    body.append("embedding", style=ACCENT)
    body.append(" converteix un fragment de text en una llista de números — un punt a l'espai — de manera que\n", style=TEXT)
    body.append("els textos que SIGNIFIQUEN coses semblants queden a prop els uns dels altres.\n\n", style=TEXT)
    body.append("Escriu una frase. En veuràs el vector i, tot seguit, com de propera és a tot el que has\n", style=TEXT)
    body.append("escrit abans, mesurat de dues maneres:\n", style=TEXT)
    body.append("  • similitud de cosinus", style=ACCENT)
    body.append("  — l'angle entre els vectors. ", style=TEXT)
    body.append("més alt = més a prop", style=GOOD)
    body.append(" (1.0 = mateixa direcció).\n", style=TEXT)
    body.append("  • distància euclidiana", style=ACCENT)
    body.append(" — la separació en línia recta entre els punts. ", style=TEXT)
    body.append("més baix = més a prop", style=GOOD)
    body.append(".\n\n", style=TEXT)
    body.append("Aquests models retornen vectors de longitud unitària, per això les dues mètriques donen EL MATEIX ordre\n", style=TEXT_DIM)
    body.append("(distància² = 2·(1 − cosinus)). Dos noms per a una mateixa geometria: observa com coincideixen.\n\n", style=TEXT_DIM)
    body.append("/seed  carrega exemples   ·   /list   ·   /clear   ·   (línia buida = surt)", style=TEXT_DIM)
    console.print(Panel(body, title="📐 Embeddings Explorer", border_style="bright_magenta",
                        style=ON_BG, padding=(1, 2)))
    console.print(Panel(Text(f"model: {MODEL}   ·   endpoint: {OPENAI_ENDPOINT}", style=TEXT_DIM),
                        title="⚙️ Configuració", border_style=BORDER, style=ON_BG, padding=(0, 1)))


def show_embedding(text: str, vec: np.ndarray) -> None:
    n = len(vec)
    norm = float(np.linalg.norm(vec))
    head = ", ".join(f"{v:+.4f}" for v in vec[:12])
    g = Table.grid(padding=(0, 0))
    g.add_row(Text(f'"{text}"', style=TEXT))
    g.add_row(Text(f"{MODEL}  ·  {n} dimensions  ·  norma = {norm:.4f}"
                   + ("  (longitud unitària)" if abs(norm - 1.0) < 0.02 else ""), style=NUM))
    g.add_row(Text(f"[ {head}, … ]   (els primers 12 de {n})", style=TEXT_DIM))
    console.print(Panel(g, title="📐 L'embedding — el significat com a coordenades",
                        border_style="yellow", style=ON_BG, padding=(0, 1)))


def show_table(new_vec: np.ndarray, entries: list) -> None:
    rows = []
    for text, vec in entries:
        rows.append((cosine_similarity(new_vec, vec), euclidean_distance(new_vec, vec), text))
    rows.sort(key=lambda r: r[0], reverse=True)  # més propers primer (cosinus més alt)

    table = Table(box=box.SIMPLE, show_header=True, header_style=f"bold {TEXT}", style=ON_BG)
    table.add_column("#", style=f"bright_cyan {ON_BG}", width=3)
    table.add_column("cosinus ↑", style=GOOD, width=9)
    table.add_column("distància ↓", style=COST, width=11)
    table.add_column("text anterior", style=TEXT)
    for i, (cos, dist, text) in enumerate(rows, 1):
        table.add_row(str(i), f"{cos:.3f}", f"{dist:.3f}", _truncate(text))
    note = Text("més propers primer · cosinus alt = a prop, distància baixa = a prop — "
                "el mateix ordre, perquè els vectors tenen longitud unitària", style=TEXT_DIM)
    grid = Table.grid()
    grid.add_row(table)
    grid.add_row(note)
    console.print(Panel(grid, title="📊 Proximitat als textos que has introduït abans",
                        border_style=BORDER, style=ON_BG, padding=(0, 1)))


# =============================================================================================================== #
# Bucle
# =============================================================================================================== #

def add_text(text: str, entries: list) -> None:
    """Genera l'embedding, mostra el vector, compara'l amb les entrades anteriors i, després, recorda'l."""
    with console.status("[bold yellow]embedding…", spinner="dots"):
        vec = embed(text)
    console.print()
    show_embedding(text, vec)
    if entries:
        console.print()
        show_table(vec, entries)
    else:
        console.print(Panel(Text("encara no hi ha res amb què comparar — afegeix una altra frase.", style=TEXT_DIM),
                            border_style="dim", style=ON_BG))
    entries.append((text, vec))


def run() -> None:
    entries: list = []  # (text, vector) — només en memòria, sense persistència
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
            console.print(Panel(Text("s'ha oblidat tot · torna a començar.", style=TEXT), border_style="green", style=ON_BG))
            continue
        if cmd == "/list":
            if not entries:
                console.print(Panel(Text("encara no has introduït res.", style=TEXT_DIM), border_style="dim", style=ON_BG))
            else:
                t = Table(box=box.SIMPLE, show_header=False, style=ON_BG)
                t.add_column("#", style=f"bright_cyan {ON_BG}", width=3)
                t.add_column("text", style=TEXT)
                for i, (text, _) in enumerate(entries, 1):
                    t.add_row(str(i), _truncate(text, 80))
                console.print(Panel(t, title="📋 Textos fins ara", border_style=BORDER, style=ON_BG, padding=(0, 1)))
            continue
        if cmd == "/seed":
            console.print(Panel(Text("carregant frases d'exemple…", style=TEXT_DIM), border_style="green", style=ON_BG))
            for s in SEED:
                add_text(s, entries)
            continue

        add_text(cmd, entries)


def main() -> None:
    console.clear()
    if not OPENAI_API_KEY:
        console.print(Panel(Text("OPENAI_API_KEY no està definida. Copia .env.example a .env.\n"
                                 "(Per a Ollama en local, qualsevol cadena no buida funciona.)",
                                 style="bold bright_white on dark_red"), title="❌ Error", border_style="red"))
        return
    try:
        run()
    except Exception as exc:  # noqa: BLE001 — mostra els errors del backend de manera clara a qui està aprenent
        console.print(Panel(Text(f"{type(exc).__name__}: {exc}\n\n"
                                 f"L'endpoint està actiu i el model descarregat?\n"
                                 f"  endpoint = {OPENAI_ENDPOINT}\n  model = {MODEL}\n"
                                 f"  (Ollama: `ollama pull {MODEL}`)",
                                 style="bold bright_white on dark_red"), title="❌ Error del backend", border_style="red"))


if __name__ == "__main__":
    main()
