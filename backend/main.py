from pathlib import Path
import os
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.api.analyze import router as analyze_router
from backend.api.chat import router as chat_router
from backend.api.history import router as history_router
from backend.api.rag import router as rag_router
from backend.api.feedback import router as feedback_router

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

logging.basicConfig(level=os.getenv("WASTEWISE_LOG_LEVEL", "INFO"))

app = FastAPI(title="WasteWise API", version="0.1.0")

# The frontend is normally served by this same FastAPI application, so CORS is
# only enabled for common local development origins rather than every website.
def _cors_origins() -> list[str]:
    raw = os.getenv(
        "WASTEWISE_CORS_ORIGINS",
        "http://127.0.0.1:8000,http://localhost:8000,http://127.0.0.1:6000,http://localhost:6000",
    )
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    # Reject very large requests early when the client provides Content-Length.
    # Multipart overhead is intentionally included in the limit.
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > 10 * 1024 * 1024:
                return JSONResponse(status_code=413, content={"detail": "Request is too large."})
        except ValueError:
            return JSONResponse(status_code=400, content={"detail": "Invalid Content-Length header."})

    response = await call_next(request)
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response

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
