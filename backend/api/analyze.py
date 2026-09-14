from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.services.history import add_scan
from backend.services.rag import get_disposal_guidance
from backend.services.responsible_ai import assess_scan
from backend.services.vision import analyze_image

router = APIRouter(tags=["analysis"])


@router.post("/analyze")
async def analyze_waste(file: UploadFile = File(...)) -> dict:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload an image file.")

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded image is empty.")

    try:
        vision = analyze_image(image_bytes)
        guidance = get_disposal_guidance(vision["category"], vision["item"])
        responsible = assess_scan(
            item=vision["item"],
            category=vision["category"],
            confidence=vision["confidence"],
            grounded=guidance.get("grounded", False),
            source_relevance=guidance.get("source_relevance", "none"),
        )
        record = add_scan(
            item=vision["item"],
            category=vision["category"],
            confidence=vision["confidence"],
            confidence_label=responsible["confidence_label"],
            observation=vision.get("observation", ""),
            recommendation=guidance["recommendation"],
            sources=guidance.get("sources", []),
            grounded=guidance.get("grounded", False),
            source_relevance=guidance.get("source_relevance", "none"),
            review_required=responsible["review_required"],
        )
        return {
            **vision,
            **guidance,
            **responsible,
            "history_id": record["id"],
        }
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI analysis failed: {exc}") from exc
