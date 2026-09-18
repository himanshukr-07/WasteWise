# WasteWise — Final QA Checklist

This checklist is the Phase 16 validation plan for the WasteWise internship project.

## Automated QA

Run:

```powershell
python -m pytest
```

Automated tests cover RAG query handling, category-specific fallback, responsible-AI checks, security validation, feedback persistence, knowledge-base completeness, and required project structure.

## Manual End-to-End QA

### Scanner

Test representative images for:

- Plastic bottle → Plastic
- Glass bottle → Glass
- Metal pen → Metal
- Paper item → Paper
- Organic item → Organic
- Battery → appropriate special-waste handling
- Ambiguous/unsupported item → Other / Unknown or verification path

For each scan verify:

1. Image upload succeeds.
2. Analysis status changes to `Analyzing…` and then completes.
3. Item and category are displayed.
4. Confidence is clearly labeled as model-estimated.
5. RAG guidance is relevant to the detected category when evidence exists.
6. Sources are displayed clearly.
7. Weak/uncertain/special-waste results can be flagged for verification.
8. The scan appears in History.
9. Dashboard statistics update.
10. User feedback can be recorded.

### AI Assistant

Test natural-language variations such as:

```text
How should I dispose of an old battery?
how to dispose a battery..?
What should I do with a used battery?
Where should used batteries go?
How should plastic waste be handled?
How do I dispose of a glass bottle?
How should I dispose of a metal pen?
```

Verify that semantically equivalent questions retrieve relevant evidence and that answers do not claim unsupported item-specific rules.

### Dashboard and History

Verify:

- total scan count
- categories seen
- tie-safe most-scanned category display
- grounding quality counts
- review-required count
- recent scan records
- scan activity visualization
- feedback metrics, where available

### Security and Privacy

Verify:

- unsupported file types are rejected
- oversized images are rejected
- invalid image bytes are rejected
- overlong chat questions are rejected
- runtime data is not tracked by Git
- `.env` is not tracked by Git
- local Qdrant data is not tracked by Git

## Known Limitations

WasteWise is a local AI-assisted prototype. Image classification may be wrong for unusual, mixed, damaged, or partially visible objects. Disposal requirements can vary by location. Model-estimated confidence is not a calibrated probability. Official local guidance should be verified for operational decisions.

## QA Sign-off

Record the local test date, environment, model versions, and final `pytest` result before the internship submission.
