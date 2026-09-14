# WasteWise

WasteWise is a local AI-powered waste segregation and disposal assistant designed to help users identify common waste items, understand their waste category, and receive grounded disposal guidance.

The project is being developed for the **1M1B AI for Sustainability Virtual Internship** and is aligned primarily with **SDG 12: Responsible Consumption and Production**, with relevance to SDG 11: Sustainable Cities and Communities.

## Problem Statement

Incorrect waste segregation and disposal can reduce recycling effectiveness and create environmental and health risks. People may also be unsure how to handle special waste such as batteries, e-waste, or hazardous materials.

WasteWise addresses this problem by combining multimodal AI, retrieval-augmented generation (RAG), and a simple web interface to provide AI-assisted waste identification and source-grounded guidance.

## Solution

WasteWise provides two main AI workflows:

### 1. Waste Scanner

The user uploads an image of a waste item.

```text
Image
  ↓
Ollama Vision Model
  ↓
Item Identification
  ↓
Waste Category
  ↓
Category-aware RAG Retrieval
  ↓
Ollama LLM
  ↓
Disposal Recommendation + Sources
```

### 2. AI Assistant

The user asks a natural-language question about waste management.

```text
User Question
  ↓
Query / Category Analysis
  ↓
RAG Retrieval
  ↓
Relevant Knowledge
  ↓
Ollama LLM
  ↓
Grounded Answer + Sources
```

## Key Features

- Image-based waste identification
- Waste category classification
- Category-aware RAG retrieval
- Local AI inference using Ollama
- Source-grounded disposal guidance
- AI sustainability assistant
- Scan history
- Scan statistics and dashboard
- Waste-management guidelines section
- Responsible AI guidance
- Responsive HTML/CSS/JavaScript interface
- FastAPI REST backend
- Local Qdrant vector storage
- Local embedding generation

## Waste Categories

The current WasteWise taxonomy includes:

- Organic
- Paper
- Plastic
- Glass
- Metal
- E-waste
- Hazardous
- Other / Unknown

The application uses category-aware retrieval so that the most relevant category guidance is preferred during recommendation generation.

## Technology Stack

### Frontend

- HTML
- CSS
- JavaScript

### Backend

- Python
- FastAPI

### AI / Local Inference

- Ollama
- `qwen2.5vl:3b` — vision-language model
- `qwen3:4b` — text generation / assistant
- `nomic-embed-text:latest` — embeddings

### Retrieval

- Qdrant
- Retrieval-Augmented Generation (RAG)

## System Architecture

```text
                         WASTEWISE
                             |
                 HTML + CSS + JavaScript
                             |
                         FastAPI
                             |
            +----------------+----------------+
            |                                 |
            v                                 v
     Ollama Vision                       RAG Pipeline
      qwen2.5vl:3b                            |
            |                            nomic-embed-text
            v                                 |
      Item / Category                          v
            |                               Qdrant
            |                                 |
            +---------------+-----------------+
                            |
                            v
                       qwen3:4b
                            |
                            v
             Recommendation / Answer + Sources
```

## Project Structure

```text
WasteWise/
│
├── frontend/
│   ├── index.html
│   ├── scanner.html
│   ├── assistant.html
│   ├── history.html
│   ├── dashboard.html
│   ├── guidelines.html
│   ├── responsible-ai.html
│   ├── css/
│   └── js/
│
├── backend/
│   ├── main.py
│   ├── api/
│   ├── services/
│   ├── models/
│   └── data/
│       └── knowledge_base/
│
├── tests/
├── docs/
├── requirements.txt
├── .gitignore
├── .env.example
└── README.md
```

## Prerequisites

Install the following before running WasteWise:

- Python 3.10+ recommended
- Ollama
- Git

Make sure Ollama is installed and available from the terminal.

## Ollama Models

Pull the models used by the project:

```bash
ollama pull qwen2.5vl:3b
ollama pull qwen3:4b
ollama pull nomic-embed-text:latest
```

Check installed models:

```bash
ollama list
```

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/WasteWise.git
cd WasteWise
```

Create a virtual environment:

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

## RAG Setup

WasteWise uses a local Qdrant store and the `nomic-embed-text:latest` Ollama model for embeddings.

After preparing the knowledge base, rebuild the index using the project's RAG reindex endpoint.

Start the backend:

```powershell
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Open the API documentation:

```text
http://127.0.0.1:8000/docs
```

Use the RAG reindex endpoint when the knowledge base changes.

## Running the Application

Start FastAPI:

```powershell
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Then open:

```text
http://127.0.0.1:8000/
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

## Responsible AI

Responsible AI is a required part of the internship project and is built into WasteWise.

### Fairness

Waste decisions are based on the uploaded item and defined waste categories rather than personal characteristics.

### Transparency

The application shows the detected category, model-estimated confidence, grounding status, and available sources.

### Ethics

The system is designed as an AI-assisted decision-support tool. It should not present uncertain or unsupported disposal advice as guaranteed fact.

### Privacy

WasteWise is designed around local AI inference. Users should avoid uploading unnecessary personal or sensitive information.

### Human Verification

Uncertain, special, hazardous, e-waste, or weakly grounded cases can require verification rather than blindly trusting an AI-generated recommendation.

## Limitations

- Image-based identification can be incorrect for damaged, mixed, partially visible, or unusual items.
- Waste-management rules can vary by location and collection system.
- The system depends on the quality and coverage of its knowledge base.
- Model-estimated confidence should not be interpreted as a scientifically calibrated probability.
- The project is an AI-assisted prototype and should not replace official local waste-management instructions.

## Testing

The project includes automated tests for key retrieval and category-handling behavior.

Run:

```powershell
pytest
```

Before using the application, also verify that Ollama is running and the required models are available.

## Development History

The project was developed iteratively through the following major stages:

```text
Phase 1  → Initial UI
Phase 2  → FastAPI + Ollama integration
Phase 3  → Vision-based waste analysis
Phase 4  → RAG implementation
Phase 5  → Category-aware RAG
Phase 6  → Retrieval quality improvements
Phase 8  → Scan history + source UI
Phase 9  → Responsible AI safeguards
Phase 10 → Sustainability dashboard
Phase 11 → RAG robustness
Phase 12 → Final QA and validation
```

## Internship Alignment

WasteWise is designed around the internship's AI + Sustainability project framework:

- Real-world sustainability problem
- SDG alignment
- Meaningful use of AI
- Prototype / working demonstration
- Responsible AI considerations
- Expected impact

Primary SDG:

**SDG 12 — Responsible Consumption and Production**

Secondary relevance:

**SDG 11 — Sustainable Cities and Communities**

## Expected Impact

WasteWise is intended to:

- improve awareness of waste segregation
- make disposal guidance easier to access
- encourage better handling of recyclable and special waste
- support users with source-grounded information
- demonstrate responsible application of local AI for sustainability

## Future Scope

Possible future improvements include:

- broader waste-category coverage
- improved image recognition for mixed waste
- location-specific disposal rules
- richer analytics
- multilingual support
- additional sustainability modules

## License

Add the license selected for the repository here.

## Author

**Himanshu Kumar**

Developed as part of the **1M1B AI for Sustainability Virtual Internship**.
