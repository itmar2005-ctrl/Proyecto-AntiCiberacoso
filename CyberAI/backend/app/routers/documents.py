from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.schemas import UploadResponse, DocumentInfo
from app.services.document_service import DocumentService
from app.services.rag_service import RAGService
import os

router = APIRouter(prefix="/api/documents", tags=["Documents"])
doc_service = DocumentService()
rag = RAGService()

@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    content = await file.read()
    doc_id, filepath = doc_service.save_file(file.filename, content)
    text = doc_service.extract_text(filepath)
    if text and not text.startswith("["):
        chunks = rag.index_document(doc_id, file.filename, text)
        return UploadResponse(filename=file.filename, message=f"Documento indexado con {chunks} fragmentos", document_id=doc_id)
    return UploadResponse(filename=file.filename, message="Archivo guardado pero no se pudo extraer texto", document_id=doc_id)

@router.get("")
async def list_documents():
    return rag.list_documents()

@router.delete("/{doc_id}")
async def delete_document(doc_id: str):
    rag.delete_document(doc_id)
    return {"message": "Documento eliminado de la base de conocimiento"}

@router.post("/upload-url")
async def upload_from_url(url: str):
    import requests
    from urllib.parse import urlparse
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        filename = os.path.basename(urlparse(url).path) or "webpage.html"
        content_type = resp.headers.get("content-type", "")
        if "text/html" in content_type or not filename:
            filename = filename or "page.html"
        doc_id, filepath = doc_service.save_file(filename, resp.content)
        text = doc_service.extract_text(filepath)
        if text and not text.startswith("["):
            chunks = rag.index_document(doc_id, filename, text)
            return {"filename": filename, "message": f"Página web indexada con {chunks} fragmentos", "document_id": doc_id}
        return {"filename": filename, "message": "URL guardada pero no se pudo extraer texto", "document_id": doc_id}
    except Exception as e:
        raise HTTPException(400, f"Error al descargar URL: {e}")
