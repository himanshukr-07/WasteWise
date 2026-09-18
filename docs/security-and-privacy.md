# WasteWise Security & Privacy Controls

Phase 14 hardens the local WasteWise prototype without adding authentication or cloud services.

## Input protection

- Scanner accepts only JPG, PNG, and WEBP uploads.
- Uploaded images are size-limited to 8 MB.
- Image pixel count is limited before vision processing.
- The file bytes are validated as a real image with Pillow before reaching Ollama.
- AI Assistant questions are limited to 2,000 characters.

## API protection

- CORS is restricted to configured local development origins rather than `*`.
- Only required HTTP methods and the `Content-Type` header are permitted by CORS.
- API responses use `Cache-Control: no-store`.
- Basic security response headers are applied.
- Oversized HTTP requests are rejected early when `Content-Length` is provided.

## Error handling

Internal exceptions are logged server-side while API responses return generic error messages. This reduces accidental exposure of internal paths, stack traces, or service details to users.

## Local data

The application does not need to persist uploaded images for the scan workflow. Runtime files such as scan history, feedback, and the local Qdrant store are excluded from Git tracking.

The public repository contains `.env.example`, not `.env`. Any future API keys or secrets must remain in `.env` or another secret-management mechanism and must never be committed.

## Human verification

WasteWise is a decision-support prototype. Uncertain, special, hazardous, e-waste, or weakly grounded results can require verification instead of being treated as guaranteed instructions.
