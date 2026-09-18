# WasteWise Architecture

## High-level flow

```text
Browser (HTML/CSS/JS)
        │
        │ HTTP / REST
        ▼
     FastAPI
        │
        ├───────────────┐
        │               │
        ▼               ▼
  Ollama Vision      RAG Services
  qwen2.5vl:3b          │
        │               ├── nomic-embed-text:latest
        │               │
        │               ▼
        │             Qdrant
        │               │
        └───────┬───────┘
                ▼
           qwen3:4b
                │
       ┌────────┼────────┐
       ▼        ▼        ▼
   Sources   Feedback  History
                          │
                          ▼
                      Dashboard
```

## Scanner path

1. User selects an image.
2. FastAPI validates the uploaded file.
3. `qwen2.5vl:3b` identifies the item and proposes a supported category.
4. WasteWise normalizes the category to its controlled taxonomy.
5. RAG retrieves category-relevant knowledge.
6. `qwen3:4b` produces a grounded recommendation.
7. The UI shows confidence labeling, grounding status, sources, and verification guidance where needed.
8. The scan can be saved to local history and evaluated through feedback.

## Assistant path

1. User submits a waste-management question.
2. The backend detects a relevant waste category when possible.
3. Qdrant retrieval uses semantic similarity plus category-aware matching/fallback.
4. Only retrieved knowledge-base context is supplied to the text model for grounded responses.
5. Sources are returned with the answer.

## Data boundaries

Tracked in Git:
- source code
- tests
- knowledge-base source documents
- documentation

Intentionally local / ignored:
- `.env`
- Python virtual environment
- Qdrant local database
- scan history
- feedback history
- temporary uploads and caches

## Design principle

The vision model answers **“What is this?”**

The retrieval system answers **“What does the available guidance say?”**

The text model answers **“How should that evidence be explained clearly?”**

This separation reduces unsupported disposal claims and makes the system easier to test and explain.
