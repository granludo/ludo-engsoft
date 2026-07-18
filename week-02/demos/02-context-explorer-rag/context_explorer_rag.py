# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# Curs per a agents de BSC — Transformers, LLMs, RAG i Agents: Des del teòric fins a la pràctica
# Amb llicència Creative Commons BY-NC-SA 4.0 – és obligatori citar l'autor, no es pot fer ús comercial, i les obres derivades han de tenir la mateixa llicència.

# =============================================================================================================== #
# Universitat Politècnica de Catalunya (UPC)                                                                      #
# =============================================================================================================== #

"""
📚 Explorador de context — RAG d'un sol fitxer: què desa l'aplicació vs. què rep el LLM.

El RAG d'un sol fitxer és el més rudimentari que es mereix aquest nom: enganxes tot un
fitxer a la prompt com a context i preguntes. Aquest explorador mostra la part que
tothom entén malament — la diferència entre la conversa que guarda la CHAT UI i la
crida que rep realment el LLM. No són el mateix, i aquest desfasament és la lliçó.

TRES CAPES (amb la mateixa forma que servir un assistent sobre una API compatible amb
OpenAI, p. ex. LAMB):

    🖥️  CHAT UI        envia:    historial (nu) + el teu darrer missatge
                                  |   historial = el que veus; sense system prompt, sense augmentació
                                  v
    🛠️  ASSISTANT ENDPOINT  (STATELESS; l'id del model tria system prompt + plantilla + RAG)
            construeix:  [system] + [history] + [ plantilla(el teu missatge, augmentació RAG) ]
                                  |   es reconstrueix a cada crida — no té estat per conservar-lo
                                  v
    🧠  LLM            retorna:   només la resposta
                                  ^
    🖥️  CHAT UI        afegeix (el teu missatge, la resposta) a l'historial   ✗ augmentació NO desada

Com que l'endpoint és stateless, l'augmentació es construeix de nou a cada torn i es
llença. L'historial de la UI es manté nu. Per CONSERVAR l'augmentació hauries de desar
l'historial augmentat i fer el xat stateful — prova `/stateful` per veure què costa.

DOS MODES DE COL·LOCACIÓ (commuta en directe amb /mode):
- user-augment    (per defecte) — el fitxer s'injecta al missatge de l'USUARI a cada torn.
                              Volàtil: viatja a la cua de la prompt, es reenvia i es torna
                              a facturar a cada crida, mai no és cacheable.
- system-grounding          — el fitxer es col·loca a la SYSTEM prompt UN sol cop (part de la
                              configuració de l'assistent). Es recupera un cop, al principi. La
                              conversa es manté "pura" (només preguntes i respostes) i el fitxer
                              seu al prefix estable i cacheable (KV cache).

Ús:
    1. Copia .env.example a .env i omple els teus valors
    2. uv run context_explorer_rag.py
    3. (opcional) RAG_MODE=system-grounding  KNOWLEDGE_FILE=mynotes.txt  uv run context_explorer_rag.py

Ordres dins del xat:
    /mode [user-augment|system-grounding]   canvia la col·locació (reinicia la conversa);
                                            sense argument, commuta. Espais/guions baixos/guions
                                            i àlies curts (system, grounding, sg / user,
                                            augment, ua) es resolen tots.
    /stateful                                commuta el desament de l'historial augmentat (l'alternativa stateful)
    /file <ruta>                             carrega un altre fitxer de coneixement
    /context                                 imprimeix el fitxer de coneixement carregat
    (línia buida)                            sortir
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

# Tema Rich d'alt contrast — evita el blau fosc i els grisos apagats sobre fons de panell foscos.
BG = "grey23"
ON_BG = f"on {BG}"
TEXT = f"bright_white {ON_BG}"
TEXT_DIM = f"grey84 {ON_BG}"
ACCENT = f"cyan1 {ON_BG}"
ACCENT_BOLD = f"bold cyan1 {ON_BG}"
ROLE = f"sky_blue1 {ON_BG}"
ALERT = f"salmon1 {ON_BG}"
COST = f"orange1 {ON_BG}"
BORDER = "bright_cyan"
BORDER_ALERT = "light_coral"
INPUT_PROMPT = "[bold bright_cyan]👤 Tu: [/bold bright_cyan]"

console = Console()
client = None

# Configuració des de .env
MODEL = os.getenv("MODEL", "gpt-4.1-mini")
OPENAI_ENDPOINT = os.getenv("OPENAI_ENDPOINT")  # Opcional: endpoint alternatiu compatible amb OpenAI
KNOWLEDGE_FILE = os.getenv("KNOWLEDGE_FILE", "knowledge.txt")

MODE_USER_AUGMENT = "user-augment"
MODE_SYSTEM_GROUNDING = "system-grounding"
RAG_MODE = os.getenv("RAG_MODE", MODE_USER_AUGMENT)

# Instrucció de grounding: respon a partir del context i admet quan la resposta no hi és.
SYSTEM_PROMPT_BASE = "Answer using only the context provided. If the answer is not in the context, say you don't know."

# La plantilla de prompt RAG — la forma que els estudiants reutilitzen tota la setmana.
PROMPT_TEMPLATE = "Context:\n----\n{context}\n----\n\nQuestion: {question}"

# Accepta arguments de mode poc tipats. Els dos noms canònics van amb guió
# ("user-augment", "system-grounding"), però davant la càmera (i per als estudiants) és
# fàcil escriure un espai en lloc del guió, o que l'autocorrecció el converteixi en un
# guió llarg. Mapem tots aquests casos —més els àlies curts— al mode canònic.
_MODE_ALIASES = {
    "user-augment": MODE_USER_AUGMENT, "user": MODE_USER_AUGMENT,
    "augment": MODE_USER_AUGMENT, "ua": MODE_USER_AUGMENT,
    "system-grounding": MODE_SYSTEM_GROUNDING, "system": MODE_SYSTEM_GROUNDING,
    "grounding": MODE_SYSTEM_GROUNDING, "sg": MODE_SYSTEM_GROUNDING,
}


def _resolve_mode(raw: str, current: str):
    """Converteix un argument poc tipat de `/mode` en un mode canònic.

    Argument buit → commuta a l'altre mode. Els espais, els guions baixos i qualsevol
    variant de guió es normalitzen a un sol guió, de manera que "system grounding",
    "system_grounding" i "system–grounding" es resolen tots. Retorna None si l'argument
    no és buit i tot i així no es reconeix.
    """
    s = raw.strip().lower()
    for dash in ("–", "—", "−", "_"):  # – — − _  → guió
        s = s.replace(dash, "-")
    s = "-".join(s.split())  # col·lapsa les tandes d'espais en un sol guió
    if not s:
        return MODE_SYSTEM_GROUNDING if current == MODE_USER_AUGMENT else MODE_USER_AUGMENT
    return _MODE_ALIASES.get(s)


# =============================================================================================================== #
# Recuperació — l'única part que canvia entre el RAG d'un sol fitxer i el RAG amb embeddings.                     #
# =============================================================================================================== #

class WholeFileRetriever:
    """RAG d'un sol fitxer: ignora la pregunta i retorna TOT el fitxer. Fer trampes al solitari.

    Sense chunking, sense embeddings, sense vector store. L'etapa de "recuperació" és
    `open().read()`. Més endavant al curs se substitueix per un EmbeddingsRetriever que
    retorna només els top-k chunks més propers — i res més d'aquest programa canvia.
    Aquest és el punt clau.
    """

    def __init__(self, path: str):
        self.path = path
        with open(path, encoding="utf-8") as f:
            self.text = f.read()

    def retrieve(self, question: str) -> str:
        return self.text  # tot el fitxer — la pregunta s'ignora expressament

    def describe(self) -> str:
        return f"WholeFileRetriever · {os.path.basename(self.path)} · whole file"


# =============================================================================================================== #
# Les dues capes que importen — i el límit entre elles.                                                           #
# =============================================================================================================== #

class AssistantEndpoint:
    """Un endpoint RAG STATELESS — amb la mateixa forma que servir un assistent sobre una
    API compatible amb OpenAI (això és el que fa LAMB).

    NO manté cap estat de conversa. A cada crida rep l'historial nu + el darrer missatge
    de l'usuari des de la UI, consulta la seva configuració (system prompt, plantilla de
    prompt, font RAG — aquí fixada en la construcció, en producció indexada per l'id del
    model) i CONSTRUEIX la crida real al LLM des de zero:

        user-augment      → [system] + history + [user: template(retrieve(msg), msg)]
        system-grounding  → [system + file] + history + [user: msg]   (nu; el fitxer és al system)

    L'augmentació que construeix no es retorna ni es desa mai. A la crida següent la torna a construir.
    """

    def __init__(self, retriever: WholeFileRetriever, mode: str):
        self.retriever = retriever
        self.mode = mode
        if mode == MODE_SYSTEM_GROUNDING:
            # Recupera UN sol cop, en la configuració: el fitxer esdevé part del system prompt de l'assistent.
            grounding = retriever.retrieve("")  # fitxer sencer; consulta ignorada
            self.system_prompt = (
                SYSTEM_PROMPT_BASE
                + "\n\nContext:\n----\n" + grounding + "\n----"
            )
            self.retrieved_at_setup = True
        else:
            self.system_prompt = SYSTEM_PROMPT_BASE
            self.retrieved_at_setup = False

    def build(self, history: list, user_message: str) -> dict:
        """Construeix la crida al LLM a partir de l'historial nu + el darrer missatge de l'usuari.

        Retorna un diccionari que descriu la construcció perquè l'explorador pugui mostrar el límit:
          messages          — la llista real que s'envia al LLM
          augmented_index   — índex del missatge que l'endpoint ha augmentat (o None)
          retrieval         — què ha fet la recuperació en aquest torn (string), o None
        """
        messages = [{"role": "system", "content": self.system_prompt}]
        messages += history  # passa directament des de la UI — encara nu

        if self.mode == MODE_SYSTEM_GROUNDING:
            # El fitxer ja viu al system prompt. El torn de l'usuari és nu. Cap recuperació ara.
            messages.append({"role": "user", "content": user_message})
            return {"messages": messages, "augmented_index": None,
                    "retrieval": "cap en aquest torn — el fitxer és a la system prompt (recuperat un sol cop, a la configuració)"}

        # user-augment: recupera ara i injecta el fitxer en AQUEST missatge de l'usuari.
        context = self.retriever.retrieve(user_message)
        built = PROMPT_TEMPLATE.format(context=context, question=user_message)
        messages.append({"role": "user", "content": built})
        return {"messages": messages, "augmented_index": len(messages) - 1,
                "retrieval": f"recuperats {len(context)} caràcters (~{_approx_tokens(context)} tokens) i injectats en AQUEST missatge de l'usuari"}

    def complete(self, history: list, user_message: str) -> dict:
        """Construeix → crida el LLM → retorna la resposta. L'endpoint no guarda res."""
        build = self.build(history, user_message)
        with wait_spinner():
            response = client.chat.completions.create(
                model=MODEL, messages=build["messages"], temperature=0.7
            )
        build["response"] = response
        return build


class ChatUI:
    """La interfície de xat. Conté la conversa que veu l'USUARI — només els torns nus.
    Sense system prompt, sense augmentació: això viu darrere de l'endpoint."""

    def __init__(self, stateful_augment: bool = False):
        self.history = []
        # Si és True, la UI desa el missatge augmentat de l'usuari en lloc del nu —
        # l'alternativa "fer el xat stateful". Desactivat per defecte (el model realista).
        self.stateful_augment = stateful_augment

    def outgoing(self, user_message: str) -> list:
        """El que la UI envia a l'endpoint: el seu historial + el nou missatge (tot nu)."""
        return self.history + [{"role": "user", "content": user_message}]

    def record(self, user_message: str, assistant_message: str, augmented_user: str = None):
        stored_user = augmented_user if (self.stateful_augment and augmented_user) else user_message
        self.history.append({"role": "user", "content": stored_user})
        self.history.append({"role": "assistant", "content": assistant_message})


# =============================================================================================================== #
# Panells                                                                                                         #
# =============================================================================================================== #

def _approx_tokens(text: str) -> int:
    """Estimació aproximada abans que respongui l'API (≈ 4 caràcters/token). El nombre real és usage.prompt_tokens."""
    return max(1, len(text) // 4)


def _truncate(text: str, width: int = 88) -> str:
    one_line = text.replace("\n", " ")
    if len(one_line) <= width:
        return one_line
    return one_line[:width] + f"… [+{len(one_line) - width} chars]"


def show_flow(mode: str, stateful: bool) -> Panel:
    """El diagrama de límits de tres capes — es mostra a l'inici i en canviar de mode/stateful."""
    aug = "desa l'historial AUGMENTAT (stateful)" if stateful else "augmentació NO desada (stateless)"
    body = Text()
    body.append("🖥️  CHAT UI", style=f"bold {ROLE}")
    body.append("        envia:  historial (nu) + el teu darrer missatge\n", style=TEXT)
    body.append("                       │  historial = el que veus; sense system, sense augmentació\n", style=TEXT_DIM)
    body.append("                       ▼\n", style=TEXT_DIM)
    body.append("🛠️  ASSISTANT ENDPOINT", style=f"bold bright_yellow {ON_BG}")
    body.append(f"  (STATELESS; mode = {mode})\n", style=TEXT)
    if mode == MODE_SYSTEM_GROUNDING:
        builds = "        construeix:  [system ＋ FILE] + [history] + [user: el teu missatge — nu]\n"
    else:
        builds = "        construeix:  [system] + [history] + [user: template(FILE, el teu missatge)]\n"
    body.append(builds, style=TEXT)
    body.append("                       │  es reconstrueix a cada crida — no té estat on desar-lo\n", style=TEXT_DIM)
    body.append("                       ▼\n", style=TEXT_DIM)
    body.append("🧠  LLM", style=f"bold bright_green {ON_BG}")
    body.append("            retorna:  només la resposta\n", style=TEXT)
    body.append("                       ▲\n", style=TEXT_DIM)
    body.append("🖥️  CHAT UI", style=f"bold {ROLE}")
    body.append(f"        afegeix (el teu missatge, resposta) → historial   ✗ {aug}", style=TEXT)
    return Panel(body, title="🔁 Les tres capes", border_style="bright_magenta", style=ON_BG, padding=(1, 2))


def show_ui_send(outgoing: list) -> Panel:
    """Què envia la Chat UI a l'endpoint — historial nu + el nou missatge."""
    table = Table(box=box.SIMPLE, show_header=True, header_style=f"bold {TEXT}", style=ON_BG)
    table.add_column("#", style=f"bright_cyan {ON_BG}", width=3)
    table.add_column("Rol", style=ROLE, width=10)
    table.add_column("Contingut (nu — sense system, sense augmentació)", style=TEXT)
    for i, m in enumerate(outgoing):
        table.add_row(str(i), m["role"], _truncate(m["content"]))
    return Panel(table, title="🖥️ → 🛠️  La Chat UI envia a l'endpoint", border_style=BORDER, style=ON_BG, padding=(0, 1))


def show_endpoint_build(build: dict, mode: str) -> Panel:
    """Què construeix l'endpoint stateless per al LLM — system + historial + el contingut de l'usuari d'aquest torn."""
    messages = build["messages"]
    aug_idx = build["augmented_index"]
    table = Table(box=box.SIMPLE, show_header=True, header_style=f"bold {TEXT}", style=ON_BG)
    table.add_column("#", style=f"bright_cyan {ON_BG}", width=3)
    table.add_column("Rol", style=f"bright_magenta {ON_BG}", width=10)
    table.add_column("Font / vida útil", style=f"bright_yellow {ON_BG}", width=26)
    table.add_column("Contingut", style=TEXT)
    last = len(messages) - 1
    grounded = mode == MODE_SYSTEM_GROUNDING
    for i, m in enumerate(messages):
        if m["role"] == "system":
            # En system-grounding el fitxer viu dins d'aquest missatge de sistema — marca'l.
            src = "config ＋ FILE · estàtic" if grounded else "config de l'assistent · estàtic"
        elif i == aug_idx:
            src = "★ construït aquí · descartat"
        elif i == last:
            src = "des de la UI (nu) · aquest torn"
        else:
            src = "des de la UI · passa directament"
        table.add_row(str(i), m["role"], src, _truncate(m["content"]))
    note = Text(f"\nrecuperació: {build['retrieval']}", style=f"bright_yellow {ON_BG}")
    grid = Table.grid()
    grid.add_row(table)
    grid.add_row(note)
    if aug_idx is not None:
        grid.add_row(Text("★ el missatge augmentat es construeix de nou ara i es llença — mai no torna a la UI",
                          style=f"bold {ALERT}"))
    return Panel(grid, title="🛠️ → 🧠  L'endpoint construeix la crida al LLM (stateless)", border_style="yellow", style=ON_BG, padding=(0, 1))


def show_api_request(messages: list) -> Panel:
    json_str = json.dumps({"model": MODEL, "messages": messages, "temperature": 0.7}, indent=2, ensure_ascii=False)
    syntax = Syntax(json_str, "json", theme="monokai", background_color=BG, word_wrap=True)
    return Panel(syntax, title="📤 La crida real al LLM", border_style="yellow", style=ON_BG, padding=(0, 1))


def show_api_response(response_data: dict) -> Panel:
    json_str = json.dumps(response_data, indent=2, ensure_ascii=False)
    syntax = Syntax(json_str, "json", theme="monokai", background_color=BG, word_wrap=True)
    return Panel(syntax, title="📥 Resposta del LLM", border_style="bright_cyan", style=ON_BG, padding=(0, 1))


def show_ui_history(history: list, stateful: bool) -> Panel:
    """Què manté la Chat UI després del torn — què veu l'usuari / què es desa."""
    table = Table(box=box.SIMPLE, show_header=True, header_style=f"bold {TEXT}", style=ON_BG)
    table.add_column("#", style=f"bright_cyan {ON_BG}", width=3)
    table.add_column("Rol", style=ROLE, width=10)
    table.add_column("Contingut", style=TEXT)
    for i, m in enumerate(history):
        table.add_row(str(i), m["role"], _truncate(m["content"]))
    if stateful:
        cap = "STATEFUL: els torns augmentats de l'usuari SÍ que es desen — ara el fitxer també viatja a l'historial"
        style = f"bold {ALERT}"
    else:
        cap = "sense system prompt · sense augmentació · només els torns que l'usuari ha vist"
        style = TEXT_DIM
    grid = Table.grid()
    grid.add_row(table)
    grid.add_row(Text(cap, style=style))
    return Panel(grid, title="🖥️  Historial de la Chat UI (el que veu l'usuari / el que es desa)", border_style=BORDER, style=ON_BG, padding=(0, 1))


def show_cost(history_tokens: list) -> Panel:
    table = Table(box=box.SIMPLE, show_header=True, header_style=f"bold {TEXT}", style=ON_BG)
    table.add_column("Torn", style=f"bright_cyan {ON_BG}", width=5)
    table.add_column("prompt_tokens", style=f"bright_yellow {ON_BG}", width=14)
    table.add_column("cached", style=f"bright_green {ON_BG}", width=8)
    table.add_column("", style=COST)
    peak = max((t[0] for t in history_tokens), default=1) or 1
    for i, (pt, cached) in enumerate(history_tokens, start=1):
        bar = "█" * max(1, int(26 * pt / peak))
        table.add_row(str(i), str(pt), ("—" if cached is None else str(cached)), bar)
    return Panel(table, title="💸 Cost en tokens per torn (prompt_tokens · cached)", border_style=BORDER_ALERT, style=ON_BG, padding=(0, 1))


def show_message(role: str, content: str) -> Panel:
    styles = {
        "user": ("bright_white on dodger_blue1", BORDER, "👤 Tu"),
        "assistant": ("bright_white on dark_green", "green", "🤖 Assistent"),
    }
    text_style, border, title = styles.get(role, (TEXT, "white", role))
    return Panel(Text(content, style=text_style), title=title, border_style=border, padding=(0, 1))


def wait_spinner():
    return Live(
        Panel(Spinner("dots", text=Text("Esperant el LLM...", style="bold black on yellow")),
              border_style="yellow", style="on yellow", padding=(0, 1)),
        console=console, refresh_per_second=10
    )


def show_setup(retriever: "WholeFileRetriever", mode: str) -> Panel:
    """Mostra la configuració de l'assistent abans de cap missatge: el system prompt, la plantilla de prompt i el fitxer de coneixement — a més d'on va el fitxer en aquest mode."""
    file_text = retriever.text
    if len(file_text) > 1500:
        file_text = file_text[:1500] + f"\n… [+{len(retriever.text) - 1500} more chars]"

    sg = mode == MODE_SYSTEM_GROUNDING

    g = Table.grid(padding=(0, 0))

    # ① SYSTEM PROMPT — en system-grounding el fitxer es concatena A DINS.
    g.add_row(Text("① SYSTEM PROMPT", style=f"bold bright_magenta {ON_BG}"))
    g.add_row(Text(SYSTEM_PROMPT_BASE, style=TEXT))
    if sg:
        g.add_row(Text("        ＋ fitxer de coneixement ③ concatenat aquí — recuperat UN sol cop, a la configuració",
                       style=f"bold bright_green {ON_BG}"))
        g.add_row(Text("   ↳ en system-grounding el fitxer ÉS part de la system prompt; la template de sota és morta",
                       style=TEXT_DIM))
    else:
        g.add_row(Text("   ↳ user-augment: només la instrucció — el fitxer NO és aquí; viatja a cada missatge "
                       "de l'usuari via la template ↓", style=TEXT_DIM))
    g.add_row(Text("", style=ON_BG))

    # ② PROMPT TEMPLATE — activa en user-augment, morta en system-grounding.
    if sg:
        g.add_row(Text("② PROMPT TEMPLATE   ⛔ NO S'USA EN AQUEST MODE", style=f"bold bright_red {ON_BG}"))
        g.add_row(Text(PROMPT_TEMPLATE, style=TEXT_DIM))
        g.add_row(Text("   ↳ inactiva — el teu missatge s'envia nu; el fitxer ja viu a la system prompt de dalt",
                       style=TEXT_DIM))
    else:
        g.add_row(Text("② PROMPT TEMPLATE   ✅ S'USA A CADA TORN", style=f"bold bright_yellow {ON_BG}"))
        g.add_row(Text(PROMPT_TEMPLATE, style=TEXT))
        g.add_row(Text("   ↳ es reconstrueix a cada torn — el fitxer va a {context}, el teu missatge a {question}",
                       style=TEXT_DIM))
    g.add_row(Text("", style=ON_BG))

    # ③ KNOWLEDGE FILE — i cap on flueix en AQUEST mode.
    where = "la SYSTEM PROMPT ① (un cop, a la configuració)" if sg else "la PROMPT TEMPLATE ② {context} (a cada torn)"
    g.add_row(Text(f"③ KNOWLEDGE FILE · {os.path.basename(retriever.path)} "
                   f"({len(retriever.text)} caràcters, ~{_approx_tokens(retriever.text)} tokens)   "
                   f"→  va a {where}", style=f"bold bright_green {ON_BG}"))
    g.add_row(Text(file_text, style=TEXT_DIM))
    return Panel(g, title=f"🧩 Configuració de l'assistent — mode = {mode}",
                 border_style="bright_cyan", style=ON_BG, padding=(1, 2))


# =============================================================================================================== #
# Cicle de conversa                                                                                               #
# =============================================================================================================== #

def run_chat(retriever: WholeFileRetriever, mode: str):
    ui = ChatUI(stateful_augment=False)
    endpoint = AssistantEndpoint(retriever, mode)
    token_history = []

    console.print()
    console.print(Panel(
        Text("Pregunta sobre el fitxer de coneixement. Cada torn mostra el desfasament entre el que\n"
             "la CHAT UI guarda (torns nus) i el que l'ENDPOINT stateless construeix per al LLM.\n\n"
             "/mode [user-augment | system-grounding]  (sense arg = commuta)   ·   /stateful   ·   /file <ruta>   ·   /context   ·   (buit = surt)",
             style=TEXT),
        title="📚 Explorador de context — RAG d'un sol fitxer", border_style="bright_magenta", style=ON_BG, padding=(1, 2)))
    console.print()
    console.print(show_flow(mode, ui.stateful_augment))
    console.print()
    console.print(show_setup(retriever, mode))

    while True:
        console.print()
        user_input = console.input(INPUT_PROMPT)
        cmd = user_input.strip()

        if not cmd:
            console.print(Panel(Text("Adéu!", style=TEXT), border_style="dim"))
            break
        if cmd == "/context":
            console.print(Panel(Text(retriever.text, style=TEXT_DIM),
                                title=f"📄 {os.path.basename(retriever.path)}", border_style="green", style=ON_BG))
            continue
        if cmd == "/stateful":
            ui.stateful_augment = not ui.stateful_augment
            ui.history = []
            console.print(Panel(Text(f"stateful_augment = {ui.stateful_augment} · conversa reiniciada.",
                                     style=TEXT), border_style="green", style=ON_BG))
            console.print(show_flow(mode, ui.stateful_augment))
            continue
        if cmd == "/mode" or cmd.startswith("/mode "):
            new_mode = _resolve_mode(cmd[len("/mode"):], mode)
            if new_mode is None:
                console.print(Panel(Text(f"mode desconegut. Usa: {MODE_USER_AUGMENT} | {MODE_SYSTEM_GROUNDING} "
                                         f"(o simplement /mode per commutar).",
                                         style="bold bright_white on dark_red"), border_style="red", style="on dark_red"))
                continue
            if new_mode == mode:
                console.print(Panel(Text(f"ja ets al mode = {mode}.", style=TEXT),
                                    border_style="green", style=ON_BG))
                continue
            mode = new_mode
            endpoint = AssistantEndpoint(retriever, mode)
            ui.history = []
            token_history = []
            console.print(Panel(Text(f"mode = {mode} · conversa reiniciada.", style=TEXT),
                                border_style="green", style=ON_BG))
            console.print(show_flow(mode, ui.stateful_augment))
            console.print()
            console.print(show_setup(retriever, mode))
            continue
        if cmd.startswith("/file "):
            new_path = cmd[len("/file "):].strip()
            try:
                retriever = WholeFileRetriever(new_path)
                endpoint = AssistantEndpoint(retriever, mode)
                ui.history = []
                token_history = []
                console.print(Panel(Text(f"S'ha carregat {new_path} ({len(retriever.text)} caràcters) · conversa reiniciada.",
                                         style=TEXT), border_style="green", style=ON_BG))
                console.print()
                console.print(show_setup(retriever, mode))
            except OSError as exc:
                console.print(Panel(Text(f"No s'ha pogut carregar {new_path}: {exc}", style="bold bright_white on dark_red"),
                                    border_style="red", style="on dark_red"))
            continue

        # 1) La UI envia el seu historial nu + el nou missatge a l'endpoint.
        outgoing = ui.outgoing(user_input)
        console.print()
        console.print(show_message("user", user_input))
        console.print()
        console.print(show_ui_send(outgoing))

        # 2) L'endpoint stateless construeix la crida real al LLM i l'executa.
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

        # 3) La resposta torna a la UI; només s'hi desen el torn nu + la resposta.
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
        console.print(Panel(Text("No s'ha trobat OPENAI_API_KEY!\n\nCopia .env.example a .env i omple-la.",
                                 style="bold bright_white on dark_red"), title="❌ Error", border_style="red", style="on dark_red"))
        return

    if RAG_MODE not in (MODE_USER_AUGMENT, MODE_SYSTEM_GROUNDING):
        console.print(Panel(Text(f"RAG_MODE desconegut '{RAG_MODE}'. Usa {MODE_USER_AUGMENT} o {MODE_SYSTEM_GROUNDING}.",
                                 style="bold bright_white on dark_red"), title="❌ Error", border_style="red", style="on dark_red"))
        return

    knowledge_path = KNOWLEDGE_FILE
    if not os.path.isabs(knowledge_path):
        knowledge_path = os.path.join(os.path.dirname(__file__), knowledge_path)
    try:
        retriever = WholeFileRetriever(knowledge_path)
    except OSError as exc:
        console.print(Panel(Text(f"No s'ha pogut carregar el fitxer de coneixement '{knowledge_path}':\n{exc}",
                                 style="bold bright_white on dark_red"), title="❌ Error", border_style="red", style="on dark_red"))
        return

    client = OpenAI(api_key=api_key, base_url=OPENAI_ENDPOINT) if OPENAI_ENDPOINT else OpenAI(api_key=api_key)

    console.print(Panel(
        Text(f"Model      : {MODEL}\n"
             f"Endpoint   : {OPENAI_ENDPOINT or 'https://api.openai.com/v1'}\n"
             f"Coneixement: {os.path.basename(knowledge_path)} ({len(retriever.text)} caràcters, ~{_approx_tokens(retriever.text)} tokens)\n"
             f"Mode       : {RAG_MODE}",
             style=TEXT),
        title="⚙️ Configuració", border_style="bright_cyan", style=ON_BG))

    run_chat(retriever, RAG_MODE)


if __name__ == "__main__":
    main()
