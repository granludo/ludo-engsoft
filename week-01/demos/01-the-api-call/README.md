# Conferència 3 — crida a l'LLM

Tot és **JSON sobre HTTP**. La mateixa crida a **Chat Completions** — `messages`
d'entrada, `choices[0].message.content` de sortida — arriba igual a OpenAI, OpenRouter,
Groq, Mistral i al model local del teu portàtil. Un sol wire format, tots els
proveïdors. Aquí la tens de dues maneres (`curl` pelat i l'SDK de Python), més dues
variants de la mateixa crida: streaming i imatges.

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

Cada carpeta és autònoma i llegeix el seu propi `.env`. Copia l'exemple, omple'l i
executa **des de dins de la carpeta** perquè s'agafi el `.env` correcte:

```bash
cd chat-completions
cp ../.env.example .env        # set OPENAI_ENDPOINT / OPENAI_API_KEY / MODEL
```

HTTP pelat — només `curl` (l'script carrega el `.env` per tu):

```bash
bash curl.sh
```

Python — mitjançant `uv`, sense instal·lació manual:

```bash
uv run --with openai --with python-dotenv python call.py
```

Les mateixes dues ordres funcionen a `streaming/` i `multimodal/`. Un advertiment:
la **visió** (`multimodal/`) necessita un model amb capacitat de visió, així que
apunta el seu `.env` a un proveïdor que en tingui. Les chat completions normals
(`chat-completions/`, `streaming/`) funcionen contra qualsevol cosa que parli el wire
format, inclòs un model local.

## El mateix cable, un substrat diferent

La forma de les Chat Completions no és exclusiva d'OpenAI. Apunta el mateix codi de
Python a un `base_url` diferent i cridarà una màquina diferent:

```python
from openai import OpenAI

# your laptop, via Ollama — no key, no money, no internet
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
```

El mateix client, la mateixa crida, el mateix JSON. El substrat és substituïble; la
interfície és portable. Aquesta portabilitat és tot el sentit de la cosa: per això
construïm sobre el format que tothom parla, i no sobre l'endpoint propietari de cap
proveïdor concret.


---

© 2026 **Marc Alier i Forment** (Universitat Politècnica de Catalunya) · <https://wasabi.essi.upc.edu/ludo> · <https://lamb-project.org>
BSC Agents Course — *Transformers, LLMs, RAG and Agents: From Theory to Production*.
Licensed under [Creative Commons BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/): reuse must credit the author, no commercial use, derivatives under the same license.
