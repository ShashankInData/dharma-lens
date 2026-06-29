# Changelog

## 2026-06-28

- Created initial project scaffold.
- Added PRD and dataset review.
- Added pytest setup.
- Added TDD tests for dataset normalization.
- Implemented `src/ingest.py`.
- Generated normalized Swami Sivananda verse dataset with 701 records.
- Added core theme taxonomy for high-value verses.
- Added TDD tests for theme tagging and verse-aware chunking.
- Implemented `src/chunking.py`.
- Generated 1,384 retrieval chunks: 701 verse chunks and 683 adjacent verse chunks.
- Added TDD tests for vector index and retrieval ranking.
- Implemented `src/retrieval.py` with SentenceTransformers embedding support, vector scoring, and theme boost.
- Added `src/evaluate_retrieval.py`.
- Built vector index with `BAAI/bge-small-en-v1.5`.
- Ran seed retrieval evaluation: expected hit in top 5 for 5/5 questions.
- Added TDD tests for answer prompt, citation validation, weak-evidence fallback, and unsupported citation blocking.
- Implemented `src/answer.py` with deterministic extractive answer fallback and optional OpenRouter hook.
- Generated `eval/sample_answer.md` from live retrieval results.
- Verified GLM-5.2 is MIT licensed but about 753B parameters, too large for local/free UI testing.
- Added Gradio UI in `src/ui.py` and root `app.py`.
- Tested local Gradio server on port 7860.
- Added Hugging Face Spaces metadata to `README.md`.
- Added `.huggingfaceignore` and `LICENSE`.
- Verified clean install path in a fresh virtual environment: 20 tests passed and handler smoke test succeeded.
- Checked HF CLI status: installed, not logged in.
- Published Hugging Face Space at `https://huggingface.co/spaces/ShashhankIndata/dharma-lens`.
- Verified live Space runtime reached RUNNING.
- Verified live Gradio API prediction returns a grounded answer citing Bhagavad Gita 2.47.
- Published GitHub repository at `https://github.com/ShashankInData/dharma-lens`.
- Configured repository homepage, description, and topics.
