# ============================================
# SecNLP Platform - Dockerfile Hardened
# ============================================
# Stage 1: Build
FROM python:3.11-slim AS builder

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime (minimal)
FROM python:3.11-slim AS runner

WORKDIR /app

RUN groupadd -r secgroup && useradd -r -g secgroup -s /sbin/nologin secuser

COPY --from=builder /root/.local /home/secuser/.local
COPY backend backend
COPY frontend frontend
COPY run.py .

ENV PATH=/home/secuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/tmp/huggingface

RUN chown -R secuser:secgroup /app /tmp
USER secuser

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
