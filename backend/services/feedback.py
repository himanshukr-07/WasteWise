from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from backend.services.history import get_history

BASE_DIR = Path(__file__).resolve().parents[2]
FEEDBACK_FILE = BASE_DIR / "backend" / "data" / "feedback.json"
ALLOWED_FEEDBACK = {"correct", "incorrect"}


def _load() -> list[dict[str, Any]]:
    if not FEEDBACK_FILE.exists():
        return []
    try:
        data = json.loads(FEEDBACK_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _save(items: list[dict[str, Any]]) -> None:
    FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)
    FEEDBACK_FILE.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


def record_feedback(*, history_id: str, feedback: str, corrected_category: str | None = None) -> dict[str, Any]:
    feedback = feedback.strip().lower()
    if feedback not in ALLOWED_FEEDBACK:
        raise ValueError("Feedback must be 'correct' or 'incorrect'.")

    if feedback == "correct":
        corrected_category = None

    history_match = next((item for item in get_history(100) if str(item.get("id")) == str(history_id)), None)
    if history_match is None:
        raise ValueError("The referenced scan could not be found.")

    record = {
        "id": uuid4().hex,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "history_id": str(history_id),
        "feedback": feedback,
        "predicted_item": str(history_match.get("item", "")),
        "predicted_category": str(history_match.get("category", "Other / Unknown")),
        "corrected_category": corrected_category,
    }

    items = _load()
    # One feedback response per scan; a newer response replaces the previous one.
    items = [item for item in items if str(item.get("history_id")) != str(history_id)]
    items.insert(0, record)
    _save(items[:500])
    return record


def get_feedback_stats() -> dict[str, Any]:
    items = _load()
    correct = sum(1 for item in items if item.get("feedback") == "correct")
    incorrect = sum(1 for item in items if item.get("feedback") == "incorrect")
    total = correct + incorrect
    accuracy = round((correct / total) * 100, 1) if total else None

    corrections: dict[str, int] = {}
    for item in items:
        if item.get("feedback") != "incorrect":
            continue
        corrected = str(item.get("corrected_category") or "Other / Unknown")
        corrections[corrected] = corrections.get(corrected, 0) + 1

    return {
        "total_feedback": total,
        "correct": correct,
        "incorrect": incorrect,
        "accuracy": accuracy,
        "corrections_by_category": dict(sorted(corrections.items(), key=lambda kv: (-kv[1], kv[0]))),
    }
