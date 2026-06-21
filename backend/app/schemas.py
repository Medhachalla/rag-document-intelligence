from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    error: str
    message: str
    citations: list["Citation"] | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "error": "OLLAMA_UNAVAILABLE",
                "message": "Unable to generate an answer because the language model service is unavailable.",
                "citations": [
                    {
                        "document_id": "a7f3d9c1-1234-4567-8901-example",
                        "filename": "software_architecture.pdf",
                        "page_number": 12,
                        "chunk_id": "chunk-001",
                        "score": 0.87,
                        "text": "The system uses a service-oriented architecture with independent backend components."
                    }
                ]
            }
        }
    }


class DocumentResponse(BaseModel):
    id: str
    filename: str
    uploaded_at: str
    status: str
    chunk_count: int | None = None
    error_message: str | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "a7f3d9c1-1234-4567-8901-example",
                "filename": "software_architecture.pdf",
                "uploaded_at": "2026-06-21T11:57:45",
                "status": "ready",
                "chunk_count": 42,
                "error_message": None
            }
        }
    }


class UploadResponse(BaseModel):
    id: str
    filename: str
    status: str
    message: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "a7f3d9c1-1234-4567-8901-example",
                "filename": "engineering_design_document.pdf",
                "status": "processing",
                "message": "Document uploaded successfully and processing has started."
            }
        }
    }


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000)
    top_k: int | None = Field(default=None, ge=1, le=10)

    model_config = {
        "json_schema_extra": {
            "example": {
                "question": "How does the authentication system work?",
                "top_k": 3
            }
        }
    }


class Citation(BaseModel):
    document_id: str
    filename: str
    page_number: int | None
    chunk_id: str
    score: float | None
    text: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "document_id": "a7f3d9c1-1234-4567-8901-example",
                "filename": "software_architecture.pdf",
                "page_number": 12,
                "chunk_id": "chunk-001",
                "score": 0.87,
                "text": "The authentication service validates user credentials and issues access tokens."
            }
        }
    }


class QueryResponse(BaseModel):
    answer: str
    citations: list[Citation]

    model_config = {
        "json_schema_extra": {
            "example": {
                "answer": "The authentication service validates credentials and generates access tokens for authorized users.",
                "citations": [
                    {
                        "document_id": "a7f3d9c1-1234-4567-8901-example",
                        "filename": "software_architecture.pdf",
                        "page_number": 12,
                        "chunk_id": "chunk-001",
                        "score": 0.87,
                        "text": "The authentication service validates user credentials and issues access tokens."
                    }
                ]
            }
        }
    }