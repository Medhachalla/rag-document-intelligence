from pathlib import Path
from uuid import uuid4

from app.core.config import get_settings
from app.repositories import create_chunks, update_document_status
from app.services.chunking import chunk_pages
from app.services.embeddings import embed_texts
from app.services.pdf import extract_pdf_pages
from app.services.vector_store import vector_store


def process_document(document_id: str, path: Path) -> None:
    settings = get_settings()

    try:
        pages = extract_pdf_pages(path)
        chunks = chunk_pages(
            pages,
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )

        if not chunks:
            update_document_status(
                document_id,
                "failed",
                "No extractable text was found in the PDF.",
            )
            return

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
                    "page_number": chunk.page_number,
                    "chunk_index": index,
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
    except Exception as exc:
        update_document_status(document_id, "failed", str(exc))
        raise
