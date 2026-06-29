# Dharma Lens Tasks

## Completed

- [x] Draft PRD.
- [x] Review dataset options.
- [x] Choose MVP dataset candidate.
- [x] Create ingestion tests using TDD.
- [x] Implement `src/ingest.py` normalization pipeline.
- [x] Generate `data/processed/dharma_lens_verses.json` with 701 records.
- [x] Verify key verses exist: 2.47, 2.48, 3.19, 6.5, 12.15.
- [x] Add theme taxonomy file at `data/themes/core_themes.json`.
- [x] Add manual tags for high-value verses.
- [x] Write chunking tests using TDD.
- [x] Implement verse chunks and adjacent verse-group chunks.
- [x] Generate `data/processed/dharma_lens_chunks.json` with 1,384 chunks.
- [x] Add embedding/index build pipeline.
- [x] Add retrieval tests.
- [x] Implement semantic retrieval over chunks.
- [x] Add metadata/theme boost to retrieval.
- [x] Run sample retrieval evaluation with 5 seed questions.
- [x] Build grounded prompt and citation validator.
- [x] Add deterministic extractive answer generation fallback.
- [x] Add optional OpenRouter answer generation hook.
- [x] Generate sample grounded answer.
- [x] Build Gradio UI.
- [x] Test UI handler and local Gradio server.
- [x] Prepare Hugging Face Spaces README metadata.
- [x] Add `.huggingfaceignore`.
- [x] Add `LICENSE`.
- [x] Test clean install path from scratch.
- [x] Check HF CLI/auth readiness.

## Next

- [x] SK logged into Hugging Face CLI.
- [x] Create/push Space after explicit approval.
- [x] Test deployed Space cold start and API prediction.

## Next

- [x] Create/push GitHub repository.
- [x] Configure GitHub repo homepage, description, and topics.

## Next

- [ ] Add project screenshots/GIF after UI review.
- [ ] Expand evaluation set from 5 to 20 questions.
- [ ] Decide small open-source synthesis model if deterministic answer quality is not enough.
- [ ] Add portfolio case-study writeup.
