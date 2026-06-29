"""Gradio UI for Dharma Lens with chat history."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Tuple, List

import gradio as gr

from src.answer import (
    build_grounded_prompt,
    build_weak_evidence_answer,
    citations_in_answer,
    generate_grounded_answer,
    has_sufficient_evidence,
    select_answer_chunks,
    validate_citations,
)
from src.retrieval import LocalSentenceTransformerEmbedder, VectorIndex, load_index, retrieve

DEFAULT_INDEX_PATH = Path("indexes/dharma_lens_vector_index.pkl")
DEFAULT_EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
DEFAULT_LLM_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
DEFAULT_LLM_PROVIDER = "featherless-ai"
USE_LLM = os.getenv("DHARMA_LENS_USE_LLM", "false").lower() == "true"
LLM_MODEL = os.getenv("DHARMA_LENS_LLM_MODEL", DEFAULT_LLM_MODEL)
LLM_PROVIDER = os.getenv("DHARMA_LENS_LLM_PROVIDER", DEFAULT_LLM_PROVIDER)


def format_sources_markdown(results: list[dict[str, Any]]) -> str:
    """Format retrieved chunks as markdown source cards."""
    if not results:
        return "_No sources retrieved._"

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


def _call_llm_provider(prompt: str) -> str:
    """Call the configured LLM provider via Hugging Face Inference API."""
    if not USE_LLM:
        raise RuntimeError("LLM use is disabled via DHARMA_LENS_USE_LLM=false")
    try:
        from huggingface_hub import InferenceClient
    except ImportError as e:
        raise RuntimeError("huggingface_hub not installed") from e

    token = os.getenv("HF_TOKEN")
    if not token:
        raise RuntimeError("HF_TOKEN environment variable not set")

    client = InferenceClient(model=LLM_MODEL, provider=LLM_PROVIDER, token=token)
    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.2,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        # If provider fails, fall back to deterministic answer
        raise RuntimeError(f"LLM provider failed: {e}") from e


def answer_question(
    question: str,
    *,
    index: VectorIndex | None = None,
    embedder: Any | None = None,
    top_k: int = 5,
) -> Tuple[str, str]:
    """Return (answer, sources_md) using retrieval and optional LLM synthesis."""
    cleaned = question.strip()
    if not cleaned:
        return (
            "Ask a specific life, work, emotion, discipline, or relationship question.",
            "_No retrieval run._",
        )

    active_index = index or get_index()
    active_embedder = embedder or get_embedder()
    results = retrieve(cleaned, active_index, active_embedder, top_k=top_k)

    if not results:
        return (
            "I could not find relevant verses for your question. Please try rephrasing.",
            "_No sources retrieved._",
        )

    # Deterministic answer as baseline
    deterministic_answer = generate_grounded_answer(cleaned, results)
    det_citations = citations_in_answer(deterministic_answer)

    # If LLM is enabled, try to generate a smoother answer
    final_answer = deterministic_answer
    if USE_LLM:
        try:
            prompt = build_grounded_prompt(cleaned, results)
            llm_answer = _call_llm_provider(prompt)
            llm_citations = citations_in_answer(llm_answer)
            # Validate that LLM only used retrieved citations
            if validate_citations(llm_citations, det_citations):
                final_answer = llm_answer
            else:
                # LLM invented a citation; fall back to deterministic
                pass
        except Exception:
            # Any error: fall back to deterministic
            pass

    sources_md = format_sources_markdown(results)
    return final_answer, sources_md


def respond(
    message: str,
    chat_history: List[List[str]],
) -> Tuple[List[List[str]], str]:
    """Chat function for Gradio: takes message and history, returns updated history and cleared textbox."""
    answer, sources_md = answer_question(message)
    # Append user message and bot response
    chat_history = chat_history + [[message, answer]]
    return chat_history, "", sources_md


def build_app() -> gr.Blocks:
    with gr.Blocks(title="Dharma Lens") as demo:
        gr.Markdown("# Dharma Lens")
        gr.Markdown(
            "Ask a life, work, emotion, discipline, or relationship question. "
            "Dharma Lens retrieves Bhagavad Gita verses and gives a grounded reflection with citations. "
            "It is not a guru, therapist, lawyer, or emergency service."
        )

        # Chatbot
        chatbot = gr.Chatbot(
            label=None,
            height=500,
            layout="bubble",
            avatar_images=(
                None,  # user avatar
                "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/embarrassed-parrot.svg",  # bot avatar
            ),
        )
        with gr.Row():
            with gr.Column():
                txt = gr.Textbox(
                    label="Question",
                    placeholder="Example: I am anxious about the results of my work. What should I remember?",
                    lines=2,
                    max_lines=4,
                    container=False,
                )
            with gr.Column():
                submit_btn = gr.Button("Reflect", variant="primary", scale=0)
                clear_btn = gr.Button("Clear", variant="secondary", scale=0)

        # Sources
        sources_md = gr.Markdown(label="Sources")

        # Examples
        gr.Examples(
            examples=[
                "I am anxious about the results of my work. What should I remember?",
                "How do I control anger before I say something harmful?",
                "How can I stay calm when people around me disturb me?",
                "I keep losing focus and my mind runs everywhere. What does the Gita suggest?",
                "I feel jealous of a colleague's success. What should I remember?",
                "I am struggling with attachment to outcomes. What does the Gita advise?",
            ],
            inputs=txt,
        )

        # Event handling
        def user_submit(message, history):
            return respond(message, history)

        txt.submit(
            fn=user_submit,
            inputs=[txt, chatbot],
            outputs=[chatbot, txt, sources_md],
        )
        submit_btn.click(
            fn=user_submit,
            inputs=[txt, chatbot],
            outputs=[chatbot, txt, sources_md],
        )
        clear_btn.click(lambda: ([], "", ""), None, [chatbot, txt, sources_md])

    return demo


if __name__ == "__main__":
    build_app().launch(server_name="0.0.0.0", server_port=7860)