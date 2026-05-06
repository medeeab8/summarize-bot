FROM python:3.12-slim
#  PYTHONDONTWRITEBYTECODE=1 tells Python not to create .pyc bytecode files. In containers, this is commonly used to avoid generating extra cache files that are usually unnecessary,
#  PYTHONUNBUFFERED=1 ensures that the output from Python is sent directly to the terminal without being buffered. This is important in containerized environments to ensure that logs are visible in real-time.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app/frontend

COPY frontend ./frontend

EXPOSE 5173

CMD ["python", "serve.py"]