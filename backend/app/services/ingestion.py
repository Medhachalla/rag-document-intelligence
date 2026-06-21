from pathlib import Path
from uuid import uuid4

from app.core.config import get_settings
from app.core.logging import get_logger
from app.repositories import create_chunks, get_document, update_document_status
from app.services.chunking import chunk_pages
from app.services.embeddings import embed_texts
from app.services.pdf import extract_pdf_pages
from app.services.vector_store import vector_store

logger = get_logger(__name__)


def process_document(document_id: str, path: Path) -> None:
    settings = get_settings()
    logger.info("Document processing started document_id=%s path=%s", document_id, path)

    try:
        pages = extract_pdf_pages(path)
        logger.info(
            "PDF extraction completed document_id=%s pages=%d",
            document_id,
            len(pages),
        )

        chunks = chunk_pages(
            pages,
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            min_chunk_chars=settings.min_chunk_chars,
        )
        logger.info(
            "Text chunking completed document_id=%s chunks=%d",
            document_id,
            len(chunks),
        )

        if not chunks:
            logger.error(
                "Document processing failed document_id=%s reason=no_extractable_text",
                document_id,
            )
            update_document_status(
                document_id,
                "failed",
                "No extractable text was found in the PDF.",
            )
            return

        document = get_document(document_id)
        filename = document["filename"] if document else path.name
        texts = [chunk.text for chunk in chunks]
        embeddings = embed_texts(texts)

        db_chunks = []
        vector_ids = []
        metadatas = []
        for index, chunk in enumerate(chunks):
            chunk_id = str(uuid4())
            vector_ids.append(chunk_id)
            metadatas.append(
                {
                    "document_id": document_id,
                    "filename": filename,
                    "page_number": chunk.page_number,
                    "chunk_index": index,
                    "text": chunk.text,
                }
            )
            db_chunks.append(
                {
                    "id": chunk_id,
                    "document_id": document_id,
                    "chunk_index": index,
                    "text": chunk.text,
                    "page_number": chunk.page_number,
                    "embedding_id": chunk_id,
                }
            )

        vector_store.upsert_chunks(vector_ids, embeddings, texts, metadatas)
        create_chunks(db_chunks)
        update_document_status(document_id, "ready")
        logger.info(
            "Document processing completed document_id=%s chunks=%d",
            document_id,
            len(chunks),
        )
    except Exception as exc:
        logger.exception(
            "Document processing failed document_id=%s",
            document_id,
        )
        update_document_status(document_id, "failed", str(exc))
        raise
