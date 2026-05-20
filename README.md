# ContextLens / Summarize Bot

ContextLens is a FastAPI-based summarization project with a lightweight frontend.
It supports two main workflows:

- Quick summaries from pasted text
- Document-based summaries using upload, text extraction, embeddings, vector search, and RAG

Today, the project includes a working backend API, a simple browser UI, local document ingestion, Ollama or OpenAI-backed LLM support, and a Qdrant-backed retrieval pipeline for uploaded documents.


## What the project does

The application is designed to help you turn raw text or uploaded documents into readable summaries in different formats.

Current capabilities:

- Summarize pasted text through `POST /api/v1/summarize`
- Choose summary styles:
	- `tldr`
	- `bullet`
	- `executive`
	- `explain_like_12`
- Choose summary lengths:
	- `short`
	- `medium`
	- `long`
	- `custom`
- Upload documents for retrieval-based workflows through `POST /api/v1/documents/upload`
- Extract text from supported files
- Chunk and embed uploaded content
- Store vectors in Qdrant
- Search indexed chunks through `POST /api/v1/rag/search`
- Generate document-grounded summaries through `POST /api/v1/summaries/rag`
- Reindex stored chunks into Qdrant through `POST /api/v1/rag/reindex`
- Ping the active LLM provider through `GET /api/v1/ping`
- Use a simple frontend served from `frontend/`

## Current architecture

The project is split into a few main layers.

Backend:

- FastAPI application in `app/`
- SQLite for relational metadata storage
- SQLAlchemy async engine and sessions
- Pydantic request and response schemas

LLM layer:

- Ollama support through LangChain and the Ollama Python client
- OpenAI support through LangChain OpenAI
- A common client selection path based on environment settings

RAG layer:

- Document ingestion and extraction
- Text chunking
- Embedding generation
- Qdrant vector storage and search
- RAG summarization over retrieved chunks

Frontend:

- Static HTML, CSS, and vanilla JavaScript in `frontend/`
- A simple Python HTTP server for local UI serving

## Repository layout

```text
.
├── app/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── exceptions/
│   ├── models/
│   ├── services/
│   └── storage/
├── docker/
├── frontend/
├── logs/
├── tests/
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

Important folders:

- `app/api/v1/routes/`: FastAPI routes
- `app/services/`: summarization, ingestion, embedding, vector store, and RAG services
- `app/models/`: SQLAlchemy models for documents and chunks
- `app/storage/uploads/`: uploaded files
- `app/storage/extracted_text/`: extracted text copies
- `frontend/`: browser UI

## Supported workflows

### 1. Quick summary

Paste text into the frontend or call `POST /api/v1/summarize` directly.

This flow:

- chooses the active LLM provider from settings
- builds a structured prompt for the selected summary type
- applies a length target
- returns the generated summary

### 2. Document-based summary

Upload one or more documents, then ask for a grounded summary.

This flow:

- stores the uploaded file on disk
- extracts text
- writes document metadata to SQLite
- chunks the extracted text
- embeds the chunks
- stores vectors in Qdrant
- retrieves relevant chunks for a query
- asks the configured LLM to summarize only the retrieved context

## Supported file types

The backend currently supports text extraction for:

- `pdf`
- `txt`
- `md`

Note:

- The frontend file picker currently allows some extra file extensions visually, but the backend only accepts the supported types above.

## Tech stack

- Python 3.12
- FastAPI
- SQLAlchemy async
- SQLite
- Pydantic v2
- LangChain
- Ollama
- OpenAI
- Qdrant
- Vanilla HTML/CSS/JavaScript frontend

## Prerequisites

For local development without Docker:

- Python 3.12+
- An Ollama installation or valid OpenAI credentials
- Qdrant if you want document search or RAG

For Docker-based development:

- Docker Engine
- Docker Compose v2 via `docker compose`

Note:

- Prefer `docker compose`, not legacy `docker-compose` v1.

## Environment configuration

The application reads settings from `app/.env`.

Start from the example file:

```bash
cp app/.env.example app/.env
```

Key variables:

| Variable | Purpose | Typical value |
| --- | --- | --- |
| `LLM_PROVIDER` | Active text generation provider | `ollama` |
| `OLLAMA_API_URL` | Ollama base URL | `http://localhost:11434` locally or `http://ollama:11434` in Compose |
| `OLLAMA_MODEL` | Main generation model | `llama3.2:1b` |
| `OPENAI_API_KEY` | OpenAI key if using OpenAI | empty unless needed |
| `OPENAI_MODEL` | OpenAI chat model | `gpt-4o-mini` |
| `SUMMARY_MAX_TOKENS` | Generation token ceiling for summaries | `400` |
| `SUMMARY_MAX_LENGTH` | Max allowed requested summary length | `5000` |
| `UPLOAD_DIR` | Raw uploaded file directory | `storage/uploads` |
| `EXTRACTED_TEXT_DIR` | Extracted text directory | `storage/extracted_text` |
| `MAX_UPLOAD_SIZE_MB` | Upload size limit | `20` |
| `QDRANT_URL` | Qdrant base URL | `http://localhost:6333` or `http://qdrant:6333` |
| `QDRANT_COLLECTION_NAME` | Vector collection name | `document_chunks_ollama` |
| `OLLAMA_EMBEDDING_MODEL` | Embedding model used for RAG | `nomic-embed-text` |

## Installation

### Local setup

1. Create and activate a virtual environment.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies.

If you use plain pip:

```bash
pip install --upgrade pip
pip install \
	aiofiles \
	aiosqlite \
	fastapi \
	langchain \
	langchain-ollama \
	langchain-openai \
	ollama \
	pydantic \
	pydantic-settings \
	pypdf \
	python-multipart \
	python-dotenv \
	qdrant-client \
	sqlalchemy \
	uvicorn
```

3. Create your environment file.

```bash
cp app/.env.example app/.env
```

4. If you use Ollama locally, pull the required models.

```bash
ollama pull llama3.2:1b
ollama pull nomic-embed-text
```

5. Start Qdrant if you need document indexing or RAG.

Example with Docker:

```bash
docker run -p 6333:6333 qdrant/qdrant:latest
```

6. Start the backend.

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

7. Start the frontend in another terminal.

```bash
cd frontend
python serve.py
```

8. Open the UI.

```text
http://localhost:5173
```

### Docker setup

The repository includes a Compose stack for:

- backend
- frontend
- ollama
- qdrant

Start everything:

```bash
docker compose up --build
```

Then pull the required models into the Ollama container:

```bash
docker compose exec ollama ollama pull llama3.2:1b
docker compose exec ollama ollama pull nomic-embed-text
```

Access points:

- Backend API: `http://localhost:8000`
- Frontend UI: `http://localhost:5173`
- Qdrant: `http://localhost:6333`

## Running the project

### Backend only

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Frontend only

```bash
cd frontend
python serve.py
```

### Full stack with Docker

```bash
docker compose up --build
```

## API overview

Base prefix:

```text
/api/v1
```

### Health

- `GET /api/v1/health`
	- Returns `{"status": "ok"}`

### LLM ping

- `GET /api/v1/ping`
	- Verifies connectivity to the configured provider

### Quick summary

- `POST /api/v1/summarize`

Example request:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/summarize \
	-H "Content-Type: application/json" \
	-d '{
		"text": "Paste a long piece of text here.",
		"summary_type": "tldr",
		"length": "custom",
		"max_length": 800
	}'
```

### Document upload

- `POST /api/v1/documents/upload`

Example request:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/documents/upload \
	-F "files=@/absolute/path/to/file1.pdf" \
	-F "files=@/absolute/path/to/file2.txt"
```

### Vector search

- `POST /api/v1/rag/search`

Example request:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/rag/search \
	-H "Content-Type: application/json" \
	-d '{
		"query": "main risks and deadlines",
		"top_k": 5,
		"document_ids": []
	}'
```

### RAG summary

- `POST /api/v1/summaries/rag`

Example request:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/summaries/rag \
	-H "Content-Type: application/json" \
	-d '{
		"query": "Summarize the main risks and next steps",
		"top_k": 5,
		"document_ids": [],
		"summary_type": "executive",
		"length": "medium"
	}'
```

### Reindex documents

- `POST /api/v1/rag/reindex`

Use this when the relational data already exists but you want to rebuild the Qdrant index.

## Data storage

### SQLite

The project stores document metadata and chunks in:

```text
app/summarize-bot-data.db
```

### File storage

- Raw uploads go to `app/storage/uploads/`
- Extracted text copies go to `app/storage/extracted_text/`

### Vector storage

Qdrant stores vectorized document chunks in the configured collection, by default:

```text
document_chunks_ollama
```

Useful commands:

```bash
curl http://localhost:6333/collections/document_chunks_ollama
curl -X DELETE "http://localhost:6333/collections/document_chunks_ollama"
```

## Frontend behavior

The frontend supports:

- setting the API base URL
- checking backend health
- uploading files
- asking for a document-based summary
- pasting raw text for quick summary
- writing all summaries into one shared output box

The frontend is intentionally simple and currently uses plain JavaScript without a framework.

## Summary behavior

Quick summary supports these styles:

- `tldr`
- `bullet`
- `executive`
- `explain_like_12`

Length modes:

- `short`
- `medium`
- `long`
- `custom`

Notes:

- `custom` is a maximum target, not a guaranteed exact output size
- the summarizer clips output cleanly at a sentence or word boundary
- if the source does not support a longer answer, the model may still return less than the requested maximum

## Known limitations

This repository is working, but it is still an in-progress project.

Current limitations include:

- Document extraction currently supports only `pdf`, `txt`, and `md`
- The RAG search service currently ignores `document_ids` filtering inside the vector store search implementation, even though the API accepts the field
- There is no authentication or multi-user separation yet
- There is no formal test suite in place yet
- The frontend is functional but minimal
- Performance and output quality depend heavily on the selected Ollama/OpenAI model
- Very small local models may ignore some prompt detail or underuse large custom length budgets

## Troubleshooting

### Ollama connection errors

If `/api/v1/ping` or `/api/v1/summarize` cannot reach Ollama:

- confirm Ollama is running
- confirm `OLLAMA_API_URL` is correct for your environment
- if using Docker Compose, prefer `http://ollama:11434`
- make sure the required models have been pulled

### Summary request fails with provider errors

Check:

- `LLM_PROVIDER`
- `OLLAMA_MODEL` or `OPENAI_MODEL`
- `OPENAI_API_KEY` if using OpenAI

### Upload fails

Check:

- file extension is supported
- file size is below `MAX_UPLOAD_SIZE_MB`
- extracted text is not empty

### RAG summary returns no useful result

Check:

- documents were uploaded successfully
- the embedding model exists in Ollama
- Qdrant is running
- the collection contains indexed chunks

## Development notes

Useful commands:

```bash
python3 -m py_compile app/services/summarizer.py
python3 -m py_compile app/api/v1/schemas/summaries.py app/api/v1/routes/summaries.py
```

Start backend manually:

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Start frontend manually:

```bash
cd frontend
python serve.py
```

## Project status

At this point, the project is no longer just a backend sketch. It includes:

- a working FastAPI API
- a working browser frontend
- text summarization through an LLM backend
- document upload and indexing
- a functional RAG summary path
- environment-based model configuration
- Docker support for local full-stack development

The next natural areas for improvement would be automated tests, tighter RAG filtering by uploaded document ids, better frontend polish, and broader document format support.
