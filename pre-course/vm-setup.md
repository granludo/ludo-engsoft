# Prepara la teva màquina — configuració de l'entorn

Aquesta guia deixa el teu ordinador a punt per al curs. Fes-la la setmana abans de començar: així, si alguna cosa surt malament, tindràs temps de demanar ajuda. Compta amb **30–40 minuts**, la major part dels quals només és esperar que acabin les baixades. Al final hi ha una **prova de foc**: cinc ordres que, si funcionen totes, volen dir que ja estàs a punt. Si alguna cosa falla, llegeix el missatge d'error i **escriu-nos abans del primer dia** — una setmana de marge només serveix si l'aprofites.

No cal que ho entenguis tot avui. El que necessites és tenir les eines instal·lades i que la prova de foc passi. Sobre la marxa, si et trobes una paraula o una idea nova, demana a ChatGPT, Claude o al teu agent de programació que te l'expliqui — aquest hàbit *forma part* del curs.

## Primer: què és «la terminal» i per què aquest curs hi transcorre?

La **terminal** (també anomenada *shell* o *línia d'ordres*) és una finestra de text on escrius ordres a l'ordinador en comptes de clicar botons. Si has viscut sempre entre aplicacions gràfiques i notebooks, pot semblar un pas enrere. No ho és. És on passa la feina de programari de debò — i, encara més important per a nosaltres, **és on treballen els agents d'IA de programació.** Un agent construeix el teu programari executant ordres a la terminal; la teva feina és llegir què ha fet, detectar-ne els errors i guiar-lo. Si no saps llegir la terminal, no pots supervisar un agent — i supervisar l'agent és tota l'habilitat que ensenya aquest curs.

No cal que siguis un expert en terminals. Només necessites un grapat d'ordres i la confiança per llegir-ne la sortida. La **xuleta** de referència que l'acompanya (`cheatsheet.md`) recull totes les ordres que et faran falta; tingues-la oberta durant la primera setmana. Si vols una base sòlida i amable, la sèrie de classes del MIT *The Missing Semester of Your CS Education* és el millor recurs gratuït: <https://missing.csail.mit.edu>.

## Les eines que instal·laràs i per a què serveix cadascuna

Instal·laràs cinc coses. Aquí t'expliquem què és cadascuna i per què importa; les instruccions d'instal·lació per al teu sistema operatiu venen després.

- **Python 3.11+** — el llenguatge de programació en què estan escrits els exemples del curs. En *llegiràs* molt i n'*editaràs* una mica; rarament n'escriuràs des de zero. La versió 3.11 o superior importa perquè algunes de les biblioteques que fem servir la necessiten. Més informació o repàs: <https://docs.python.org/3/tutorial/>.

- **`uv`** — una eina que executa programes de Python i en gestiona les dependències (les biblioteques addicionals que un programa necessita). Sense ella, el «funciona al meu ordinador però no al teu» és un problema constant, perquè cadascú té instal·lades biblioteques diferents. `uv` fa que un programa porti les seves pròpies dependències, així que simplement s'executa. Una sola ordre (`uv run …`) i ja no t'hi has de tornar a amoïnar. Més informació: <https://docs.astral.sh/uv/>.

- **git** — el sistema de control de versions que registra l'historial del teu codi i et permet compartir-lo. En aquest curs, els teus lliuraments *viuen en un repositori git*: construeixes alguna cosa, en fas un `commit` (en guardes una instantània) i el `push` cap a GitHub perquè el puguem veure. Sovint l'agent d'IA farà els commits per tu — i és justament per això que has d'entendre git prou bé per mirar què ha fet i desfer-ho quan s'equivoqui. No has fet servir mai git? Llegeix els capítols 1–3 del llibre *Pro Git*, gratuït (<https://git-scm.com/book>), o fes el tutorial visual de <https://learngitbranching.js.org>.

- **Ollama** + un model petit — Ollama executa un model de llenguatge **al teu propi ordinador**, sense clau API, sense cost i sense necessitat d'internet un cop feta la primera baixada. El fem servir per als *experiments* del curs, de manera que pots provar coses lliurement sense rebre cap factura. El model petit que fem servir per defecte (`qwen3:1.7b`) ocupa uns 1,5 GB i funciona en gairebé qualsevol portàtil. Més informació i altres models: <https://ollama.com>.

- **OpenCode** — l'agent d'IA de programació que *pilotaràs* a partir de la segona setmana per construir el teu programari. **Important:** un agent de programació és tan bo com el model que té al darrere, i un model local *diminut* **no** és prou bo per pilotar-ne un en feina de debò. Per això OpenCode necessita un model **potent**: un endpoint sòlid que et proporcioni el curs (si en té), o la teva pròpia subscripció a un model agèntic potent (Qwen, DeepSeek, Pi, MiniMax; Claude si t'ho vols prendre seriosament). Reserva el model local petit d'Ollama per als *experiments*; fes servir el model potent per *pilotar l'agent*. (Aquesta divisió en dos models la tornem a explicar a la segona setmana — al principi confon tothom, així que no pateixis si encara no ho tens del tot clar.) Més informació: <https://opencode.ai>.

Ara segueix la secció del **teu** sistema operatiu.

---

## macOS

macOS ja porta una terminal (obre **Terminal.app**, o instal·la **iTerm2** si ho prefereixes). Ho instal·lem tot amb **Homebrew**, el gestor de paquets estàndard de macOS — l'eina que et descarrega i instal·la el programari de desenvolupament. Si encara no el tens, instal·la'l amb aquesta única línia (t'explicarà què fa i et demanarà la contrasenya):

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

(Més sobre Homebrew: <https://brew.sh>.) Després, instal·la les eines:

```bash
# Python, git, and uv
brew install python@3.11 git
curl -LsSf https://astral.sh/uv/install.sh | sh

# Ollama — installs the app; it then runs quietly in your menu bar
brew install ollama
ollama serve &                 # or just launch the Ollama app from Applications
ollama pull qwen3:1.7b         # downloads the small model (~1.5 GB) — be patient

# OpenCode — the coding agent
curl -fsSL https://opencode.ai/install | bash
```

Un cop instal·lat, **obre una finestra de terminal nova** perquè es trobin `uv` i `opencode` (els instal·ladors els afegeixen al teu `PATH`, la llista de llocs on la terminal busca les ordres, i això només té efecte en una finestra nova).

---

## Linux (Ubuntu / Debian)

Ja tens una terminal de debò. Instal·la els elements bàsics del sistema amb `apt` (el gestor de paquets d'Ubuntu) i, després, la resta:

```bash
# System basics
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip git curl wget

# uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen3:1.7b         # the small model (~1.5 GB)

# OpenCode — the coding agent
curl -fsSL https://opencode.ai/install | bash
```

Després, obre una terminal nova (o executa `source ~/.bashrc`) perquè les eines noves quedin al teu `PATH`.

---

## Windows — necessites una terminal Unix de debò (PowerShell no serveix)

Aquest curs funciona en una terminal **Unix** (del tipus que tenen macOS i Linux). El **PowerShell** que ve amb Windows **és un sistema diferent**: moltes de les nostres ordres i eines senzillament no hi funcionen, i barallar-se amb aquesta diferència tot el curs no val la pena. Per això, a Windows executes un petit Linux *dins* de Windows. La manera fàcil i recomanada és **WSL2** (el subsistema de Windows per a Linux): et dona una terminal d'Ubuntu autèntica que es comporta exactament com la de la secció de Linux anterior, sense cap màquina virtual a part per gestionar.

1. Obre el **PowerShell com a administrador** (clic dret → «Executa com a administrador») i executa:
   ```powershell
   wsl --install
   ```
   Reinicia quan t'ho demani. Per defecte instal·la Ubuntu. (Guia oficial de Microsoft, si en vols els detalls: <https://learn.microsoft.com/windows/wsl/install>.)
2. Des del menú d'Inici, obre l'**Ubuntu**. El primer cop et demanarà que creïs un nom d'usuari i una contrasenya de Linux — són independents del teu compte de Windows.
3. Dins d'aquesta terminal d'Ubuntu, segueix la secció **Linux (Ubuntu / Debian)** d'aquí sobre. Tot funciona igual.

> **No pots executar WSL2?** (Maquinari molt antic, o un portàtil de la feina blindat que no ho permet.) No t'hi barallis tot sol — escriu-nos abans que comenci el curs i t'ajudarem a trobar una configuració que funcioni.

---

## Fes un cicle complet de git ara (perquè no et sigui nou el primer dia)

git té un vocabulari reduït que faràs servir constantment. Practicar-lo un cop, ara, en un repositori d'usar i llençar fa que no et resulti estrany quan la nota en depengui. Primer, digues a git qui ets — això només ho fas un cop:

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

Després, clona un repositori públic, mira'n el contingut i llegeix-ne l'historial:

```bash
git clone https://github.com/octocat/Hello-World.git   # copy a repo to your machine
cd Hello-World                                          # go into it
git status                                              # what's changed right now?
git log --oneline                                       # the history, one line per commit
```

Aquest és el ritme que repetiràs tot el curs: **clonar → modificar → `add` → `commit` → `push`.** Si algun d'aquests termes et balla, els capítols de *Pro Git* enllaçats més amunt els expliquen tots amb claredat.

---

## Prova de foc — estàs a punt?

Executa aquestes cinc ordres. Cadascuna comprova que una eina està instal·lada i funciona. Si totes cinc responen sense problemes, estàs llest per al primer dia:

```bash
python3 --version    # should print 3.11 or higher
uv --version         # any version
git --version        # any version
ollama run qwen3:1.7b "reply with exactly one short sentence"
opencode --version   # any version
```

La quarta ordre és la interessant: el primer cop que l'executes, acaba de baixar el model i tot seguit imprimeix una única frase **generada al teu propi ordinador** — sense internet, sense compte, sense cost. Quan vegis aparèixer aquesta frase, la part difícil de la configuració ja està feta.

**Si alguna ordre dona error:** llegeix el missatge amb atenció (els errors s'imprimeixen en un canal a part anomenat `stderr` — consulta la xuleta), assegura't d'haver obert una terminal nova després d'instal·lar i prova de demanar a ChatGPT o Claude que t'expliqui el text exacte de l'error. Si tot i així et quedes encallat, **escriu-nos abans que comenci el curs.**
