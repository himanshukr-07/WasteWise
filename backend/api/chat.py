import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.services.rag import generate_grounded_answer, retrieve
from backend.services.security import validate_chat_question

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


@router.post("/chat")
def chat(request: ChatRequest) -> dict:
    try:
        question = validate_chat_question(request.question)
    except ValueError as exc:
        return {"answer": str(exc), "grounded": False, "sources": []}

    try:
        results = retrieve(question)
        if not results:
            return {
                "answer": "I couldn't find relevant information in the WasteWise knowledge base. Please check your local waste-management guidance.",
                "grounded": False,
                "sources": [],
            }
        answer = generate_grounded_answer(question, results)
        sources = []
        seen = set()
        for result in results:
            key = (result["title"], result["source"])
            if key not in seen:
                seen.add(key)
                sources.append({"title": result["title"], "url": result["source"]})
        return {"answer": answer, "grounded": True, "sources": sources}
    except Exception as exc:
        logger.exception("RAG chat failed")
        raise HTTPException(status_code=502, detail="AI Assistant is temporarily unavailable. Please try again.") from exc
