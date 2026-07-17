<!-- =============================================================================================================== -->
<!-- Universitat Politècnica de Catalunya (UPC) -->
<!-- =============================================================================================================== -->

# 🗂️ Collections Manager

**Una eina que ja et donem feta, no pas una demo.** Una base de dades d'embeddings implementa
taules indexades amb embeddings: aquestes taules són el que anomenem **col·leccions**. N'hi ha
moltes implementacions; aquest paquet redueix tota la idea a **tres funcions**, construïdes sobre
[ChromaDB](https://www.trychroma.com/):

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

## L'API

| Funció | Què fa |
|---|---|
| `create_collection(name, embedding_function=None, description="", metric="cosine", persist_path=None)` | Crea —o torna a obrir— una col·lecció. Amb `persist_path` viu al disc i sobreviu als reinicis; sense, viu a la memòria. `metric` és `"cosine"` (com més alt, més a prop) o `"euclidean"` (com més baix, més a prop). |
| `insert(collection, chunk, metadata)` | Desa un chunk. Retorna `{"ok", "id", "error"}`. Les metadades han de portar com a mínim `source`; el `chunk_number` (la posició dins de la font) s'assigna automàticament si no hi és. Els identificadors són `source::chunk_number`, de manera que tornar a inserir una posició falla de manera neta. |
| `query(collection, query_text, top_k=3, threshold=None)` | Els chunks més propers, del més proper endavant, cadascun amb les seves metadades i el seu valor de `similarity` (cosinus) o `distance` (euclidiana). `threshold` = similitud mínima / distància màxima. |

La funció d'embedding per defecte crida qualsevol endpoint compatible amb OpenAI (des de `.env`:
`OPENAI_ENDPOINT`, `EMBED_MODEL`, `OPENAI_API_KEY` — per defecte, Ollama local +
`nomic-embed-text`, sense clau i sense cost). Pots passar-hi la teva pròpia
`embedding_function(list[str]) -> list[list[float]]`. Una única regla: tot el que hi ha dins d'una
col·lecció s'ha d'embedir amb el **mateix model**, o la geometria no vol dir res.

## Per què una capa d'abstracció

Per a la majoria de projectes petits i mitjans, Chroma ja fa de sobres el fet: no ho compliquis. Però
els requisits creixen. Com que la teva aplicació parla amb *aquesta* interfície i no directament amb
Chroma, pots canviar el motor de sota —pgvector, un magatzem al núvol gestionat, el que sigui que
algú estigui disposat a pagar— reescrivint un sol fitxer petit, no pas la teva aplicació.

## Fes-lo servir des del teu propi projecte

Afegeix-lo com a dependència de ruta al teu `pyproject.toml`:

```toml
dependencies = ["collections-manager"]

[tool.uv.sources]
collections-manager = { path = "../../collections-manager", editable = true }
```

(Ajusta la ruta relativa. Consulta `week-02/demos/04-collections-explorer/` per veure un exemple funcional.)

## 📖 Llicència

Licensed under [Creative Commons BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) (`CC BY-NC-SA 4.0`).

## 👤 Autor

[@granludo](https://github.com/granludo) — Marc Alier, Universitat Politècnica de Catalunya (UPC)
