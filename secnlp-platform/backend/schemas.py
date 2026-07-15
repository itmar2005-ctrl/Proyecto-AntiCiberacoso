from pydantic import BaseModel, Field


class ModerateRequest(BaseModel):
    text: str = Field(..., max_length=1000, description="Texto a analizar")
    context: str | None = Field(None, max_length=500, description="Contexto opcional")


class ModerateResponse(BaseModel):
    action: str
    score: float
    reason: str | None = None
    categories: dict | None = None
    sanitized: str | None = None
    latency_ms: float | None = None


class FeedbackRequest(BaseModel):
    original_text: str
    action_taken: str
    is_false_positive: bool
    comment: str | None = None


class BatchModerateRequest(BaseModel):
    texts: list[str] = Field(..., max_length=50)
