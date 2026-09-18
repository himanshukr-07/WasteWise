from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.api.analyze import router as analyze_router
from backend.api.chat import router as chat_router
from backend.api.history import router as history_router
from backend.api.rag import router as rag_router
from backend.api.feedback import router as feedback_router

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(title="WasteWise API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(history_router, prefix="/api")
app.include_router(rag_router, prefix="/api")
app.include_router(feedback_router, prefix="/api")

@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "WasteWise"}

# Serve the frontend directly from FastAPI.
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
