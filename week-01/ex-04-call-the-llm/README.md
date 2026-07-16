# Exercici 4 – Crida al LLM des del codi

Teniu un model que s'executa al vostre ordinador (exercici 3). Ara, el crideu des de
còd - de la mateixa manera que crides a un model en núvol. El punt:
**És la mateixa petició.** Una sol·licitud de completament d'un missatge de text és JSON sobre HTTP, i una altra.
El format de fitxer s'envia a plataformes com OpenAI, OpenRouter, Groq i també a Ollama, que està instal·lat al vostre ordinador portàtil.

## Què hi ha aquí?

```
call.py              Chat Completions via the openai SDK   (runs on Ollama)
call.sh              the same call, raw curl — no SDK       (runs on Ollama)
.env.example         config; copy to .env
```

## Configuració

1. Executa el programa Ollama amb un model que puguis ajustar (segons l'exercici 3):

   ```bash
   ollama serve            # if it isn't already running
   ollama pull ministral-3:8b
   ```

2. Configurar i instal·lar el client:

   ```bash
   cp .env.example .env    # the defaults point at your local Ollama
   pip install openai python-dotenv
   ```

Modifiqueu `MODEL` a `.env` per tal que s'adapti a la vostra màquina – `ministral-3:8b`
(al voltant de 6 GB), `qwen3:1.7b` (al voltant de 1,5 GB), o qualsevol cosa que hàies fet a l'exercici 3.

## Executar-ho

```bash
# .env loads automatically — call.py reads it via python-dotenv, call.sh sources it.
python call.py
bash   call.sh
```

Haureu de rebre una resposta en una sola frase, juntament amb les referències token i `usage`, i...
`finish_reason`. Aquest `usage` bloc és la vostra factura per un servei pagat API – llegeu-la.

## Prova això

- Canvia el `temperature` (de 0,0 a 1,5) i executa-ho diverses vegades. Quines canvis observes?
- Canviar el model a `.env`. El mateix codi, però amb una estructura diferent.
- Si teniu una clau de núvol (OpenAI, OpenRouter, Groq): configureu els valors del núvols a
`.env` i tornar a executar `call.py` — **sense canvis**. El mateix codi, el mateix wire format.
un model de frontiera en lloc del que teniu al vostre ordinador portàtil. Només el `.env` ha canviat.



---

© 2026 **Marc Alier i Forment** (Universitat Politècnica de Catalunya) · <https://wasabi.essi.upc.edu/ludo> · <https://lamb-project.org>
Curs per a agents de BSC — *Transformers, LLMs, RAG i Agents: Des del teòric a la pràctica*.
Licensed under [Creative Commons BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/): reuse must credit the author, no commercial use, derivatives under the same license.
