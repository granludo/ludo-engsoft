# Un agent mínim per a la línia de comanda (CLI) – memòria en fitxers, habilitats a demanda, i un terminal per a les mans.

Exemple de final de la setmana 3: tot el que s'ha après durant la setmana, en un sol fitxer. El motor és el mateix bucle de sis línies des del `02-give-the-llm-hands`. El que és nou és el **"jo"**:

```
04-minimal-cli-agent/
├── minimal_cli_agent.py   # ~120 lines: build the self, two tools, the loop
├── agent.md               # who the agent is, what it must do
├── memory/                # markdown files, loaded whole at startup
│   └── preferences.md
├── skills/                # one folder per skill — INDEXED at startup,
│   └── word-report/       # READ on demand with read_skill
│       └── skill.md
└── workspace/             # the documents the sample agent works on
```

- **`agent.md`** es posa al cap de la system prompt: finalitat i regles.
- **`memory/*.md`** es carrega completament – memòria fixa, barata i sempre disponible.
- **`skills/`** es carrega com un *índex únic* (la primera línia de cada `skill.md`). Quan una tasca coincideix, el model crida a `read_skill` i obté les instruccions completes: descobriment a demanda, la mateixa estratègia que fa `--help`. Compareu amb el registre **MCP** del tercer mòdul, que s'utilitza en cada sol·licitud.
- **Dos eines:** `run_command` (un comandament de terminal, imprès, amb restriccions de seguretat) i `read_skill`.

## Correr

```bash
cd week-03/demos/04-minimal-cli-agent
uv venv && source .venv/bin/activate && uv sync
python minimal_cli_agent.py "make me a word report of the workspace"
```

Observa l'ordre: l'agent primer llegeix la habilitat, després demana permís per a `ls`, després per a `wc`, i finalment informa – en el estil `memory/preferences.md` que sol·licita, signant d'acord amb les exigències de la habilitat. Ningú va escriure aquesta seqüència.

Cada crida genera `prompt_tokens`: la totalitat de l'agent – la seva personalitat, memòria, índex de habilitats i dos esquemes d'eines – té un cost d'unes centenars tokens. Tingueu això en compte al costat dels vostres mesures del Exercici 2.

## Fes-ho teu/a.

Edita `agent.md`, afegeix el teu propi codi Markdown a `memory/`, i afegeix una `skills/<name>/skill.md` amb la primera línia que indiqui quan utilitzar-la. No cal fer cap canvi de codi per a això. Aquest és el punt clau.

## Configuració

Els valors per defecte prioritzen Ollama (`qwen3:1.7b` — els models petits condueixen l'agent de manera irregular; un motor més gran ho fa millor). Copia `.env.example` a `.env` per apuntar a qualsevol endpoint compatible amb OpenAI.

## 📖 Llicència i autor

Licensed under **CC BY-NC-SA 4.0**. © 2026 **Marc Alier i Forment** (UPC) · <https://wasabi.essi.upc.edu/ludo> · <https://lamb-project.org>. BSC Agents Course.
