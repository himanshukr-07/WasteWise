from __future__ import annotations

from typing import Any

LOW_CONFIDENCE = 0.65
REVIEW_CONFIDENCE = 0.80
SPECIAL_CATEGORIES = {"E-waste", "Hazardous"}


def assess_scan(*, item: str, category: str, confidence: float, grounded: bool, source_relevance: str) -> dict[str, Any]:
    """Return transparent, conservative flags for a scan result.

    This is decision-support metadata, not a medical/legal/safety certification.
    """
    reasons: list[str] = []
    review_required = False

    if confidence < LOW_CONFIDENCE:
        review_required = True
        reasons.append("Low model-estimated confidence; verify the item manually.")
    elif confidence < REVIEW_CONFIDENCE:
        review_required = True
        reasons.append("Moderate model-estimated confidence; verify before disposal.")

    if category == "Other / Unknown":
        review_required = True
        reasons.append("The item is outside the supported classification set or unclear.")

    if category in SPECIAL_CATEGORIES:
        review_required = True
        reasons.append("Special waste streams should be handled using applicable authorised/local guidance.")

    if not grounded:
        review_required = True
        reasons.append("No relevant grounded knowledge-base guidance was retrieved.")

    if source_relevance == "limited":
        review_required = True
        reasons.append("Only general guidance was found; no category-specific source was retrieved.")
    elif source_relevance == "none":
        review_required = True

    if confidence >= REVIEW_CONFIDENCE:
        confidence_label = "High (model-estimated)"
    elif confidence >= LOW_CONFIDENCE:
        confidence_label = "Moderate (model-estimated)"
    else:
        confidence_label = "Low (model-estimated)"

    return {
        "confidence_label": confidence_label,
        "review_required": review_required,
        "review_reasons": reasons,
        "privacy_note": "Uploaded images are processed for analysis; avoid submitting images containing unnecessary personal or sensitive information.",
        "disclaimer": "WasteWise is an educational decision-support prototype. Verify local disposal requirements before acting.",
    }
