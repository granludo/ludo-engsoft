# Conferència 3 – Crida a LLM

Tot està **JSON** a punt per **HTTP**. La mateixa **Chat Completions**, la mateixa crida — `messages`
entrades, `choices[0].message.content`; sortides, OpenAI, OpenRouter, Groq, Mistral.
i també el model local del teu ordinador portàtil. Cada proveïdor ofereix wire format. Aquí teniu:
dos maneres (la primera `curl` i la segona SDK), més dues variants de la mateixa funció:
streaming i imatges.

```
chat-completions/   the call itself      (/v1/chat/completions)
  curl.sh             raw HTTP, no SDK
  call.py             the same call via the openai SDK
streaming/          tokens as they are produced (the typewriter effect)
  curl.sh             raw SSE (data: chunks) over the wire — no SDK
  stream.py           stream=True over chat completions
multimodal/         send an image, not just text
  send_image.py       content as a list of parts (text + image)
```

## Executar-ho

Cada carpeta és autònoma i llegeix el seu propi `.env`. Copia l'exemple.
Ompliu-ho i executeu l'operació **des de dins del directori**, perquè es triï la opció correcta `.env`:

```bash
cd chat-completions
cp ../.env.example .env        # set OPENAI_ENDPOINT / OPENAI_API_KEY / MODEL
```

Font original HTTP – només `curl` (els fonts del guió `.env` per a vosaltres):

```bash
bash curl.sh
```

Python – a través de `uv`, sense instal·lació manual:

```bash
uv run --with openai --with python-dotenv python call.py
```

Els mateixos dos comandaments funcionen a `streaming/` i `multimodal/`. Una advertència:
**Visió** (`multimodal/`) necessita un model amb capacitat de visió, per tant, dirigeix el `.env` cap a...
proveïdor que en tingui. Proveïdor senzill chat completions (`chat-completions/`, `streaming/`)
operar contra qualsevol cosa que parli de wire format, incloent-hi un model local.

## Més o menys el mateix cable, però amb un substrat diferent.

La forma Chat Completions no és exclusiva per a OpenAI. Apliqueu el mateix codi de Python a un
diferents `base_url` i crida a una màquina diferent:

```python
from openai import OpenAI

# your laptop, via Ollama — no key, no money, no internet
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
```

El mateix client, la mateixa trucada, el mateix JSON. El substrat és substituible; l'interfície
és portàtil. Aquesta portabilitat és el punt clau, per tant, ens centrem en aquest aspecte.
Tots parlen, però no en referència a la propietat exclusiva d'un proveïdor específic endpoint.


---

© 2026 **Marc Alier i Forment** (Universitat Politècnica de Catalunya) · <https://wasabi.essi.upc.edu/ludo> · <https://lamb-project.org>
Curs per a agents de BSC — *Transformers, LLMs, RAG i Agents: Des del teòric a la pràctica*.
Licensed under [Creative Commons BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/): reuse must credit the author, no commercial use, derivatives under the same license.
