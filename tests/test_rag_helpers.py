import sys
import types

# Stub optional runtime dependencies for pure-helper tests in this build environment.
ollama_stub = types.ModuleType("ollama")
class DummyOllamaClient:
    def __init__(self, *args, **kwargs): pass
ollama_stub.Client = DummyOllamaClient
sys.modules.setdefault("ollama", ollama_stub)

qdrant_stub = types.ModuleType("qdrant_client")
class DummyQdrantClient:
    def __init__(self, *args, **kwargs): pass
qdrant_stub.QdrantClient = DummyQdrantClient
sys.modules.setdefault("qdrant_client", qdrant_stub)

http_stub = types.ModuleType("qdrant_client.http")
models_stub = types.ModuleType("qdrant_client.http.models")
class DummyModels: pass
models_stub.PointStruct = DummyModels
models_stub.VectorParams = DummyModels
models_stub.Distance = types.SimpleNamespace(COSINE="cosine")
http_stub.models = models_stub
sys.modules.setdefault("qdrant_client.http", http_stub)
sys.modules.setdefault("qdrant_client.http.models", models_stub)

from backend.services.rag import _detect_query_category, _filesystem_fallback


def test_question_variants_map_to_expected_category():
    assert _detect_query_category("how to dispose a battery..?") == "E-waste"
    assert _detect_query_category("what should i do with an old battery?") == "E-waste"
    assert _detect_query_category("how should plastic waste be handled?") == "Plastic"
    assert _detect_query_category("where should a glass bottle go?") == "Glass"
    assert _detect_query_category("how should i dispose of a metal pen?") == "Metal"


def test_battery_fallback_is_category_specific():
    results = _filesystem_fallback("E-waste", 4)
    assert results
    assert any(r["primary_category"] == "E-waste" for r in results)


def test_plastic_fallback_is_category_specific():
    results = _filesystem_fallback("Plastic", 4)
    assert results
    assert any(r["primary_category"] == "Plastic" for r in results)
