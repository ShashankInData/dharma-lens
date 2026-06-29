from src.ui import answer_question, format_sources_markdown


class FakeEmbedder:
    def encode(self, texts):
        vectors = []
        for text in texts:
            lowered = text.lower()
            vectors.append([
                1.0 if "result" in lowered or "work" in lowered else 0.0,
                1.0 if "anger" in lowered else 0.0,
            ])
        return vectors


class FakeIndex:
    chunks = [
        {
            "chunk_id": "verse:2.47",
            "chunk_type": "verse",
            "citation": "Bhagavad Gita 2.47",
            "verse_ids": ["2.47"],
            "themes": ["work", "outcome-anxiety", "detachment"],
            "text": "Bhagavad Gita 2.47\nTranslation (Swami Sivananda): Your right is only to work, but not to its results.",
        },
        {
            "chunk_id": "verse:2.63",
            "chunk_type": "verse",
            "citation": "Bhagavad Gita 2.63",
            "verse_ids": ["2.63"],
            "themes": ["anger"],
            "text": "Bhagavad Gita 2.63\nTranslation (Swami Sivananda): From anger comes delusion.",
        },
    ]
    vectors = [[1.0, 0.0], [0.0, 1.0]]


def test_format_sources_markdown_lists_retrieved_chunks():
    sources = format_sources_markdown([
        {
            "chunk_id": "verse:2.47",
            "citation": "Bhagavad Gita 2.47",
            "score": 0.91,
            "theme_overlap": ["work", "outcome-anxiety"],
            "text": "Bhagavad Gita 2.47\nTranslation: Your right is only to work.",
        }
    ])

    assert "Bhagavad Gita 2.47" in sources
    assert "score: 0.910" in sources
    assert "work, outcome-anxiety" in sources


def test_answer_question_returns_answer_and_sources_without_storage():
    answer, sources = answer_question(
        "I am anxious about work results",
        index=FakeIndex(),
        embedder=FakeEmbedder(),
        top_k=2,
    )

    assert "Question interpreted as" in answer
    assert "Bhagavad Gita 2.47" in answer
    assert "Confidence:" in answer
    assert "Retrieved sources" in sources
    assert "Bhagavad Gita 2.47" in sources


def test_answer_question_rejects_blank_input():
    answer, sources = answer_question("   ", index=FakeIndex(), embedder=FakeEmbedder())

    assert answer == "Ask a specific life, work, emotion, discipline, or relationship question."
    assert sources == "No retrieval run."
