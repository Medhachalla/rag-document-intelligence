from app.api.query import _deduplicate_citations
from app.schemas import Citation


def test_deduplicate_citations_keeps_highest_score_for_same_source() -> None:
    citations = [
        Citation(
            document_id="doc-1",
            filename="Accounting_Cheat_Sheet.pdf",
            page_number=1,
            chunk_id="chunk-low",
            score=0.72,
            text="Assets equal liabilities plus equity.",
        ),
        Citation(
            document_id="doc-2",
            filename="Accounting_Cheat_Sheet.pdf",
            page_number=1,
            chunk_id="chunk-high",
            score=0.91,
            text="Assets equal liabilities plus equity.",
        ),
    ]

    deduplicated = _deduplicate_citations(citations)

    assert len(deduplicated) == 1
    assert deduplicated[0].chunk_id == "chunk-high"
    assert deduplicated[0].score == 0.91
