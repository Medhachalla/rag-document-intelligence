import pytest

from app.services.chunking import chunk_pages


def test_chunk_pages_filters_short_heading_chunks() -> None:
    pages = [
        {"page_number": 1, "text": "Actuators"},
        {
            "page_number": 2,
            "text": "Actuators convert energy into controlled mechanical motion for industrial systems.",
        },
    ]

    chunks = chunk_pages(
        pages,
        chunk_size=500,
        chunk_overlap=100,
        min_chunk_chars=80,
    )

    assert len(chunks) == 1
    assert chunks[0].page_number == 2
    assert chunks[0].text.startswith("Actuators convert energy")


def test_chunk_pages_rejects_invalid_min_chunk_chars() -> None:
    with pytest.raises(ValueError, match="min_chunk_chars"):
        chunk_pages(
            [{"page_number": 1, "text": "Enough text to reach the chunker."}],
            chunk_size=500,
            chunk_overlap=100,
            min_chunk_chars=0,
        )
