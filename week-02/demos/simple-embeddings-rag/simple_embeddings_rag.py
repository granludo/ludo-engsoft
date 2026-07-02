# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# BSC Agents Course — Transformers, LLMs, RAG and Agents: From Theory to Production
# Licensed under Creative Commons BY-NC-SA 4.0 — reuse must credit the author, no commercial use, derivatives under the same license.

"""Simple embeddings RAG — retrieve by meaning, with a vector database (Chroma).

The single-file demo pasted the WHOLE file into the prompt every turn. That does not
scale: prompt_tokens climbs with the size of your knowledge, not with the question.

Here we do it properly. Once, at startup, we:
  1. CHUNK the knowledge file into overlapping pieces,
  2. EMBED each chunk (turn it into a vector) with an embeddings model,
  3. STORE the vectors in Chroma, a vector database.

Then, on every turn, we:
  4. EMBED the question,
  5. RETRIEVE only the few nearest chunks (search by meaning, not by keyword),
  6. INJECT just those chunks into the prompt and answer.

The payoff: we send a handful of chunks, not the whole library. Watch prompt_tokens
stay small and flat even as knowledge.txt grows — because we send what is RELEVANT,
not what is THERE. Notice too that the question and the chunk that answers it often
share almost no words: retrieval is by meaning.

Two models do two jobs: an EMBEDDINGS model (turns text into vectors) and a CHAT model
(writes the answer). Both are reached through the same OpenAI-compatible endpoint.

Empty line to quit. No persistence — the index lives in memory for this run.
"""
import os
from dotenv import load_dotenv
from openai import OpenAI
import chromadb

load_dotenv()

client = OpenAI(
    base_url=os.environ.get("OPENAI_ENDPOINT", "http://localhost:11434/v1"),
    api_key=os.environ.get("OPENAI_API_KEY", "ollama"),
)
MODEL = os.environ.get("MODEL", "qwen3:1.7b")            # writes the answers
EMBED_MODEL = os.environ.get("EMBED_MODEL", "nomic-embed-text")  # turns text into vectors

# The knobs of a RAG pipeline. Change them and feel the trade-offs:
#   CHUNK_SIZE  — bigger keeps facts together but pulls in noise; smaller is precise
#                 but can cut a single fact in two.
#   CHUNK_OVERLAP — a shared margin between chunks so a fact split at a boundary still
#                 survives whole in one of them.
#   TOP_K       — how many nearest chunks to retrieve and inject per question.
CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", "320"))
CHUNK_OVERLAP = int(os.environ.get("CHUNK_OVERLAP", "40"))
TOP_K = int(os.environ.get("TOP_K", "3"))


def embed(texts):
    """Turn a list of strings into a list of embedding vectors."""
    resp = client.embeddings.create(model=EMBED_MODEL, input=texts)
    return [row.embedding for row in resp.data]


def chunk(text, size, overlap):
    """Slide a window of `size` characters across the text, stepping by size-overlap."""
    step = max(1, size - overlap)
    pieces = []
    i = 0
    while i < len(text):
        piece = text[i:i + size].strip()
        if piece:
            pieces.append(piece)
        i += step
    return pieces


# --- Build the index once, at startup -----------------------------------------
text = open(os.path.join(os.path.dirname(__file__), "knowledge.txt")).read()
chunks = chunk(text, CHUNK_SIZE, CHUNK_OVERLAP)

# Chroma runs in-memory here. We hand it OUR embeddings (computed above) so nothing
# is hidden — Chroma's job is to store the vectors and find nearest neighbours fast.
# We ask it for cosine distance, the same geometry the embeddings lesson used.
collection = chromadb.EphemeralClient().create_collection(
    name="knowledge", metadata={"hnsw:space": "cosine"}
)
collection.add(
    ids=[f"chunk-{i}" for i in range(len(chunks))],
    embeddings=embed(chunks),
    documents=chunks,
)

print(f"Simple embeddings RAG · chat={MODEL} · embed={EMBED_MODEL}")
print(f"Indexed {len(chunks)} chunks (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP}) into Chroma. "
      f"Retrieving top-{TOP_K} per question.")
print("Ask about the document. Empty line to quit.\n")

history = []  # BARE turns only — what a real chat UI keeps; retrieved chunks are ephemeral

while True:
    question = input("you> ").strip()
    if not question:
        break

    # Retrieve by MEANING: embed the question, ask Chroma for the nearest chunks.
    hits = collection.query(query_embeddings=embed([question]), n_results=TOP_K)
    docs = hits["documents"][0]
    dists = hits["distances"][0]
    ids = hits["ids"][0]

    # Inject ONLY the retrieved chunks — not the whole file.
    context = "\n----\n".join(docs)
    augmented = f"Context:\n----\n{context}\n----\n\nQuestion: {question}"
    SYSTEM = "Answer using only the context. If it is not there, say so."
    messages = [{"role": "system", "content": SYSTEM}] + history + [{"role": "user", "content": augmented}]

    resp = client.chat.completions.create(model=MODEL, messages=messages)
    answer = resp.choices[0].message.content
    print(f"bot> {answer}")

    # Show what retrieval did: which chunks, how near, and how few tokens we sent.
    retrieved = ", ".join(f"{cid}(d={d:.3f})" for cid, d in zip(ids, dists))
    print(f"     [retrieved {retrieved}]")
    print(f"     [{resp.usage.prompt_tokens} prompt tokens — only {TOP_K} chunks rode along, "
          f"not the whole file]\n")

    history += [{"role": "user", "content": question},
                {"role": "assistant", "content": answer}]
