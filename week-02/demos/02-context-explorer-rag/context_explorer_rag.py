# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# Curs per a agents de BSC — Transformers, LLMs, RAG i Agents: Des del teòric fins a la pràctica
# Amb llicència Creative Commons BY-NC-SA 4.0 – és obligatori citar l'autor, no es pot fer ús comercial, i les obres derivades han de tenir la mateixa llicència.

# =============================================================================================================== #
# Universitat Politècnica de Catalunya (UPC)                                                                      #
# =============================================================================================================== #

"""
📚 Explorador de context – un fitxer RAG: què emmagatzema l'aplicació contra el que rep LLM.

"Mostrar un fitxer individual (RAG) és la manera més bàsica de fer-ho: copiar tot el fitxer a la prompt com a context i preguntar. Aquest explorador mostra la part on la gent sol cometre errors – la diferència entre la conversa que manté l'interfície de chat i la crida real que rep la LLM. No són iguals, i aquesta diferència és el punt clau."

TRES CAPES (amb la mateixa forma que servir un ajudant sobre un OpenAI compatible amb API, per exemple, XEMA):

    🖥️ INTERFÀCIA DE CHAT: envia: historial (sense context) + el vostre últim missatge | Historial = el que veieu; sense missatge del sistema, sense augmentació 🛠️ PUNT FINAL DEL ASSISTENT (sense estat; l'ID del model selecciona el missatge del sistema + plantilla + RAG) construeix: [sistema] + [històric] + [plantilla (el vostre missatge, augmentació RAG)] | Es reconstruïx cada crida — no té estat per conservar-lo 🧠 LLM retorna: només la resposta ^ 🖥️ INTERFÀCIA DE CHAT: afegeix (el vostre missatge, la resposta) al historial ✗ Augmentació no s'emmagatzema

Com que el endpoint és sense estat, l'augmentació es crea cada vegada i s'elimina. L'històric de la interfície queda buit. Per a MANTENIR l'augmentació, hauríeu d'emmagatzemar l'històric augmentat i fer que el programa sigui d'estat — proveu `/stateful` per veure quines són les conseqüències.

DOS modes de col·locació (canviar entre "live" i "/mode"):
- user-augment (per defecte) – el fitxer s'injecta en cada missatge de l'usuari.
                              Volàtil: es manté en la cua de prompt, i es reenvia i se li cobra cada trucada, sense poder emmagatzemar-lo.
- sistema de connexió — el fitxer es col·loca a la SYSTEM prompt vegades (com part del
                              Configuració de l'assistent. Recòrrer una vegada, al principi. La conversa es manté "pura" (només preguntes i respostes), i el fitxer es guarda en el prefix estable i accessible (memòria caché KV).

Ús:
    1. Còpia el fitxer ".env.example" a ".env" i omple els valors corresponents.
    2. Executar el script context_explorer_rag.py amb l'entorn UV.
    3. (opcional) RAG_MODE=system-grounding, ARXIU_DE_CONEGNEMENTS=mynotes.txt, executa uv context_explorer_rag.py

Comandes en el chat: /mode [usuari-augment|sistema-fundament] – canviar la posició (restaurar la conversa); sense arguments, activa/desactiva. Els espais, guions i tirets, així com els alias curts (sistema, fundament, sg / usuari, augment, ua) es resolen tots. /stateful – activar l'emmagatzematge de l'històriu augmentada (l'alternativa "stateful") /file <ruta> – carregar un fitxer de coneixement diferent /context – imprimir el fitxer de coneixement carregat (línia buida) – sortir
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

# Tema de contrast elevat i colors intens – evita el blau fosc o els grisos apagats en fons negres.
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
INPUT_PROMPT = "[bold bright_cyan]👤 You: [/bold bright_cyan]"

console = Console()
client = None

# Configuració des del fitxer .env
MODEL = os.getenv("MODEL", "gpt-4.1-mini")
OPENAI_ENDPOINT = os.getenv("OPENAI_ENDPOINT")  # Opcional: alternativa compatible amb OpenAI i endpoint.
KNOWLEDGE_FILE = os.getenv("KNOWLEDGE_FILE", "knowledge.txt")

MODE_USER_AUGMENT = "user-augment"
MODE_SYSTEM_GROUNDING = "system-grounding"
RAG_MODE = os.getenv("RAG_MODE", MODE_USER_AUGMENT)

# Instruccions sobre la connexió a terra: resposta basada en el context, i reconèixer que la resposta no està disponible.
SYSTEM_PROMPT_BASE = "Answer using only the context provided. If the answer is not in the context, say you don't know."

# El model RAG prompt – la forma que els estudiants utilitzen durant tota la setmana.
PROMPT_TEMPLATE = "Context:\n----\n{context}\n----\n\nQuestion: {question}"

# Accepta arguments de tipus flexible. Els dos noms estàndard es presenten amb guions.
# ("usuari-augment", "sistema-fundament"), però per a la càmera (i per als estudiants), és
# és fàcil escriure un espai en lloc de la hiat, o corregir automàticament la hiat per a una altra cosa.
# Mostra's tots aquests elements – així com els seus alias més curts – en el mode estàndard.
_MODE_ALIASES = {
    "user-augment": MODE_USER_AUGMENT, "user": MODE_USER_AUGMENT,
    "augment": MODE_USER_AUGMENT, "ua": MODE_USER_AUGMENT,
    "system-grounding": MODE_SYSTEM_GROUNDING, "system": MODE_SYSTEM_GROUNDING,
    "grounding": MODE_SYSTEM_GROUNDING, "sg": MODE_SYSTEM_GROUNDING,
}


def _resolve_mode(raw: str, current: str):
    """Assignar un argument de tipus flexible (`/mode`) a un mode estàndard.

    Argument buit → canviar al mode contrari. Els espais, els guions i qualsevol variant de guió es normalitzen a un sol guió, per tant, "system grounding", "system_grounding" i "system–grounding" es resolen tots. Retorna None si l'argument no està buit i encara no és reconegut.
    """
    s = raw.strip().lower()
    for dash in ("–", "—", "−", "_"):  # – — − → guió
        s = s.replace(dash, "-")
    s = "-".join(s.split())  # Eliminar espais en blanc i combinar-los amb un guió sol.
    if not s:
        return MODE_SYSTEM_GROUNDING if current == MODE_USER_AUGMENT else MODE_USER_AUGMENT
    return _MODE_ALIASES.get(s)


# =============================================================================================================== #
# Recuperació – l'únic element que canvia entre el mode de fila única RAG i embeddings RAG. #
# =============================================================================================================== #

class WholeFileRetriever:
    """En línia única RAG: Ignorar la pregunta i retornar tot el fitxer. Jugant a solitari de manera deshonesta.

    No chunking, no embeddings, sense de "vector store". L'etapa de "recuperació" és `open().read()`. Posteriorment, en el curs, es substitueix per un "EmbeddingsRetriever" que retorna només els k elements més propers chunks — i res més. Aquest és el punt clau.
    """

    def __init__(self, path: str):
        self.path = path
        with open(path, encoding="utf-8") as f:
            self.text = f.read()

    def retrieve(self, question: str) -> str:
        return self.text  # tot el fitxer – la pregunta es ignora deliberadament

    def describe(self) -> str:
        return f"WholeFileRetriever · {os.path.basename(self.path)} · whole file"


# =============================================================================================================== #
# Les dues capes que són importants – i el límit entre elles. #
# =============================================================================================================== #

class AssistantEndpoint:
    """Un punt final "STATELESS RAG" – amb la mateixa estructura que servir un assistent a través d'una API compatible amb OpenAI (això és el que fa LAMB).

    No manté cap estat de conversa. En cada trucada, rep la història bàsica + el darrer missatge de l'usuari provinent de la interfície, busca la seva configuració (system prompt, prompt plantilla, RAG font — aquí fixada en la construcció, en producció identificada per ID del model), i construeix la real trucada LLM des del principi:

        augmentació per a l'usuari → [sistema] + historial + [usuari: plantilla (recuperar missatge, missatge)] fonamentació del sistema → [sistema + fitxer] + historial + [usuari: missatge] (sense cap addicional; el fitxer està al sistema)

    La augmentació que es crea no es retorna ni s'emmagatzema mai. La següent crida la crea de nou.
    """

    def __init__(self, retriever: WholeFileRetriever, mode: str):
        self.retriever = retriever
        self.mode = mode
        if mode == MODE_SYSTEM_GROUNDING:
            # Obtenir una vegada, durant la configuració: el fitxer esdevé part de la system prompt de l'assistent.
            grounding = retriever.retrieve("")  # arxiu complet; consulta ignorada
            self.system_prompt = (
                SYSTEM_PROMPT_BASE
                + "\n\nContext:\n----\n" + grounding + "\n----"
            )
            self.retrieved_at_setup = True
        else:
            self.system_prompt = SYSTEM_PROMPT_BASE
            self.retrieved_at_setup = False

    def build(self, history: list, user_message: str) -> dict:
        """Crea la crida LLM a partir de l'històric i del més recent missatge de l'usuari.

        Retorna un diccionari que descriu la construcció, de manera que l'explorador pugui mostrar el límit: missatges — la llista real enviada al model lingüístic index augmentat — índex del missatge que ha estat augmentat (o None) recuperació — quin tipus de recuperació s'ha fet en aquest pas (string), o None
        """
        messages = [{"role": "system", "content": self.system_prompt}]
        messages += history  # passava directament des de la interfície d'usuari – encara estava buit

        if self.mode == MODE_SYSTEM_GROUNDING:
            # El fitxer ja existeix al system prompt. El torn de l'usuari és buit. No hi ha cap acció per recuperar-lo.
            messages.append({"role": "user", "content": user_message})
            return {"messages": messages, "augmented_index": None,
                    "retrieval": "none this turn — the file is in the system prompt (retrieved once, at setup)"}

        # augmentació d'usuari: recollir el fitxer i injectar-lo en aquest missatge de l'usuari.
        context = self.retriever.retrieve(user_message)
        built = PROMPT_TEMPLATE.format(context=context, question=user_message)
        messages.append({"role": "user", "content": built})
        return {"messages": messages, "augmented_index": len(messages) - 1,
                "retrieval": f"retrieved {len(context)} chars (~{_approx_tokens(context)} tokens) and injected into THIS user message"}

    def complete(self, history: list, user_message: str) -> dict:
        """Construir → fer una crida a LLM → rebre la resposta. El endpoint no emmagatzema res."""
        build = self.build(history, user_message)
        with wait_spinner():
            response = client.chat.completions.create(
                model=MODEL, messages=build["messages"], temperature=0.7
            )
        build["response"] = response
        return build


class ChatUI:
    """La interfície de la conversa. Conté la conversa que l'USUARI veu – només els canvis directes. Sense missatge del sistema, sense addicions: aquests es gestionen des del punt final."""

    def __init__(self, stateful_augment: bool = False):
        self.history = []
        # Si és cert, l'interfície d'usuari emmagatzema el missatge augmentat en comptes del missatge original.
        # l'alternativa "fer que la conversa sigui persistent". Desactivada per defecte (el model realista).
        self.stateful_augment = stateful_augment

    def outgoing(self, user_message: str) -> list:
        """El que l'interfície d'usuari envia a endpoint: el seu historial + el nou missatge (tot sense format)."""
        return self.history + [{"role": "user", "content": user_message}]

    def record(self, user_message: str, assistant_message: str, augmented_user: str = None):
        stored_user = augmented_user if (self.stateful_augment and augmented_user) else user_message
        self.history.append({"role": "user", "content": stored_user})
        self.history.append({"role": "assistant", "content": assistant_message})


# =============================================================================================================== #
# Panells
# =============================================================================================================== #

def _approx_tokens(text: str) -> int:
    """Estimació aproximada abans de rebre les respostes (API) (aproximadament 4 caràcters per token). El nombre real és l'ús dels tokens proporcionats a la consulta."""
    return max(1, len(text) // 4)


def _truncate(text: str, width: int = 88) -> str:
    one_line = text.replace("\n", " ")
    if len(one_line) <= width:
        return one_line
    return one_line[:width] + f"… [+{len(one_line) - width} chars]"


def show_flow(mode: str, stateful: bool) -> Panel:
    """El diagrama de límits de tres capes – que es mostra al principi i en la configuració/estat del commutador."""
    aug = "store AUGMENTED history (stateful)" if stateful else "augmentation NOT saved (stateless)"
    body = Text()
    body.append("🖥️  CHAT UI", style=f"bold {ROLE}")
    body.append("        sends:  history (bare) + your latest message\n", style=TEXT)
    body.append("                       │  history = what you see; no system, no augmentation\n", style=TEXT_DIM)
    body.append("                       ▼\n", style=TEXT_DIM)
    body.append("🛠️  ASSISTANT ENDPOINT", style=f"bold bright_yellow {ON_BG}")
    body.append(f"  (STATELESS; mode = {mode})\n", style=TEXT)
    if mode == MODE_SYSTEM_GROUNDING:
        builds = "        builds:  [system ＋ FILE] + [history] + [user: your message — bare]\n"
    else:
        builds = "        builds:  [system] + [history] + [user: template(FILE, your message)]\n"
    body.append(builds, style=TEXT)
    body.append("                       │  rebuilt every call — no state to keep it in\n", style=TEXT_DIM)
    body.append("                       ▼\n", style=TEXT_DIM)
    body.append("🧠  LLM", style=f"bold bright_green {ON_BG}")
    body.append("            returns:  the response only\n", style=TEXT)
    body.append("                       ▲\n", style=TEXT_DIM)
    body.append("🖥️  CHAT UI", style=f"bold {ROLE}")
    body.append(f"        appends (your message, response) → history   ✗ {aug}", style=TEXT)
    return Panel(body, title="🔁 The three layers", border_style="bright_magenta", style=ON_BG, padding=(1, 2))


def show_ui_send(outgoing: list) -> Panel:
    """Què envia la interfície de chat a endpoint: historial pur més el nou missatge."""
    table = Table(box=box.SIMPLE, show_header=True, header_style=f"bold {TEXT}", style=ON_BG)
    table.add_column("#", style=f"bright_cyan {ON_BG}", width=3)
    table.add_column("Role", style=ROLE, width=10)
    table.add_column("Content (bare — no system, no augmentation)", style=TEXT)
    for i, m in enumerate(outgoing):
        table.add_row(str(i), m["role"], _truncate(m["content"]))
    return Panel(table, title="🖥️ → 🛠️  Chat UI sends to the endpoint", border_style=BORDER, style=ON_BG, padding=(0, 1))


def show_endpoint_build(build: dict, mode: str) -> Panel:
    """El punt final sense estat crea per al model de llenguatge: sistema + historial + contingut de l'usuari d'aquesta ronda."""
    messages = build["messages"]
    aug_idx = build["augmented_index"]
    table = Table(box=box.SIMPLE, show_header=True, header_style=f"bold {TEXT}", style=ON_BG)
    table.add_column("#", style=f"bright_cyan {ON_BG}", width=3)
    table.add_column("Role", style=f"bright_magenta {ON_BG}", width=10)
    table.add_column("Source / lifetime", style=f"bright_yellow {ON_BG}", width=26)
    table.add_column("Content", style=TEXT)
    last = len(messages) - 1
    grounded = mode == MODE_SYSTEM_GROUNDING
    for i, m in enumerate(messages):
        if m["role"] == "system":
            # En el context del sistema, aquest fitxer es troba dins d'aquest missatge del sistema – marcat-lo.
            src = "config ＋ FILE · static" if grounded else "assistant config · static"
        elif i == aug_idx:
            src = "★ built here · discarded"
        elif i == last:
            src = "from UI (bare) · this turn"
        else:
            src = "from UI · passed through"
        table.add_row(str(i), m["role"], src, _truncate(m["content"]))
    note = Text(f"\nretrieval: {build['retrieval']}", style=f"bright_yellow {ON_BG}")
    grid = Table.grid()
    grid.add_row(table)
    grid.add_row(note)
    if aug_idx is not None:
        grid.add_row(Text("★ the augmented message is built fresh now and thrown away — it never returns to the UI",
                          style=f"bold {ALERT}"))
    return Panel(grid, title="🛠️ → 🧠  Endpoint builds the LLM call (stateless)", border_style="yellow", style=ON_BG, padding=(0, 1))


def show_api_request(messages: list) -> Panel:
    json_str = json.dumps({"model": MODEL, "messages": messages, "temperature": 0.7}, indent=2, ensure_ascii=False)
    syntax = Syntax(json_str, "json", theme="monocai", background_color=BG, word_wrap=True)
    return Panel(syntax, title="📤 The actual request to the LLM", border_style="yellow", style=ON_BG, padding=(0, 1))


def show_api_response(response_data: dict) -> Panel:
    json_str = json.dumps(response_data, indent=2, ensure_ascii=False)
    syntax = Syntax(json_str, "json", theme="monocai", background_color=BG, word_wrap=True)
    return Panel(syntax, title="📥 LLM response", border_style="bright_cyan", style=ON_BG, padding=(0, 1))


def show_ui_history(history: list, stateful: bool) -> Panel:
    """Què manté la interfície de chat després d'una interacció – què veu l'usuari / què es guarda."""
    table = Table(box=box.SIMPLE, show_header=True, header_style=f"bold {TEXT}", style=ON_BG)
    table.add_column("#", style=f"bright_cyan {ON_BG}", width=3)
    table.add_column("Role", style=ROLE, width=10)
    table.add_column("Content", style=TEXT)
    for i, m in enumerate(history):
        table.add_row(str(i), m["role"], _truncate(m["content"]))
    if stateful:
        cap = "STATEFUL: augmented user turns ARE stored — the file now rides in history too"
        style = f"bold {ALERT}"
    else:
        cap = "no system prompt · no augmentation · just the turns the user saw"
        style = TEXT_DIM
    grid = Table.grid()
    grid.add_row(table)
    grid.add_row(Text(cap, style=style))
    return Panel(grid, title="🖥️  Chat UI history (what the user sees / what is stored)", border_style=BORDER, style=ON_BG, padding=(0, 1))


def show_cost(history_tokens: list) -> Panel:
    table = Table(box=box.SIMPLE, show_header=True, header_style=f"bold {TEXT}", style=ON_BG)
    table.add_column("Turn", style=f"bright_cyan {ON_BG}", width=5)
    table.add_column("prompt_tokens", style=f"bright_yellow {ON_BG}", width=14)
    table.add_column("cached", style=f"bright_green {ON_BG}", width=8)
    table.add_column("", style=COST)
    peak = max((t[0] for t in history_tokens), default=1) or 1
    for i, (pt, cached) in enumerate(history_tokens, start=1):
        bar = "█" * max(1, int(26 * pt / peak))
        table.add_row(str(i), str(pt), ("—" if cached is None else str(cached)), bar)
    return Panel(table, title="💸 Token cost per turn (prompt_tokens · cached)", border_style=BORDER_ALERT, style=ON_BG, padding=(0, 1))


def show_message(role: str, content: str) -> Panel:
    styles = {
        "user": ("bright_white on dodger_blue1", BORDER, "👤 You"),
        "assistant": ("bright_white on dark_green", "green", "🤖 Assistant"),
    }
    text_style, border, title = styles.get(role, (TEXT, "white", role))
    return Panel(Text(content, style=text_style), title=title, border_style=border, padding=(0, 1))


def wait_spinner():
    return Live(
        Panel(Spinner("dots", text=Text("Esperant per a LLM.", style="negre gros sobre fons groc")),
              border_style="groc", style="en groc", padding=(0, 1)),
        console=console, refresh_per_second=10
    )


def show_setup(retriever: "WholeFileRetriever", mode: str) -> Panel:
    """Mostrar la configuració de l'assistent abans de enviar qualsevol missatge: el system prompt, la plantilla prompt i el fitxer de coneixement – així com on es guarda aquest fitxer en aquest mode."""
    file_text = retriever.text
    if len(file_text) > 1500:
        file_text = file_text[:1500] + f"\n… [+{len(retriever.text) - 1500} more chars]"

    sg = mode == MODE_SYSTEM_GROUNDING

    g = Table.grid(padding=(0, 0))

    # ① SYSTEM PROMPT — En el procés de "arrelament" del sistema, el fitxer es concatena DINS ell.
    g.add_row(Text("① SYSTEM PROMPT", style=f"bold bright_magenta {ON_BG}"))
    g.add_row(Text(SYSTEM_PROMPT_BASE, style=TEXT))
    if sg:
        g.add_row(Text("        ＋ knowledge file ③ concatenated here — retrieved ONCE, at setup",
                       style=f"bold bright_green {ON_BG}"))
        g.add_row(Text("   ↳ in system-grounding the file IS part of the system prompt; the template below is dead",
                       style=TEXT_DIM))
    else:
        g.add_row(Text("   ↳ user-augment: just the instruction — the file is NOT here; it rides in each user "
                       "message via the template ↓", style=TEXT_DIM))
    g.add_row(Text("", style=ON_BG))

    # ② PROMPT PLANTLLA – activa en la funcionalitat d'augment de l'usuari, però inactiva en la funció de referència al sistema.
    if sg:
        g.add_row(Text("② PROMPT TEMPLATE   ⛔ NOT USED IN THIS MODE", style=f"bold bright_red {ON_BG}"))
        g.add_row(Text(PROMPT_TEMPLATE, style=TEXT_DIM))
        g.add_row(Text("   ↳ inactive — your message is sent bare; the file already lives in the system prompt above",
                       style=TEXT_DIM))
    else:
        g.add_row(Text("② PROMPT TEMPLATE   ✅ USED EVERY TURN", style=f"bold bright_yellow {ON_BG}"))
        g.add_row(Text(PROMPT_TEMPLATE, style=TEXT))
        g.add_row(Text("   ↳ rebuilt every turn — the file goes into {context}, your message into {question}",
                       style=TEXT_DIM))
    g.add_row(Text("", style=ON_BG))

    # ③ ARXIU DE CONEIXEMENT – i com es distribueix aquesta informació en aquest mode.
    where = "the SYSTEM PROMPT ① (once, at setup)" if sg else "the PROMPT TEMPLATE ② {context} (every turn)"
    g.add_row(Text(f"③ KNOWLEDGE FILE · {os.path.basename(retriever.path)} "
                   f"({len(retriever.text)} chars, ~{_approx_tokens(retriever.text)} tokens)   "
                   f"→  goes into {where}", style=f"bold bright_green {ON_BG}"))
    g.add_row(Text(file_text, style=TEXT_DIM))
    return Panel(g, title=f"🧩 Assistant setup — mode = {mode}",
                 border_style="cian brillant", style=ON_BG, padding=(1, 2))


# =============================================================================================================== #
# Cicle de conversa
# =============================================================================================================== #

def run_chat(retriever: WholeFileRetriever, mode: str):
    ui = ChatUI(stateful_augment=False)
    endpoint = AssistantEndpoint(retriever, mode)
    token_history = []

    console.print()
    console.print(Panel(
        Text("Ask about the knowledge file. Each turn shows the gap between what the\n"
             "CHAT UI keeps (bare turns) and what the stateless ENDPOINT builds for the LLM.\n\n"
             "/mode [user-augment | system-grounding]  (no arg = toggle)   ·   /stateful   ·   /file <path>   ·   /context   ·   (empty = quit)",
             style=TEXT),
        title="📚 Context Explorer — single-file RAG", border_style="bright_magenta", style=ON_BG, padding=(1, 2)))
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
            console.print(Panel(Text(f"stateful_augment = {ui.stateful_augment} · conversation reset.",
                                     style=TEXT), border_style="verd", style=ON_BG))
            console.print(show_flow(mode, ui.stateful_augment))
            continue
        if cmd == "/mode" or cmd.startswith("/mode "):
            new_mode = _resolve_mode(cmd[len("/mode"):], mode)
            if new_mode is None:
                console.print(Panel(Text(f"unknown mode. Use: {MODE_USER_AUGMENT} | {MODE_SYSTEM_GROUNDING} "
                                         f"(or just /mode to toggle).",
                                         style="negre i brillant, blanc sobre vermell fosc"), border_style="vermell", style="en vermell fosc"))
                continue
            if new_mode == mode:
                console.print(Panel(Text(f"already in mode = {mode}.", style=TEXT),
                                    border_style="verd", style=ON_BG))
                continue
            mode = new_mode
            endpoint = AssistantEndpoint(retriever, mode)
            ui.history = []
            token_history = []
            console.print(Panel(Text(f"mode = {mode} · conversation reset.", style=TEXT),
                                border_style="verd", style=ON_BG))
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
                console.print(Panel(Text(f"Loaded {new_path} ({len(retriever.text)} chars) · conversation reset.",
                                         style=TEXT), border_style="verd", style=ON_BG))
                console.print()
                console.print(show_setup(retriever, mode))
            except OSError as exc:
                console.print(Panel(Text(f"Could not load {new_path}: {exc}", style="negre i brillant, blanc sobre vermell fosc"),
                                    border_style="vermell", style="en vermell fosc"))
            continue

        # 1) L'interfície d'usuari envia la seva història bàsica juntament amb el nou missatge al endpoint.
        outgoing = ui.outgoing(user_input)
        console.print()
        console.print(show_message("user", user_input))
        console.print()
        console.print(show_ui_send(outgoing))

        # 2) El mòdul sense estat endpoint crea la crida real LLM i l'executa.
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

        # 3) La resposta torna a la interfície d'usuari; només es guarden les parts essencials de la petició i la resposta.
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
        console.print(Panel(Text("La clau API d'OPENAI no s'ha trobat!\\n\\nCòpia el fitxer .env.example al fitxer .env i omple les dades necessàries.",
                                 style="negre i brillant, blanc sobre vermell fosc"), title="❌ Error", border_style="red", style="on dark_red"))
        return

    if RAG_MODE not in (MODE_USER_AUGMENT, MODE_SYSTEM_GROUNDING):
        console.print(Panel(Text(f"Unknown RAG_MODE '{RAG_MODE}'. Use {MODE_USER_AUGMENT} or {MODE_SYSTEM_GROUNDING}.",
                                 style="negre i brillant, blanc sobre vermell fosc"), title="❌ Error", border_style="red", style="on dark_red"))
        return

    knowledge_path = KNOWLEDGE_FILE
    if not os.path.isabs(knowledge_path):
        knowledge_path = os.path.join(os.path.dirname(__file__), knowledge_path)
    try:
        retriever = WholeFileRetriever(knowledge_path)
    except OSError as exc:
        console.print(Panel(Text(f"Could not load knowledge file '{knowledge_path}':\n{exc}",
                                 style="negre i brillant, blanc sobre vermell fosc"), title="❌ Error", border_style="red", style="on dark_red"))
        return

    client = OpenAI(api_key=api_key, base_url=OPENAI_ENDPOINT) if OPENAI_ENDPOINT else OpenAI(api_key=api_key)

    console.print(Panel(
        Text(f"Model     : {MODEL}\n"
             f"Endpoint  : {OPENAI_ENDPOINT or 'https://api.openai.com/v1'}\n"
             f"Knowledge : {os.path.basename(knowledge_path)} ({len(retriever.text)} chars, ~{_approx_tokens(retriever.text)} tokens)\n"
             f"Mode      : {RAG_MODE}",
             style=TEXT),
        title="⚙️ Configuration", border_style="bright_cyan", style=ON_BG))

    run_chat(retriever, RAG_MODE)


if __name__ == "__main__":
    main()
