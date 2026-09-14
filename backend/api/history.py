from fastapi import APIRouter

from backend.services.history import get_history, get_stats, get_analytics

router = APIRouter(prefix="/history", tags=["history"])


@router.get("")
def history(limit: int = 50) -> dict:
    return {"items": get_history(limit)}


@router.get("/analytics")
def history_analytics() -> dict:
    return get_analytics()


@router.get("/stats")
def history_stats() -> dict:
    return get_stats()
