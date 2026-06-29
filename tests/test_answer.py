from src.answer import (
    build_grounded_prompt,
    build_weak_evidence_answer,
    citations_in_answer,
    generate_grounded_answer,
    has_sufficient_evidence,
    select_answer_chunks,
    validate_citations,
)


def sample_chunks():
    return [
        {
            "chunk_id": "verse:2.47",
            "citation": "Bhagavad Gita 2.47",
            "score": 0.93,
            "theme_overlap": ["work", "outcome-anxiety", "detachment"],
            "text": "Bhagavad Gita 2.47\nThemes: action, detachment, duty\nTranslation (Swami Sivananda): Your right is only to work, but not to its results; do not let the results of action be your motive, nor let your attachment be to inaction.",
        },
        {
            "chunk_id": "group:2.47-2.48",
            "citation": "Bhagavad Gita 2.47-2.48",
            "score": 0.89,
            "theme_overlap": ["work", "detachment"],
            "text": "Bhagavad Gita 2.48\nTranslation (Swami Sivananda): Perform action, O Arjuna, being steadfast in Yoga, abandoning attachment and balanced in success and failure.",
        },
    ]


def test_build_grounded_prompt_contains_context_rules_and_sources():
    prompt = build_grounded_prompt("I am anxious about work results", sample_chunks())

    assert "Use only the provided Bhagavad Gita context" in prompt
    assert "Do not invent verses" in prompt
    assert "Bhagavad Gita 2.47" in prompt
    assert "Bhagavad Gita 2.47-2.48" in prompt
    assert "What this does not decide" in prompt


def test_validate_citations_rejects_uncited_answer():
    answer = "Bhagavad Gita 18.66 says surrender everything."

    result = validate_citations(answer, sample_chunks())

    assert result.is_valid is False
    assert result.unsupported_citations == ["Bhagavad Gita 18.66"]


def test_citations_in_answer_finds_single_and_range_citations():
    answer = "See Bhagavad Gita 2.47 and Bhagavad Gita 2.47-2.48."

    assert citations_in_answer(answer) == ["Bhagavad Gita 2.47", "Bhagavad Gita 2.47-2.48"]


def test_has_sufficient_evidence_uses_score_and_theme_overlap():
    assert has_sufficient_evidence(sample_chunks(), min_score=0.5) is True
    assert has_sufficient_evidence([{"score": 0.2, "theme_overlap": []}], min_score=0.5) is False


def test_build_weak_evidence_answer_has_no_fake_citation():
    answer = build_weak_evidence_answer("Should I move countries tomorrow?")

    assert "I do not have strong enough Bhagavad Gita evidence" in answer
    assert "Bhagavad Gita" not in answer.split("Sources:")[-1]


def test_select_answer_chunks_keeps_ranked_context_but_skips_full_duplicates():
    chunks = [
        {"chunk_id": "verse:2.47", "chunk_type": "verse", "verse_ids": ["2.47"], "citation": "Bhagavad Gita 2.47"},
        {"chunk_id": "group:2.47-2.48", "chunk_type": "adjacent_verses", "verse_ids": ["2.47", "2.48"], "citation": "Bhagavad Gita 2.47-2.48"},
        {"chunk_id": "verse:2.47-copy", "chunk_type": "verse", "verse_ids": ["2.47"], "citation": "Bhagavad Gita 2.47"},
        {"chunk_id": "group:3.19-3.20", "chunk_type": "adjacent_verses", "verse_ids": ["3.19", "3.20"], "citation": "Bhagavad Gita 3.19-3.20"},
    ]

    selected = select_answer_chunks(chunks, max_chunks=3)

    assert [chunk["chunk_id"] for chunk in selected] == [
        "verse:2.47",
        "group:2.47-2.48",
        "group:3.19-3.20",
    ]


def test_generate_grounded_answer_uses_model_output_when_citations_are_valid():
    def fake_llm(prompt: str) -> str:
        return """Question interpreted as: Anxiety about work outcomes.

Relevant verses: Bhagavad Gita 2.47, Bhagavad Gita 2.47-2.48

What the verses say: Your control is over disciplined action, not over owning the result.

Reflection: The Gita points you back to steady work without attachment to success or failure.

Practical step: Do today's work clearly, then stop replaying the outcome.

What this does not decide: It does not replace practical planning.

Sources: Bhagavad Gita 2.47; Bhagavad Gita 2.47-2.48

Confidence: high"""

    answer = generate_grounded_answer(
        "I am anxious about work results", sample_chunks(), llm=fake_llm
    )

    assert "Question interpreted as" in answer
    assert "Bhagavad Gita 2.47" in answer
    assert "Confidence: high" in answer


def test_generate_grounded_answer_falls_back_when_model_invents_citation():
    def bad_llm(prompt: str) -> str:
        return "Bhagavad Gita 18.66 says this is definitely the answer."

    answer = generate_grounded_answer(
        "I am anxious about work results", sample_chunks(), llm=bad_llm
    )

    assert "The generated answer referenced unsupported citations" in answer
    assert "Bhagavad Gita 18.66" in answer
