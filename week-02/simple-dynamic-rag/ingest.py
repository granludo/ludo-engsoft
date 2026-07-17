# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# Curs d'agents de BSC — Transformers, LLMs, RAG i Agents: De la teoria a la producció
# Amb llicència Creative Commons BY-NC-SA 4.0 – és obligatori citar l'autor, no es pot fer ús comercial, i les obres derivades han de tenir la mateixa llicència.

"""Ingesta — com un document entra en una col·lecció.

La ingesta és el procés pel qual un document s'afegeix a una col·lecció, en quatre passos:

  1. CONVERTEIX el document a markdown (aquí: markitdown — pdf, docx, pptx, html,
     txt... tot acaba en md). Per a documents escanejats faries servir un model
     d'OCR: mistral-ocr al núvol, o deepseek-ocr executant-se en local (mlx a
     Apple Silicon, CUDA a NVIDIA).
  2. DESA tant l'original com la seva destil·lació en markdown en un lloc enllaçable —
     aquí `static/` (la mateixa idea que /static en una aplicació FastAPI), de manera
     que cada chunk pugui apuntar al seu document per URL.
  3. FES CHUNK del markdown — veure chunking.py: una finestra lliscant de caràcters amb
     overlap, o les seccions ## pròpies del document.
  4. INSEREIX cada chunk a la col·lecció amb les seves metadades: la url del document,
     el títol, la url de la destil·lació md, el número de chunk, l'estratègia de
     chunking i la data d'ingesta.

Ús:
    uv run ingest.py path/to/document.pdf
    uv run ingest.py handbook.md --strategy sections --level 2
    uv run ingest.py notes.txt   --strategy chars --size 800 --overlap 100
"""
import argparse
import datetime
import shutil
from pathlib import Path

from dotenv import load_dotenv
from markitdown import MarkItDown

from chunking import chunk_by_chars, chunk_by_sections
from collections_manager import create_collection, insert

load_dotenv()

HERE = Path(__file__).resolve().parent
STATIC = HERE / "static"


def ingest(path: str, collection_name: str = "handbook", persist_path: str = "./collections-store",
           strategy: str = "chars", size: int = 800, overlap: int = 100, level: int = 2) -> None:
    doc = Path(path)
    if not doc.exists():
        raise SystemExit(f"no such file: {doc}")
    STATIC.mkdir(exist_ok=True)

    # 1 — converteix a markdown
    result = MarkItDown().convert(str(doc))
    markdown = result.text_content
    title = (result.title or doc.stem).strip()
    print(f"1. converted {doc.name} -> markdown ({len(markdown)} chars) · title: {title!r}")

    # 2 — desa l'original i la destil·lació allà on es puguin enllaçar
    doc_url = f"static/{doc.name}"
    md_name = f"{doc.stem}.md" if doc.suffix.lower() != ".md" else f"{doc.stem}.distilled.md"
    md_url = f"static/{md_name}"
    shutil.copy(doc, STATIC / doc.name)
    (STATIC / md_name).write_text(markdown, encoding="utf-8")
    print(f"2. stored     {doc_url}  +  {md_url}")

    # 3 — chunk
    if strategy == "sections":
        chunks = chunk_by_sections(markdown, level=level)
        strategy_label = f"sections(level={level})"
    else:
        chunks = chunk_by_chars(markdown, size=size, overlap=overlap)
        strategy_label = f"chars(size={size},overlap={overlap})"
    print(f"3. chunked    {len(chunks)} chunks · strategy {strategy_label}")

    # 4 — insereix amb les metadades
    col = create_collection(collection_name, description="simple-dynamic-rag knowledge",
                            metric="cosine", persist_path=persist_path)
    ok = 0
    for n, chunk in enumerate(chunks):
        r = insert(col, chunk, {
            "source": doc.stem,
            "doc_url": doc_url,
            "md_url": md_url,
            "title": title,
            "chunk_number": n,
            "chunking_strategy": strategy_label,
            "ingested_at": datetime.date.today().isoformat(),
        })
        ok += r["ok"]
        if not r["ok"]:
            print(f"   ✘ chunk {n}: {r['error']}")
    print(f"4. inserted   {ok}/{len(chunks)} chunks into collection {collection_name!r} "
          f"({col.count()} total, persisted at {persist_path})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Ingest a document into a collection.")
    ap.add_argument("files", nargs="+", help="document(s): pdf, docx, md, txt, html...")
    ap.add_argument("--collection", default="handbook")
    ap.add_argument("--persist", default="./collections-store")
    ap.add_argument("--strategy", choices=["chars", "sections"], default="chars")
    ap.add_argument("--size", type=int, default=800, help="chars per chunk (chars strategy)")
    ap.add_argument("--overlap", type=int, default=100, help="shared margin between chunks (chars strategy)")
    ap.add_argument("--level", type=int, default=2, help="heading level to cut at (sections strategy)")
    args = ap.parse_args()
    for f in args.files:
        ingest(f, collection_name=args.collection, persist_path=args.persist,
               strategy=args.strategy, size=args.size, overlap=args.overlap, level=args.level)
