FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc g++ && rm -rf /var/lib/apt/lists/*

COPY secnlp-platform/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY secnlp-platform/backend backend
COPY secnlp-platform/frontend frontend

ENV PYTHONUNBUFFERED=1 HF_HOME=/tmp/huggingface

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
