from backend.services.rag import _detect_query_category


def test_battery_variants_detect_e_waste():
    variants = [
        "How should I dispose of a battery?",
        "how to dispose a battery..?",
        "What should I do with an old battery?",
        "Where should used batteries go?",
    ]
    for question in variants:
        assert _detect_query_category(question) == "E-waste"


def test_common_categories_detect():
    assert _detect_query_category("How should plastic waste be handled?") == "Plastic"
    assert _detect_query_category("How do I dispose of a glass bottle?") == "Glass"
    assert _detect_query_category("How should I dispose of a metal pen?") == "Metal"
