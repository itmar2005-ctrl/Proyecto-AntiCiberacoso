from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from app.config import settings
from app.routers import chat, documents, voice, system
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"  {settings.app_name} v{settings.version} iniciando...")
    print(f"  Modelo: {settings.groq_model}")
    yield
    print("  Servicio detenido.")

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(documents.router)
app.include_router(voice.router)
app.include_router(system.router)

@app.get("/")
async def root():
    return {"message": f"{settings.app_name} API", "version": settings.version, "docs": "/docs"}

@app.get("/nlp")
async def nlp_page():
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    nlp_path = os.path.join(base, "cyberguard_nlp.html")
    if os.path.exists(nlp_path):
        return FileResponse(nlp_path)
    return {"error": "cyberguard_nlp.html no encontrado en la raíz del proyecto."}
