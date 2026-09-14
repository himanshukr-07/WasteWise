from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path
from typing import Any

from ollama import Client
from qdrant_client import QdrantClient
from qdrant_client.http import models

BASE_DIR = Path(__file__).resolve().parents[2]
KB_DIR = BASE_DIR / "backend" / "data" / "knowledge_base"
QDRANT_PATH = BASE_DIR / "backend" / "data" / "qdrant"
COLLECTION_NAME = "wastewise_knowledge"
EMBEDDING_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text:latest")
TEXT_MODEL = os.getenv("OLLAMA_TEXT_MODEL", "qwen3:4b")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
TOP_K = int(os.getenv("RAG_TOP_K", "4"))

CATEGORY_NAMES = [
    "Organic", "Paper", "Plastic", "Glass", "Metal",
    "E-waste", "Hazardous", "Other / Unknown",
]

FILE_CATEGORIES = {
    "01_solid_waste_management.txt": ["Other / Unknown"],
    "02_plastic_waste.txt": ["Plastic"],
    "03_e_waste.txt": ["E-waste"],
    "04_battery_waste.txt": ["E-waste", "Hazardous"],
    "05_biomedical_and_medicine_related_waste.txt": ["Hazardous"],
    "06_wastewise_general_principles.txt": CATEGORY_NAMES,
    "07_metal_waste.txt": ["Metal"],
    "08_glass_waste.txt": ["Glass"],
    "09_paper_waste.txt": ["Paper"],
    "10_organic_waste.txt": ["Organic"],
}

# Dedicated category documents outrank general documents.
FILE_PRIMARY_CATEGORY = {
    "02_plastic_waste.txt": "Plastic",
    "03_e_waste.txt": "E-waste",
    "04_battery_waste.txt": "E-waste",
    "05_biomedical_and_medicine_related_waste.txt": "Hazardous",
    "07_metal_waste.txt": "Metal",
    "08_glass_waste.txt": "Glass",
    "09_paper_waste.txt": "Paper",
    "10_organic_waste.txt": "Organic",
}

CATEGORY_KEYWORDS = {
    "Organic": ["organic", "food waste", "food", "peel", "fruit", "vegetable", "biodegradable"],
    "Paper": ["paper", "newspaper", "cardboard", "carton"],
    "Plastic": ["plastic", "polythene", "polythene bag", "wrapper", "bottle cap"],
    "Glass": ["glass", "bottle", "jar"],
    "Metal": ["metal", "pen", "steel", "aluminium", "aluminum", "tin", "can"],
    "E-waste": ["e-waste", "electronic", "electronics", "laptop", "phone", "mobile", "charger", "keyboard", "mouse", "circuit", "battery", "batteries"],
    "Hazardous": ["hazardous", "medicine", "medical", "biomedical", "chemical", "paint", "pesticide"],
}

ollama_client = Client(host=OLLAMA_HOST)
qdrant_client = QdrantClient(path=str(QDRANT_PATH))


def _chunk_text(text: str, chunk_size: int = 900, overlap: int = 120) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == len(text):
            break
        start = max(0, end - overlap)
    return chunks


def _embed(text: str) -> list[float]:
    if hasattr(ollama_client, "embed"):
        response = ollama_client.embed(model=EMBEDDING_MODEL, input=text)
        return [float(x) for x in response["embeddings"][0]]
    response = ollama_client.embeddings(model=EMBEDDING_MODEL, prompt=text)
    return [float(x) for x in response["embedding"]]


def _file_source(path: Path) -> str:
    first_lines = path.read_text(encoding="utf-8").splitlines()[:6]
    for line in first_lines:
        if line.startswith("Source URL:"):
            return line.split(":", 1)[1].strip()
    return path.name


def _file_title(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines()[:6]:
        if line.startswith("Title:"):
            return line.split(":", 1)[1].strip()
    return path.stem.replace("_", " ").title()


def collection_exists() -> bool:
    return qdrant_client.collection_exists(COLLECTION_NAME)


def knowledge_base_status() -> dict[str, Any]:
    exists = collection_exists()
    count = 0
    if exists:
        count = qdrant_client.count(collection_name=COLLECTION_NAME, exact=True).count
    files = sorted(KB_DIR.glob("*.txt"))
    return {
        "collection": COLLECTION_NAME,
        "indexed": exists,
        "vectors": count,
        "documents": len(files),
        "embedding_model": EMBEDDING_MODEL,
        "top_k": TOP_K,
        "path": str(QDRANT_PATH),
    }


def index_knowledge_base(force: bool = False) -> dict[str, Any]:
    files = sorted(KB_DIR.glob("*.txt"))
    if not files:
        raise RuntimeError(f"No knowledge-base .txt files found in {KB_DIR}")
    if collection_exists() and not force:
        return {"status": "already_indexed", **knowledge_base_status()}

    first_vector = _embed("WasteWise waste management knowledge base")
    qdrant_client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(size=len(first_vector), distance=models.Distance.COSINE),
    )

    points: list[models.PointStruct] = []
    for path in files:
        raw = path.read_text(encoding="utf-8")
        title = _file_title(path)
        source = _file_source(path)
        for chunk_index, chunk in enumerate(_chunk_text(raw)):
            text_for_embedding = f"Title: {title}\nSource: {source}\n{chunk}"
            vector = _embed(text_for_embedding)
            stable_id = int(hashlib.sha1(f"{path.name}:{chunk_index}".encode()).hexdigest()[:15], 16)
            categories = FILE_CATEGORIES.get(path.name, ["Other / Unknown"])
            primary = FILE_PRIMARY_CATEGORY.get(path.name)
            points.append(
                models.PointStruct(
                    id=stable_id,
                    vector=vector,
                    payload={
                        "text": chunk,
                        "title": title,
                        "source": source,
                        "document": path.name,
                        "chunk": chunk_index,
                        "categories": categories,
                        "primary_category": primary,
                        "is_general": path.name in {"01_solid_waste_management.txt", "06_wastewise_general_principles.txt"},
                    },
                )
            )
    qdrant_client.upsert(collection_name=COLLECTION_NAME, points=points)
    return {"status": "indexed", **knowledge_base_status()}


QUERY_ALIASES = {
    "battery": ["battery", "batteries", "used battery", "old battery", "cell"],
    "e-waste": ["e-waste", "ewaste", "electronic waste", "electronics", "electronic item", "charger", "laptop", "phone", "mobile", "keyboard", "mouse"],
    "plastic": ["plastic", "plastic bottle", "polythene", "polyethylene", "wrapper", "plastic packaging"],
    "glass": ["glass", "glass bottle", "jar", "container"],
    "metal": ["metal", "metal pen", "pen", "steel", "aluminium", "aluminum", "tin", "can"],
    "paper": ["paper", "newspaper", "cardboard", "carton", "paper waste"],
    "organic": ["organic", "food waste", "food", "peel", "fruit peel", "vegetable", "biodegradable", "kitchen waste"],
    "hazardous": ["hazardous", "hazardous waste", "medicine", "medical", "biomedical", "chemical", "paint", "pesticide"],
}


def _detect_query_category(query: str) -> str | None:
    text = re.sub(r"[^a-z0-9\- ]+", " ", query.lower())
    # Explicit phrases first so "battery" reliably maps to the special stream.
    if any(alias in text for alias in QUERY_ALIASES["battery"]):
        return "E-waste"
    if any(alias in text for alias in QUERY_ALIASES["hazardous"]):
        return "Hazardous"
    checks = [
        ("E-waste", QUERY_ALIASES["e-waste"]),
        ("Plastic", QUERY_ALIASES["plastic"]),
        ("Glass", QUERY_ALIASES["glass"]),
        ("Metal", QUERY_ALIASES["metal"]),
        ("Paper", QUERY_ALIASES["paper"]),
        ("Organic", QUERY_ALIASES["organic"]),
    ]
    for category, aliases in checks:
        if any(alias in text for alias in aliases):
            return category
    return None


def _scroll_all_points() -> list[Any]:
    points: list[Any] = []
    offset = None
    while True:
        batch, offset = qdrant_client.scroll(
            collection_name=COLLECTION_NAME,
            limit=256,
            offset=offset,
            with_payload=True,
            with_vectors=True,
        )
        points.extend(batch)
        if offset is None:
            break
    return points


def _collection_category_coverage(points: list[Any]) -> set[str]:
    coverage: set[str] = set()
    for point in points:
        payload = point.payload or {}
        cats = payload.get("categories", [])
        if isinstance(cats, list):
            coverage.update(str(x) for x in cats)
        primary = payload.get("primary_category")
        if primary:
            coverage.add(str(primary))
    return coverage


def _ensure_index_coverage(category: str | None = None) -> list[Any]:
    """Ensure the persisted Qdrant index matches the current knowledge-base files."""
    files = sorted(KB_DIR.glob("*.txt"))
    if not files:
        return []
    points = _scroll_all_points() if collection_exists() else []
    indexed_documents = {str((p.payload or {}).get("document", "")) for p in points}
    expected_documents = {p.name for p in files}
    coverage = _collection_category_coverage(points)
    needs_reindex = (
        not collection_exists()
        or not expected_documents.issubset(indexed_documents)
        or (category is not None and category not in coverage)
    )
    if needs_reindex:
        index_knowledge_base(force=True)
        points = _scroll_all_points()
    return points


def _vector_from_point(point: Any) -> list[float] | None:
    vector = getattr(point, "vector", None)
    if isinstance(vector, list):
        return [float(x) for x in vector]
    if isinstance(vector, dict):
        # Qdrant can expose named vectors; use the first vector for this single-vector collection.
        for value in vector.values():
            if isinstance(value, list):
                return [float(x) for x in value]
    return None


def _semantic_score(query_vector: list[float], document_vector: list[float] | None) -> float:
    """Return cosine similarity between two embedding vectors.

    Qdrant is used as the persistent vector store, but this local prototype also
    reranks its small knowledge base in Python. The previous Phase 11 build
    referenced this helper without defining it, which caused every scan/chat
    request that reached reranking to fail with NameError.
    """
    if not query_vector or not document_vector or len(query_vector) != len(document_vector):
        return 0.0

    dot = sum(a * b for a, b in zip(query_vector, document_vector))
    query_norm = sum(a * a for a in query_vector) ** 0.5
    document_norm = sum(b * b for b in document_vector) ** 0.5
    if query_norm == 0.0 or document_norm == 0.0:
        return 0.0

    score = dot / (query_norm * document_norm)
    # Floating-point noise can push the value a tiny amount outside the cosine range.
    return max(-1.0, min(1.0, float(score)))


def _keyword_overlap(query: str, text: str) -> int:
    qwords = {w for w in re.findall(r"[a-z0-9-]+", query.lower()) if len(w) >= 3}
    t = text.lower()
    return sum(1 for w in qwords if w in t)


def _alias_overlap(query: str, text: str) -> int:
    q = query.lower()
    t = text.lower()
    score = 0
    for aliases in QUERY_ALIASES.values():
        if any(alias in q for alias in aliases):
            score += sum(1 for alias in aliases if alias in t)
    return score



def _filesystem_fallback(category: str | None, limit: int) -> list[dict[str, Any]]:
    """Return category-relevant knowledge directly from the KB when vector retrieval is empty.

    This is a last-resort retrieval fallback for the small local prototype. It preserves
    grounding by using only files that are explicitly mapped to the requested category.
    """
    if not category:
        return []
    candidates: list[dict[str, Any]] = []
    for path in sorted(KB_DIR.glob("*.txt")):
        cats = FILE_CATEGORIES.get(path.name, ["Other / Unknown"])
        if category not in cats:
            continue
        raw = path.read_text(encoding="utf-8").strip()
        if not raw:
            continue
        title = _file_title(path)
        source = _file_source(path)
        chunks = _chunk_text(raw)
        for idx, chunk in enumerate(chunks[:2]):
            candidates.append({
                "score": 0.0,
                "semantic_score": 0.0,
                "keyword_overlap": 0,
                "alias_overlap": 0,
                "text": chunk,
                "title": title,
                "source": source,
                "document": path.name,
                "categories": cats,
                "primary_category": FILE_PRIMARY_CATEGORY.get(path.name),
                "is_general": path.name in {"01_solid_waste_management.txt", "06_wastewise_general_principles.txt"},
                "category_match": 1 if FILE_PRIMARY_CATEGORY.get(path.name) == category else 0,
                "broad_category_match": 1,
            })
        if len(candidates) >= limit:
            break
    candidates.sort(key=lambda r: (r["category_match"], not r["is_general"]), reverse=True)
    return candidates[:limit]

def retrieve(query: str, top_k: int | None = None, category: str | None = None) -> list[dict[str, Any]]:
    if not query.strip():
        return []
    category = category if category in CATEGORY_NAMES else _detect_query_category(query)
    points = _ensure_index_coverage(category)
    if not points:
        return []

    query_vector = _embed(query)
    limit = top_k or TOP_K
    results: list[dict[str, Any]] = []

    for point in points:
        payload = point.payload or {}
        categories = payload.get("categories", [])
        categories = categories if isinstance(categories, list) else [str(categories)]
        primary = payload.get("primary_category")
        semantic = _semantic_score(query_vector, _vector_from_point(point))
        text_blob = f"{payload.get('title', '')} {payload.get('text', '')}"
        overlap = _keyword_overlap(query, text_blob)
        alias_overlap = _alias_overlap(query, text_blob)
        exact_category = 1 if category and primary == category else 0
        broad_category = 1 if category and category in categories else 0
        is_general = bool(payload.get("is_general", False))

        # Rerank instead of hard-filtering. This avoids the earlier failure where
        # a valid category could disappear simply because its metadata was weak.
        rank_score = (
            semantic * 1.0
            + min(overlap, 8) * 0.035
            + min(alias_overlap, 6) * 0.04
            + exact_category * 0.32
            + broad_category * 0.16
            + (0.04 if is_general else 0.0)
        )
        results.append({
            "score": rank_score,
            "semantic_score": semantic,
            "keyword_overlap": overlap,
            "alias_overlap": alias_overlap,
            "text": str(payload.get("text", "")),
            "title": str(payload.get("title", "")),
            "source": str(payload.get("source", "")),
            "document": str(payload.get("document", "")),
            "categories": categories,
            "primary_category": primary,
            "is_general": is_general,
            "category_match": exact_category,
            "broad_category_match": broad_category,
        })

    results.sort(key=lambda r: r["score"], reverse=True)

    selected: list[dict[str, Any]] = []
    seen_docs: set[str] = set()
    for result in results:
        doc = result["document"]
        if doc in seen_docs:
            continue
        # A category-specific source is accepted with a lower semantic floor;
        # otherwise common phrasing differences can wrongly trigger the fallback.
        if category:
            category_relevant = result["category_match"] or result["broad_category_match"]
            if category_relevant:
                pass
            elif result["semantic_score"] < 0.45 and result["keyword_overlap"] == 0 and result["alias_overlap"] == 0:
                continue
        elif result["semantic_score"] < 0.35 and result["keyword_overlap"] == 0:
            continue
        seen_docs.add(doc)
        selected.append(result)
        if len(selected) >= limit:
            break

    if selected:
        return selected

    # Deterministic category fallback: if a user asks about a known waste stream and
    # Qdrant semantic retrieval yields nothing useful, use the explicitly mapped KB files.
    # This keeps the answer grounded instead of hallucinating.
    fallback = _filesystem_fallback(category, limit)
    return fallback

def _build_context(results: list[dict[str, Any]]) -> str:
    return "\n\n".join(
        f"[Source {idx}]\nTitle: {r['title']}\nSource URL: {r['source']}\nContent: {r['text']}"
        for idx, r in enumerate(results, start=1)
    )


def generate_grounded_answer(question: str, results: list[dict[str, Any]]) -> str:
    context = _build_context(results)
    system = (
        "You are WasteWise, an India-focused waste-management assistant. "
        "Answer using ONLY the supplied knowledge-base context. "
        "Do not invent legal requirements, bin colors, recycling availability, or local rules. "
        "If the context is insufficient, clearly say that the available sources do not establish the answer. "
        "Explain that local authority instructions can differ where applicable. "
        "Keep the answer practical and concise. Do not add a separate Sources line because sources are shown by the application."
    )
    response = ollama_client.chat(
        model=TEXT_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": f"Knowledge-base context:\n{context}\n\nQuestion: {question.strip()}"},
        ],
    )
    return response["message"]["content"].strip()


def get_disposal_guidance(category: str, item: str) -> dict[str, Any]:
    query = f"How should this waste item be segregated or disposed of in India? Item: {item}. Category: {category}."
    results = retrieve(query, top_k=TOP_K, category=category)
    if not results:
        return {
            "recommendation": "No grounded guidance was found. Check your local waste-management instructions before disposal.",
            "source": "No RAG sources found",
            "sources": [],
            "grounded": False,
            "source_relevance": "none",
        }

    dedicated = [r for r in results if r.get("category_match") == 1 and not r.get("is_general")]
    category_relevant = [r for r in results if r.get("broad_category_match") == 1 and not r.get("is_general")]
    source_relevance = "category-specific" if dedicated else ("limited" if category_relevant or any(r.get("is_general") for r in results) else "none")

    answer = generate_grounded_answer(query, results)
    source_candidates = dedicated or category_relevant or [r for r in results if r.get("is_general")]
    sources = []
    seen = set()
    for result in source_candidates:
        key = (result["title"], result["source"])
        if key not in seen:
            seen.add(key)
            sources.append({"title": result["title"], "url": result["source"]})

    grounded = bool(sources) and source_relevance != "none"
    return {
        "recommendation": answer,
        "source": sources[0]["title"] if sources else "RAG knowledge base",
        "sources": sources,
        "grounded": grounded,
        "source_relevance": source_relevance,
    }
