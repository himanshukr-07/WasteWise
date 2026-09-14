import base64
import json
import re
from typing import Any

from ollama import Client

OLLAMA_HOST = "http://127.0.0.1:11434"
VISION_MODEL = "qwen2.5vl:3b"

client = Client(host=OLLAMA_HOST)


def _extract_json(text: str) -> dict[str, Any]:
    """Extract a JSON object from model output, tolerating fenced code blocks."""
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
    if not match:
        raise ValueError("Vision model did not return a JSON object.")

    return json.loads(match.group(0))


def analyze_image(image_bytes: bytes) -> dict[str, Any]:
    """Analyze a waste image with the local Ollama vision model."""
    encoded = base64.b64encode(image_bytes).decode("utf-8")

    prompt = """
You are the vision component of an AI waste-segregation assistant.
Analyze the provided image and identify the most likely waste item.
Use ONLY one of these categories:
Organic, Paper, Plastic, Glass, Metal, E-waste, Hazardous, Other / Unknown.

Return ONLY valid JSON in this exact shape:
{
  "item": "...",
  "category": "...",
  "confidence": 0.0,
  "observation": "brief visual observation"
}

Confidence must be between 0 and 1.
If the image is unclear or the item cannot be identified reliably, use category
"Other / Unknown" and a low confidence value.
""".strip()

    response = client.chat(
        model=VISION_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
                "images": [encoded],
            }
        ],
    )

    result = _extract_json(response["message"]["content"])

    # Keep output predictable for the API/frontend.
    allowed = {
        "Organic",
        "Paper",
        "Plastic",
        "Glass",
        "Metal",
        "E-waste",
        "Hazardous",
        "Other / Unknown",
    }
    category = result.get("category", "Other / Unknown")
    if category not in allowed:
        category = "Other / Unknown"

    try:
        confidence = float(result.get("confidence", 0.0))
    except (TypeError, ValueError):
        confidence = 0.0

    confidence = max(0.0, min(1.0, confidence))

    return {
        "item": str(result.get("item", "Unknown item")),
        "category": category,
        "confidence": confidence,
        "observation": str(result.get("observation", "")),
    }
