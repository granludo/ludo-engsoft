<!-- =============================================================================================================== -->
<!-- Universitat Politècnica de Catalunya (UPC) -->
<!-- =============================================================================================================== -->

# Gestor/a de col·leccions

**Una eina proporcionada, no una demostració.** Una base de dades (embeddings) implementa taules indexades.
amb embeddings – anomenem aquestes taules **col·leccions**. Hi ha moltes implementacions.
allà; aquest paquet és la idea completa reduïda a **tres funcions**, implementades.
on [ChromaDB](https://www.trychroma.com/):

```python
from collections_manager import create_collection, insert, query

col = create_collection("handbook", description="Acme's product docs",
                        metric="cosine", persist_path="./my-collections")

insert(col, "The Pallet Pup has a top speed of 2.4 m/s.", {"source": "acme-handbook"})
# -> {"ok": True, "id": "acme-handbook::0", "error": None}

query(col, "how quick is the delivery robot?", top_k=3)
# -> [{"chunk": "...", "metadata": {"source": "acme-handbook", "chunk_number": 0},
#      "similarity": 0.71}, ...]
```

## API

| Funcció | El que fa |
|---|---|
| `create_collection(name, embedding_function=None, description="", metric="cosine", persist_path=None)` | Crear – o tornar a obrir – una col·lecció. Amb `persist_path`, es guarda al disc i sobreviureix als reinici; sense, en la memòria. `metric` és igual que `"cosine"` (més alt = més proper) o `"euclidean"` (més baix = més proper). |
| `insert(collection, chunk, metadata)` | Almacenar chunk. Retornar `{"ok", "id", "error"}`. La metadades han contenir almenys `source`; `chunk_number` (posició dins de la font) es assigna automàticament si no està present. Els identificadors són `source::chunk_number`, per tant, intentar reintroduir una posició falla correctament. |
| `query(collection, query_text, top_k=3, threshold=None)` | L'opció més propera chunks, la primera opció, cada una amb les seves metadades i el seu `similarity` (cosinus) o `distance` (euclidi). `threshold` = mínim similaritat / màxim distància. |

La funció per defecte embedding crida a qualsevol mòdul OpenAI compatible amb endpoint (des de `.env`:
`OPENAI_ENDPOINT`, `EMBED_MODEL`, `OPENAI_API_KEY` — valor per defecte de la ubicació Ollama +
`nomic-embed-text`, sense clau, sense cost. Podeu afegir la vostra pròpia.
`embedding_function(list[str]) -> list[list[float]]`. Una regla: tot dins d'un...
La col·lecció ha de ser creada amb el mateix model, o la geometria no tindrà cap significat.

## Per què necessitem una capa d'abstracció

Per a la majoria de projectes de petites a mitjanes dimensions, Chroma és més que suficient – mantingueu-ho senzill.
Però els requisits augmenten. Com que la vostra aplicació interactua amb aquesta interfície i no amb...
Directament amb Chroma, podeu canviar el motor que hi ha sota – pgvector, un servei gestionat en la nuvem.
magatzem, independentment del preu que algú estigui disposat a pagar – simplement, mitjançant la modificació d'un petit fitxer.
la vostra sol·licitud.

## Utilitzeu-lo en el vostre propi projecte.

Afegiu-ho com a dependència en la ruta del `pyproject.toml`:

```toml
dependencies = ["collections-manager"]

[tool.uv.sources]
collections-manager = { path = "../../collections-manager", editable = true }
```

(Ajusteu la ruta relativa. Vegeu `week-02/demos/04-collections-explorer/` per veure un exemple de com fer-ho.)

## 📖 Llicència

Licensed under [Creative Commons BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) (`CC BY-NC-SA 4.0`).

## 👤 Autor

[@granludo](https://github.com/granludo) – Marc Alier, Universitat Politècnica de Catalunya (UPC)
