import logging
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CyberGuard API",
    description="Detección de discurso malicioso y ciberacoso usando NLP",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

detector = None


class AnalyzeRequest(BaseModel):
    text: str


class AnalyzeResponse(BaseModel):
    scores: dict
    overall_toxicity: float
    highlighted_spans: list
    top_categories: list
    is_toxic: bool
    label_descriptions: dict


@app.on_event("startup")
async def startup():
    global detector
    from backend.model import ToxicityDetector

    detector = ToxicityDetector()
    logger.info("CyberGuard API iniciada")


@app.get("/health")
async def health():
    return {"status": "ok", "model_loaded": detector is not None}


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="El texto no puede estar vacío")

    if detector is None:
        raise HTTPException(status_code=503, detail="Modelo no cargado")

    result = detector.predict(request.text)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")

if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="frontend")

    @app.get("/")
    async def serve_frontend():
        index_path = os.path.join(FRONTEND_DIR, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"error": "Frontend no encontrado"}
else:
    @app.get("/")
    async def root():
        return {
            "message": "CyberGuard API",
            "docs": "/docs",
            "frontend": "Ejecuta: uvicorn backend.main:app --reload",
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
