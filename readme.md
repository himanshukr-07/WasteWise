# WasteWise

## Local AI-Powered Waste Segregation & Disposal Assistant

WasteWise combines multimodal AI, category-aware RAG, scan history, dashboard analytics, and human feedback for responsible waste-management assistance.

### Changes
- Added deterministic category-aware knowledge-base fallback when semantic retrieval returns no usable results.
- Battery, plastic, glass, metal and other supported categories can fall back to explicitly mapped knowledge-base documents.
- Preserved grounded-only generation: the LLM receives only retrieved/fallback knowledge-base context.
- Added tests for query-category detection, knowledge-base coverage, and deterministic fallback behavior.
- Kept the responsive HTML/CSS/JS frontend and FastAPI/Ollama/Qdrant architecture unchanged.

### Run
```cmd
cd /d E:\AI-WasteWise
.venv\Scripts\activate
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

### Reindex
After replacing the project, run:
```text
POST /api/rag/reindex
```

### Local AI
- qwen2.5vl:3b — image analysis
- qwen3:4b — grounded text generation
- nomic-embed-text:latest — embeddings
- Qdrant local — vector storage

### Final QA test questions
- How should I dispose of an old battery?
- how to dispose a battery..?
- What should I do with a used battery?
- How should plastic waste be handled?
- Where should a glass bottle go?
- How should I dispose of a metal pen?

### Recommended image tests
- Plastic bottle
- Glass bottle
- Paper/cardboard
- Food/organic waste
- Metal object
- Battery/electronic item
- Unclear image

### Responsible use
WasteWise is an educational decision-support prototype. Grounded evidence is preferred; when category-specific evidence cannot be established, the system falls back conservatively and asks users to verify applicable local disposal requirements.


### Human-in-the-loop feedback
The Waste Scanner lets users confirm a result or submit a corrected waste category. Feedback is stored locally for evaluation and is not used for automatic model retraining. Runtime feedback and scan-history files are intentionally excluded from Git.
