---
# FastAPI Capabilities Checklist

## API & Validation

- **Pydantic request/response models**
	- Nested models
	- Unions
	- Enums
- **Custom validators**
	- Summary length bounds
	- URL format
	- File size
- **Response models** for consistent API shape
- **Pagination** for listing projects/documents/summaries
- **API versioning** (`/api/v1/...`)

## Dependency Injection

- Proper FastAPI style
- `Depends()` for:
	- DB session
	- Auth user
	- Rate limiting / quotas
	- Service wiring (LLM client, summarizer, storage)

## Exception Handling

- **Global handlers:**
	- `RequestValidationError`
	- `HTTPException`
	- Custom `AppError`
	- Unknown exceptions → safe 500 response + correlation ID
- **Domain errors:**
	- `DocumentNotFound`
	- `UnsupportedFileType`
	- `QuotaExceeded`
	- `ProviderTimeout`
- **Consistent error schema**

## Auth & Security

- Start simple: API key header (`X-API-Key`)
- Upgrade path: JWT + users + roles
- CORS config (for frontend)
- Rate limiting (optional)

## Async & Background Work

- **Background tasks for:**
	- URL fetching
	- File parsing
	- Long summarizations
- **Job status endpoints** (polling): queued/running/done/failed

## Streaming (Advanced)

- Stream tokens back (SSE) for “live summary generation”
- Optional WebSocket chat mode

## Observability

- Structured logging (JSON logs) + request ID
- Timing middleware (latency per request)
- **Health endpoint:**
	- `/health` (basic)
	- `/ready` (checks DB + provider connectivity)

## Testing

- **Unit tests:**
	- Summarizer service
	- Prompt builder
	- Validation edge cases
- **Integration tests:**
	- FastAPI test client
	- DB test container or SQLite test DB
	- Contract-like tests for error shapes

## Good Backend Practices

- **High-level layers:**
	- API layer: routers + schemas (Pydantic)
	- Service layer: business logic (e.g., `SummarizeService`, `DocumentService`)
	- Domain layer: entities + domain exceptions
	- Infrastructure layer: DB, LLM provider clients, storage, fetchers
- Routers stay thin (just validate + call services)
- Services are testable without HTTP
- Provider-specific AI code is isolated (swap OpenAI/local easily)
- Clear separation of concerns

## Storage & Data Model

- Use SQLite for dev (upgradeable to Postgres)
- **Tables:**
	- `projects(id, name, created_at)`
	- `documents(id, project_id, source_type, source_ref, extracted_text, created_at)`
	- `summary_runs(id, document_id, kind, params_json, summary_text, created_at)`
	- `chat_sessions(id, document_id, created_at)`
	- `chat_messages(id, session_id, role, content, created_at)`

## AI/LLM Design

- **Provider abstraction:**
	- Interface: `LLMClient.generate(messages, params) -> text`
	- Interface: `LLMClient.stream(messages, params) -> chunks`
	- Implementations:
		- `MockLLMClient` (for tests + no API key)
		- `OpenAIClient` (real)
		- Later: local model client (Ollama, etc.)
- **Prompting strategy (versioned):**
	- Prompt templates stored with a version tag
	- Summary run stores `prompt_version`, model, temperature, max_tokens
	- Outputs are reproducible

## Safety & Robustness

- Content length limits + chunking strategy
- Retry + timeout policy per provider
- Graceful fallback: if streaming fails, return normal response

## Simple Frontend (Optional)

- Server-rendered Jinja2 (fastest, simplest) or tiny React/Vite SPA
- Features:
	- Submit text/URL
	- Select summary type
	- Display summary
	- Show list of previous summaries
	- “Copy” button
	- Optional: chat box for follow-up questions

## MVP Milestones

1. **MVP-0:** Health endpoint + logging + global error handler
2. **MVP-1:** `/summaries` endpoint (text input) + mock LLM
3. **MVP-2:** DB persistence: documents + summary_runs
4. **MVP-3:** URL summarization + background task + job status
5. **MVP-4:** Simple frontend (Jinja2) calling your API
6. **MVP-5:** Chat over a document + message history
7. **MVP-6:** Streaming summaries (SSE) + integration tests + CI