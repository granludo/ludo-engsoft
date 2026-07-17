<!-- =============================================================================================================== -->
<!-- Universitat Politècnica de Catalunya (UPC) -->
<!-- =============================================================================================================== -->

# 📚 Context Explorer — RAG d'un sol fitxer

El RAG d'un sol fitxer és la cosa més bàsica que es mereix el nom: enganxes tot un fitxer al prompt
com a context i preguntes. Aquest explorador mostra la part que tothom entén malament: **la
diferència entre la conversa que guarda la interfície de xat i la crida que rep realment l'LLM.** No
són el mateix, i la lliçó és justament aquesta distància.

## Les tres capes

Té la mateixa forma que servir un assistent a través d'una API compatible amb OpenAI (per exemple, LAMB):

```
🖥️  CHAT UI        sends:  history (bare) + your latest message
                       │   history = what you see; no system prompt, no augmentation
                       ▼
🛠️  ASSISTANT ENDPOINT  (STATELESS; the model id selects system prompt + template + RAG)
        builds:  [system] + [history] + [ template(your message, RAG augmentation) ]
                       │   rebuilt every call — it has no state to keep it in
                       ▼
🧠  LLM            returns:  the response only
                       ▲
🖥️  CHAT UI        appends (your message, response) → history   ✗ augmentation NOT saved
```

En arrencar (i cada vegada que fas `/mode` o `/file`), l'explorador et mostra la **configuració de
l'assistent** —el system prompt, la plantilla de prompt i el fitxer de coneixement— i t'indica on va
a parar el fitxer en el mode actual. Així veus què hi ha configurat abans de veure com es munta.

Com que l'endpoint és **sense estat**, l'augmentació es construeix de nou a cada torn i es
llença. L'historial de la interfície es manté pelat. El system prompt i el fitxer que veu l'LLM **no
són mai** dins de la conversa que veu l'usuari. Fixa't en els dos panells a cada torn:

- **`🛠️ → 🧠 Endpoint builds the LLM call`** — system + historial + el missatge augmentat d'aquest torn
- **`🖥️ Chat UI history`** — només els torns pelats

La distància entre tots dos —el system prompt i l'augmentació— és exactament allò que l'aplicació no
recorda.

## Dos modes de col·locació (canvia'ls en viu amb `/mode`)

| Mode | El fitxer va… | Missatge de l'usuari per torn | Què mostra |
|---|---|---|---|
| **`user-augment`** *(per defecte)* | dins el **missatge de l'usuari**, a cada torn | augmentat (fitxer + pregunta) | la distància entre l'aplicació i l'LLM; el fitxer viatja a la cua volàtil, es reenvia i es torna a facturar a cada crida |
| **`system-grounding`** | dins el **system prompt**, **un sol cop** | pregunta pelada | recupera un cop al principi → una conversa «pura» → el fitxer queda al prefix estable i cacheable (cache KV) |

Canvia d'un a l'altre en directe i torna a fer les mateixes preguntes: amb `user-augment`, el fitxer
es reconstrueix a cada crida; amb `system-grounding`, es recupera un sol cop i la conversa es manté neta.

El contrafactual: per **conservar** l'augmentació hauries de desar l'historial augmentat i fer que el
xat tingués **estat** — `/stateful` ho activa perquè puguis veure què costa.

## Configuració

```bash
cd context-explorer-rag
uv venv && source .venv/bin/activate && uv sync
```

Copia `.env.example` a `.env`:

```bash
OPENAI_API_KEY=your-key-here
MODEL=gpt-4.1-mini
OPENAI_ENDPOINT=https://api.openai.com/v1
KNOWLEDGE_FILE=knowledge.txt
RAG_MODE=user-augment            # or system-grounding
```

Opció amb Ollama primer (sense clau, sense diners, sense internet):

```bash
OPENAI_ENDPOINT=http://localhost:11434/v1
MODEL=qwen3:1.7b
```

## Execució

```bash
uv run context_explorer_rag.py
```

Comandes dins del xat:

| Comanda | Què fa |
|---|---|
| `/mode user-augment` · `/mode system-grounding` | canvia on va a parar el fitxer (reinicia la conversa). Sense argument, **alterna**; espais, guions baixos, guions i àlies curts (`system`/`grounding`/`sg`, `user`/`augment`/`ua`) es resolen tots |
| `/stateful` | activa o desactiva el desament de l'historial augmentat (l'alternativa amb estat) |
| `/file <path>` | carrega un altre fitxer de coneixement |
| `/context` | imprimeix el fitxer de coneixement carregat |
| *(línia buida)* | surt |

## El que has de notar

1. Fes una pregunta que el fitxer respongui i, tot seguit, una de seguiment. Amb `user-augment`,
   mira com es construeix l'endpoint al torn 2: els torns *anteriors* passen **pelats** —l'augmentació
   del torn passat ha desaparegut—. El fitxer només es torna a injectar al missatge actual.
2. L'historial de la interfície no conté mai el system prompt ni l'augmentació. El model llegeix molt
   més del que l'aplicació recorda.
3. Canvia a `system-grounding`. Ara el fitxer és al system prompt, els torns de l'usuari van pelats i
   la recuperació passa un sol cop: la conversa és «pura».

## Com hi encaixa a continuació el RAG amb embeddings

El pas de recuperació és una sola classe, `WholeFileRetriever`. Tota la resta —la interfície,
l'endpoint sense estat, els panells, la comptabilitat de tokens— és independent de com funciona la
recuperació. El graó següent hi encaixa un `EmbeddingsRetriever` que embedeix la pregunta, troba els
chunks més propers i retorna només aquests. **El bucle no canvia. Només canvia el recuperador.** Aquí
tens l'arquitectura del RAG en un sol canvi.

## 📖 Llicència

Licensed under [Creative Commons BY-NC-SA 4.0](../../../week-01/demos/context-explorer/LICENSE) (`CC BY-NC-SA 4.0`).

## 👤 Autor

[@granludo](https://github.com/granludo) - Marc Alier, Universitat Politècnica de Catalunya (UPC)

---

© 2026 **Marc Alier i Forment** (Universitat Politècnica de Catalunya) · <https://wasabi.essi.upc.edu/ludo> · <https://lamb-project.org>
BSC Agents Course — *Transformers, LLMs, RAG and Agents: From Theory to Production*.
Licensed under [Creative Commons BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/): reuse must credit the author, no commercial use, derivatives under the same license.
