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

Action items / key takeaways

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