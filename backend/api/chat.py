from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.rag import generate_grounded_answer, retrieve

router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    question: str


@router.post("/chat")
def chat(request: ChatRequest) -> dict:
    question = request.question.strip()
    if not question:
        return {"answer": "Please enter a sustainability question.", "grounded": False, "sources": []}

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
        raise HTTPException(status_code=502, detail=f"RAG chat failed: {exc}") from exc
