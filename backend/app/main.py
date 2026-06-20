from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.documents import router as document_router
from app.api.query import router as query_router
from app.core.config import get_settings
from app.db import init_db
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    init_db()

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Enterprise-style RAG document search API.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    settings = get_settings()

    app.include_router(
        document_router,
        prefix=settings.api_prefix
    )

    app.include_router(
        query_router,
        prefix=settings.api_prefix
    )
    return app


app = create_app()
