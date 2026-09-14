from backend.services.responsible_ai import assess_scan


def test_low_confidence_requires_review():
    r = assess_scan(item="unknown", category="Other / Unknown", confidence=0.4, grounded=False, source_relevance="none")
    assert r["review_required"] is True
    assert r["confidence_label"].startswith("Low")


def test_special_category_requires_review():
    r = assess_scan(item="battery", category="E-waste", confidence=0.95, grounded=True, source_relevance="category-specific")
    assert r["review_required"] is True
