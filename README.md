---
title: Dharma Lens
emoji: 🕉️
colorFrom: indigo
colorTo: yellow
sdk: gradio
sdk_version: 6.19.0
app_file: app.py
pinned: false
license: mit
---

# Dharma Lens

Dharma Lens is a Bhagavad Gita-grounded RAG reflection assistant.

GitHub repo: https://github.com/ShashankInData/dharma-lens

Live app: https://shashhankindata-dharma-lens.hf.space/

The goal is not to create an AI guru. The goal is to retrieve real Bhagavad Gita verses and generate careful, cited reflections for life, work, discipline, emotion, and relationship questions.

## Current Status

Phase: deployed on Hugging Face Spaces. Next: GitHub repository setup and broader evaluation.

Implemented:
- Dataset review.
- Verse normalization pipeline.
- Swami Sivananda English translation selection.
- Processed dataset with 701 verse records.
- Core theme taxonomy for selected high-value verses.
- Verse-aware retrieval chunks.
- Adjacent verse-group chunks for context continuity.
- SentenceTransformers vector index.
- Semantic retrieval with transparent theme boost.
- Seed retrieval evaluation.
- Grounded prompt builder.
- Citation validator.
- Weak-evidence fallback.
- Unsupported-citation blocking.
- Deterministic extractive answer fallback.
- Optional OpenRouter answer generation hook.
- Local Gradio UI.
- Pytest coverage for ingestion, chunking, retrieval, answer grounding, and UI handler behavior.

Not implemented yet:
- Hugging Face Spaces deployment.
- Optional small open-source LLM synthesis path.

## Model note

`zai-org/GLM-5.2` is available on Hugging Face under MIT, but the model metadata reports about 753B parameters. That is not realistic for local testing or a free/low-resource Hugging Face Space. Dharma Lens currently uses the open-source `BAAI/bge-small-en-v1.5` embedding model plus deterministic grounded answer synthesis. This is safer for v1 because citations stay under control.

## Dataset

MVP source: `ravisiyer/gita-data`

License: Unlicense

Note: this source contains 701 verse records because Chapter 13 has 35 verses in this edition convention. The Bhagavad Gita is commonly described as about 700 verses.

## Run Tests

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q
```

## Build Normalized Dataset

```bash
. .venv/bin/activate
python -m src.ingest --output data/processed/dharma_lens_verses.json
```

Expected output:

```text
Wrote 701 normalized records to data/processed/dharma_lens_verses.json
```

## Build Retrieval Chunks

```bash
. .venv/bin/activate
python -m src.chunking \
  --records data/processed/dharma_lens_verses.json \
  --themes data/themes/core_themes.json \
  --output data/processed/dharma_lens_chunks.json
```

Expected output:

```text
Wrote 1384 chunks to data/processed/dharma_lens_chunks.json
```

## Build Vector Index

```bash
. .venv/bin/activate
python -m src.retrieval \
  --chunks data/processed/dharma_lens_chunks.json \
  --output indexes/dharma_lens_vector_index.pkl \
  --model BAAI/bge-small-en-v1.5
```

Expected output:

```text
Wrote index with 1384 chunks to indexes/dharma_lens_vector_index.pkl
```

## Evaluate Retrieval

```bash
. .venv/bin/activate
python -m src.evaluate_retrieval \
  --index indexes/dharma_lens_vector_index.pkl \
  --questions eval/questions.json \
  --output eval/retrieval_results.md \
  --model BAAI/bge-small-en-v1.5 \
  --top-k 5
```

Current seed result:

```text
expected_hit_rate_top_5=5/5
```

## Generate Sample Answer

```bash
. .venv/bin/activate
python -m src.answer "I am anxious about the results of my work. What should I remember?" \
  --index indexes/dharma_lens_vector_index.pkl \
  --model BAAI/bge-small-en-v1.5 \
  --top-k 5
```

This uses deterministic extractive answer generation by default. To use OpenRouter later, set `OPENROUTER_API_KEY` and pass `--use-openrouter`.

## Run Local UI

```bash
. .venv/bin/activate
python app.py
```

Open:

```text
http://127.0.0.1:7860
```

## Hugging Face Spaces Deployment

Public Space repo:

```text
https://huggingface.co/spaces/ShashhankIndata/dharma-lens
```

Live app:

```text
https://shashhankindata-dharma-lens.hf.space/
```

The project is packaged for a Gradio Space with root `app.py`, `requirements.txt`, README YAML metadata, `.huggingfaceignore`, and a prebuilt vector index.

Verified live:
- Space runtime reached `RUNNING`.
- `/config` returned title `Dharma Lens`.
- Gradio API prediction returned a grounded answer citing Bhagavad Gita 2.47.

## Privacy

Version 1 will not store user questions, answers, sessions, analytics, or chat history.
