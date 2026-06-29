import math
from pathlib import Path

from src.retrieval import VectorIndex, build_index, load_index, retrieve, save_index


class FakeEmbedder:
    def encode(self, texts):
        vectors = []
        for text in texts:
            lowered = text.lower()
            vectors.append(
                [
                    1.0 if "result" in lowered or "fruit" in lowered else 0.0,
                    1.0 if "anger" in lowered else 0.0,
                    1.0 if "duty" in lowered or "work" in lowered else 0.0,
                ]
            )
        return vectors


def sample_chunks():
    return [
        {
            "chunk_id": "verse:2.47",
            "chunk_type": "verse",
            "citation": "Bhagavad Gita 2.47",
            "themes": ["action", "detachment", "duty", "outcome-anxiety", "work"],
            "text": "Your right is only to work, but not to its results or fruits.",
        },
        {
            "chunk_id": "verse:2.63",
            "chunk_type": "verse",
            "citation": "Bhagavad Gita 2.63",
            "themes": ["anger", "confusion", "self-control"],
            "text": "From anger comes delusion and confusion of memory.",
        },
        {
            "chunk_id": "verse:12.15",
            "chunk_type": "verse",
            "citation": "Bhagavad Gita 12.15",
            "themes": ["calmness", "relationship", "non-reactivity"],
            "text": "He whom the world does not agitate is dear.",
        },
    ]


def test_build_index_normalizes_vectors_and_preserves_chunk_order():
    index = build_index(sample_chunks(), FakeEmbedder())

    assert isinstance(index, VectorIndex)
    assert [chunk["chunk_id"] for chunk in index.chunks] == [
        "verse:2.47",
        "verse:2.63",
        "verse:12.15",
    ]
    assert math.isclose(sum(value * value for value in index.vectors[0]), 1.0)


def test_save_and_load_index_roundtrip_without_pickling_class_identity(tmp_path: Path):
    index = build_index(sample_chunks(), FakeEmbedder())
    path = tmp_path / "index.pkl"

    save_index(index, path)
    loaded = load_index(path)

    assert loaded == index


def test_retrieve_ranks_by_vector_similarity():
    index = build_index(sample_chunks(), FakeEmbedder())

    results = retrieve("I am anxious about results from my work", index, FakeEmbedder(), top_k=2)

    assert [result["chunk_id"] for result in results] == ["verse:2.47", "verse:2.63"]
    assert results[0]["score"] > results[1]["score"]
    assert results[0]["citation"] == "Bhagavad Gita 2.47"


def test_retrieve_applies_theme_boost_for_explicit_query_themes():
    index = build_index(sample_chunks(), FakeEmbedder())

    results = retrieve(
        "I keep reacting emotionally in a relationship",
        index,
        FakeEmbedder(),
        top_k=1,
        query_themes=["relationship", "non-reactivity"],
    )

    assert results[0]["chunk_id"] == "verse:12.15"
    assert results[0]["theme_overlap"] == ["non-reactivity", "relationship"]
