from pathlib import Path
from unittest.mock import patch


def test_process_document_stores_rich_vector_metadata(test_data_dir) -> None:
    from app.services.ingestion import process_document

    chunk_text = (
        "Actuators convert energy into controlled mechanical motion for valves, "
        "robotic arms, and other industrial mechanisms."
    )

    with patch(
        "app.services.ingestion.extract_pdf_pages",
        return_value=[{"page_number": 3, "text": chunk_text}],
    ), patch(
        "app.services.ingestion.get_document",
        return_value={"filename": "Actuators.pdf"},
    ), patch(
        "app.services.ingestion.embed_texts",
        return_value=[[0.1, 0.2, 0.3]],
    ), patch(
        "app.services.ingestion.vector_store"
    ) as mock_vector_store, patch(
        "app.services.ingestion.create_chunks"
    ), patch(
        "app.services.ingestion.update_document_status"
    ):
        process_document("doc-1", Path("stored.pdf"))

    _ids, _embeddings, texts, metadatas = mock_vector_store.upsert_chunks.call_args.args
    assert texts == [chunk_text]
    assert metadatas == [
        {
            "document_id": "doc-1",
            "filename": "Actuators.pdf",
            "page_number": 3,
            "chunk_index": 0,
            "text": chunk_text,
        }
    ]
