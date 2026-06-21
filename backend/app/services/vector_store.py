from typing import Any

import chromadb

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class VectorStore:
    def __init__(self) -> None:
        settings = get_settings()
        self._client = chromadb.PersistentClient(path=str(settings.chroma_path))
        self._collection = self._client.get_or_create_collection(
            name=settings.chroma_collection,
            metadata={"hnsw:space": "cosine"},
        )

    def upsert_chunks(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        texts: list[str],
        metadatas: list[dict[str, Any]],
    ) -> None:
        if not ids:
            return

        try:
            self._collection.upsert(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
            )
        except Exception:
            logger.exception("Vector store upsert failed count=%d", len(ids))
            raise

        logger.info("Vector store upsert completed count=%d", len(ids))

    def query(
        self,
        embedding: list[float],
        top_k: int,
        min_score: float | None = None,
    ) -> list[dict[str, Any]]:
        try:
            results = self._collection.query(
                query_embeddings=[embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"],
            )
        except Exception:
            logger.exception("Vector store query failed top_k=%d", top_k)
            raise

        ids = results.get("ids", [[]])[0]
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        matches: list[dict[str, Any]] = []
        for index, chunk_id in enumerate(ids):
            distance = distances[index] if index < len(distances) else None
            score = None if distance is None else 1 - float(distance)
            if min_score is not None and (score is None or score < min_score):
                continue
            matches.append(
                {
                    "chunk_id": chunk_id,
                    "text": documents[index] if index < len(documents) else "",
                    "metadata": metadatas[index] if index < len(metadatas) else {},
                    "score": score,
                }
            )

        logger.info(
            "Vector store query completed top_k=%d min_score=%s matches=%d",
            top_k,
            min_score,
            len(matches),
        )
        return matches


class LazyVectorStore:
    def __init__(self) -> None:
        self._store: VectorStore | None = None

    def _get_store(self) -> VectorStore:
        if self._store is None:
            self._store = VectorStore()
        return self._store

    def upsert_chunks(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        texts: list[str],
        metadatas: list[dict[str, Any]],
    ) -> None:
        self._get_store().upsert_chunks(ids, embeddings, texts, metadatas)

    def query(
        self,
        embedding: list[float],
        top_k: int,
        min_score: float | None = None,
    ) -> list[dict[str, Any]]:
        return self._get_store().query(embedding, top_k, min_score)


vector_store = LazyVectorStore()
