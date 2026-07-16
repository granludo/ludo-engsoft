<!-- =============================================================================================================== -->
<!-- Universitat Politècnica de Catalunya (UPC) -->
<!-- =============================================================================================================== -->

# 📐 Embeddings Explorador

Acompanyament per a l'explorador de context, per a la [embeddings] lliçó. Escriu una frase; el programa demostra.
**el integra** (el transforma en una llista de números), **mostra el vector**, i després mostra **com**.
És igual al nombre de frases que he introduit abans **— mesurat de dues maneres simultàniament, en una taula**
ordenament per proximitat.

La lliçó és la idea central que es troba al darrere de tot el concepte de RAG: **el significat es converteix en geometria**. Un cop...
Una frase és un punt en l'espai, "semblant" simplement significa "proper", i es pot assignar un número a això.

## Les dues mètriques

| Mètric | Què mesura | Lectura |
|---|---|---|
| **similitud cosinada** | l'angle entre els dos vectors | `1.0` = mateixa direcció · `0.0` = no relacionada · **més alt = més proper** |
| **Distància euclidiana** | la distància recta entre els dos punts | `0.0` = idèntic · **menys = més proper** |

Aquests models retornen vectors de longitud unitària (norma ≈ 1.0 – la demo ho mostra). Per a vectors
unitaris, les dues mètriques donen el mateix rànquing, perquè `distance² = 2·(1 − cosine)`. Així,
Troba dos noms per a una mateixa geometria, i pots veure com es posen d'acord.

## Configuració

```bash
cd embeddings-explorer
uv venv && source .venv/bin/activate && uv sync
```

Còpia `.env.example` a `.env`. L'opció per defecte és **Ollama local + `nomic-embed-text`** – sense tecla.
sense costos. Primer, treu el model:

```bash
ollama serve
ollama pull nomic-embed-text
```

```bash
OPENAI_API_KEY=ollama
MODEL=nomic-embed-text
OPENAI_ENDPOINT=http://localhost:11434/v1
```

Per utilitzar les "embeddings" pagades d'OpenAI, assigneu el valor `.env` al valor `https://api.openai.com/v1` amb un
Clau real i `MODEL=text-embedding-3-small`. El codi no canvia; només la configuració.

## Correr

```bash
uv run embeddings_explorer.py
```

Comandes a la xat:

| Comanda; ordre | El que fa |
|---|---|
| (escriu qualsevol frase) | incorporar-lo, mostrar el vector, comparar-lo amb els anteriors |
| `/seed` | Carregar algunes frases d'exemple perquè les distàncies es visualitzin immediatament. |
| `/list` | enumerar les frases que s'han introduit fins ara |
| `/clear` | Oblida tot i comença de nou. |
| (línia buida) | parar; deixar |

## La cosa important a tenir en compte

Premi a `/seed`, després introdueix "**quant de temps tarda el robot d'almacenament?**". Té gairebé cap paraula.
semblant al que diu "*La velocitat màxima del robot d'almacenament és de 2,4 metres per segon*", però aconsegueix aterrar.
**el més proper**, tant en termes de distància com en altres mètriques. Els números reflecteixen el **significat**, no les paraules compartides. Després, introdueix
receta i observa com cau al fons. No hi ha cap continuïtat: tanca el programa i...
L'espai s'ha acabat.

## 📖 Llicència

Licensed under [Creative Commons BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) (`CC BY-NC-SA 4.0`).

## 👤 Autor

[@granludo](https://github.com/granludo) – Marc Alier, Universitat Politècnica de Catalunya (UPC)

---

© 2026 **Marc Alier i Forment** (Universitat Politècnica de Catalunya) · <https://wasabi.essi.upc.edu/ludo> · <https://lamb-project.org>
Curs per a agents de BSC — *Transformers, LLMs, RAG i Agents: Des del teòric a la pràctica*.
