from __future__ import annotations

from io import BytesIO
from typing import Iterator

import pytest
from fastapi.testclient import TestClient
from pypdf import PdfWriter

from app.core.config import get_settings


@pytest.fixture
def test_data_dir(tmp_path, monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    data_dir = tmp_path / "data"
    upload_dir = data_dir / "uploads"
    chroma_path = data_dir / "chroma"
    sqlite_path = data_dir / "test.db"

    monkeypatch.setenv("DOCSENSE_DATA_DIR", str(data_dir))
    monkeypatch.setenv("DOCSENSE_UPLOAD_DIR", str(upload_dir))
    monkeypatch.setenv("DOCSENSE_SQLITE_PATH", str(sqlite_path))
    monkeypatch.setenv("DOCSENSE_CHROMA_PATH", str(chroma_path))
    monkeypatch.setenv("DOCSENSE_OLLAMA_BASE_URL", "http://localhost:11434")
    monkeypatch.setenv("DOCSENSE_OLLAMA_MODEL", "test-model")
    monkeypatch.setenv("DOCSENSE_LOG_LEVEL", "WARNING")

    get_settings.cache_clear()

    import app.core.logging as logging_module

    logging_module._CONFIGURED = False

    yield


@pytest.fixture
def client(test_data_dir: None) -> Iterator[TestClient]:
    from app.main import create_app

    with TestClient(create_app()) as test_client:
        yield test_client


@pytest.fixture
def sample_pdf_bytes() -> bytes:
    buffer = BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    writer.write(buffer)
    return buffer.getvalue()
