"""Grounded answer generation and citation validation for Dharma Lens."""

from __future__ import annotations

import argparse
import json
import os
import re
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from src.retrieval import LocalSentenceTransformerEmbedder, load_index, retrieve

CITATION_RE = re.compile(r"Bhagavad Gita \d+\.\d+(?:-\d+\.\d+)?")


@dataclass
class CitationValidationResult:
    is_valid: bool
    allowed_citations: list[str]
    found_citations: list[str]
    unsupported_citations: list[str]


def citations_in_answer(answer: str) -> list[str]:
    """Return unique Bhagavad Gita citations in first-seen order."""
    citations = CITATION_RE.findall(answer)
    return list(dict.fromkeys(citations))


def allowed_citations(chunks: list[dict[str, Any]]) -> list[str]:
    return list(dict.fromkeys(chunk["citation"] for chunk in chunks))


def validate_citations(
    answer: str, chunks: list[dict[str, Any]]
) -> CitationValidationResult:
    allowed = allowed_citations(chunks)
    found = citations_in_answer(answer)
    unsupported = [citation for citation in found if citation not in allowed]
    return CitationValidationResult(
        is_valid=not unsupported,
        allowed_citations=allowed,
        found_citations=found,
        unsupported_citations=unsupported,
    )


def has_sufficient_evidence(
    chunks: list[dict[str, Any]], *, min_score: float = 0.5
) -> bool:
    if not chunks:
        return False
    best = chunks[0]
    return best.get("score", 0.0) >= min_score or bool(best.get("theme_overlap"))


def build_grounded_prompt(question: str, chunks: list[dict[str, Any]]) -> str:
    context_blocks = []
    for rank, chunk in enumerate(chunks, start=1):
        context_blocks.append(
            "\n".join(
                [
                    f"[Source {rank}] {chunk['citation']}",
                    f"Chunk ID: {chunk['chunk_id']}",
                    f"Themes: {', '.join(chunk.get('themes', [])) or 'none'}",
                    f"Text:\n{chunk['text']}",
                ]
            )
        )

    return f"""You are Dharma Lens, a Bhagavad Gita-grounded reflection assistant.

Rules:
- Use only the provided Bhagavad Gita context.
- Do not invent verses, citations, Sanskrit, or commentary.
- Do not claim divine authority.
- Do not give medical, legal, emergency, or therapy advice.
- If the context is weak, say the answer is only a possible reflection.
- Every verse reference in the answer must be one of the provided source citations exactly.
- Keep the answer practical, calm, and non-preachy.

User question:
{question}

Provided Bhagavad Gita context:
{chr(10).join(context_blocks)}

Answer using exactly this structure:

Question interpreted as:

Relevant verses:

What the verses say:

Reflection:

Practical step:

What this does not decide:

Sources:

Confidence: high / medium / low
"""


def build_weak_evidence_answer(question: str) -> str:
    return f"""Question interpreted as: {question}

I do not have strong enough Bhagavad Gita evidence from the retrieved verses to answer this cleanly.

Try rephrasing the question around a clearer theme, for example duty, attachment, anger, fear, grief, self-control, discipline, work, or steadiness.

What this does not decide: This app should not force a spiritual answer when the source support is weak.

Sources:

Confidence: low
"""


def build_unsupported_citation_answer(
    validation: CitationValidationResult,
) -> str:
    return """The generated answer referenced unsupported citations, so I am not showing it as a grounded response.

Unsupported citations: {unsupported}
Allowed citations for this query: {allowed}

Please retry with stricter grounding or inspect the retrieved verses directly.

Sources: {allowed}

Confidence: low
""".format(
        unsupported=", ".join(validation.unsupported_citations),
        allowed=", ".join(validation.allowed_citations),
    )


def select_answer_chunks(
    chunks: list[dict[str, Any]], *, max_chunks: int = 3
) -> list[dict[str, Any]]:
    """Pick concise answer context, preferring direct verse chunks over duplicate groups."""
    selected: list[dict[str, Any]] = []
    seen_verse_ids: set[str] = set()

    def try_add(chunk: dict[str, Any], *, allow_partial_overlap: bool = False) -> None:
        if len(selected) >= max_chunks:
            return
        verse_ids = set(chunk.get("verse_ids", []))
        if verse_ids and verse_ids.issubset(seen_verse_ids):
            return
        if verse_ids and verse_ids.intersection(seen_verse_ids) and not allow_partial_overlap:
            return
        selected.append(chunk)
        seen_verse_ids.update(verse_ids)

    for chunk in chunks:
        try_add(chunk, allow_partial_overlap=True)
    return selected


def extractive_grounded_answer(question: str, chunks: list[dict[str, Any]]) -> str:
    """Deterministic fallback answer that quotes retrieved context without LLM generation."""
    top_chunks = select_answer_chunks(chunks, max_chunks=2)
    citations = "; ".join(chunk["citation"] for chunk in top_chunks)
    summaries = []
    for chunk in top_chunks:
        first_translation_line = next(
            (line for line in chunk["text"].splitlines() if line.startswith("Translation")),
            chunk["text"].splitlines()[-1],
        )
        summaries.append(f"- {chunk['citation']}: {first_translation_line}")

    return f"""Question interpreted as: {question}

Relevant verses: {citations}

What the verses say:
{chr(10).join(summaries)}

Reflection: Based on these retrieved verses, the Gita points attention back to disciplined action, steadiness of mind, and reducing attachment to outcomes. This is a grounded reflection from the selected sources, not a command.

Practical step: Identify the action that is actually yours to perform today. Do that clearly, then pause before mentally trying to control the result.

What this does not decide: It does not replace practical planning, professional advice, or a direct human conversation where needed.

Sources: {citations}

Confidence: medium
"""


def generate_grounded_answer(
    question: str,
    chunks: list[dict[str, Any]],
    *,
    llm: Callable[[str], str] | None = None,
    min_score: float = 0.5,
) -> str:
    if not has_sufficient_evidence(chunks, min_score=min_score):
        return build_weak_evidence_answer(question)

    if llm is None:
        answer = extractive_grounded_answer(question, chunks)
    else:
        prompt = build_grounded_prompt(question, chunks)
        answer = llm(prompt)

    validation = validate_citations(answer, chunks)
    if not validation.is_valid:
        return build_unsupported_citation_answer(validation)
    return answer


def openrouter_llm(prompt: str) -> str:
    """Call OpenRouter using OPENROUTER_API_KEY. Not used in tests."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    model = os.getenv("DHARMA_LENS_MODEL", "openai/gpt-4o-mini")
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You answer only from provided Bhagavad Gita context and cite sources exactly.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }
    request = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/ShashankInData/dharma-lens",
            "X-Title": "Dharma Lens",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        data = json.loads(response.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"]


def featherless_llm(prompt: str) -> str:
    """Call Featherless AI provider via Hugging Face Inference API."""
    token = os.getenv("HF_TOKEN")
    if not token:
        raise RuntimeError("HF_TOKEN is not set")
    try:
        from huggingface_hub import InferenceClient
    except ImportError as e:
        raise RuntimeError("huggingface_hub not installed") from e

    model = os.getenv("DHARMA_LENS_LLM_MODEL", "Qwen/Qwen2.5-1.5B-Instruct")
    provider = os.getenv("DHARMA_LENS_LLM_PROVIDER", "featherless-ai")
    client = InferenceClient(model=model, provider=provider, token=token)
    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.2,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        raise RuntimeError(f"Featherless provider failed: {e}") from e


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate grounded Dharma Lens answer")
    parser.add_argument("question", help="User question")
    parser.add_argument("--index", default="indexes/dharma_lens_vector_index.pkl")
    parser.add_argument("--model", default="BAAI/bge-small-en-v1.5")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument(
        "--use-openrouter",
        action="store_true",
        help="Use OpenRouter instead of deterministic extractive fallback",
    )
    args = parser.parse_args()

    index = load_index(Path(args.index))
    embedder = LocalSentenceTransformerEmbedder(args.model)
    chunks = retrieve(args.question, index, embedder, top_k=args.top_k)
    answer = generate_grounded_answer(
        args.question,
        chunks,
        llm=openrouter_llm if args.use_openrouter else None,
    )
    print(answer)


if __name__ == "__main__":
    main()