from __future__ import annotations

import chromadb

from app.config import CHROMA_DIR, SEARCH_TOP_K
from app.models.schemas import Chunk, SearchResult
from app.services.embedder import embed_query, embed_texts

_client: chromadb.PersistentClient | None = None


def get_client() -> chromadb.PersistentClient:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return _client


def index_video(video_id: str, chunks: list[Chunk]) -> int:
    """Embed and store chunks for a video. Returns number of chunks indexed."""
    client = get_client()
    # Delete existing collection if re-uploading
    try:
        client.delete_collection(name=video_id)
    except Exception:
        pass

    collection = client.create_collection(
        name=video_id,
        metadata={"hnsw:space": "cosine"},
    )

    texts = [c.text for c in chunks]
    embeddings = embed_texts(texts)

    collection.add(
        ids=[f"{video_id}_chunk_{c.chunk_index}" for c in chunks],
        embeddings=embeddings,
        documents=texts,
        metadatas=[
            {
                "start_time": c.start_time,
                "end_time": c.end_time,
                "chunk_index": c.chunk_index,
            }
            for c in chunks
        ],
    )
    return len(chunks)


def search_video(video_id: str, query: str, top_k: int = SEARCH_TOP_K) -> list[SearchResult]:
    """Search chunks for a video by semantic similarity."""
    client = get_client()
    try:
        collection = client.get_collection(name=video_id)
    except ValueError:
        return []

    query_embedding = embed_query(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    search_results = []
    if results["documents"] and results["documents"][0]:
        for doc, meta, distance in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            # ChromaDB cosine distance for normalized vectors: 0 = identical, ~1 = orthogonal
            score = max(0.0, 1.0 - distance)
            if score < 0.05:
                continue
            search_results.append(SearchResult(
                start_time=meta["start_time"],
                end_time=meta["end_time"],
                text=doc,
                score=round(score, 4),
            ))

    return search_results
