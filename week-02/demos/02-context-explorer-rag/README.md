<!-- =============================================================================================================== -->
<!-- Universitat Politècnica de Catalunya (UPC) -->
<!-- =============================================================================================================== -->

# 📚 Explorador de context – un fitxer RAG

El sistema de recuperació d'informació (RAG) amb un sol fitxer és la forma més bàsica, però que permet obtenir el nom: simplement copiar tot el contingut d'un fitxer.
prompt com a context i per preguntar-ne. Aquest explorador mostra la part que tothom falla – **la**
la diferència entre la conversa que manté l'interfície de xat i la realització de la crida LLM.
reben. No són iguals, i la diferència és l'aula d'aprenentatge.

## Les tres capes

Això és igual que servir un ajudant a través d'un OpenAI compatible amb API (per exemple, LAMB):

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

Al iniciar (i cada vegada que feu [`/mode`] o [`/file`]), l'explorador mostra l'**assistent**.
configuració — el system prompt, la plantilla prompt i el fitxer de coneixement — i us informa de...
on es guarda el fitxer en l'estat actual. Així pots veure què està configurat abans de visualitzar-lo.
ser muntat.

Com que el endpoint és **sense estat**, l'augmentació es crea des de zero cada vegada.
descartats. L'històric de la interfície es manté buit. Els elements system prompt i el fitxer que veu LLM són
**mai** durant la conversa, l'usuari veu les dues panells a la vegada. Observeu cada panel per separat:

- **`🛠️ → 🧠 Endpoint builds the LLM call`** – sistema + història + missatge augmentat d'aquesta tornada
- **`🖥️ Chat UI history`** – només els canvis bàsics

La diferència entre ells – el system prompt i l'augment – és exactament el que ofereix l'aplicació.
no recorda.

## Dos modes de posicionament (canviar a la posició activa amb `/mode`)

| Mod | El fitxer... | Missatge per a l'usuari cada vegada | Què mostra |
|---|---|---|---|
| **`user-augment`** (valor per defecte) | en el **missatge de l'usuari**, cada pas | amplificat (fitxer + pregunta) | l'abast entre l'aplicació i els models de llenguatge (LLM); el fitxer segueix una trajectòria inestable, que es repeteix i se li cobra cada vegada. |
| **`system-grounding`** | a la **system prompt**, **una vegada** | pregunta directa | recuperar una vegada al principi → una conversa "pura" → el fitxer es guarda en la prefeix estable i accessible (memòria KV) |

Canvia entre elles a la càmera i torna a preguntar les mateixes preguntes: al `user-augment`, el fitxer és
reconstruït en cada trucada; a `system-grounding`, es recull una vegada i la conversa continua.
s'esporta net.

L'hipòtet: per mantenir l'augmentació, hauríeu de guardar la història augmentada.
i fer que el programa sigui **estat-dependent**, amb botons `/stateful` perquè puguis veure el cost.

## Configuració

```bash
cd context-explorer-rag
uv venv && source .venv/bin/activate && uv sync
```

Copiar `.env.example` a `.env`:

```bash
OPENAI_API_KEY=your-key-here
MODEL=gpt-4.1-mini
OPENAI_ENDPOINT=https://api.openai.com/v1
KNOWLEDGE_FILE=knowledge.txt
RAG_MODE=user-augment            # or system-grounding
```

Ollama - Primera opció (sense clau, sense diners, sense accés a Internet):

```bash
OPENAI_ENDPOINT=http://localhost:11434/v1
MODEL=qwen3:1.7b
```

## Correr

```bash
uv run context_explorer_rag.py
```

Comandes a la xat:

| Comanda; ordre | El que fa |
|---|---|
| `/mode user-augment` · `/mode system-grounding` | canvia el lloc on es guarda el fitxer (restaurar la conversa). Sense arguments. Les opcions "on/off" funcionen; els espais, els guions i els alias curts (`system`/`grounding`/`sg`, `user`/`augment`/`ua`) es resoldran. |
| `/stateful` | activar/desactivar l'emmagatzematge d'una història augmentada (l'alternativa que manté el context) |
| `/file <path>` | carregar un fitxer de coneixement diferent |
| `/context` | imprimir el fitxer de coneixement carregat |
| (línia buida) | parar; deixar |

## La cosa important a tenir en compte

1. Formuleu una pregunta que el fitxer respongui, i després feu una segona pregunta relacionada. A la secció `user-augment`, consulteu el
endpoint Construir a la segona tornada: les tornades anteriors es passen per **sense cap element** – l'última tornada.
L'augmentació ha desaparegut. El fitxer només es afegeix al missatge actual.
2. La història de l'interfície d'usuari mai no conté el system prompt ni la augmentació. El model llegeix un
Més del que l'aplicació recorda.
3. Canviar a `system-grounding`. Ara el fitxer està al system prompt. L'usuari pot començar.
sense elements addicionals, i la recuperació es fa una sola vegada – la conversa és "pura".

## Com encaixar embeddings i RAG espais el següent

L'etapa de recuperació és una categoria específica, `WholeFileRetriever`. Tot el resta – la interfície d'usuari, el...
sense identitat endpoint, les plaques, l'token comptabilitat — són independents de la forma en què es recuperen
treballs. El següent pas implica canviar un `EmbeddingsRetriever` que incorpora la pregunta i la troba.
el més proper chunks, i retorna només aquests. **El bucle no es modifica. Només el component de recuperació.**
funciona. Això és l'arquitectura de RAG en un sol intercanvi.

## 📖 Llicència

Licensed under [Creative Commons BY-NC-SA 4.0](../../../week-01/demos/context-explorer/LICENSE) (`CC BY-NC-SA 4.0`).

## 👤 Autor

[@granludo](https://github.com/granludo) – Marc Alier, Universitat Politècnica de Catalunya (UPC)

---

© 2026 **Marc Alier i Forment** (Universitat Politècnica de Catalunya) · <https://wasabi.essi.upc.edu/ludo> · <https://lamb-project.org>
Curs per a agents de BSC — *Transformers, LLMs, RAG i Agents: Des del teòric a la pràctica*.
Licensed under [Creative Commons BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/): reuse must credit the author, no commercial use, derivatives under the same license.
