# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# Curs per a agents de BSC — Transformers, LLMs, RAG i Agents: Des del teòric fins a la pràctica
# Amb llicència Creative Commons BY-NC-SA 4.0 – és obligatori citar l'autor, no es pot fer ús comercial, i les obres derivades han de tenir la mateixa llicència.

# =============================================================================================================== #
# Universitat Politècnica de Catalunya (UPC)                                                                      #
# =============================================================================================================== #

"""
📚 Explorador d'embeddings-RAG: tot el cicle dinàmic de RAG, per seccions.

Al començament, la demostració "INGEST" processa el fitxer de coneixement "knowledge.txt": chunks. Aquest procés implica utilitzar una finestra que es desplassa (amb solapaments — chunking és un bucle) i inserir cada chunk en una col·lecció a través del gestor de col·lecions del curs. Les mateixes tres funcions formen la base d'aquesta demostració, l'explorador de col·lecions, l'eina "simple-dynamic-rag" proporcionada i el vostre projecte final; totes utilitzen la mateixa interfície.

Després, a cada gir, observeu com es desenvolupa RAG:

    🖥️ INTERFÀCIA DE XAT: envia: historial (sense context) + el vostre últim missatge | v 🛠️ ASSISTENT ENDPOINT (sense context)
            1. el vostre missatge es converteix en la consulta.
            2. La col·lecció retorna l'element més proper al chunks (el millor de la K primers, superant un límit).
            3. crea: [sistema] + [història] + [plantilla (el teu missatge, AQUESTES chunks)]
                                  | v 🧠  LLM            resultat: només la resposta ^ 🖥️  IU de chat       afegeix (el teu missatge, la resposta) a l'històric ✗ chunks No s'ha guardat

Comandes en el chat: /topk N – canvia el nombre de [chunks] que es recuperen /threshold X – canvia la barrera de similaritat (chunks per sota d'aquesta es descarta) (línia buida) sortir

La col·lecció existeix en la memòria i es reconstruïx a partir de "knowledge.txt" cada vegada que s'executa — cada prova inicial comença de forma idèntica. Configureu la variable PERSIST_PATH al fitxer .env per conservar-la.
"""
import json
import os
from dotenv import load_dotenv
from openai import OpenAI

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
from rich import box

from collections_manager import create_collection, insert, query

load_dotenv()

# Tema "High-contrast Rich": s'adapta al estil de la pàgina d'exploració del context.
BG = "grey23"
ON_BG = f"on {BG}"
TEXT = f"bright_white {ON_BG}"
TEXT_DIM = f"grey84 {ON_BG}"
ACCENT = f"bold cyan1 {ON_BG}"
NUM = f"bright_yellow {ON_BG}"
GOOD = f"bright_green {ON_BG}"
BAD = f"orange1 {ON_BG}"

console = Console()

client = OpenAI(
    base_url=os.environ.get("OPENAI_ENDPOINT", "http://localhost:11434/v1"),
    api_key=os.environ.get("OPENAI_API_KEY", "ollama"),
)
MODEL = os.environ.get("MODEL", "qwen3:1.7b")

CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", "320"))
CHUNK_OVERLAP = int(os.environ.get("CHUNK_OVERLAP", "40"))

SYSTEM = "Answer using only the context. If it is not there, say you don't know."
TEMPLATE = "Context:\n----\n{context}\n----\n\nQuestion: {user_input}"

# Preguntes suggerides, en un ordre fàcil de seguir durant una demostració. Cada una d'elles destaca un aspecte clau:
# significat (no les paraules), una parafrasi, l'origen en diferents àrees, i finalment el
# Lliçona de límits (la pregunta fora del tema).
SUGGESTIONS = [
    "how quick is the delivery robot?",            # Paraules que no apareixen al text – recuperació per significat
    "what does the night drone do?",               # "Drone nocturn" no apareix en cap lloc; "Shelf Owl" guanya.
    "how long does an installation take?",         # una cosa completament diferent chunk
    "what does a Pallet Pup cost, with the dock?", # preus en dues categories chunks
    "can it work inside a freezer?",               # Resposta matisada (Àrtic, 2027)
    "give me a noodle recipe",                     # fora del tema – observeu el límit, després / límit 0.5
]


def chunk(text: str, size: int, overlap: int) -> list[str]:
    """Desplaça una finestra de `size` caràcters al llarg del text, avançant per intervals de superposició de mida."""
    step = max(1, size - overlap)
    pieces = []
    i = 0
    while i < len(text):
        piece = text[i:i + size].strip()
        if piece:
            pieces.append(piece)
        i += step
    return pieces


def _truncate(text: str, width: int = 70) -> str:
    one = " ".join(text.split())
    return one if len(one) <= width else one[: width - 1] + "…"


def show_ui_send(history: list, user_input: str) -> None:
    body = Text()
    body.append("The chat UI sends the BARE conversation — no system prompt, no chunks:\n\n", style=TEXT_DIM)
    for m in history:
        body.append(f"  {m['role']:9s} ", style=ACCENT)
        body.append(_truncate(m["content"]) + "\n", style=TEXT_DIM)
    body.append(f"  user      ", style=ACCENT)
    body.append(user_input + "\n", style=TEXT)
    console.print(Panel(body, title="🖥️ 1 · what the CHAT UI sends", border_style="bright_cyan",
                        style=ON_BG, padding=(0, 1)))


def show_retrieval(user_input: str, kept: list, dropped: list, top_k: int, threshold: float) -> None:
    table = Table(box=box.SIMPLE_HEAVY, style=ON_BG, header_style=ACCENT,
                  title=f"query = the user message · top-{top_k} · threshold {threshold}",
                  title_style=TEXT_DIM)
    table.add_column("similarity", justify="right", style=NUM)
    table.add_column("source", style=TEXT_DIM)
    table.add_column("#", justify="right", style=TEXT_DIM)
    table.add_column("chunk", style=TEXT)
    table.add_column("", style=GOOD)
    for h in kept:
        m = h["metadata"]
        table.add_row(f"{h['similarity']:.3f}", str(m.get("source")), str(m.get("chunk_number")),
                      _truncate(h["chunk"], 56), "→ injected")
    for h in dropped:
        m = h["metadata"]
        table.add_row(Text(f"{h['similarity']:.3f}", style=BAD), str(m.get("source")),
                      str(m.get("chunk_number")), Text(_truncate(h["chunk"], 56), style=TEXT_DIM),
                      Text("✗ below threshold", style=BAD))
    console.print(Panel(table, title="🔎 2 · RETRIEVAL — the collection chooses the context",
                        border_style="magenta brillant", style=ON_BG, padding=(0, 1)))


def show_api_request(messages: list) -> None:
    payload = json.dumps({"model": MODEL, "messages": messages}, indent=2, ensure_ascii=False)
    if len(payload) > 2400:
        payload = payload[:2400] + "\n  ... (truncated for display)"
    console.print(Panel(Syntax(payload, "json", background_color="gris 11", word_wrap=True),
                        title="🧠 3 · what we actually send to the LLM",
                        border_style="galt жёлт", style=ON_BG, padding=(0, 1)))


def show_response(answer: str, usage, kept: int, total: int) -> None:
    body = Text()
    body.append(answer + "\n\n", style=TEXT)
    body.append(f"prompt_tokens={usage.prompt_tokens} · completion_tokens={usage.completion_tokens} "
                f"· {kept} chunks rode along, out of {total} in the collection\n", style=NUM)
    body.append("History keeps only (your message, this answer). The chunks are already gone.", style=TEXT_DIM)
    console.print(Panel(body, title="💬 4 · the response — and what persists",
                        border_style="verd brillant", style=ON_BG, padding=(0, 1)))


def main() -> None:
    persist = os.environ.get("PERSIST_PATH")  # unset -> en la memòria, igual en cada execució
    col = create_collection(os.environ.get("COLLECTION", "knowledge"),
                            description="embeddings-rag-explorer demo",
                            metric="cosine", persist_path=persist)
    top_k = int(os.environ.get("TOP_K", "4"))
    threshold = float(os.environ.get("THRESHOLD", "0.4"))

    # --- Ingestió al moment de l'inici: chunk, fitxer "knowledge.txt", inserint-lo a través del gestor ----
    text = open(os.path.join(os.path.dirname(__file__), "knowledge.txt")).read()
    pieces = chunk(text, CHUNK_SIZE, CHUNK_OVERLAP)
    stored = sum(insert(col, p, {"source": "knowledge.txt"})["ok"] for p in pieces)

    intro = Text()
    intro.append("Ingested ", style=TEXT)
    intro.append(f"{stored} chunks", style=NUM)
    intro.append(f" from knowledge.txt (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP}) into the collection "
                 f"({col.count()} total, {'persisted' if persist else 'in memory'}).\n", style=TEXT)
    intro.append("Ask something; watch which chunks get chosen — and which get dropped. "
                 "Some questions to aim with:\n\n", style=TEXT)
    for i, s in enumerate(SUGGESTIONS, 1):
        intro.append(f"  {i}. ", style=NUM)
        intro.append(s + "\n", style=TEXT)
    intro.append("\n/topk N   /threshold X   (empty line = quit)", style=TEXT_DIM)
    console.print(Panel(intro, title="📚 Embeddings-RAG Explorer — simple dynamic RAG",
                        border_style="magenta brillant", style=ON_BG, padding=(1, 2)))

    history = []
    next_tip = 0
    while True:
        try:
            line = console.input("[bold bright_cyan]📝 you: [/bold bright_cyan]").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not line:
            break
        if line.startswith("/topk"):
            top_k = int(line.split()[1]); console.print(Text(f"  top_k = {top_k}", style=NUM)); continue
        if line.startswith("/threshold"):
            threshold = float(line.split()[1]); console.print(Text(f"  threshold = {threshold}", style=NUM)); continue

        show_ui_send(history, line)

        # Obtenir els elements sense primer establir un límit, de manera que també siguin visibles els chunks.
        all_hits = query(col, line, top_k=top_k)
        kept = [h for h in all_hits if h["similarity"] >= threshold]
        dropped = [h for h in all_hits if h["similarity"] < threshold]
        show_retrieval(line, kept, dropped, top_k, threshold)
        if not kept:
            console.print(Text("  nothing passes the threshold — nothing to inject. "
                               "The model gets no context; lower /threshold to compare.\n", style=BAD))
            continue

        context = "\n\n".join(f"[{h['metadata'].get('source')} · chunk {h['metadata'].get('chunk_number')} "
                              f"· similarity {h['similarity']:.3f}]\n{h['chunk']}" for h in kept)
        augmented = TEMPLATE.format(context=context, user_input=line)
        messages = [{"role": "system", "content": SYSTEM}] + history + [{"role": "user", "content": augmented}]
        show_api_request(messages)

        resp = client.chat.completions.create(model=MODEL, messages=messages)
        answer = resp.choices[0].message.content
        show_response(answer, resp.usage, len(kept), col.count())

        history += [{"role": "user", "content": line},
                    {"role": "assistant", "content": answer}]

        # Manteniu la demostració en marxa: doni una pista sobre la pròxima suggerència que l'usuari encara no ha provat.
        while next_tip < len(SUGGESTIONS) and SUGGESTIONS[next_tip].lower() in line.lower():
            next_tip += 1
        if next_tip < len(SUGGESTIONS):
            tip = SUGGESTIONS[next_tip]
            extra = "  (then /threshold 0.5 and ask again)" if tip.startswith("give me") else ""
            console.print(Text(f"💡 try: {tip}{extra}\n", style=TEXT_DIM))
            next_tip += 1

    console.print(Text("Adéu.", style=TEXT_DIM))


if __name__ == "__main__":
    main()
