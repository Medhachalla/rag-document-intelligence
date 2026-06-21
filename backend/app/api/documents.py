from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, File, UploadFile, status

from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.exceptions import (
    DocumentNotFoundError,
    EmptyFileError,
    FileTooLargeError,
    InvalidFileTypeError,
)
from app.repositories import create_document, get_document, list_documents
from app.schemas import DocumentResponse, UploadResponse
from app.services.ingestion import process_document

logger = get_logger(__name__)
router = APIRouter()


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
        raise InvalidFileTypeError()

    document_id = str(uuid4())
    stored_path = settings.upload_dir / f"{document_id}.pdf"

    contents = await file.read()
    if not contents:
        raise EmptyFileError()
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(contents) > max_bytes:
        raise FileTooLargeError(settings.max_upload_mb)
    stored_path.write_bytes(contents)

    document = create_document(document_id, original_name, str(stored_path))
    background_tasks.add_task(process_document, document_id, stored_path)
    logger.info(
        "Document upload accepted document_id=%s filename=%s size_bytes=%d",
        document_id,
        original_name,
        len(contents),
    )

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
        raise DocumentNotFoundError()
    return DocumentResponse(**document)
