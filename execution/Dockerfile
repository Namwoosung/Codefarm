FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      ca-certificates curl && \
    curl -fsSL https://get.docker.com | sh && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir fastapi uvicorn pydantic

WORKDIR /app
COPY app /app/app

EXPOSE 8088
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8088"]