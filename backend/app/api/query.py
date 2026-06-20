from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter

from app.core.config import get_settings
from app.repositories import create_document, get_chunks_by_ids, get_document, list_documents
from app.schemas import Citation, QueryRequest, QueryResponse
from app.services.embeddings import embed_query
from app.services.ingestion import process_document
from app.services.ollama import generate_answer
from app.services.vector_store import vector_store


from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

@router.post("/query", response_model=QueryResponse)
async def query_documents(payload: QueryRequest) -> QueryResponse:
    settings = get_settings()
    top_k = payload.top_k or settings.retrieval_k
    question_embedding = embed_query(payload.question)
    matches = vector_store.query(question_embedding, top_k=top_k)

    if not matches:
        return QueryResponse(
            answer="No indexed document chunks were found. Upload and process PDFs first.",
            citations=[],
        )

    chunk_rows = get_chunks_by_ids([match["chunk_id"] for match in matches])
    citations: list[Citation] = []
    context_chunks: list[str] = []

    for match in matches:
        row = chunk_rows.get(match["chunk_id"])
        if not row:
            continue
        context_chunks.append(row["text"])
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

    answer = await generate_answer(payload.question, context_chunks)
    return QueryResponse(answer=answer, citations=citations)

