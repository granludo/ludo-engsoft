# Un agent CLI mínim — memòria en fitxers, habilitats sota demanda i un terminal per mans

Exemple de tancament de la setmana 3: tot el que ha ensenyat la setmana, en una sola carpeta. El motor és el mateix bucle de sis línies del `02-give-the-llm-hands`. El que és nou és el **jo**:

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

- **`agent.md`** va al capdamunt del system prompt: propòsit i regles.
- **`memory/*.md`** es carrega sencer: memòria fixa, barata i sempre present.
- **`skills/`** es carrega només com un *índex* (la primera línia de cada `skill.md`). Quan una tasca hi encaixa, el model crida `read_skill` i obté les instruccions completes: descobriment sota demanda, el mateix truc que fa `--help`. Compara-ho amb el registre MCP de la classe 3.3, que viatja sencer a cada petició.
- **Dues eines:** `run_command` (una ordre de terminal, impresa, protegida amb la `y` —la seguretat a l'estructura—) i `read_skill`.

## Executar

```bash
cd week-03/demos/04-minimal-cli-agent
uv venv && source .venv/bin/activate && uv sync
python minimal_cli_agent.py "make me a word report of the workspace"
```

Observa l'ordre: l'agent primer llegeix l'habilitat, després demana permís per a `ls`, després per a `wc`, i finalment informa, amb l'estil que demana `memory/preferences.md` i signat tal com exigeix l'habilitat. Ningú no va programar aquesta seqüència.

Cada crida imprimeix `prompt_tokens`: tot el jo de l'agent —la personalitat, la memòria, l'índex d'habilitats i els dos esquemes d'eines— costa unes poques centenes de tokens. Tingues aquest número present al costat de les mesures del teu Exercici 2.

## Fes-lo teu

Edita `agent.md`, deixa el teu propi Markdown a `memory/`, afegeix un `skills/<name>/skill.md` amb una primera línia que digui quan fer-lo servir. Res d'això no requereix tocar codi. Aquest és el quid.

## Configuració

Els valors per defecte prioritzen Ollama (`qwen3:1.7b` — els models petits condueixen l'agent de manera irregular; un motor més gran el condueix millor). Copia `.env.example` a `.env` per apuntar a qualsevol endpoint compatible amb OpenAI.

## 📖 Llicència i autor

Licensed under **CC BY-NC-SA 4.0**. © 2026 **Marc Alier i Forment** (UPC) · <https://wasabi.essi.upc.edu/ludo> · <https://lamb-project.org>. BSC Agents Course.
