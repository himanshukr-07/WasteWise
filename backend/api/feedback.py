from fastapi import APIRouter, HTTPException
from typing import Literal

from pydantic import BaseModel, Field

from backend.services.feedback import get_feedback_stats, record_feedback
from backend.services.security import ALLOWED_CATEGORIES

router = APIRouter(prefix="/feedback", tags=["feedback"])


Category = Literal["Organic", "Paper", "Plastic", "Glass", "Metal", "E-waste", "Hazardous", "Other / Unknown"]


class FeedbackRequest(BaseModel):
    history_id: str = Field(min_length=1, max_length=100)
    feedback: Literal["correct", "incorrect"]
    corrected_category: Category | None = None


@router.post("")
def submit_feedback(request: FeedbackRequest) -> dict:
    try:
        if request.corrected_category is not None and request.corrected_category not in ALLOWED_CATEGORIES:
            raise HTTPException(status_code=422, detail="Invalid waste category.")

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
