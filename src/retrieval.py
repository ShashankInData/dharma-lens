"""Embedding index and retrieval for Dharma Lens."""

from __future__ import annotations

import argparse
import json
import math
import pickle
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol


class Embedder(Protocol):
    def encode(self, texts: list[str]) -> list[list[float]]: ...


@dataclass
class VectorIndex:
    chunks: list[dict[str, Any]]
    vectors: list[list[float]]


class LocalSentenceTransformerEmbedder:
    """SentenceTransformer wrapper loaded only when needed."""

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5") -> None:
        from sentence_transformers import SentenceTransformer

        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def encode(self, texts: list[str]) -> list[list[float]]:
        vectors = self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=False)
        return vectors.tolist()


def normalize_vector(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return [0.0 for _ in vector]
    return [value / norm for value in vector]


def cosine_similarity(vector_a: list[float], vector_b: list[float]) -> float:
    return sum(a * b for a, b in zip(vector_a, vector_b))


def build_index(chunks: list[dict[str, Any]], embedder: Embedder) -> VectorIndex:
    texts = [chunk["text"] for chunk in chunks]
    vectors = [normalize_vector(list(vector)) for vector in embedder.encode(texts)]
    return VectorIndex(chunks=chunks, vectors=vectors)


def save_index(index: VectorIndex, path: Path) -> None:
    """Save index as primitive data so CLI-built indexes load from any module."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"chunks": index.chunks, "vectors": index.vectors}
    with path.open("wb") as handle:
        pickle.dump(payload, handle)


def load_index(path: Path) -> VectorIndex:
    with path.open("rb") as handle:
        payload = pickle.load(handle)
    if isinstance(payload, VectorIndex):
        return payload
    return VectorIndex(chunks=payload["chunks"], vectors=payload["vectors"])


def infer_query_themes(query: str) -> list[str]:
    """Small transparent keyword-to-theme layer before heavier classifiers exist."""
    lowered = query.lower()
    rules = {
        "outcome-anxiety": ["result", "results", "outcome", "outcomes", "fail", "failure"],
        "work": ["work", "job", "career", "study", "exam", "application"],
        "anger": ["anger", "angry", "rage", "irritated", "irritation"],
        "self-control": ["control", "react", "reaction", "impulse"],
        "relationship": ["relationship", "partner", "friend", "family", "people"],
        "non-reactivity": ["react", "reaction", "disturb", "disturbed", "calm"],
        "mind": ["mind", "thought", "thoughts", "focus", "distracted"],
        "focus": ["focus", "concentrate", "attention"],
        "detachment": ["attached", "attachment", "detach", "detachment"],
        "duty": ["duty", "responsibility", "responsibilities", "should do"],
    }
    themes: list[str] = []
    for theme, keywords in rules.items():
        if any(re.search(rf"\b{re.escape(keyword)}\b", lowered) for keyword in keywords):
            themes.append(theme)
    return themes


def retrieve(
    query: str,
    index: VectorIndex,
    embedder: Embedder,
    *,
    top_k: int = 5,
    query_themes: list[str] | None = None,
    theme_boost: float = 0.12,
) -> list[dict[str, Any]]:
    if top_k < 1:
        raise ValueError("top_k must be at least 1")

    inferred_themes = infer_query_themes(query)
    all_query_themes = sorted(dict.fromkeys((query_themes or []) + inferred_themes))
    query_vector = normalize_vector(list(embedder.encode([query])[0]))

    scored: list[dict[str, Any]] = []
    for chunk, vector in zip(index.chunks, index.vectors):
        similarity = cosine_similarity(query_vector, vector)
        overlap = sorted(set(all_query_themes).intersection(chunk.get("themes", [])))
        score = similarity + (theme_boost * len(overlap))
        result = dict(chunk)
        result["score"] = score
        result["vector_score"] = similarity
        result["theme_overlap"] = overlap
        scored.append(result)

    scored.sort(key=lambda item: item["score"], reverse=True)
    return scored[:top_k]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Dharma Lens vector index")
    parser.add_argument(
        "--chunks",
        default="data/processed/dharma_lens_chunks.json",
        help="Chunk JSON path",
    )
    parser.add_argument(
        "--output",
        default="indexes/dharma_lens_vector_index.pkl",
        help="Pickle output path",
    )
    parser.add_argument(
        "--model",
        default="BAAI/bge-small-en-v1.5",
        help="SentenceTransformers model name",
    )
    args = parser.parse_args()

    chunks = json.loads(Path(args.chunks).read_text(encoding="utf-8"))
    embedder = LocalSentenceTransformerEmbedder(args.model)
    index = build_index(chunks, embedder)
    save_index(index, Path(args.output))
    print(f"Wrote index with {len(index.chunks)} chunks to {args.output}")


if __name__ == "__main__":
    main()
