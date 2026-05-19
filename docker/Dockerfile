FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml ./

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    aiofiles>=24.1.0 \
    aiosqlite>=0.22.1 \
      fastapi>=0.128.0 \
      langchain>=1.2.15 \
      langchain-ollama>=1.1.0 \
      langchain-openai>=1.2.0 \
      pydantic>=2.12.5 \
      pydantic-settings>=2.11.0 \
    pypdf>=6.0.0 \
    python-multipart>=0.0.20 \
      python-dotenv>=1.2.1 \
    sqlalchemy>=2.0.41 \
      uvicorn>=0.40.0

COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]