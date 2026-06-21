# DocSense AI

A production-style Retrieval Augmented Generation (RAG) document intelligence system that allows users to upload PDF documents, perform semantic search over their contents, and generate AI-powered answers with source citations.

The system combines modern search infrastructure with local AI inference by using vector embeddings, ChromaDB retrieval, and Ollama-powered LLM generation.

The goal of this project is to explore how production RAG systems are designed: document ingestion pipelines, vector databases, retrieval strategies, API architecture, and reliable AI application engineering.

---

# Features

## Document Intelligence Pipeline

- Upload PDF documents through an API
- Extract text from documents
- Split documents into optimized chunks
- Generate semantic embeddings
- Store vectors for similarity search
- Retrieve relevant context for user queries

## AI Question Answering

- Ask natural language questions about uploaded documents
- Retrieve the most relevant document sections
- Generate answers using a local LLM
- Return citations with:
  - document name
  - page number
  - retrieved text

## Backend Engineering

- FastAPI REST architecture
- Service-layer separation
- SQLite metadata storage
- ChromaDB vector storage
- Background document processing
- Structured API error handling
- Configurable pipeline parameters
- Automated testing

---

# System Architecture

```
                    User
                      |
                      v
              React Frontend
                      |
                      v
              FastAPI Backend
                      |
        --------------------------------
        |              |               |
        v              v               v

    SQLite        ChromaDB          Ollama
  Metadata        Vectors            LLM
        |
        |
        v

Document Processing Pipeline


PDF Upload

     |
     v

Text Extraction

     |
     v

Chunking

     |
     v

Embedding Generation

     |
     v

Vector Storage

     |
     v

Semantic Retrieval

     |
     v

LLM Answer Generation

     |
     v

Response + Citations
```

---

# Technical Stack

## Frontend

- React
- JavaScript
- REST API integration

## Backend

- Python
- FastAPI
- Pydantic
- SQLite

## AI / Search

- Sentence Transformers embeddings
- ChromaDB vector database
- Ollama local LLM inference

## Testing

- Pytest
- Mocked AI/vector dependencies for deterministic tests

---

# How RAG Works In This Project

Traditional search matches keywords.

RAG performs semantic search.

Example:

A user asks:

```
"What are actuators used for?"
```

The system does not search for the exact words.

Instead:

1. The question is converted into an embedding vector.
2. ChromaDB compares this vector against document chunk embeddings.
3. The most relevant chunks are retrieved.
4. The retrieved context is passed to the LLM.
5. The LLM generates an answer grounded in the retrieved documents.

This reduces hallucination because the model answers using retrieved document evidence.

---

# Project Structure

```
docsense-ai/

├── frontend/
│
│   └── React application
│
├── backend/
│
│   ├── app/
│   │
│   ├── api/
│   │   └── REST endpoints
│   │
│   ├── services/
│   │   ├── document ingestion
│   │   ├── PDF extraction
│   │   ├── embeddings
│   │   ├── vector search
│   │   └── LLM generation
│   │
│   ├── core/
│   │   └── configuration and logging
│   │
│   └── tests/
│
└── README.md
```

---

# Setup

## Prerequisites

Install:

- Python 3.11+
- Node.js
- Ollama


---

# Backend Setup

Navigate to backend:

```bash
cd backend
```

Create virtual environment:

```bash
python3 -m venv .venv
```

Activate:

Linux/macOS:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Environment Configuration

Create:

```
backend/.env
```

Example:

```env
DOCSENSE_OLLAMA_BASE_URL=http://localhost:11434
DOCSENSE_OLLAMA_MODEL=llama3.2:3b
DOCSENSE_OLLAMA_TIMEOUT_SECONDS=120

DOCSENSE_CHUNK_SIZE=500
DOCSENSE_CHUNK_OVERLAP=100
DOCSENSE_MIN_CHUNK_CHARS=80
DOCSENSE_MIN_RETRIEVAL_SCORE=0.2
```

These variables control:

### Ollama Configuration

`OLLAMA_BASE_URL`

Location of local LLM server.

`OLLAMA_MODEL`

Model used for answer generation.

`OLLAMA_TIMEOUT_SECONDS`

Maximum generation wait time.

---

### RAG Configuration

`CHUNK_SIZE`

Maximum size of document chunks.

`CHUNK_OVERLAP`

Overlap between chunks to preserve context.

`MIN_CHUNK_CHARS`

Removes very small useless chunks such as isolated headings.

`MIN_RETRIEVAL_SCORE`

Filters low-quality similarity matches.

---

## Start Ollama

Pull model:

```bash
ollama pull llama3.2:3b
```

Start server:

```bash
ollama serve
```

---

## Run Backend

From backend:

```bash
uvicorn app.main:app --reload
```

Backend runs at:

```
http://localhost:8000
```

API documentation:

```
http://localhost:8000/docs
```

---

# Frontend Setup

Navigate:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Run:

```bash
npm run dev
```

---

# API Examples

## Upload Document

Endpoint:

```
POST /api/v1/documents/upload
```

Purpose:

Uploads a PDF and starts document ingestion.

Flow:

```
PDF Upload
      |
      v
Validation
      |
      v
Background Processing
      |
      v
Text Extraction
      |
      v
Embedding Generation
      |
      v
Vector Storage
```

Example:

```bash
curl -X POST \
http://localhost:8000/api/v1/documents/upload \
-F "file=@example.pdf"
```

Response:

```json
{
  "document_id": "1234",
  "filename": "example.pdf",
  "status": "processing"
}
```

---

# Query Documents

Endpoint:

```
POST /api/v1/query
```

Purpose:

Performs semantic search and generates an answer using retrieved document context.

Request:

```json
{
  "question": "What are actuators used for?",
  "top_k": 3
}
```

Processing:

```
Question

   |
   v

Embedding Generation

   |
   v

Vector Similarity Search

   |
   v

Retrieve Relevant Chunks

   |
   v

LLM Generation

   |
   v

Answer + Citations
```

Response:

```json
{
  "answer": "Actuators convert energy into motion...",
  "citations": [
    {
      "filename": "Actuators.pdf",
      "page_number": 1,
      "score": 0.85,
      "text": "An actuator is..."
    }
  ]
}
```

The citation metadata allows users to verify that answers are grounded in the original document.

---

# Error Handling

All API errors follow a consistent format:

```json
{
  "error": "ERROR_CODE",
  "message": "Human readable explanation"
}
```

Example:

```json
{
  "error": "OLLAMA_UNAVAILABLE",
  "message": "Unable to generate answer. Start Ollama service."
}
```

---

# Testing

Run backend tests:

```bash
cd backend

pytest -v
```

Tests cover:

- document chunking
- ingestion pipeline
- vector retrieval
- API behavior
- error handling

External services such as Ollama and Chroma are isolated/mocked during tests.

---

# Engineering Decisions

## Why ChromaDB?

A vector database enables semantic retrieval rather than keyword matching.

## Why local Ollama?

Allows private AI inference without external API costs.

## Why separate SQLite and Chroma?

SQLite stores application metadata.

Chroma stores high-dimensional vector representations.

Keeping responsibilities separate improves maintainability.

## Why service-layer architecture?

The backend separates:

- API handling
- business logic
- data access
- AI components

making the system easier to test and extend.

---

# Future Improvements

- Hybrid keyword + semantic search
- Reranking models
- Multi-document conversations
- Streaming LLM responses
- Cloud deployment
- Authentication and user document isolation