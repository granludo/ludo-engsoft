# Exercici 4 — Crida el LLM des del codi

Tens un model executant-se a la teva màquina (exercici 3). Ara el crides des del
codi, igual que cridaries un model de frontera al núvol. La idea clau:
**és la mateixa crida.** Una petició de chat completions és JSON sobre HTTP, i un
únic wire format arriba per igual a OpenAI, OpenRouter, Groq i a l'Ollama del teu portàtil.

## Què hi ha aquí

```
call.py              Chat Completions via the openai SDK   (runs on Ollama)
call.sh              the same call, raw curl — no SDK       (runs on Ollama)
.env.example         config; copy to .env
```

## Configuració

1. Tingues Ollama en marxa amb un model que et càpiga (de l'exercici 3):

   ```bash
   ollama serve            # if it isn't already running
   ollama pull ministral-3:8b
   ```

2. Configura i instal·la el client:

   ```bash
   cp .env.example .env    # the defaults point at your local Ollama
   pip install openai python-dotenv
   ```

   Edita `MODEL` a `.env` amb el que et vagi bé per a la teva màquina — `ministral-3:8b`
   (~6 GB), `qwen3:1.7b` (~1,5 GB), o qualsevol que hagis executat a l'exercici 3.

## Executar-ho

```bash
# .env loads automatically — call.py reads it via python-dotenv, call.sh sources it.
python call.py
bash   call.sh
```

Hauràs d'obtenir una resposta d'una sola frase, més el `usage` de tokens i el
`finish_reason`. Aquest bloc `usage` és la teva factura en una API de pagament — llegeix-lo.

## Prova això

- Canvia la `temperature` (0,0 vs 1,5) i executa-ho unes quantes vegades. Què canvia?
- Canvia el model a `.env`. El mateix codi, un cervell diferent.
- Si tens una clau al núvol (OpenAI, OpenRouter, Groq): posa els valors del núvol al
`.env` i torna a executar `call.py` — **sense canvis**. El mateix codi, el mateix wire format,
un model de frontera en lloc del del teu portàtil. Només ha canviat el `.env`.



---

© 2026 **Marc Alier i Forment** (Universitat Politècnica de Catalunya) · <https://wasabi.essi.upc.edu/ludo> · <https://lamb-project.org>
Curs per a agents de BSC — *Transformers, LLMs, RAG i Agents: Des del teòric a la pràctica*.
Licensed under [Creative Commons BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/): reuse must credit the author, no commercial use, derivatives under the same license.
