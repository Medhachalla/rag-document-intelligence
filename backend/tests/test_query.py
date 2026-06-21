from unittest.mock import AsyncMock, patch

from app.core.exceptions import OllamaUnavailableError


def test_query_returns_answer_and_citations(client) -> None:
    mock_matches = [
        {
            "chunk_id": "chunk-1",
            "score": 0.92,
            "text": "Actuators control mechanical movement in industrial systems.",
            "metadata": {},
        }
    ]
    mock_rows = {
        "chunk-1": {
            "id": "chunk-1",
            "document_id": "doc-1",
            "filename": "manual.pdf",
            "page_number": 4,
            "text": "Actuators control mechanical movement in industrial systems.",
        }
    }

    mock_generate_answer = AsyncMock(return_value="Actuators convert energy into motion.")

    with patch("app.api.query.embed_query", return_value=[0.1, 0.2, 0.3]), \
         patch("app.api.query.vector_store") as mock_vector_store, \
         patch("app.api.query.get_chunks_by_ids", return_value=mock_rows), \
         patch("app.api.query.generate_answer", new=mock_generate_answer):
        mock_vector_store.query.return_value = mock_matches
        response = client.post(
            "/api/v1/query",
            json={"question": "What are actuators?"},
        )

    mock_vector_store.query.assert_called_once_with(
        [0.1, 0.2, 0.3],
        top_k=5,
        min_score=0.2,
    )
    generated_context = mock_generate_answer.await_args.args[1]
    assert "File:\nmanual.pdf" in generated_context[0]
    assert "Page:\n4" in generated_context[0]
    assert "Content:\nActuators control" in generated_context[0]

    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "Actuators convert energy into motion."
    assert len(body["citations"]) == 1

    citation = body["citations"][0]
    assert citation["document_id"] == "doc-1"
    assert citation["filename"] == "manual.pdf"
    assert citation["page_number"] == 4
    assert citation["chunk_id"] == "chunk-1"
    assert citation["score"] == 0.92
    assert "Actuators control mechanical movement" in citation["text"]


def test_query_with_no_matches_returns_helpful_answer(client) -> None:
    with patch("app.api.query.embed_query", return_value=[0.1, 0.2]), \
         patch("app.api.query.vector_store") as mock_vector_store:
        mock_vector_store.query.return_value = []
        response = client.post(
            "/api/v1/query",
            json={"question": "What is in the documents?"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["citations"] == []
    assert "No indexed document chunks" in body["answer"]


def test_query_ollama_failure_preserves_citations(client) -> None:
    mock_matches = [
        {
            "chunk_id": "chunk-1",
            "score": 0.88,
            "text": "Hydraulic actuators use fluid pressure.",
            "metadata": {},
        }
    ]
    mock_rows = {
        "chunk-1": {
            "id": "chunk-1",
            "document_id": "doc-1",
            "filename": "systems.pdf",
            "page_number": 7,
            "text": "Hydraulic actuators use fluid pressure.",
        }
    }

    with patch("app.api.query.embed_query", return_value=[0.5, 0.4]), \
         patch("app.api.query.vector_store") as mock_vector_store, \
         patch("app.api.query.get_chunks_by_ids", return_value=mock_rows), \
         patch(
             "app.api.query.generate_answer",
             new=AsyncMock(side_effect=OllamaUnavailableError()),
         ):
        mock_vector_store.query.return_value = mock_matches
        response = client.post(
            "/api/v1/query",
            json={"question": "How do hydraulic actuators work?"},
        )

    assert response.status_code == 503
    body = response.json()
    assert body["error"] == "OLLAMA_UNAVAILABLE"
    assert len(body["citations"]) == 1
    assert body["citations"][0]["filename"] == "systems.pdf"
    assert body["citations"][0]["page_number"] == 7
