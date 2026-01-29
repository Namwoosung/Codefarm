FROM python:3.11-slim

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app
COPY app /app/app

EXPOSE 8089
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8089"]