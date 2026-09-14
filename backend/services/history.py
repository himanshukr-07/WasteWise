from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parents[2]
HISTORY_FILE = BASE_DIR / "backend" / "data" / "scan_history.json"


def _load() -> list[dict[str, Any]]:
    if not HISTORY_FILE.exists():
        return []
    try:
        data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _save(items: list[dict[str, Any]]) -> None:
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


def add_scan(*, item: str, category: str, confidence: float, observation: str, recommendation: str, sources: list[dict[str, str]], grounded: bool = False, source_relevance: str = "none", review_required: bool = True, confidence_label: str = "Unknown") -> dict[str, Any]:
    items = _load()
    record = {
        "id": datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "item": item,
        "category": category,
        "confidence": round(float(confidence), 4),
        "confidence_label": confidence_label,
        "observation": observation,
        "recommendation": recommendation,
        "sources": sources,
        "grounded": bool(grounded),
        "source_relevance": source_relevance,
        "review_required": bool(review_required),
    }
    items.insert(0, record)
    _save(items[:100])
    return record


def get_history(limit: int = 50) -> list[dict[str, Any]]:
    return _load()[: max(1, min(limit, 100))]


def get_stats() -> dict[str, Any]:
    items = _load()
    counts: dict[str, int] = {}
    grounded = 0
    review_required = 0
    for record in items:
        category = str(record.get("category", "Other / Unknown"))
        counts[category] = counts.get(category, 0) + 1
        grounded += 1 if record.get("grounded", bool(record.get("sources"))) else 0
        review_required += 1 if record.get("review_required", False) else 0

    max_count = max(counts.values(), default=0)
    top_categories = sorted([c for c, n in counts.items() if n == max_count]) if max_count else []
    return {
        "total_scans": len(items),
        "category_counts": counts,
        "top_categories": top_categories,
        "top_category_count": max_count,
        "grounded_scans": grounded,
        "review_required_scans": review_required,
    }


def get_analytics() -> dict[str, Any]:
    items = _load()
    category_counts: dict[str, int] = {}
    daily_counts: dict[str, int] = {}
    grounding_counts = {"category-specific": 0, "limited": 0, "none": 0}
    review_yes = 0

    for record in items:
        category = str(record.get("category", "Other / Unknown"))
        category_counts[category] = category_counts.get(category, 0) + 1

        ts = str(record.get("timestamp", ""))
        day = ts[:10] if len(ts) >= 10 else "Unknown"
        daily_counts[day] = daily_counts.get(day, 0) + 1

        relevance = str(record.get("source_relevance", "none"))
        if relevance not in grounding_counts:
            relevance = "none"
        grounding_counts[relevance] += 1

        if bool(record.get("review_required", False)):
            review_yes += 1

    sorted_daily = sorted(daily_counts.items())[-14:]
    total = len(items)
    grounded = grounding_counts["category-specific"]
    limited = grounding_counts["limited"]
    no_grounding = grounding_counts["none"]

    return {
        "total_scans": total,
        "category_counts": dict(sorted(category_counts.items(), key=lambda kv: (-kv[1], kv[0]))),
        "daily_counts": [{"date": d, "count": c} for d, c in sorted_daily],
        "grounding_counts": grounding_counts,
        "review_required": review_yes,
        "grounding_rate": round((grounded / total) * 100, 1) if total else 0.0,
        "limited_rate": round((limited / total) * 100, 1) if total else 0.0,
        "no_grounding_rate": round((no_grounding / total) * 100, 1) if total else 0.0,
    }
