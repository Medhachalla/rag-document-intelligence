from unittest.mock import patch

from app.core.config import get_settings


def test_upload_rejects_non_pdf(client) -> None:
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("notes.txt", b"hello world", "text/plain")},
    )

    assert response.status_code == 400
    body = response.json()
    assert body["error"] == "INVALID_FILE_TYPE"
    assert "message" in body


def test_upload_rejects_empty_pdf(client) -> None:
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("empty.pdf", b"", "application/pdf")},
    )

    assert response.status_code == 400
    assert response.json()["error"] == "EMPTY_FILE"


def test_upload_accepts_pdf(client, sample_pdf_bytes: bytes) -> None:
    with patch("app.api.documents.process_document"):
        response = client.post(
            "/api/v1/documents/upload",
            files={"file": ("report.pdf", sample_pdf_bytes, "application/pdf")},
        )

    assert response.status_code == 202
    body = response.json()
    assert body["filename"] == "report.pdf"
    assert body["status"] == "processing"
    assert body["id"]
    assert "Upload accepted" in body["message"]

    settings = get_settings()
    stored_path = settings.upload_dir / f"{body['id']}.pdf"
    assert stored_path.exists()


def test_list_and_get_document(client, sample_pdf_bytes: bytes) -> None:
    with patch("app.api.documents.process_document"):
        upload_response = client.post(
            "/api/v1/documents/upload",
            files={"file": ("manual.pdf", sample_pdf_bytes, "application/pdf")},
        )

    document_id = upload_response.json()["id"]

    list_response = client.get("/api/v1/documents")
    assert list_response.status_code == 200
    documents = list_response.json()
    assert any(document["id"] == document_id for document in documents)

    detail_response = client.get(f"/api/v1/documents/{document_id}")
    assert detail_response.status_code == 200
    document = detail_response.json()
    assert document["id"] == document_id
    assert document["filename"] == "manual.pdf"
    assert document["status"] == "processing"


def test_get_missing_document_returns_not_found(client) -> None:
    response = client.get("/api/v1/documents/missing-document-id")

    assert response.status_code == 404
    assert response.json()["error"] == "DOCUMENT_NOT_FOUND"
