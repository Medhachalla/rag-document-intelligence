# DocSense AI Backend

Phase 1 FastAPI backend for PDF ingestion, local embeddings, Chroma retrieval, and Ollama answer generation.

## Run Locally

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API is available at `http://localhost:8000`.

Useful endpoints:

- `GET /api/v1/health`
- `POST /api/v1/documents/upload`
- `GET /api/v1/documents`
- `POST /api/v1/query`

Ollama should be running locally with the configured model, for example:

```bash
ollama pull llama3.2:3b
ollama serve
```

If Ollama is unavailable, `/query` still returns retrieved citations and an explanatory answer.
