# Preparar la vostra màquina – configuració de l'entorn

Aquesta guia et prepara el teu ordinador per al curs. Fes-ho la setmana abans de començar, perquè si hi ha algun problema, tinguis temps de sol·licitar ajuda. Assegura't d'assignar uns **30–40 minuts** — la major part del temps serà per esperar que s'inicien les baixades. Al final, hi ha una **prova de comprovació**: cinc comandes que, si funcionen totes, signifiquen que estàs preparat. Si alguna cosa falla, llegeix el missatge d'error i **envia-nos un correu electrònic abans del primer dia** — una setmana de preparació només és útil si la utilitzes.

No cal que entengueu tots els detalls avui. Necessiteu les eines instal·lades i que la prova de funcionament sigui reeixida. Si apareix alguna paraula o idea nova, pregunteu a ChatGPT, Claude o al vostre agent de programació per explicar-la – aquesta pràctica *és* part del curs.

## Primer: què és "la terminal" i per què aquest curs es desenvolupa allà?

La **terminal** (també coneguda com la *línia de comandament* o el *shell*) és una finestra de text on escriviu ordres al vostre ordinador en lloc d'utilitzar botons. Si esteu acostumats a aplicacions gràfiques i ordinadors portàtils, pot semblar un pas enrere. No ho és. És allà on es realitza el treball del programari — i, sobretot per a nosaltres, **és allà on funcionen els agents d'IA per escriure codi.** Un agent crea el vostre programa executant ordres a la terminal; la vostra tasca és llegir què ha fet, detectar errors i guiar-lo. Si no podeu llegir la terminal, no podeu supervisar un agent — i supervisar l'agent és l'habilitat principal que ensenya aquest curs.

No cal ser un expert en terminals. Necessiteu una sèrie de comandes i la capacitat de llegir les sortides. La fitxa d'ajuda **"[cheatsheet]"** (`cheatsheet.md`) enumera totes les comandes que necessitareu; mantingueu-la oberta durant la primera setmana. Si voleu una base sòlida i amigable, la sèrie de conferències de MIT *El semestre perdut de la vostra formació en informàtica* és el millor recurs gratuït: <https://missing.csail.mit.edu>.

## Les eines que instal·laràs, i el propòsit de cada una.

Instal·laràs cinc coses. Aquí teniu què són i per què són importants – les instruccions d'instal·lació per al teu sistema operatiu vindran després.

- **Python 3.11+** — el llenguatge de programació en què estan escrits els exemples del curs. Llegiràreu molta Python i la modifiqueu, però rarament l'escriureu des del principi. La versió 3.11 o posterior és important perquè alguns dels biblioteques que utilitzem les requereixen. Més informació / repàs: <https://docs.python.org/3/tutorial/>.

- **`uv`** — una eina que executa programes en Python i gestiona les seves dependències (les biblioteques addicionals que necessita un programa). Sense aquesta eina, el problema de "funciona al meu ordinador, però no al vostre" és constant, ja que cada persona té instal·lades diferents biblioteques. `uv` permet que un programa porti les seves pròpies dependències, per la qual cosa simplement s'executa. Un sol comandament (`uv run …`) i ja no hi penseu més. Més informació: <https://docs.astral.sh/uv/>.

- **git** — el sistema de control de versions que registra la història del vostre codi i us permet compartir-lo. En aquest curs, els vostres resultats *s'emmagatzemen en un repositori git*: creeu alguna cosa, la `commit` (guarden una còpia), i la `push` a GitHub perquè puguem veure-la. L'agent d'IA sovint farà el commit per vosaltres — que és exactament per què heu de comprendre bé git per poder veure què ha fet i revertir-ho quan faci alguna cosa incorrecta. Nou en git? Llegiu els capítols 1–3 del llibre *Pro Git* (gratís) (<https://git-scm.com/book>), o feu servir el tutorial visual a <https://learngitbranching.js.org>.

- **Ollama** + un model petit — Ollama executa un model de llenguatge **en el vostre propi ordinador**, sense necessitat d'una clau API, sense cost i sense necessitat d'internet després del primer descàrrega. L'utilitzem per a les *experiments* del curs, de manera que podeu fer-ho lliurement sense haver de pagar. El model petit que utilitzem per defecte (`qwen3:1.7b`) té uns 1,5 GB i funciona en gairebé qualsevol ordinador portàtil. Més informació i altres models: <https://ollama.com>.

- **OpenCode** – l'agent d'IA per a la programació que utilitzareu des de la segona setmana per construir el vostre programa. **Important:** un agent de programació només és tan bo com el model que hi ha darrere, i un model local *molt petit* no és suficient per utilitzar-lo en projectes reals. Per tant, OpenCode necessita un model *capaç*: un punt final sòlid que el curs ofereix (si n'hi ha), o una subscripció a un agent de programació capaç (Qwen, DeepSeek, Pi, MiniMax; Claude si voleu ser seriosos). Mantingueu el petit model local d'Ollama per a les *experiments*; utilitzeu el model capaç per *utilitzar l'agent*. (Expliquem aquesta divisió en dos models de nou a la segona setmana – al principi confon a tothom, així que no us preocupeu si encara no és clar.) Més informació: <https://opencode.ai>.

Ara, seguiu la secció corresponent al vostre sistema d'operació.

---

## macOS

macOS inclou un terminal (obriu **Terminal.app**, o instal·leu **iTerm2** si preferiu). Instal·lem tot amb **Homebrew**, el gestor de paquets estàndard per a macOS – és l'eina que descarrega i instala el software de desenvolupament per a vosaltres. Si encara no teniu-ho, podeu instal·lar-lo amb aquesta única línia (explicarà què fa i us demanarà la vostra contrasenya):

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

(Més informació sobre "Homebrew": <https://brew.sh>). Després, instal·leu les eines:

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

Després d'instal·lar, **obriu una nova finestra de terminal** perquè es trobin `uv` i `opencode` (els instal·ladors els afegeixen a la vostra `PATH`, que és la llista de llocs on el vostre terminal busca comandes, i això només funciona en una finestra nova).

---

## Linux (Ubuntu / Debian)

Ja teniu un terminal real. Instaleu els elements bàsics del sistema amb `apt` (el gestor de paquets d'Ubuntu), i després el que queda:

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

Després, obriu un nou terminal (o executeu `source ~/.bashrc`), perquè les noves eines estiguin disponibles al vostre `PATH`.

---

## Sistema operatiu – necessiteu un terminal d'Unix real (PowerShell no és suficient).

Aquest curs es realitza en un terminal de **Unix** (el tipus que tenen macOS i Linux). El **PowerShell** integrat de Windows és un sistema diferent — moltes de les nostres comandes i eines no funcionen allà, i intentar solucionar aquesta diferència durant tot el curs no val la pena. Per tant, a Windows es pot executar una petita versió de Linux *dins* de Windows. La manera fàcil i recomanada és **WSL2** (el subsistema de Linux per a Windows) — que us ofereix un terminal d'Ubuntu autèntic que funciona exactament com la secció de Linux anterior, sense necessitat de gestionar una màquina virtual separada.

1. Obre **PowerShell com a administrador** (fes clic dret i selecciona "Executar amb privilegis d'administrador") i executa:
   ```powershell
   wsl --install
   ```
Reinicia quan ho demani. Per defecte, s'instal·larà Ubuntu. (La guia oficial de Microsoft, si voleu més detalls: <https://learn.microsoft.com/windows/wsl/install>).
2. Des del menú d'inici, obriu **Ubuntu**. La primera vegada, us demanarà crear un nom d'usuari i una contrasenya per a Linux – aquests són diferents als que utilitzeu per accedir a Windows.
3. Dins d'aquesta terminal d'Ubuntu, seguiu la secció "**Linux (Ubuntu / Debian)**" que s'ha mencionat anteriorment. Tot funciona de la mateixa manera.

> **No podeu utilitzar WSL2?** (Per defecte del maquinari antic o d'una ordinadora portàtil de la feina amb restriccions que no permeten-ho). No intenteu fer-ho sols — envieu-nos un correu abans de començar el curs i us ajudarem a trobar una configuració funcional.

---

## Fes un "git" de tornada ara (perquè no sigui la primera vegada que ho fas).

Git té un vocabulari petit que utilitzareu constantment. Practicar-lo una vegada, ara, en un repositori temporal, evitarà que sigui desconegut quan depengui del seu ús. Primer, feu saber a Git qui sou – això només es fa una vegada:

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

Després, clona un repositori públic, examina-lo i llegeix el seu historial:

```bash
git clone https://github.com/octocat/Hello-World.git   # copy a repo to your machine
cd Hello-World                                          # go into it
git status                                              # what's changed right now?
git log --oneline                                       # the history, one line per commit
```

Aquest és el ritme que haureu de repetir durant tot el curs: **clonar → modificar → `add` → `commit` → `push`.** Si algun d'aquests termes no us és clar, els capítols de *Pro Git* enllaçats anteriorment expliquen cada un d'ells amb claredat.

---

## Prova de fum: esteu preparat?

Executa aquests cinc comandaments. Cadascun d'ells comprova si una eina està instal·lada i funcionant correctament. Si tots els cinc donen un resultat positiu, estaràs preparat per al primer dia:

```bash
python3 --version    # should print 3.11 or higher
uv --version         # any version
git --version        # any version
ollama run qwen3:1.7b "reply with exactly one short sentence"
opencode --version   # any version
```

El quart comandament és el més interessant: la primera vegada que l'executeu, es carregaran els models necessaris, i després mostrarà una única frase **generada pel vostre propi ordinador** – sense internet, sense compte, sense cost. Quan veieu aquesta frase aparèixer, la part més difícil de la configuració s'ha completat.

**Si qualsevol ordre genera un error:** llegiu el missatge amb atenció (els errors es mostren en un canal separat anomenat `stderr` — vegeu la guia), assegureu-vos que heu obert una nova terminal després de l'instal·lació, i intenteu preguntar a ChatGPT o Claude per obtenir una explicació precisa del text d'error. Si encara no trobeu la solució, **envieu-nos un correu electrònic abans que comenci el curs.**
