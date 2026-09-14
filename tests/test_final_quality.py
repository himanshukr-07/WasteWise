from pathlib import Path

KB = Path(__file__).resolve().parents[1] / "backend" / "data" / "knowledge_base"


def test_expected_category_documents_exist():
    expected = [
        "02_plastic_waste.txt",
        "03_e_waste.txt",
        "04_battery_waste.txt",
        "07_metal_waste.txt",
        "08_glass_waste.txt",
        "09_paper_waste.txt",
        "10_organic_waste.txt",
    ]
    for filename in expected:
        assert (KB / filename).exists(), filename


def test_knowledge_base_not_empty():
    files = list(KB.glob("*.txt"))
    assert len(files) >= 10
    assert all(p.read_text(encoding="utf-8").strip() for p in files)
