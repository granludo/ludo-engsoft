# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# Curs per a agents de BSC — Transformers, LLMs, RAG i Agents: Des del teòric fins a la pràctica
# Amb llicència Creative Commons BY-NC-SA 4.0 – és obligatori citar l'autor, no es pot fer ús comercial, i les obres derivades han de tenir la mateixa llicència.

"""collections_manager — el gestor de bases de dades d'embeddings més senzill possible.

Una base de dades d'embeddings implementa taules indexades amb embeddings. Anomenem
aquestes taules COLLECTIONS. N'hi ha moltes implementacions (de codi obert, locals, al
núvol); aquest paquet redueix tota la idea a tres funcions, sobre ChromaDB:

    create_collection(name, ...)            -> Collection   (en memòria, o persistida al disc)
    insert(collection, chunk, metadata)     -> {"ok", "id", "error"}
    query(collection, query_text, top_k)    -> [{"chunk", "metadata", "similarity"|"distance"}, ...]

Les metadades bàsiques són com a mínim `source` i `chunk_number` (dins de la font);
`chunk_number` s'assigna automàticament per font quan no en dones cap.

Això és una utilitat que et donem, no una demo: construeix les teves aplicacions contra
AQUESTA interfície. Chroma fa de sobres per a projectes de mida petita a mitjana (mantén-ho
senzill) — i, com que el teu codi parla amb aquesta capa d'abstracció, més endavant pots
canviar-lo per un motor més potent, si algú està disposat a pagar-lo, sense tocar el codi
de l'aplicació.
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

# Les dues mètriques de la classe d'embeddings, mapejades als espais d'índex de Chroma.
# NOTA: l'espai "l2" de Chroma retorna la distància euclidiana AL QUADRAT — en fem
# l'arrel quadrada perquè `distance` signifiqui el que deia la classe.
_METRICS = {"cosine": "cosine", "euclidean": "l2"}


def default_embedding_function(texts: list[str]) -> list[list[float]]:
    """Genera embeddings mitjançant qualsevol endpoint compatible amb OpenAI (per defecte: Ollama local + nomic-embed-text)."""
    client = OpenAI(
        base_url=os.environ.get("OPENAI_ENDPOINT", "http://localhost:11434/v1"),
        api_key=os.environ.get("OPENAI_API_KEY", "ollama"),
    )
    model = os.environ.get("EMBED_MODEL", "nomic-embed-text")
    resp = client.embeddings.create(model=model, input=texts)
    return [row.embedding for row in resp.data]


@dataclass
class Collection:
    """Una referència a una col·lecció: la seva taula Chroma + com generar-ne els embeddings + com mesurar-la."""
    name: str
    description: str
    metric: str  # "cosine" | "euclidean"
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
    """Crea (o torna a obrir) una col·lecció.

    Amb `persist_path`, la col·lecció viu al disc en aquesta carpeta i sobreviu als
    reinicis; sense ell, viu en memòria durant aquesta execució. `metric` és "cosine"
    (més alt = més proper) o "euclidean" (més baix = més proper). Si no passes cap
    `embedding_function`, es fa servir la de per defecte (endpoint compatible amb OpenAI
    des de .env). Tot el que insereixes en una col·lecció S'HA d'haver representat amb el
    mateix model, o la geometria no vol dir res.
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
    """Insereix un fragment amb les seves metadades. Retorna un missatge d'èxit o d'error.

    `metadata` ha de portar com a mínim `source` (d'on ve el fragment). `chunk_number`
    (la posició dins d'aquesta font) s'assigna automàticament —el següent número lliure
    per a aquesta font— tret que el donis tu. L'id del fragment és "<source>::<chunk_number>",
    de manera que reinserir la mateixa posició falla netament en comptes de duplicar-la
    silenciosament.
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
        # L'add() de Chroma ignora silenciosament els id existents; ho comprovem explícitament perquè un error signifiqui error de veritat.
        return {"ok": False, "id": chunk_id, "error": f"id {chunk_id!r} already exists"}
    try:
        [vector] = collection.embedding_function([chunk])
        collection._chroma.add(ids=[chunk_id], embeddings=[vector], documents=[chunk], metadatas=[meta])
        return {"ok": True, "id": chunk_id, "error": None}
    except Exception as e:  # l'endpoint d'embeddings ha caigut, ...
        return {"ok": False, "id": chunk_id, "error": str(e)}


def query(collection: Collection, query_text: str, top_k: int = 3, threshold: float | None = None) -> list[dict]:
    """Recupera els fragments més propers a `query_text`, els més propers primer.

    Cada resultat és {"chunk", "metadata", i "similarity" (cosine, més alt = més
    proper) o "distance" (euclidean, més baix = més proper)}. `threshold` filtra:
    similitud mínima per a cosine, distància màxima per a euclidean.
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
            score_name, score = "distance", math.sqrt(dist)       # chroma l2 retorna la distància AL QUADRAT
            if threshold is not None and score > threshold:
                continue
        results.append({"chunk": chunk, "metadata": meta, score_name: round(score, 4)})
    return results
