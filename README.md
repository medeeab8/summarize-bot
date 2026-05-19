“An AI chatbot API built with FastAPI that supports conversation history, tool usage, authentication, logging, and model abstraction.”

Key decisions now (keep them simple):

Backend only (API-first) ✅

AI = LLM-based chatbot (OpenAI / local model / mock initially)

Users interact via REST (later WebSocket optional)

Linux dev via WSL

What the Summarize Bot should do
Core product behavior

Accept content to summarize

Plain text

URL (fetch page text)

File upload (PDF/DOCX/TXT) (optional at first; PDF can come later)

Generate multiple summary types

TL;DR (2–3 lines)

Bullet summary

Executive summary

“Explain like I’m 12”

Support “chat with your summary”

Ask questions about the summarized content

Follow-ups like “expand bullet 3” or “find risks” or “extract deadlines”

Manage “projects” and “documents”

Project = collection of docs + summaries

Document = raw content + metadata + extracted text

Versioned summaries

You can re-run summary with different settings (tone/length/audience)

Store each run with model params and prompt version

## uvicorn app.main:app --reload

## cd /home/mbarbat/Projects/summarize-bot OPENAI_API_KEY=dummy python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

## cd /home/mbarbat/Projects/summarize-bot/frontend python serve.py

## Docker development

`docker compose up --build` now starts the backend, frontend, and Ollama together. The backend uses `http://ollama:11434` by default inside the Compose network.

After the first startup, pull the model into the Ollama container:

`docker-compose exec ollama ollama pull llama2:latest`

Then test the API:

`curl http://127.0.0.1:8000/api/v1/ping`

## Make the summarize endpoint faster

Short steps that were needed:

1. Use the Ollama service inside Docker, so the backend talks to `http://ollama:11434` over the Compose network instead of relying on host networking.
2. Make the `/summarize` endpoint call the LangChain + Ollama summarizer directly, instead of using only the fallback extractive summary path.
3. Set real generation limits on the model call, so Ollama stops after a small summary instead of generating extra text that gets trimmed later.
4. Keep the prompt short and explicit, asking for a concise summary in the requested format.
5. Prefer a smaller or faster Ollama model if responses are still slow on CPU.
6. Cleanly clip the final text at a sentence or word boundary, instead of forcing long outputs and ending them with `...`.

## RAG steps

1. User uploads a document → backend validates it → saves it → extracts text → stores document metadata → makes it available for future RAG.

## Qdrant

- curl http://localhost:6333/collections/document_chunks_ollama

- Delete: curl -X DELETE "http://localhost:6333/collections/document_chunks_ollama"
