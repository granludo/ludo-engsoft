# Setmana 1 – Bases: LLMs, la funció API i la interfície universal

Material complementari per al curs **Agents BSC · Setmana 1**. Les conferències presenten la teoria, i els exercicis aquí són on es posa en pràctica.

## Què cobreix la primera setmana

- **Tokenització** – què realment veu el model, i per què la vostra factura està en "tokens" (unitats) i no en paraules.
- **Base contra alineat** — GPT-2 (en un base model, mai RLHF) vs. Qwen3-1.7B (alineat). El mateix prompt genera una qüestió d'un costat i la resposta de l'altre. L'estacada d'alineació del seminari 2 és la diferència.
- **La API comunicació** — JSON(entrada), JSON(sortida), sobre HTTP. Comunicació universal wire format a través dels proveïdors (OpenAI, Anthropic mitjançant OpenRouter, Mistral, …) i els servidors locals (Ollama, vLLM, LM Studio). Vegeu [`demos/context-explorer/`](./demos/context-explorer/) i [`demos/the-api-call/`](./demos/the-api-call/) — la comunicació bàsica, que inclou `curl` i la comunicació a través de SDK, juntament amb streaming] i imatges.

## Exercicis

| # | Què fas | Carpeta |
|---|---|---|
| **1 — Tokenize** | Carregar tokenizer localment, comptar tokens, mesurar la penalització per la multilingüisme, comparar dues tokenizers en quatre tipus d'entrada. | [`ex-01-tokenise/`](ex-01-tokenise/) |
| **2 – Base (fonètica bàsica) contra fonètica alineada** | Analitza les cromosomes GPT-2 (cromosoma principal, aproximadament 124M) i Qwen3-1.7B (alineats) un al costat de l'altre. Pregunta per a amb els mateixos quatre prompts; observa la diferència. | [`ex-02-base-vs-aligned/`](ex-02-base-vs-aligned/) |
| **3 – Trucar a LLM** | Utilitza [`demos/context-explorer/`](./demos/context-explorer/) contra un servidor local que serveix Ollama amb una versió Qwen3-1.7B. El mateix model que en l'exercici 2, però aquesta vegada empaquetat amb OpenAI i wire format. Sense clau API, sense diners. | [`demos/context-explorer/`](./demos/context-explorer/) |
| **4 – Crida al LLM des del codi** | La crida bàsica: `curl` i un curt script en Python contra el vostre Ollama, sobre el model que podeu executar. El mateix wire format que arriba a un model de frontera – només canvia el `.env`. | [`ex-04-call-the-llm/`](ex-04-call-the-llm/) |

## Com executar qualsevol programa o fitxer dins d'aquesta carpeta.

Cada carpeta de exercicis és independent – té la seva pròpia identificació (`pyproject.toml`) i la seva pròpia identificació (`.venv`). Patró estàndard:

```bash
cd week-01/ex-01-tokenise
uv venv && source .venv/bin/activate
uv sync
python ex_01_tokenise.py
```

`.venv/` i `.env` estan ignorats per Git en totes les ubicacions – mai no cal que es commitin.

## Curs VM

Si no teniu un entorn de Python 3.10 o superior funcional, la versió virtual de curs està disponible aquí: [`../pre-course/vm-setup.md`](../pre-course/vm-setup.md) (VirtualBox + Ubuntu Server, imatge OVA distribuïda pel curs); a [`../pre-course/cheatsheet.md`](../pre-course/cheatsheet.md) trobareu les ordres per començar.

## Llicència

[CC BY-NC-SA 4.0](../LICENSE) – Permetre el compartiment i l'adaptació per a usos no comercials, amb la indicació d'autor i la possibilitat de redistribuir sota la mateixa llicència.


---

© 2026 **Marc Alier i Forment** (Universitat Politècnica de Catalunya) · <https://wasabi.essi.upc.edu/ludo> · <https://lamb-project.org>
Curs per a agents de BSC — *Transformers, LLMs, RAG i Agents: Des del teòric a la pràctica*.
Licensed under [Creative Commons BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/): reuse must credit the author, no commercial use, derivatives under the same license.
