"""Routers de moderación (API principal)"""
import time
from fastapi import APIRouter, HTTPException
from backend.schemas import ModerateRequest, ModerateResponse, BatchModerateRequest
from backend.pipeline import ModerationPipeline

router = APIRouter(prefix="/v1", tags=["Moderation"])

pipeline: ModerationPipeline | None = None


def init_pipeline():
    global pipeline
    if pipeline is None:
        pipeline = ModerationPipeline()


@router.post("/moderate", response_model=ModerateResponse)
async def moderate(req: ModerateRequest):
    init_pipeline()
    start = time.time()
    result = pipeline.analyze(req.text)
    result["latency_ms"] = round((time.time() - start) * 1000, 2)
    return result


@router.post("/moderate/batch")
async def moderate_batch(req: BatchModerateRequest):
    init_pipeline()
    results = pipeline.analyze_batch(req.texts)
    return {"results": results, "count": len(results)}
