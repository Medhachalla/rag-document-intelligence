from fastapi import APIRouter

from app.core.config import get_settings
from app.core.exceptions import DocSenseError, OllamaError
from app.core.logging import get_logger
from app.repositories import get_chunks_by_ids
from app.schemas import Citation, QueryRequest, QueryResponse
from app.services.embeddings import embed_query
from app.services.ollama import format_source_context, generate_answer
from app.services.vector_store import vector_store

logger = get_logger(__name__)
router = APIRouter(
    tags=["Query"]
)


def _deduplicate_citations(citations: list[Citation]) -> list[Citation]:
    unique: dict[tuple[str, int | None, str], Citation] = {}

    for citation in citations:
        key = (citation.filename, citation.page_number, citation.text)
        existing = unique.get(key)
        existing_score = existing.score if existing and existing.score is not None else -1
        citation_score = citation.score if citation.score is not None else -1

        if existing is None or citation_score > existing_score:
            unique[key] = citation

    return list(unique.values())


@router.post(
    "/query",
    response_model=QueryResponse,
    summary="Query documents using RAG",
    description="""
    Answers questions using the uploaded document knowledge base.

    The RAG pipeline performs:
    - Query embedding generation
    - Semantic similarity search
    - Relevant context retrieval
    - AI response generation using the configured language model

    Returns:
    - Generated answer
    - Source citations
    - Relevant document references

    The response is grounded using retrieved document chunks.
    """,
    responses={
        400: {
            "description": "Invalid file type or invalid request"
        },
        413: {
            "description": "Uploaded file exceeds size limit"
        }
    },
    tags=["Query"]
)
async def query_documents(payload: QueryRequest) -> QueryResponse:
    settings = get_settings()
    top_k = payload.top_k or settings.retrieval_k
    question_embedding = embed_query(payload.question)
    matches = vector_store.query(
        question_embedding,
        top_k=top_k,
        min_score=settings.min_retrieval_score,
    )
    logger.info("Retrieval completed top_k=%d matches=%d", top_k, len(matches))

    if not matches:
        return QueryResponse(
            answer="No indexed document chunks matched the query. Upload and process PDFs first, or try a more specific question.",
            citations=[],
        )

    chunk_rows = get_chunks_by_ids([match["chunk_id"] for match in matches])
    citations: list[Citation] = []

    for match in matches:
        row = chunk_rows.get(match["chunk_id"])
        if not row:
            continue
        citations.append(
            Citation(
                document_id=row["document_id"],
                filename=row["filename"],
                page_number=row["page_number"],
                chunk_id=row["id"],
                score=match["score"],
                text=row["text"],
            )
        )

    citations = _deduplicate_citations(citations)
    context_chunks = [
        format_source_context(
            filename=citation.filename,
            page_number=citation.page_number,
            content=citation.text,
        )
        for citation in citations
    ]

    try:
        answer = await generate_answer(payload.question, context_chunks)
    except OllamaError as exc:
        logger.error(
            "Answer generation failed error=%s citations=%d",
            exc.error_code,
            len(citations),
        )
        raise DocSenseError(
            error_code=exc.error_code,
            message=exc.message,
            status_code=exc.status_code,
            citations=citations,
        ) from exc

    logger.info("Query response generated citations=%d", len(citations))
    return QueryResponse(answer=answer, citations=citations)
