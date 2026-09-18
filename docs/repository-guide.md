# GitHub Repository Guide

This repository contains the stable WasteWise internship build.

## What is versioned

- `backend/` source code
- `frontend/` source code
- `tests/` automated tests
- `backend/data/knowledge_base/` source knowledge
- `docs/` documentation and screenshots
- `README.md`
- `requirements.txt`
- `.gitignore`

## What is not versioned

The `.gitignore` intentionally excludes local runtime and environment files, including:

```text
.venv/
.env
backend/data/qdrant/
backend/data/scan_history.json
backend/data/feedback.json
__pycache__/
.pytest_cache/
uploads/
temp/
*.zip
```

## Release baseline

The repository baseline corresponds to the stable, QA-tested WasteWise application used for the internship submission preparation.

## Recommended workflow

```bash
git status
git diff
python -m pytest
git add .
git commit -m "type: concise change description"
git push origin main
```
