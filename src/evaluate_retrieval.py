"""Run Dharma Lens retrieval over evaluation questions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.retrieval import LocalSentenceTransformerEmbedder, load_index, retrieve


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate Dharma Lens retrieval samples")
    parser.add_argument("--index", default="indexes/dharma_lens_vector_index.pkl")
    parser.add_argument("--questions", default="eval/questions.json")
    parser.add_argument("--output", default="eval/retrieval_results.md")
    parser.add_argument("--model", default="BAAI/bge-small-en-v1.5")
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()

    index = load_index(Path(args.index))
    questions = json.loads(Path(args.questions).read_text(encoding="utf-8"))
    embedder = LocalSentenceTransformerEmbedder(args.model)

    lines = ["# Dharma Lens Retrieval Results", ""]
    total_hits = 0
    for question in questions:
        results = retrieve(
            question["question"],
            index,
            embedder,
            top_k=args.top_k,
            query_themes=question.get("themes", []),
        )
        expected = set(question.get("expected_verses", []))
        returned = [verse_id for result in results for verse_id in result["verse_ids"]]
        hit = bool(expected.intersection(returned))
        total_hits += int(hit)

        lines.extend(
            [
                f"## {question['id']}",
                "",
                f"Question: {question['question']}",
                f"Expected verses: {', '.join(question.get('expected_verses', []))}",
                f"Hit expected verse in top {args.top_k}: {'yes' if hit else 'no'}",
                "",
                "| Rank | Chunk | Citation | Score | Theme overlap |",
                "|---:|---|---|---:|---|",
            ]
        )
        for rank, result in enumerate(results, start=1):
            lines.append(
                "| {rank} | `{chunk}` | {citation} | {score:.3f} | {themes} |".format(
                    rank=rank,
                    chunk=result["chunk_id"],
                    citation=result["citation"],
                    score=result["score"],
                    themes=", ".join(result["theme_overlap"]),
                )
            )
        lines.append("")

    lines.insert(2, f"Questions with expected hit in top {args.top_k}: {total_hits}/{len(questions)}")
    lines.insert(3, "")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote retrieval report to {output_path}")
    print(f"expected_hit_rate_top_{args.top_k}={total_hits}/{len(questions)}")


if __name__ == "__main__":
    main()
