from io import BytesIO

from PIL import Image

from backend.services.security import (
    MAX_CHAT_CHARS,
    validate_chat_question,
    validate_image_upload,
)


def _png_bytes(width: int = 10, height: int = 10) -> bytes:
    image = Image.new("RGB", (width, height), "white")
    buf = BytesIO()
    image.save(buf, format="PNG")
    return buf.getvalue()


def test_chat_question_is_trimmed_and_bounded():
    assert validate_chat_question("  battery disposal?  ") == "battery disposal?"
    try:
        validate_chat_question("x" * (MAX_CHAT_CHARS + 1))
    except ValueError as exc:
        assert "too long" in str(exc)
    else:
        raise AssertionError("Expected long question to be rejected")


def test_image_validation_accepts_real_png():
    ok, error = validate_image_upload(content_type="image/png", image_bytes=_png_bytes())
    assert ok is True
    assert error == ""


def test_image_validation_rejects_wrong_type_and_invalid_bytes():
    ok, error = validate_image_upload(content_type="application/pdf", image_bytes=b"not-an-image")
    assert ok is False
    assert "Only JPG" in error

    ok, error = validate_image_upload(content_type="image/png", image_bytes=b"not-an-image")
    assert ok is False
    assert "valid supported image" in error
