"""Feedback router - reportes de falsos positivos"""
from fastapi import APIRouter
from backend.schemas import FeedbackRequest

router = APIRouter(prefix="/v1", tags=["Feedback"])

feedback_log = []


@router.post("/feedback/false-positive")
async def report_false_positive(req: FeedbackRequest):
    entry = {
        "original_text": req.original_text[:200],
        "action_taken": req.action_taken,
        "is_false_positive": req.is_false_positive,
        "comment": req.comment,
    }
    feedback_log.append(entry)
    return {
        "status": "Reporte recibido",
        "total_reports": len(feedback_log),
    }


@router.get("/feedback/log")
async def get_feedback_log(limit: int = 50):
    return {"feedback": feedback_log[-limit:]}
