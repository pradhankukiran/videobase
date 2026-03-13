from __future__ import annotations

from sentence_transformers import SentenceTransformer

from app.config import MODEL_NAME

_model: SentenceTransformer | None = None


def load_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    model = load_model()
    embeddings = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
    return embeddings.tolist()


def embed_query(query: str) -> list[float]:
    model = load_model()
    embedding = model.encode(query, show_progress_bar=False, normalize_embeddings=True)
    return embedding.tolist()
