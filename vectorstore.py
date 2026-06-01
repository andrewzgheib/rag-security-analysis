import sys
from typing import Any
import chromadb
from chromadb import Collection
from embeddings import embed_documents, embed_query
from config import CHROMA_PERSIST_DIR, CHROMA_COLLECTION_NAME, TOP_K

if not CHROMA_PERSIST_DIR:
    raise EnvironmentError("[!] CHROMA_PERSIST_DIR is not set in config.py.")

if not CHROMA_COLLECTION_NAME:
    raise EnvironmentError("[!] CHROMA_COLLECTION_NAME is not set in config.py.")

if not TOP_K:
    raise EnvironmentError("[!] TOP_K is not set in config.py.")

def get_client() -> chromadb.PersistentClient:
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    if not client:
        raise EnvironmentError(
            f"[!] Failed to initialize ChromaDB client with persistence at '{CHROMA_PERSIST_DIR}'. "
            "Please check config.py."
        )
    return chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)

def get_collection(client = None) -> Collection:
    if client is None:
        client = get_client()
    return client.get_or_create_collection(
        name=CHROMA_COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
    )

def collection_count() -> int:
    return get_collection().count()

def ingest_chunks(chunks: list[str], source: str = "website") -> None:
    collection = get_collection()
    embeddings = embed_documents(chunks)
    ids = [f"{source}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [{"source": source, "chunk_id": i} for i in range(len(chunks))]
    collection.upsert(ids=ids, embeddings=embeddings, documents=chunks, metadatas=metadatas)

def ingest_vault_chunks(chunks: list[dict]) -> None:
    if not chunks:
        return

    collection = get_collection()

    texts = [c["text"] for c in chunks]
    embeddings = embed_documents(texts)

    # Build deterministic IDs keyed on file path + position within that file
    file_counter: dict[str, int] = {}
    ids: list[str] = []
    for c in chunks:
        # Normalise path separators and non-alphanum chars so IDs are safe
        safe_file = c["file"].replace("\\", "/").replace("/", "__").replace(" ", "_")
        idx = file_counter.get(safe_file, 0)
        file_counter[safe_file] = idx + 1
        ids.append(f"{c['source']}_{safe_file}_{idx}")

    metadatas = [
        {
            "source": c["source"],
            "file":   c["file"],
            "note":   c["note"],
            "chunk_id": i,
        }
        for i, c in enumerate(chunks)
    ]

    collection.upsert(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)

# Ingest arbitrary text with custom IDs, used by exploit scripts
def ingest_arbitrary(texts: list[str], ids: list[str], source: str = "injected") -> None:
    collection = get_collection()
    embeddings = embed_documents(texts)
    metadatas = [{"source": source, "chunk_id": i} for i in range(len(texts))]
    collection.upsert(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)

def query_store(query: str, top_k: int = TOP_K, where: dict | None = None) -> list[dict]:
    collection = get_collection()
    q_embedding = embed_query(query)

    kwargs: dict = dict(
        query_embeddings=[q_embedding],
        n_results=min(top_k, collection.count()),
        include=["documents", "distances", "metadatas"],
    )
    if where:
        kwargs["where"] = where

    results = collection.query(**kwargs)

    return [
        {"id": rid, "document": doc, "metadata": meta, "distance": dist}
        for doc, meta, dist, rid in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
            results["ids"][0],
        )
    ]

def list_all_chunks(limit: int = 100) -> list[dict]:
    collection = get_collection()
    result = collection.get(limit=limit, include=["documents", "metadatas"])
    return [
        {"id": rid, "document": doc, "metadata": meta}
        for rid, doc, meta in zip(
            result["ids"], result["documents"], result["metadatas"]
        )
    ]

def delete_by_ids(ids: list[str]) -> None:
    get_collection().delete(ids=ids)

def delete_by_source(source: str) -> None:
    get_collection().delete(where={"source": source})

def reset_collection() -> None:
    client = get_client()
    client.delete_collection(CHROMA_COLLECTION_NAME)
    client.get_or_create_collection(
        name=CHROMA_COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
    )