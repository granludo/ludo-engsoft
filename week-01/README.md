# Setmana 1 — Bases: els LLM, la crida a l'API i la interfície universal

Codi complementari per al **curs d'agents del BSC · Setmana 1**. Les classes expliquen la teoria; els exercicis d'aquí són on la toques amb les mans.

## Què cobreix la Setmana 1

- **Tokenization** — què veu realment el model, i per què la teva factura es mesura en tokens i no en paraules.
- **Base contra alineat** — GPT-2 (un base model, mai passat per RLHF) enfront de Qwen3-1.7B (aligned). El mateix prompt genera un qüestionari en un cantó i una resposta en l'altre. La diferència és l'stack d'alineació de la Conferència 2.
- **La crida a l'API** — JSON d'entrada, JSON de sortida, sobre HTTP. Un wire format universal per a tots els proveïdors (OpenAI, Anthropic mitjançant OpenRouter, Mistral, …) i servidors locals (Ollama, vLLM, LM Studio). Consulta [`demos/context-explorer/`](./demos/context-explorer/) i [`demos/the-api-call/`](./demos/the-api-call/) — la crida bàsica a chat completions amb `curl` i mitjançant l'SDK, més streaming i imatges.

## Exercicis

| # | Què fas | Carpeta |
|---|---|---|
| **1 — Tokenize** | Carrega un tokenizer localment, compta tokens, mesura la penalització multilingüe i compara dos tokenizers amb quatre tipus d'entrada. | [`ex-01-tokenise/`](ex-01-tokenise/) |
| **2 — Base contra alineat** | Executa GPT-2 (base, ~124M) i Qwen3-1.7B (aligned) un al costat de l'altre. Fes a tots dos els mateixos quatre prompts i observa la diferència. | [`ex-02-base-vs-aligned/`](ex-02-base-vs-aligned/) |
| **3 — Crida un LLM** | Fes servir [`demos/context-explorer/`](./demos/context-explorer/) contra un Qwen3-1.7B servit localment amb Ollama. El mateix model que a l'exercici 2, però aquest cop embolcallat en el wire format d'OpenAI. Sense clau API, sense diners. | [`demos/context-explorer/`](./demos/context-explorer/) |
| **4 — Crida el LLM des del codi** | La crida bàsica: `curl` i un breu script de Python contra el teu propi Ollama, amb el model que pots executar. El mateix wire format que arriba a un model de frontera: només canvia el `.env`. | [`ex-04-call-the-llm/`](ex-04-call-the-llm/) |

## Com executar qualsevol cosa d'aquesta carpeta

Cada subcarpeta d'exercici és independent: té el seu propi `pyproject.toml` i el seu propi `.venv`. Patró estàndard:

```bash
cd week-01/ex-01-tokenise
uv venv && source .venv/bin/activate
uv sync
python ex_01_tokenise.py
```

`.venv/` i `.env` estan al `.gitignore` a tot arreu: no els facis commit mai.

## VM del curs

Si no tens un entorn de Python 3.10+ funcional, la VM oficial del curs està a [`../pre-course/vm-setup.md`](../pre-course/vm-setup.md) (VirtualBox + Ubuntu Server, imatge OVA distribuïda pel curs); a [`../pre-course/cheatsheet.md`](../pre-course/cheatsheet.md) hi trobaràs les ordres del primer dia.

## Llicència

[CC BY-NC-SA 4.0](../LICENSE) — comparteix i adapta per a usos no comercials, amb atribució i redistribució sota la mateixa llicència.


---

© 2026 **Marc Alier i Forment** (Universitat Politècnica de Catalunya) · <https://wasabi.essi.upc.edu/ludo> · <https://lamb-project.org>
BSC Agents Course — *Transformers, LLMs, RAG and Agents: From Theory to Production*.
Licensed under [Creative Commons BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/): reuse must credit the author, no commercial use, derivatives under the same license.
