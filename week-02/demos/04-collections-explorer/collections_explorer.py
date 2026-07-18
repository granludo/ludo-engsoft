# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# Curs d'agents del BSC — Transformers, LLMs, RAG i Agents: de la teoria a la producció
# Amb llicència Creative Commons BY-NC-SA 4.0 – és obligatori citar l'autor, no es pot fer ús comercial, i les obres derivades han de tenir la mateixa llicència.

"""
🗂️ Collections Explorer — una base de dades d'embeddings amb què pots experimentar.

Una COL·LECCIÓ és una taula indexada amb embeddings. Aquesta demostració n'obre una — persistent al disc per defecte, de manera que els teus chunks segueixen sent-hi quan hi tornes — i et permet omplir-la i cercar-hi per significat.

Tot passa per la utilitat collections_manager del curs (tres funcions: create_collection / insert / query, sobre ChromaDB). I aquest és justament el propòsit de la demostració: la teva aplicació parla amb la capa d'abstracció, no amb el motor que hi ha a sota.

Comandes:
    /add <text>        afegeix un chunk (se't demanarà la font)
    /seed              carrega chunks d'exemple perquè les consultes encertin de seguida
    /list              què hi ha a la col·lecció (source · chunk_number · text)
    <qualsevol altre text>   consulta la col·lecció per significat, els top-K més propers primer
    (línia buida)      surt

Executa-la amb --memory per tenir una col·lecció efímera en memòria en comptes de la del disc.
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

# Tema d'alt contrast — coincideix amb l'estil visual de l'explorador de context / d'embeddings.
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
    body.append("Una ", style=TEXT)
    body.append("col·lecció", style=ACCENT)
    body.append(" és una taula indexada amb embeddings. Aquesta està ", style=TEXT)
    body.append(store, style=NUM)
    body.append(f" i ara mateix conté {col.count()} chunks.\n\n", style=TEXT)
    body.append("Escriu text per ", style=TEXT)
    body.append("consultar per significat", style=ACCENT)
    body.append(f" (top-{TOP_K}, els més propers primer). Afegeix coneixement amb ", style=TEXT)
    body.append("/add <text>", style=NUM)
    body.append(" — cada chunk porta, com a mínim, el seu ", style=TEXT)
    body.append("source", style=ACCENT)
    body.append(" i el seu ", style=TEXT)
    body.append("chunk_number", style=ACCENT)
    body.append(" dins d'aquesta font.\n\n", style=TEXT)
    body.append("/add <text>   /seed   /list   (línia buida = surt)", style=TEXT_DIM)
    console.print(Panel(body, title="🗂️ Collections Explorer", border_style="bright_magenta",
                        style=ON_BG, padding=(1, 2)))


def show_insert(result: dict) -> None:
    if result["ok"]:
        console.print(Text(f"  ✔ desat com a {result['id']}", style=GOOD))
    else:
        console.print(Text(f"  ✘ no s'ha desat — {result['error']}", style=BAD))


def show_hits(question: str, hits: list[dict]) -> None:
    if not hits:
        console.print(Text("  (la col·lecció és buida — fes /add o /seed primer)", style=BAD))
        return
    table = Table(box=box.SIMPLE_HEAVY, style=ON_BG, header_style=ACCENT,
                  title=f"més propers a: «{question}»", title_style=TEXT_DIM)
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
    ap = argparse.ArgumentParser(description="Experimenta amb una col·lecció d'embeddings.")
    ap.add_argument("--memory", action="store_true", help="col·lecció en memòria (desapareix en sortir)")
    ap.add_argument("--name", default="playground", help="nom de la col·lecció (per defecte: playground)")
    args = ap.parse_args()

    persist = None if args.memory else os.environ.get("PERSIST_PATH", "./collections-store")
    col = create_collection(args.name, description="collections-explorer playground",
                            metric="cosine", persist_path=persist)
    store = "en memòria (desapareix quan surts)" if args.memory else f"persistida al disc a {persist}"
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
                console.print(Text("  ús: /add <text del chunk>", style=BAD))
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

    console.print(Text("adéu — la col·lecció del disc ho conserva tot per a la propera vegada.", style=TEXT_DIM))


if __name__ == "__main__":
    main()
