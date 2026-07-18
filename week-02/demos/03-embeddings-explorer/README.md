<!-- =============================================================================================================== -->
<!-- Universitat Politècnica de Catalunya (UPC) -->
<!-- =============================================================================================================== -->

# 📐 Embeddings Explorer

El company del context explorer, per a la lliçó d'embeddings. Escriu una frase; la demo **l'embedeix**
(la converteix en una llista de números), **et mostra el vector** i, tot seguit, et mostra **com de
prop està de cada frase que has introduït abans** —mesurat de dues maneres alhora, en una taula
ordenada de la més propera a la més llunyana.

La lliçó és la idea única que hi ha darrere de tot el RAG dinàmic: **el significat es torna
geometria.** Un cop una frase és un punt a l'espai, «semblant» no és res més que «a prop», i li pots
posar un número.

## Les dues mètriques

| Mètrica | Què mesura | Com es llegeix |
|---|---|---|
| **similitud del cosinus** | l'angle entre els dos vectors | `1.0` = mateixa direcció · `0.0` = sense relació · **més alt = més a prop** |
| **distància euclidiana** | la separació en línia recta entre els dos punts | `0.0` = idèntics · **més baix = més a prop** |

Aquests models retornen vectors de **longitud unitària** (norma ≈ 1.0 —la demo ho mostra). Per a
vectors unitaris les dues mètriques donen el mateix ordre, perquè `distance² = 2·(1 − cosine)`. Així
tens dos noms per a una mateixa geometria, i pots veure com es posen d'acord.

## Configuració

```bash
cd embeddings-explorer
uv venv && source .venv/bin/activate && uv sync
```

Copia `.env.example` a `.env`. El valor per defecte és **Ollama local + `nomic-embed-text`** —sense
clau, sense cost—. Primer descarrega el model:

```bash
ollama serve
ollama pull nomic-embed-text
```

```bash
OPENAI_API_KEY=ollama
MODEL=nomic-embed-text
OPENAI_ENDPOINT=http://localhost:11434/v1
```

Per fer servir els embeddings de pagament d'OpenAI, apunta `.env` a `https://api.openai.com/v1` amb
una clau real i `MODEL=text-embedding-3-small`. El codi no canvia: només la configuració.

## Execució

```bash
uv run embeddings_explorer.py
```

Comandes dins del xat:

| Comanda | Què fa |
|---|---|
| *(escriu qualsevol frase)* | l'embedeix, en mostra el vector i el compara amb les anteriors |
| `/seed` | carrega unes quantes frases d'exemple perquè les distàncies surtin de seguida |
| `/list` | llista les frases introduïdes fins ara |
| `/clear` | ho oblida tot i comença de nou |
| *(línia buida)* | surt |

## El que has de notar

Executa `/seed` i, tot seguit, escriu **«how quick is the warehouse robot?»**. No té gairebé cap
paraula en comú amb *«The warehouse robot's top speed is 2.4 metres per second»* i, tot i així, cau
**la més propera** per totes dues mètriques. Els números segueixen el **significat**, no pas les
paraules compartides. Després escriu una recepta i mira com cau al final de tot. No hi ha
persistència: tanca el programa i l'espai desapareix.

## 📖 Llicència

Licensed under [Creative Commons BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) (`CC BY-NC-SA 4.0`).

## 👤 Autor

[@granludo](https://github.com/granludo) — Marc Alier, Universitat Politècnica de Catalunya (UPC)

---

© 2026 **Marc Alier i Forment** (Universitat Politècnica de Catalunya) · <https://wasabi.essi.upc.edu/ludo> · <https://lamb-project.org>
BSC Agents Course — *Transformers, LLMs, RAG and Agents: From Theory to Production*.
