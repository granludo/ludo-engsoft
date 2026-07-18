# Guia ràpida del curs — terminal · git · Python · el model

Una pàgina per tenir oberta durant la primera setmana. No cal que memoritzis res d'això: el que has de saber és **reconèixer-ho** quan un agent ho fa i ser capaç de fer-ho tu mateix quan calgui. Genera'n un PDF amb `/md2pdf` per repartir a classe.

---

## El terminal

| Comanda | Què fa |
|---|---|
| `ls` | llista què hi ha a la carpeta actual (`ls -la` = tot, amb detalls) |
| `cd foo` | entra a la carpeta `foo` · `cd ..` = puja un nivell · `cd ~` = inici · `cd -` = torna enrere |
| `pwd` | mostra on ets |
| `cat file` | mostra un fitxer per pantalla |
| `less file` | recorre un fitxer llarg pàgina a pàgina (`q` per sortir) |
| `nano file` | edita un fitxer (`Ctrl-O` desa, `Ctrl-X` surt) |
| `mkdir foo` | crea una carpeta · `rm file` esborra · `rm -r foo` esborra una carpeta (amb compte) |
| `cp a b` / `mv a b` | copia / mou (o canvia el nom) |
| `head -n 20 file` / `tail` | primeres / últimes 20 línies |
| `grep "text" file` | cerca les línies que contenen `text` |

**Els tres fluxos** que té tot programa — a la pantalla semblen iguals, però no ho són:

| Flux | Què transporta |
|---|---|
| **entrada estàndard** (stdin) | el que el programa llegeix com a entrada |
| **sortida estàndard** (stdout) | la sortida normal del programa |
| **sortida d'error** (stderr) | els missatges d'error: un canal *separat* de la sortida estàndard |

**Redirecció i canonades** — veuràs que els agents les fan servir constantment:

| Símbol | Significat |
|---|---|
| `cmd > file` | envia la sortida estàndard **cap a** un fitxer (sobreescriu-ne el contingut) |
| `cmd >> file` | afegeix la sortida estàndard al final d'un fitxer |
| `cmd 2> errs.txt` | envia la **stderr** a un fitxer (el `2` és el número de la stderr) |
| `cmd1 \| cmd2` | connecta la sortida estàndard de `cmd1` amb l'entrada estàndard de `cmd2` |

---

## git — els cinc verbs que cobreixen el 90%

| Comanda | Què fa |
|---|---|
| `git clone <url>` | clona un repositori remot a la teva màquina |
| `git status` | què has canviat o preparat (staged) ara mateix |
| `git add <file>` (o `git add .`) | prepara els canvis per al proper commit |
| `git commit -m "message"` | desa una instantània amb un missatge |
| `git push` | envia els teus commits a GitHub |
| `git pull` | baixa el que altres (o tu, des d'un altre lloc) han pujat |
| `git log --oneline` | l'historial, una línia per commit |

**Branques** — prova coses sense trencar el que ja funciona:

| Comanda | Què fa |
|---|---|
| `git branch` | llista les branques · `git branch foo` crea'n una |
| `git checkout foo` | canvia a la branca `foo` (`git checkout -b foo` = crear-la i canviar-hi) |
| `git checkout -- file` | descarta els canvis no confirmats de `file` |

**Configuració inicial de git** (només un cop a la vida):
```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
git config --global init.defaultBranch main
```

---

## Python amb `uv`

`uv` executa Python i gestiona les dependències, de manera que els scripts «simplement funcionen».

| Comanda | Què fa |
|---|---|
| `python3 --version` | comprova la teva versió de Python (la volem ≥ 3.11) |
| `uv run script.py` | executa un script en un entorn gestionat |
| `uv run --with openai --with chromadb python script.py` | executa amb paquets addicionals, sense instal·lar-los a mà |
| `uv venv && source .venv/bin/activate` | crea i entra en un entorn virtual (la manera manual) |
| `uv sync` | instal·la tot el que declara el `pyproject.toml` d'un projecte |

---

## El model a la teva màquina — Ollama

| Comanda | Què fa |
|---|---|
| `ollama serve` | engega el servidor local del model (sovint ja s'està executant com a aplicació) |
| `ollama pull qwen3:1.7b` | baixa un model petit (~1,5 GB — funciona en gairebé qualsevol màquina) |
| `ollama run qwen3:1.7b "say hi"` | una conversa ràpida des del terminal |
| `ollama list` | què tens baixat |

El curs es comunica amb Ollama a través de l'endpoint compatible amb **OpenAI** de `http://localhost:11434/v1`: sense clau d'API, sense despeses i sense internet. El mateix codi arriba a un model al núvol canviant una sola línia de configuració. (Això és una lliçó, no una drecera — ho veuràs a la setmana 2.)

## L'agent de programació — OpenCode

Instal·la'l ara (consulta la guia d'instal·lació); el farem servir de debò a partir de la setmana 2.

| Comanda | Què fa |
|---|---|
| `opencode` | l'engega a la carpeta actual |
| `opencode --version` | confirma que està instal·lat |

---

## «Estic a punt?» — la prova de foc

Executa-les. Si les cinc responen sense errors, estàs a punt per al primer dia:

```bash
python3 --version          # 3.11 or higher
uv --version               # any version
git --version              # any version
ollama run qwen3:1.7b "reply with exactly one short sentence"
opencode --version         # any version
```

Si alguna dóna error, llegeix el missatge que apareix a **stderr**, consulta la guia d'instal·lació i, si encara et quedes encallat, **escriu-nos un correu abans que comenci el curs.**

---

## On aprendre'n més (opcional, si alguna secció t'ha resultat nova)

- **Terminal:** *The Missing Semester of Your CS Education* (MIT) — `missing.csail.mit.edu` — les classes sobre la shell i les eines cobreixen just aquest nivell base.
- **git:** el llibre *Pro Git* (gratuït) — `git-scm.com/book` — llegeix-ne els capítols 1–3. O `learngitbranching.js.org` per a un recorregut visual i pràctic per les branques.
- **Python (per refrescar):** el tutorial oficial — `docs.python.org/3/tutorial`.
- **`uv`:** `docs.astral.sh/uv`.
- **Ollama:** `ollama.com` → la biblioteca de models i el README.
