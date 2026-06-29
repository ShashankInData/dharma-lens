"""Gradio UI for Dharma Lens."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

from src.answer import generate_grounded_answer
from src.retrieval import LocalSentenceTransformerEmbedder, VectorIndex, load_index, retrieve

DEFAULT_INDEX_PATH = Path("indexes/dharma_lens_vector_index.pkl")
DEFAULT_EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"


def format_sources_markdown(results: list[dict[str, Any]]) -> str:
    if not results:
        return "No sources retrieved."

    lines = ["### Retrieved sources", ""]
    for rank, result in enumerate(results, start=1):
        preview = result.get("text", "").replace("\n", " ")[:260]
        theme_overlap = ", ".join(result.get("theme_overlap", [])) or "none"
        lines.extend(
            [
                f"{rank}. **{result['citation']}**",
                f"   - chunk: `{result['chunk_id']}`",
                f"   - score: {result.get('score', 0.0):.3f}",
                f"   - theme overlap: {theme_overlap}",
                f"   - preview: {preview}",
                "",
            ]
        )
    return "\n".join(lines).strip()


@lru_cache(maxsize=1)
def get_index(index_path: str = str(DEFAULT_INDEX_PATH)) -> VectorIndex:
    return load_index(Path(index_path))


@lru_cache(maxsize=1)
def get_embedder(model_name: str = DEFAULT_EMBEDDING_MODEL) -> LocalSentenceTransformerEmbedder:
    return LocalSentenceTransformerEmbedder(model_name)


def answer_question(
    question: str,
    *,
    index: VectorIndex | None = None,
    embedder: Any | None = None,
    top_k: int = 5,
) -> tuple[str, str]:
    cleaned = question.strip()
    if not cleaned:
        return (
            "Ask a specific life, work, emotion, discipline, or relationship question.",
            "No retrieval run.",
        )

    active_index = index or get_index()
    active_embedder = embedder or get_embedder()
    results = retrieve(cleaned, active_index, active_embedder, top_k=top_k)
    answer = generate_grounded_answer(cleaned, results)
    sources = format_sources_markdown(results)
    return answer, sources


def build_app():
    import gradio as gr

    description = "Ask a life, work, emotion, discipline, or relationship question. Dharma Lens retrieves Bhagavad Gita verses and gives a grounded reflection with citations. It is not a guru, therapist, lawyer, or emergency service."

    examples = [
        "I am anxious about the results of my work. What should I remember?",
        "How do I control anger before I say something harmful?",
        "How can I stay calm when people around me disturb me?",
        "I keep losing focus and my mind runs everywhere. What does the Gita suggest?",
    ]

    with gr.Blocks(title="Dharma Lens") as demo:
        gr.Markdown("# Dharma Lens")
        gr.Markdown(description)
        with gr.Row():
            question = gr.Textbox(
                label="Question",
                placeholder="Example: I am anxious about the results of my work. What should I remember?",
                lines=4,
            )
        submit = gr.Button("Reflect", variant="primary")
        with gr.Row():
            answer = gr.Markdown(label="Answer")
        with gr.Accordion("Retrieved sources", open=False):
            sources = gr.Markdown()
        gr.Examples(examples=examples, inputs=question)
        submit.click(fn=answer_question, inputs=question, outputs=[answer, sources])
        question.submit(fn=answer_question, inputs=question, outputs=[answer, sources])
    return demo


if __name__ == "__main__":
    build_app().launch(server_name="127.0.0.1", server_port=7860)
