from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    error: str
    message: str
    citations: list["Citation"] | None = None


class DocumentResponse(BaseModel):
    id: str
    filename: str
    uploaded_at: str
    status: str
    chunk_count: int | None = None
    error_message: str | None = None


class UploadResponse(BaseModel):
    id: str
    filename: str
    status: str
    message: str


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000)
    top_k: int | None = Field(default=None, ge=1, le=10)


class Citation(BaseModel):
    document_id: str
    filename: str
    page_number: int | None
    chunk_id: str
    score: float | None
    text: str


class QueryResponse(BaseModel):
    answer: str
    citations: list[Citation]
