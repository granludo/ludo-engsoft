# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# Curs per a agents de BSC — Transformers, LLMs, RAG i Agents: Des del teòric fins a la pràctica
# Amb llicència Creative Commons BY-NC-SA 4.0 – és obligatori citar l'autor, no es pot fer ús comercial, i les obres derivades han de tenir la mateixa llicència.

"""
🗂️ Explorador de col·leccions – una base de dades embeddings amb la qual podeu interactuar.

Una "COL·LECCIÓ" és una taula indexada amb embeddings. Aquesta demostració obre una – que es guarda permanentment al disc per defecte, de manera que les vostres chunks continuen sent accessibles quan torni – i us permet omplir-la i buscar-hi elements per significat.

Tot passa a través de l'eina "collections\\_manager" del curs (que consta de tres funcions: `create_collection`, `insert` i `query`, segons ChromaDB). Aquesta demostració també és el punt clau: la vostra aplicació interactua amb la capa d'abstracció, no amb el motor que hi ha sota.

Comandes: /add <text> afegir un chunk (se us demanarà la font) /seed carregar un exemple chunks perquè les consultes es facin automàticament /list mostrar el contingut de la col·lecció (font · número de fragment · text) <qualsevol altre text> consultar la col·lecció per significat, mostrant els més propers (línia buida) sortir

Utilitzeu l'opció `--memory` per crear una col·lecció en memòria temporal, en comptes de la que es guarda al disc.
"""
import argparse
import os
from dotenv import load_dotenv

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

from collections_manager import create_collection, insert, query

load_dotenv()

# Tema de contrast elevat – es correspon amb l'estil de disseny de les cases "context-explorer" / embeddings.
BG = "grey23"
ON_BG = f"on {BG}"
TEXT = f"bright_white {ON_BG}"
TEXT_DIM = f"grey84 {ON_BG}"
ACCENT = f"bold cyan1 {ON_BG}"
NUM = f"bright_yellow {ON_BG}"
GOOD = f"bright_green {ON_BG}"
BAD = f"orange1 {ON_BG}"
BORDER = "bright_cyan"

console = Console()

TOP_K = int(os.environ.get("TOP_K", "4"))

SEED = [
    ("acme-handbook", "The warehouse robot's top speed is 2.4 metres per second."),
    ("acme-handbook", "The Pallet Pup carries up to 600 kg and its battery lasts nine hours."),
    ("acme-handbook", "Acme Robotics was founded in 2019 in Girona, Catalonia."),
    ("acme-handbook", "Every Pallet Pup ships with an emergency stop any nearby worker can press."),
    ("recipes", "The recipe needs two eggs and a cup of flour."),
]


def show_intro(col, store: str) -> None:
    body = Text()
    body.append("A ", style=TEXT)
    body.append("collection", style=ACCENT)
    body.append(" is a table indexed with embeddings. This one is ", style=TEXT)
    body.append(store, style=NUM)
    body.append(f" and holds {col.count()} chunks right now.\n\n", style=TEXT)
    body.append("Type text to ", style=TEXT)
    body.append("query by meaning", style=ACCENT)
    body.append(f" (top-{TOP_K}, nearest first). Add knowledge with ", style=TEXT)
    body.append("/add <text>", style=NUM)
    body.append(" — every chunk carries at least its ", style=TEXT)
    body.append("source", style=ACCENT)
    body.append(" and its ", style=TEXT)
    body.append("chunk_number", style=ACCENT)
    body.append(" within that source.\n\n", style=TEXT)
    body.append("/add <text>   /seed   /list   (empty line = quit)", style=TEXT_DIM)
    console.print(Panel(body, title="🗂️ Collections Explorer", border_style="bright_magenta",
                        style=ON_BG, padding=(1, 2)))


def show_insert(result: dict) -> None:
    if result["ok"]:
        console.print(Text(f"  ✔ stored as {result['id']}", style=GOOD))
    else:
        console.print(Text(f"  ✘ not stored — {result['error']}", style=BAD))


def show_hits(question: str, hits: list[dict]) -> None:
    if not hits:
        console.print(Text("  (collection is empty — /add or /seed first)", style=BAD))
        return
    table = Table(box=box.SIMPLE_HEAVY, style=ON_BG, header_style=ACCENT,
                  title=f"nearest to: “{question}”", title_style=TEXT_DIM)
    score_name = "similarity" if "similarity" in hits[0] else "distance"
    table.add_column(score_name, justify="right", style=NUM)
    table.add_column("source", style=TEXT_DIM)
    table.add_column("#", justify="right", style=TEXT_DIM)
    table.add_column("chunk", style=TEXT)
    for h in hits:
        m = h["metadata"]
        table.add_row(f"{h[score_name]:.3f}", str(m.get("source", "?")),
                      str(m.get("chunk_number", "?")), h["chunk"])
    console.print(table)


def main() -> None:
    ap = argparse.ArgumentParser(description="Poke an embeddings collection.")
    ap.add_argument("--memory", action="store_true", help="in-memory collection (gone on quit)")
    ap.add_argument("--name", default="playground", help="collection name (default: playground)")
    args = ap.parse_args()

    persist = None if args.memory else os.environ.get("PERSIST_PATH", "./collections-store")
    col = create_collection(args.name, description="collections-explorer playground",
                            metric="cosine", persist_path=persist)
    store = "in memory (gone when you quit)" if args.memory else f"persisted on disk at {persist}"
    show_intro(col, store)

    while True:
        try:
            line = console.input("[bold bright_cyan]📝 > [/bold bright_cyan]").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not line:
            break
        if line.startswith("/add"):
            chunk = line[4:].strip()
            if not chunk:
                console.print(Text("Ús: /add <text del chunk>", style=BAD))
                continue
            source = console.input("[bold bright_cyan]   source? [/bold bright_cyan]").strip() or "manual"
            show_insert(insert(col, chunk, {"source": source}))
        elif line == "/seed":
            for source, chunk in SEED:
                show_insert(insert(col, chunk, {"source": source}))
        elif line == "/list":
            got = col._chroma.get()
            rows = sorted(zip(got["metadatas"], got["documents"]),
                          key=lambda r: (str(r[0].get("source")), r[0].get("chunk_number", 0)))
            for meta, doc in rows:
                console.print(Text(f"  {meta.get('source')} · {meta.get('chunk_number')} · {doc}", style=TEXT_DIM))
            console.print(Text(f"  ({col.count()} chunks)", style=NUM))
        else:
            show_hits(line, query(col, line, top_k=TOP_K))

    console.print(Text("bye — the on-disk collection keeps everything for next time.", style=TEXT_DIM))


if __name__ == "__main__":
    main()
