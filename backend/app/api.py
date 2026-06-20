from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile, status

from app.core.config import get_settings
from app.repositories import create_document, get_chunks_by_ids, get_document, list_documents
from app.schemas import Citation, DocumentResponse, QueryRequest, QueryResponse, UploadResponse
from app.services.embeddings import embed_query
from app.services.ingestion import process_document
from app.services.ollama import generate_answer
from app.services.vector_store import vector_store

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post(
    "/documents/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
) -> UploadResponse:
    settings = get_settings()
    original_name = Path(file.filename or "document.pdf").name
    is_pdf_name = original_name.lower().endswith(".pdf")
    is_pdf_type = file.content_type in {
        "application/pdf",
        "application/x-pdf",
        "application/octet-stream",
    }
    if not (is_pdf_name and is_pdf_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF uploads are supported.",
        )

    document_id = str(uuid4())
    stored_path = settings.upload_dir / f"{document_id}.pdf"

    contents = await file.read()
    if not contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded PDF is empty.",
        )
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"PDF exceeds the {settings.max_upload_mb} MB upload limit.",
        )
    stored_path.write_bytes(contents)

    document = create_document(document_id, original_name, str(stored_path))
    background_tasks.add_task(process_document, document_id, stored_path)

    return UploadResponse(
        id=document["id"],
        filename=document["filename"],
        status=document["status"],
        message="Upload accepted. Document processing has started.",
    )


@router.get("/documents", response_model=list[DocumentResponse])
def documents() -> list[DocumentResponse]:
    return [DocumentResponse(**document) for document in list_documents()]


@router.get("/documents/{document_id}", response_model=DocumentResponse)
def document_detail(document_id: str) -> DocumentResponse:
    document = get_document(document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    return DocumentResponse(**document)


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
