"""SecNLP Platform - API principal"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from prometheus_client import Counter, Histogram
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = FastAPI(
    title="SecNLP Platform",
    description="Motor de moderación de lenguaje natural con detección de discurso malicioso",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import time as time_module

REQ_COUNT = Counter("secnlp_requests_total", "Total de solicitudes")
BLOCKED_COUNT = Counter("secnlp_blocked_total", "Mensajes bloqueados")
LATENCY_HIST = Histogram("secnlp_latency_seconds", "Latencia del pipeline")
FP_COUNT = Counter("secnlp_false_positives_total", "Falsos positivos reportados")


@app.middleware("http")
async def metrics_middleware(request, call_next):
    start = time_module.time()
    response = await call_next(request)
    LATENCY_HIST.observe(time_module.time() - start)
    if request.url.path == "/v1/moderate" and request.method == "POST":
        REQ_COUNT.inc()
    return response

from backend.routers import moderation, feedback, metrics

app.include_router(moderation.router)
app.include_router(feedback.router)
app.include_router(metrics.router)

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="frontend")

    @app.get("/")
    async def serve_frontend():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

    @app.get("/classifier")
    async def serve_classifier():
        return FileResponse(os.path.join(FRONTEND_DIR, "classifier.html"))

    @app.get("/guia-seguridad")
    async def guide_seguridad():
        return FileResponse(os.path.join(FRONTEND_DIR, "guia-seguridad.html"))

    @app.get("/guia-padres")
    async def guide_padres():
        return FileResponse(os.path.join(FRONTEND_DIR, "guia-padres.html"))

    @app.get("/reportar")
    async def reportar():
        return FileResponse(os.path.join(FRONTEND_DIR, "reportar-plataformas.html"))


@app.get("/health")
async def health():
    return {"status": "ok", "version": "2.0.0", "model": "dehatebert-mono-spanish"}


@app.on_event("startup")
async def startup():
    logging.getLogger("SecNLP").info("=" * 50)
    logging.getLogger("SecNLP").info("SecNLP Platform iniciada")
    logging.getLogger("SecNLP").info("Endpoints:")
    logging.getLogger("SecNLP").info("  POST /v1/moderate")
    logging.getLogger("SecNLP").info("  POST /v1/moderate/batch")
    logging.getLogger("SecNLP").info("  POST /v1/feedback/false-positive")
    logging.getLogger("SecNLP").info("  GET  /metrics")
    logging.getLogger("SecNLP").info("=" * 50)
