# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# Curs d'agents del BSC — Transformers, LLMs, RAG i Agents: de la teoria a la producció
# Amb llicència Creative Commons BY-NC-SA 4.0 – és obligatori citar l'autor, no es pot fer ús comercial, i les obres derivades han de tenir la mateixa llicència.

# =============================================================================================================== #
# Universitat Politècnica de Catalunya (UPC)                                                                      #
# =============================================================================================================== #

"""
📚 Embeddings-RAG Explorer — tot el cicle del RAG dinàmic, panell a panell.

En arrencar, la demostració fa la INGESTA de knowledge.txt: el parteix en chunks (una finestra
lliscant amb solapament — el chunking és un bucle for) i insereix cada chunk en una col·lecció
a través del collections_manager del curs. Les mateixes tres crides són la base de tot el que fem
aquesta setmana: aquesta demostració, el collections-explorer, l'eina simple-dynamic-rag que es
proporciona i EL TEU projecte final parlen tots la mateixa interfície.

Després, a cada torn, veus com passa el RAG dinàmic:

    🖥️  CHAT UI        envia:  l'historial (pelat) + el teu últim missatge
                                  |
                                  v
    🛠️  ASSISTANT ENDPOINT  (SENSE ESTAT)
            1. el teu missatge es converteix en la CONSULTA
            2. la col·lecció retorna els chunks més propers (top-K, per sobre d'un llindar)
            3. construeix: [system] + [history] + [ template(el teu missatge, AQUESTS chunks) ]
                                  |
                                  v
    🧠  LLM            retorna:  només la resposta
                                  ^
    🖥️  CHAT UI        afegeix (el teu missatge, la resposta) a l'historial   ✗ els chunks NO es desen

Comandes dins del xat:
    /topk N      canvia quants chunks es recuperen
    /threshold X canvia el llindar de similitud (els chunks per sota es descarten)
    (línia buida) surt

La col·lecció viu en memòria i es reconstrueix a partir de knowledge.txt a cada execució —
cada presa de la demostració comença idèntica. Defineix PERSIST_PATH al .env per conservar-la.
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

# Tema Rich d'alt contrast — coincideix amb l'estil visual de l'explorador de context.
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

# Preguntes suggerides, en un ordre pensat per a la demostració. Cadascuna mostra un moment clau:
# el significat (no les paraules), una paràfrasi, la procedència en diferents àmbits i, finalment,
# la lliçó del llindar (la pregunta fora de tema).
SUGGESTIONS = [
    "how quick is the delivery robot?",            # paraules que no són al text — recuperació per significat
    "what does the night drone do?",               # «night drone» no apareix enlloc; guanya Shelf Owl
    "how long does an installation take?",         # un chunk completament diferent
    "what does a Pallet Pup cost, with the dock?", # preus repartits en dos chunks
    "can it work inside a freezer?",               # resposta matisada (Àrtic, 2027)
    "give me a noodle recipe",                     # fora de tema — observa el llindar, després /threshold 0.5
]


def chunk(text: str, size: int, overlap: int) -> list[str]:
    """Fa lliscar una finestra de `size` caràcters al llarg del text, avançant en passos de size-overlap."""
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
    body.append("La interfície de xat envia la conversa PELADA — sense system prompt, sense chunks:\n\n", style=TEXT_DIM)
    for m in history:
        body.append(f"  {m['role']:9s} ", style=ACCENT)
        body.append(_truncate(m["content"]) + "\n", style=TEXT_DIM)
    body.append(f"  user      ", style=ACCENT)
    body.append(user_input + "\n", style=TEXT)
    console.print(Panel(body, title="🖥️ 1 · què envia la CHAT UI", border_style="bright_cyan",
                        style=ON_BG, padding=(0, 1)))


def show_retrieval(user_input: str, kept: list, dropped: list, top_k: int, threshold: float) -> None:
    table = Table(box=box.SIMPLE_HEAVY, style=ON_BG, header_style=ACCENT,
                  title=f"consulta = el missatge de l'usuari · top-{top_k} · llindar {threshold}",
                  title_style=TEXT_DIM)
    table.add_column("similarity", justify="right", style=NUM)
    table.add_column("source", style=TEXT_DIM)
    table.add_column("#", justify="right", style=TEXT_DIM)
    table.add_column("chunk", style=TEXT)
    table.add_column("", style=GOOD)
    for h in kept:
        m = h["metadata"]
        table.add_row(f"{h['similarity']:.3f}", str(m.get("source")), str(m.get("chunk_number")),
                      _truncate(h["chunk"], 56), "→ injectat")
    for h in dropped:
        m = h["metadata"]
        table.add_row(Text(f"{h['similarity']:.3f}", style=BAD), str(m.get("source")),
                      str(m.get("chunk_number")), Text(_truncate(h["chunk"], 56), style=TEXT_DIM),
                      Text("✗ per sota del llindar", style=BAD))
    console.print(Panel(table, title="🔎 2 · RECUPERACIÓ — la col·lecció tria el context",
                        border_style="bright_magenta", style=ON_BG, padding=(0, 1)))


def show_api_request(messages: list) -> None:
    payload = json.dumps({"model": MODEL, "messages": messages}, indent=2, ensure_ascii=False)
    if len(payload) > 2400:
        payload = payload[:2400] + "\n  ... (truncat per a la visualització)"
    console.print(Panel(Syntax(payload, "json", background_color="grey11", word_wrap=True),
                        title="🧠 3 · què enviem realment a l'LLM",
                        border_style="bright_yellow", style=ON_BG, padding=(0, 1)))


def show_response(answer: str, usage, kept: int, total: int) -> None:
    body = Text()
    body.append(answer + "\n\n", style=TEXT)
    body.append(f"prompt_tokens={usage.prompt_tokens} · completion_tokens={usage.completion_tokens} "
                f"· han viatjat {kept} chunks, de {total} que hi ha a la col·lecció\n", style=NUM)
    body.append("L'historial només conserva (el teu missatge, aquesta resposta). Els chunks ja han desaparegut.", style=TEXT_DIM)
    console.print(Panel(body, title="💬 4 · la resposta — i què perdura",
                        border_style="bright_green", style=ON_BG, padding=(0, 1)))


def main() -> None:
    persist = os.environ.get("PERSIST_PATH")  # sense definir -> en memòria, idèntica a cada execució
    col = create_collection(os.environ.get("COLLECTION", "knowledge"),
                            description="embeddings-rag-explorer demo",
                            metric="cosine", persist_path=persist)
    top_k = int(os.environ.get("TOP_K", "4"))
    threshold = float(os.environ.get("THRESHOLD", "0.4"))

    # --- INGESTA en arrencar: parteix knowledge.txt en chunks i insereix a través del gestor ----
    text = open(os.path.join(os.path.dirname(__file__), "knowledge.txt")).read()
    pieces = chunk(text, CHUNK_SIZE, CHUNK_OVERLAP)
    stored = sum(insert(col, p, {"source": "knowledge.txt"})["ok"] for p in pieces)

    intro = Text()
    intro.append("S'han ingerit ", style=TEXT)
    intro.append(f"{stored} chunks", style=NUM)
    intro.append(f" de knowledge.txt (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP}) a la col·lecció "
                 f"({col.count()} en total, {'persistida' if persist else 'en memòria'}).\n", style=TEXT)
    intro.append("Pregunta alguna cosa; observa quins chunks es trien — i quins es descarten. "
                 "Algunes preguntes per encaminar-te:\n\n", style=TEXT)
    for i, s in enumerate(SUGGESTIONS, 1):
        intro.append(f"  {i}. ", style=NUM)
        intro.append(s + "\n", style=TEXT)
    intro.append("\n/topk N   /threshold X   (línia buida = surt)", style=TEXT_DIM)
    console.print(Panel(intro, title="📚 Embeddings-RAG Explorer — RAG dinàmic senzill",
                        border_style="bright_magenta", style=ON_BG, padding=(1, 2)))

    history = []
    next_tip = 0
    while True:
        try:
            line = console.input("[bold bright_cyan]📝 tu: [/bold bright_cyan]").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not line:
            break
        if line.startswith("/topk"):
            top_k = int(line.split()[1]); console.print(Text(f"  top_k = {top_k}", style=NUM)); continue
        if line.startswith("/threshold"):
            threshold = float(line.split()[1]); console.print(Text(f"  threshold = {threshold}", style=NUM)); continue

        show_ui_send(history, line)

        # Recupera SENSE el llindar primer, perquè els chunks descartats també siguin visibles.
        all_hits = query(col, line, top_k=top_k)
        kept = [h for h in all_hits if h["similarity"] >= threshold]
        dropped = [h for h in all_hits if h["similarity"] < threshold]
        show_retrieval(line, kept, dropped, top_k, threshold)
        if not kept:
            console.print(Text("  res no supera el llindar — no hi ha res a injectar. "
                               "El model no rep context; abaixa /threshold per comparar.\n", style=BAD))
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

        # Mantén la demostració en marxa: suggereix la propera pregunta que l'usuari encara no ha provat.
        while next_tip < len(SUGGESTIONS) and SUGGESTIONS[next_tip].lower() in line.lower():
            next_tip += 1
        if next_tip < len(SUGGESTIONS):
            tip = SUGGESTIONS[next_tip]
            extra = "  (després /threshold 0.5 i torna a preguntar)" if tip.startswith("give me") else ""
            console.print(Text(f"💡 prova: {tip}{extra}\n", style=TEXT_DIM))
            next_tip += 1

    console.print(Text("Adéu.", style=TEXT_DIM))


if __name__ == "__main__":
    main()
