from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_required_frontend_pages_exist():
    pages = [
        "index.html",
        "scanner.html",
        "assistant.html",
        "history.html",
        "dashboard.html",
        "guidelines.html",
        "responsible-ai.html",
    ]
    for page in pages:
        assert (ROOT / "frontend" / page).is_file(), page


def test_required_backend_modules_exist():
    modules = [
        "main.py",
        "api/analyze.py",
        "api/chat.py",
        "api/history.py",
        "api/rag.py",
        "api/feedback.py",
        "services/rag.py",
        "services/vision.py",
        "services/history.py",
        "services/feedback.py",
        "services/responsible_ai.py",
        "services/security.py",
    ]
    for module in modules:
        assert (ROOT / "backend" / module).is_file(), module


def test_gitignore_protects_runtime_and_secret_files():
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    required_entries = [
        ".venv/",
        ".env",
        "backend/data/qdrant/",
        "backend/data/scan_history.json",
        "backend/data/feedback.json",
        "uploads/",
    ]
    for entry in required_entries:
        assert entry in gitignore, entry
