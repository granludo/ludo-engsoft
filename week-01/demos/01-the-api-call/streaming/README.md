# Streaming d'una chat completion

La mateixa crida a chat completions, però reps la resposta **token a token a mesura
que es produeix** en lloc d'esperar que estigui tota acabada. És l'efecte màquina
d'escriure de ChatGPT. El temps total és pràcticament el mateix; només *sembla* més
ràpid, i en respostes llargues l'usuari veu que avança en comptes d'un spinner
congelat.

En el codi, l'únic canvi és `stream=True`: la resposta esdevé un *iterador de chunks*,
i cada chunk porta una mica més de text a `choices[0].delta.content`. L'imprimeixes
tan bon punt arriba (`flush=True`). Passa `stream_options={"include_usage": True}`
per obtenir un chunk final amb el `usage` de tokens, que una resposta en streaming
altrament omet.

## Executar-ho

```bash
cp ../.env.example .env        # OPENAI_ENDPOINT / OPENAI_API_KEY / MODEL
uv run --with openai --with python-dotenv python stream.py
```

Observa com el text apareix uns quants tokens cada cop, i al final la línia de `usage`.

O mira-ho des del punt de vista de l'HTTP pelat — la mateixa crida amb
`"stream": true`, sense SDK. `curl -N` imprimeix cada chunk `data: {...}` a l'instant
que arriba:

```bash
bash curl.sh
```

Obtens els Server-Sent Events que l'SDK t'amaga: una sèrie de línies `data:`,
cadascuna amb una mica més de text a `choices[0].delta.content`, acabant en
`data: [DONE]`.

---

© 2026 **Marc Alier i Forment** (Universitat Politècnica de Catalunya) · <https://wasabi.essi.upc.edu/ludo> · <https://lamb-project.org>
BSC Agents Course — *Transformers, LLMs, RAG and Agents: From Theory to Production*.
Licensed under [Creative Commons BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/): reuse must credit the author, no commercial use, derivatives under the same license.
