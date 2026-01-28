FROM python:3.11-slim

RUN pip install --no-cache-dir fastapi uvicorn pydantic

WORKDIR /app
COPY app /app/app

EXPOSE 8089
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8089"]