“An AI chatbot API built with FastAPI that supports conversation history, tool usage, authentication, logging, and model abstraction.”

Key decisions now (keep them simple):

Backend only (API-first) ✅

AI = LLM-based chatbot (OpenAI / local model / mock initially)

Users interact via REST (later WebSocket optional)

Linux dev via WSL