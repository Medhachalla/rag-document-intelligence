from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "DocSense AI"
    api_prefix: str = "/api/v1"
    data_dir: Path = Path("backend/data")
    upload_dir: Path = Path("backend/data/uploads")
    sqlite_path: Path = Path("backend/data/docsense.db")
    chroma_path: Path = Path("backend/data/chroma")
    chroma_collection: str = "document_chunks"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    chunk_size: int = 900
    chunk_overlap: int = 180
    retrieval_k: int = 5
    max_upload_mb: int = 25
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"
    ollama_timeout_seconds: float = 120.0

    model_config = SettingsConfigDict(env_prefix="DOCSENSE_", env_file=".env")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    settings.chroma_path.mkdir(parents=True, exist_ok=True)
    return settings
