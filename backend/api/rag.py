from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.rag import index_knowledge_base, knowledge_base_status

router = APIRouter(tags=["rag"])


class ReindexRequest(BaseModel):
    force: bool = False


@router.get("/rag/status")
def rag_status() -> dict:
    return knowledge_base_status()


@router.post("/rag/reindex")
def rag_reindex(request: ReindexRequest) -> dict:
    try:
        return index_knowledge_base(force=request.force)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"RAG indexing failed: {exc}") from exc
