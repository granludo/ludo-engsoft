# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# Curs per a agents de BSC — Transformers, LLMs, RAG i Agents: Des del teòric fins a la pràctica
# Amb llicència Creative Commons BY-NC-SA 4.0 – és obligatori citar l'autor, no es pot fer ús comercial, i les obres derivades han de tenir la mateixa llicència.

"""collections_manager – el gestor de bases de dades més senzill possible per a la creació d'índexs.

Una base de dades embeddings implementa taules indexades amb embeddings. Anomenem aquestes taules COLLECTIONS. Hi ha moltes implementacions (de codi obert, locals, en núvol); aquest paquet és la idea completa reduïda a tres funcions, que es troben a ChromaDB:

    create_collection(nom, ...) -> Recollida (en memòria, o persistida al disc) insert(recollida, chunk, metadades) -> {"ok", "id", "error"} query(recollida, text_de_consulta, top_k) -> [{"chunk", "metadades", "similitud"|"distància"}, ...]

Les metadades bàsiques són almenys `source` i `chunk_number` (dins de la font); `chunk_number` es assigna automàticament per a cada font quan no s'especifica.

Aquest és un conjunt d'eines, no una demostració: desenvolupa les teves aplicacions utilitzant AQUESTA interfície. Chroma és suficient per a projectes de petites a mitanes dimensions (mantén-ho senzill) — i perquè el teu codi interactua amb aquest nivell d'abstracció, pots canviar per un motor més potent en el futur, si algú està disposat a pagar-ne, sense modificar el codi de l'aplicació.
"""
import math
import os
from dataclasses import dataclass, field
from typing import Callable

import chromadb
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

__all__ = ["Collection", "create_collection", "insert", "query", "default_embedding_function"]

# Les dues mètriques de la embeddings conferència, mapejades als espais d'índex de Chroma.
# NOTA: L'espai "l2" de Chroma retorna la distància euclidiana al quadrat — prenem-ho com a valor.
# la arrel quadrada de `distance` significa el que va explicar la conferència.
_METRICS = {"cosine": "cosine", "euclidean": "l2"}


def default_embedding_function(texts: list[str]) -> list[list[float]]:
    """Integrar mitjançant qualsevol OpenAI compatible amb endpoint (per defecte: el Ollama local + nomic-embed-text)."""
    client = OpenAI(
        base_url=os.environ.get("OPENAI_ENDPOINT", "http://localhost:11434/v1"),
        api_key=os.environ.get("OPENAI_API_KEY", "ollama"),
    )
    model = os.environ.get("EMBED_MODEL", "nomic-embed-text")
    resp = client.embeddings.create(model=model, input=texts)
    return [row.embedding for row in resp.data]


@dataclass
class Collection:
    """Un manual per a una col·lecció específica: la seva taula Chroma + com incorporar-la + com mesurar-la."""
    name: str
    description: str
    metric: str  # «cosinus» | «euclidià»
    embedding_function: Callable[[list[str]], list[list[float]]]
    _chroma: "chromadb.Collection" = field(repr=False)

    def count(self) -> int:
        return self._chroma.count()


def create_collection(
    name: str,
    embedding_function: Callable[[list[str]], list[list[float]]] | None = None,
    description: str = "",
    metric: str = "cosine",
    persist_path: str | None = None,
) -> Collection:
    """Crear (o tornar a crear) una col·lecció.

    Amb `persist_path`, la col·lecció es guarda al disc en aquesta carpeta i persisteix després de reiniciar; sense això, es manté en memòria durant aquesta execució. `metric` és "cosinus" (més alt = més proper) o "euclidi" (més baix = més proper). Si no s'indica un `embedding_function`, es fa servir el valor per defecte (OpenAI compatible amb endpoint des de .env), que és tot allò que s'ha inserit en una col·lecció. PERÒ, tot allò que s'afegeix a una col·lecció ha d'estar representat pel mateix model, o la geometria no tindrà cap significat.
    """
    if metric not in _METRICS:
        raise ValueError(f"metric must be one of {list(_METRICS)}, got {metric!r}")
    client = chromadb.PersistentClient(path=persist_path) if persist_path else chromadb.EphemeralClient()
    chroma_col = client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": _METRICS[metric], "description": description},
    )
    return Collection(
        name=name,
        description=description,
        metric=metric,
        embedding_function=embedding_function or default_embedding_function,
        _chroma=chroma_col,
    )


def insert(collection: Collection, chunk: str, metadata: dict) -> dict:
    """Insereix un fragment amb les seves metadades. Retorna un missatge de "correcte" o "incorrect".

    `metadata` ha de contenir almenys `source` (indicant l'origen del fragment). `chunk_number` (posició dins d'aquesta font) es assigna automàticament – el següent número disponible per a aquesta font – tret que ho especifiqueu. L'ID del fragment és "<font>::<número_del_fragment>", de manera que si intenteu reintroduir la mateixa posició, no es duplica silenciosament, sinó que falla correctament.
    """
    if not chunk or not chunk.strip():
        return {"ok": False, "id": None, "error": "empty chunk"}
    if "source" not in metadata:
        return {"ok": False, "id": None, "error": "metadata must include 'source'"}
    meta = dict(metadata)
    if "chunk_number" not in meta:
        existing = collection._chroma.get(where={"source": meta["source"]})
        taken = [m.get("chunk_number", -1) for m in existing["metadatas"]]
        meta["chunk_number"] = (max(taken) + 1) if taken else 0
    chunk_id = f"{meta['source']}::{meta['chunk_number']}"
    if collection._chroma.get(ids=[chunk_id])["ids"]:
        # La funció `add()` de Chroma ignora silenciosament els IDs existents; és important verificar-los explícitament per assegurar-se que signifiquen el que es pretén.
        return {"ok": False, "id": chunk_id, "error": f"id {chunk_id!r} already exists"}
    try:
        [vector] = collection.embedding_function([chunk])
        collection._chroma.add(ids=[chunk_id], embeddings=[vector], documents=[chunk], metadatas=[meta])
        return {"ok": True, "id": chunk_id, "error": None}
    except Exception as e:  # embeddings endpoint cap avall, ...
        return {"ok": False, "id": chunk_id, "error": str(e)}


def query(collection: Collection, query_text: str, top_k: int = 3, threshold: float | None = None) -> list[dict]:
    """Recupera els fragments més propers a `query_text`, prioritzant-los per proximitat.

    Cada resultat inclou "chunk", "metadades" i "similitud" (cosinè, major valor = més proper), o "distància" (euclidiana, menor valor = més proper). `threshold`: filtres: mínima similitud per al cosinè, màxima distància per a l'euclidiana.
    """
    if collection.count() == 0:
        return []
    [query_vector] = collection.embedding_function([query_text])
    hits = collection._chroma.query(
        query_embeddings=[query_vector],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )
    results = []
    for chunk, meta, dist in zip(hits["documents"][0], hits["metadatas"][0], hits["distances"][0]):
        if collection.metric == "cosine":
            score_name, score = "similarity", 1.0 - dist          # chroma cosine retorna 1 - cos_sim
            if threshold is not None and score < threshold:
                continue
        else:
            score_name, score = "distance", math.sqrt(dist)       # La funció chroma L2 retorna la distància al quadrat.
            if threshold is not None and score > threshold:
                continue
        results.append({"chunk": chunk, "metadata": meta, score_name: round(score, 4)})
    return results
