from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import ChatRequest, ChatResponse
from app.services.llm_service import LLMService
from app.services.rag_service import RAGService
from app.services.history_service import HistoryService

router = APIRouter(prefix="/api/chat", tags=["Chat"])
llm = LLMService()
rag = RAGService()
history = HistoryService()

@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest):
    context = ""
    sources = []

    if req.use_knowledge_base:
        docs, sources = rag.search(req.message)
        context = "\n\n---\n\n".join(docs) if docs else ""

    conv = history.load(req.conversation_id) if req.conversation_id else None
    if not conv:
        conv = history.create()

    hist = [{"role": m.role, "content": m.content} for m in conv.messages]

    if req.message == "__CALL_START__":
        reply, tokens, elapsed = llm.generate_call_start()
    else:
        reply, tokens, elapsed = llm.generate(req.message, context, hist)

    history.add_message(conv.id, "user", req.message if req.message != "__CALL_START__" else "[Llamada iniciada]")
    history.add_message(conv.id, "assistant", reply)

    return ChatResponse(
        reply=reply,
        conversation_id=conv.id,
        sources=sources,
        model=llm.model,
        tokens_used=tokens,
        processing_time=round(elapsed, 2)
    )

@router.post("/models")
async def switch_model(model_id: str = Query(...)):
    llm.switch_model(model_id)
    return {"model": model_id}

@router.get("/models")
async def list_models():
    return {"models": llm.list_models()}

@router.get("/history")
async def list_history():
    return history.list_conversations()

@router.get("/history/{conversation_id}")
async def get_conversation(conversation_id: str):
    conv = history.load(conversation_id)
    if not conv:
        raise HTTPException(404, "Conversación no encontrada")
    return conv

@router.delete("/history/{conversation_id}")
async def delete_conversation(conversation_id: str):
    history.delete(conversation_id)
    return {"message": "Conversación eliminada"}
