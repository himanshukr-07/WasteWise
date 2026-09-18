from pathlib import Path
import json

import backend.services.feedback as feedback_service


def test_record_feedback_and_replace_existing(tmp_path, monkeypatch):
    feedback_file = tmp_path / "feedback.json"
    monkeypatch.setattr(feedback_service, "FEEDBACK_FILE", feedback_file)

    monkeypatch.setattr(
        feedback_service,
        "get_history",
        lambda limit=100: [
            {"id": "scan-1", "item": "bottle", "category": "Plastic"}
        ],
    )

    first = feedback_service.record_feedback(history_id="scan-1", feedback="correct")
    assert first["feedback"] == "correct"

    second = feedback_service.record_feedback(
        history_id="scan-1", feedback="incorrect", corrected_category="Glass"
    )
    assert second["feedback"] == "incorrect"
    assert second["corrected_category"] == "Glass"

    data = json.loads(feedback_file.read_text(encoding="utf-8"))
    assert len(data) == 1

    stats = feedback_service.get_feedback_stats()
    assert stats["total_feedback"] == 1
    assert stats["correct"] == 0
    assert stats["incorrect"] == 1
    assert stats["corrections_by_category"] == {"Glass": 1}


def test_feedback_requires_existing_scan(tmp_path, monkeypatch):
    monkeypatch.setattr(feedback_service, "FEEDBACK_FILE", tmp_path / "feedback.json")
    monkeypatch.setattr(feedback_service, "get_history", lambda limit=100: [])

    try:
        feedback_service.record_feedback(history_id="missing", feedback="correct")
    except ValueError as exc:
        assert "could not be found" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
