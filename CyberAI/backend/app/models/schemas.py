from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class Message(BaseModel):
    role: str
    content: str
    timestamp: Optional[datetime] = None

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    use_knowledge_base: bool = True

class ChatResponse(BaseModel):
    reply: str
    conversation_id: str
    sources: List[str] = []
    model: str
    tokens_used: int = 0
    processing_time: float = 0.0

class Conversation(BaseModel):
    id: str
    title: str
    messages: List[Message]
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class DocumentInfo(BaseModel):
    id: str
    filename: str
    filetype: str
    size: int
    chunks: int = 0
    uploaded_at: str
    indexed: bool = False

class VoiceRequest(BaseModel):
    text: str
    voice: str = "shimmer"

class UploadResponse(BaseModel):
    filename: str
    message: str
    document_id: str
