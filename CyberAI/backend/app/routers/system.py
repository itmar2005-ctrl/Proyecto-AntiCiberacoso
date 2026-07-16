from fastapi import APIRouter
from app.config import settings

router = APIRouter(prefix="/api", tags=["System"])

@router.get("/health")
async def health():
    return {"status": "ok", "app": settings.app_name, "version": settings.version}

@router.get("/models")
async def get_models():
    return {"models": [{"id": settings.groq_model, "name": "Groq Llama 3 70B", "provider": "groq"}]}
