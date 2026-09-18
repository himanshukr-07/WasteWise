from __future__ import annotations

from io import BytesIO
from typing import Final

from PIL import Image, UnidentifiedImageError

MAX_IMAGE_BYTES: Final[int] = 8 * 1024 * 1024
MAX_IMAGE_PIXELS: Final[int] = 25_000_000
MAX_CHAT_CHARS: Final[int] = 2_000
MAX_FILENAME_CHARS: Final[int] = 255
ALLOWED_IMAGE_TYPES: Final[set[str]] = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_CATEGORIES: Final[set[str]] = {
    "Organic",
    "Paper",
    "Plastic",
    "Glass",
    "Metal",
    "E-waste",
    "Hazardous",
    "Other / Unknown",
}


def validate_image_upload(*, content_type: str | None, image_bytes: bytes) -> tuple[bool, str]:
    """Validate an uploaded image before it reaches the vision model."""
    if not content_type:
        return False, "Image content type is missing."
    content_type = content_type.lower().split(";", 1)[0].strip()
    if content_type not in ALLOWED_IMAGE_TYPES:
        return False, "Only JPG, PNG, and WEBP images are supported."
    if not image_bytes:
        return False, "Uploaded image is empty."
    if len(image_bytes) > MAX_IMAGE_BYTES:
        return False, f"Image is too large. Maximum size is {MAX_IMAGE_BYTES // (1024 * 1024)} MB."

    try:
        with Image.open(BytesIO(image_bytes)) as image:
            width, height = image.size
            if width <= 0 or height <= 0:
                return False, "Image dimensions are invalid."
            if width * height > MAX_IMAGE_PIXELS:
                return False, "Image dimensions are too large for safe processing."
            image.verify()
    except (UnidentifiedImageError, OSError, ValueError):
        return False, "The uploaded file is not a valid supported image."

    return True, ""


def validate_chat_question(question: str) -> str:
    """Normalize and bound chat input to reduce accidental or abusive payloads."""
    cleaned = question.strip()
    if not cleaned:
        raise ValueError("Please enter a sustainability question.")
    if len(cleaned) > MAX_CHAT_CHARS:
        raise ValueError(f"Question is too long. Maximum length is {MAX_CHAT_CHARS} characters.")
    return cleaned
