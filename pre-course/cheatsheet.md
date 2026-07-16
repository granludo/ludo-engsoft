# Guia ràpida del curs — terminal · Git · Python · el model

Una pàgina per mantenir oberta durant la primera setmana. No cal que recordeu cap d'aquests elements; és important que els **identifiqueu** quan un agent els faci, i que siguin capaces de fer-los ells mateixos quan sigui necessari. Imprimeu en PDF amb `/md2pdf` per a distribució.

---

## El terminal

| Comanda; ordre | El que fa |
|---|---|
| `ls` | llista què hi ha a la carpeta actual (`ls -la` = tot, amb detalls) |
| `cd foo` | entrar a la carpeta `foo` · `cd ..` = arriba · `cd ~` = inici · `cd -` = retrocés |
| `pwd` | imprimeu on esteu |
| `cat file` | imprimir un fitxer a la pantalla |
| `less file` | navega per un fitxer llarg (`q` per sortir) |
| `nano file` | editar un fitxer (`Ctrl-O` guardar, `Ctrl-X` sortir) |
| `mkdir foo` | crear una carpeta · `rm file` eliminar · `rm -r foo` eliminar una carpeta (amb precaució) |
| `cp a b` / `mv a b` | copiar / moure (o canviar el nom) |
| `head -n 20 file` / `tail` | primeres/últimes 20 línies |
| `grep "text" file` | Trobar línies que contenen `text` |

**Els tres canals** que té cada programa – semblen igual a la pantalla, però no són el mateix:

| Flux | El que transporta |
|---|---|
| **entrada estàndard** | els dades que el programa rep com a entrada |
| Sortida estàndard | la sortida normal del programa |
| **sortida d'error** | Missatges d'error – un canal *separat* de la sortida estàndard (stdout) |

**Reenviar i canonades:** Veureu els agents utilitzar-les constantment:

| Símbol | Significat |
|---|---|
| `cmd > file` | enviar la sortida estàndard **a un fitxer** (escriure sobre el contingut existent) |
| `cmd >> file` | afegir la sortida estàndard a un fitxer |
| `cmd 2> errs.txt` | envia **stderr** a un fitxer (el `2` és el número de stderr) |
| `cmd1 \| cmd2` | redirigir la sortida estàndard (stdout) del comanda "cmd1" a l'entrada estàndard (stdin) del comanda "cmd2" |

---

## «git» – els cinc verbs que cobreixen el 90%

| Comanda; ordre | El que fa |
|---|---|
| `git clone <url>` | clonar un repositori remot al teu ordinador |
| `git status` | Què ha canviat/què està passant actualment |
| `git add <file>` (or `git add .`) | Canvis de fase per al proper commit |
| `git commit -m "message"` | guarda una captura amb un missatge |
| `git push` | envia les teves modificacions fins a GitHub |
| `git pull` | restablir allò que altres (o vostè, en un altre lloc) han destruït |
| `git log --oneline` | història, una línia per cada commit |

**Ramificació** – prova noves idees sense arriscar allò que ja funciona:

| Comanda; ordre | El que fa |
|---|---|
| `git branch` | llistar ramals · `git branch foo` crear un nou |
| `git checkout foo` | canvia a la branca `foo` (`git checkout -b foo` = crear + canviar) |
| `git checkout -- file` | eliminar les modificacions no confirmades a `file` |

**Configuració inicial de Git** (una sola vegada, per sempre):
```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
git config --global init.defaultBranch main
```

---

## Python amb `uv`

`uv` executa Python i gestiona les dependències, per tant, els scripts "simplement es poden executar".

| Comanda; ordre | El que fa |
|---|---|
| `python3 --version` | comproveu la vostra versió de Python (volem una versió igual o superior a 3.11) |
| `uv run script.py` | executar un script en un entorn gestionat |
| `uv run --with openai --with chromadb python script.py` | Executa amb paquets addicionals, sense instal·lació manual. |
| `uv venv && source .venv/bin/activate` | crear i entrar en un entorn virtual (de forma manual) |
| `uv sync` | Instal·lar tot el que un projecte declara amb la etiqueta `pyproject.toml`. |

---

## El model al vostre ordinador — Ollama

| Comanda; ordre | El que fa |
|---|---|
| `ollama serve` | iniciar el servidor local del model (normalment ja en funcionament com a aplicació) |
| `ollama pull qwen3:1.7b` | Descarrega un petit model (aproximadament 1,5 GB – funciona amb gairebé qualsevol dispositiu) |
| `ollama run qwen3:1.7b "say hi"` | Una conversa ràpida a través del terminal |
| `ollama list` | els fitxers que teniu descarregats |

El curs explica com fer servir Ollama mitjançant l'endpoint compatible amb **OpenAI** a `http://localhost:11434/v1` – sense clau API, sense diners ni connexió a internet. El mateix codi pot accedir a un model en la nuvem simplement canviant una línia de configuració. (Això és una lliçó, no una solució ràpida – vegeu la setmana 2.)

## L'agent de codificació — OpenCode

Instal·leu-lo ara (vegeu la guia d'instal·lació); començarem a utilitzar-lo correctament a partir de la segona setmana.

| Comanda; ordre | El que fa |
|---|---|
| `opencode` | Comenceu-ho en el directori actual. |
| `opencode --version` | confirmeu que està instal·lat |

---

## "Estic preparat?", – la prova amb fum

Realitzeu aquestes activitats. Si totes les cinc es completen correctament, estareu preparats per al primer dia:

```bash
python3 --version          # 3.11 or higher
uv --version               # any version
git --version              # any version
ollama run qwen3:1.7b "reply with exactly one short sentence"
opencode --version         # any version
```

Si hi ha algun error, consulteu el missatge a **stderr**, reviseu la guia d'instal·lació, i si encara teniu problemes – **envieu-nos un correu abans que comenci el curs.**

---

## On aprendre més (opcional, si la secció era nova)

- **Terminal:** *El semestre perdut de la vostra formació en informàtica* (MIT) — `missing.csail.mit.edu` — les classes sobre l'entorn i les eines són exactament a aquest pis.
- **git:** el llibre *Pro Git* (gratís) — `git-scm.com/book` — Llegiu els capítols 1-3. O `learngitbranching.js.org` per a una visió pràctica i visual dels braços.
- **Python (revisió):** el tutorial oficial — `docs.python.org/3/tutorial`.
- **`uv`:** `docs.astral.sh/uv`.
- **Ollama:** `ollama.com` → la biblioteca del model + el fitxer README.
