from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.services.feedback import get_feedback_stats, record_feedback

router = APIRouter(prefix="/feedback", tags=["feedback"])


class FeedbackRequest(BaseModel):
    history_id: str = Field(min_length=1, max_length=100)
    feedback: str = Field(min_length=1, max_length=20)
    corrected_category: str | None = Field(default=None, max_length=50)


@router.post("")
def submit_feedback(request: FeedbackRequest) -> dict:
    try:
        record = record_feedback(
            history_id=request.history_id,
            feedback=request.feedback,
            corrected_category=request.corrected_category,
        )
        return {"status": "saved", "feedback": record}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/stats")
def feedback_stats() -> dict:
    return get_feedback_stats()
