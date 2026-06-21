from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.documents import router as document_router
from app.api.health import router as health_router
from app.api.query import router as query_router
from app.core.config import get_settings
from app.core.exceptions import DocSenseError
from app.core.logging import get_logger, setup_logging
from app.db import init_db
from app.schemas import Citation, ErrorResponse

logger = get_logger(__name__)


def _serialize_citations(citations: list | None) -> list[dict] | None:
    if citations is None:
        return None
    serialized: list[dict] = []
    for citation in citations:
        if isinstance(citation, Citation):
            serialized.append(citation.model_dump())
        elif isinstance(citation, dict):
            serialized.append(citation)
        else:
            serialized.append(dict(citation))
    return serialized


def create_app() -> FastAPI:
    setup_logging()
    settings = get_settings()
    init_db()

    app = FastAPI(
        title="DocSense AI API",
        description="""
        AI-powered document intelligence platform using Retrieval Augmented Generation (RAG).

        Users can upload documents, index their contents,
        and query documents using semantic search and LLM-based generation.
        """,
        version="1.0.0"
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(DocSenseError)
    async def docsense_error_handler(
        _request: Request,
        exc: DocSenseError,
    ) -> JSONResponse:
        if exc.status_code >= 500:
            logger.error("API error: %s - %s", exc.error_code, exc.message)
        else:
            logger.warning("API error: %s - %s", exc.error_code, exc.message)

        body = ErrorResponse(
            error=exc.error_code,
            message=exc.message,
            citations=_serialize_citations(exc.citations),
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=body.model_dump(exclude_none=True),
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        _request: Request,
        exc: HTTPException,
    ) -> JSONResponse:
        detail = exc.detail
        if isinstance(detail, dict):
            error_code = str(detail.get("error", "HTTP_ERROR"))
            message = str(detail.get("message", "Request failed."))
        else:
            error_code = "HTTP_ERROR"
            message = str(detail)
        body = ErrorResponse(error=error_code, message=message)
        return JSONResponse(
            status_code=exc.status_code,
            content=body.model_dump(exclude_none=True),
        )

    app.include_router(health_router, prefix=settings.api_prefix)
    app.include_router(document_router, prefix=settings.api_prefix)
    app.include_router(query_router, prefix=settings.api_prefix)
    return app


app = create_app()
