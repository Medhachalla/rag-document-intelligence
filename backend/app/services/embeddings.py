from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


@lru_cache
def _model() -> SentenceTransformer:
    settings = get_settings()
    logger.info("Loading embedding model model=%s", settings.embedding_model)
    return SentenceTransformer(settings.embedding_model)


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    try:
        embeddings = _model().encode(texts, normalize_embeddings=True)
    except Exception:
        logger.exception("Embedding generation failed count=%d", len(texts))
        raise

    logger.info("Embedding generation completed count=%d", len(texts))
    return embeddings.tolist()


def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]
