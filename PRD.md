# Dharma Lens PRD

Date: 2026-06-28
Owner: SK
Status: Draft v0.1

## 1. Problem

People ask practical questions about life, work, emotions, discipline, relationships, conflict, anxiety, ego, duty, and attachment. Normal AI chatbots answer broadly, often without spiritual grounding or citations. For Bhagavad Gita-based reflection, hallucination and overconfident interpretation are unacceptable.

Dharma Lens will answer user questions through a Bhagavad Gita-grounded RAG pipeline. The app must retrieve real verses and produce careful, cited reflections. It must not behave like an all-knowing guru or claim divine authority.

## 2. Goal

Build a public portfolio-ready web app where a user asks a question and receives a grounded Bhagavad Gita-based reflection with verse citations, practical interpretation, and clear uncertainty boundaries.

Primary goal for MVP:
- Gradio app hosted on Hugging Face Spaces.
- Verse-aware RAG over Bhagavad Gita text.
- Answers cite chapter and verse.
- No user question/answer storage in MVP.
- GitHub repo ready for portfolio and CV.

## 3. User

Primary users:
- SK.
- People interested in Bhagavad Gita-based reflection.
- Recruiters or hiring managers reviewing SK's AI/RAG project.

User needs:
- Ask normal human questions in plain English.
- Receive grounded responses, not generic motivational text.
- See which verses were used.
- Trust that the model is not inventing scripture.

## 4. Pain Points

- Existing chatbots often answer without citations.
- Naive RAG chunks religious text badly and breaks verse structure.
- Fine-tuned spiritual models can hallucinate confidently.
- Scraped books/commentaries can mix sources and interpretations without attribution.
- Public apps may accidentally store sensitive personal questions.
- Streamlit-style UIs are less preferred; Gradio is simpler for Hugging Face deployment.

## 5. Success Criteria

MVP is successful when:
- User can open a public Hugging Face Space link.
- User can ask a question and get an answer within reasonable latency.
- Every answer includes at least 1 cited Bhagavad Gita verse when retrieval confidence is sufficient.
- App refuses or softens answers when retrieved evidence is weak.
- Retrieval preserves chapter and verse metadata.
- GitHub README explains architecture, dataset, retrieval, grounding, and limitations.
- At least 20 evaluation questions are tested manually.
- No user questions/answers are persisted in MVP.

Portfolio success:
- Repo demonstrates RAG, embeddings, vector search, metadata-aware retrieval, prompt control, evaluation, and deployment.
- CV bullet can honestly describe the project.

## 6. Scope

MVP in scope:
- Bhagavad Gita verse dataset ingestion.
- Verse-aware chunking.
- Embeddings.
- FAISS or Chroma vector index.
- Hybrid retrieval using semantic search plus metadata/theme tags.
- Citation-grounded answer generation.
- Gradio UI.
- Hugging Face Spaces deployment.
- Basic evaluation set.
- README and architecture diagram.

MVP not in scope:
- Fine-tuning.
- User accounts.
- Persistent chat history.
- Storing private questions and answers.
- Mobile app.
- Multi-religion support.
- React frontend.
- Voice mode.
- Payments.
- Complex analytics.

## 7. Out-of-Scope

- Claiming to provide religious authority.
- Acting as a therapist, doctor, lawyer, or relationship counselor.
- Telling users what God wants them to do.
- Replacing serious mental-health, medical, legal, or safety support.
- Scraping copyrighted books without checking license.
- Mixing multiple commentaries without source labels.

## 8. Inputs

User input:
- Plain English question.
- Optional mode later: life, work, relationship, discipline, emotion, decision.

System inputs:
- Bhagavad Gita verses/translations.
- Optional curated short meanings/theme tags.
- Embedding model.
- LLM API key for answer generation.

## 9. Outputs

Answer format:

1. Question interpreted as
2. Relevant verses
3. What the verses say
4. Reflection for the situation
5. Practical step
6. What this does not decide
7. Sources
8. Confidence: high / medium / low

Example source format:
- Bhagavad Gita 2.47
- Bhagavad Gita 2.48

## 10. Data Storage Policy

MVP storage:
- Store only static scripture dataset, metadata, embeddings, and vector index.
- Do not store user questions.
- Do not store generated answers.
- Do not store chat sessions.
- Gradio may hold transient in-memory UI state during a session, but the app code should not write user Q&A to disk.

Future optional storage:
- Local-only browser history, controlled by user.
- Anonymous feedback on answer quality.
- Private journal with authentication.

Default decision:
- No Q&A storage for v1.

## 11. Dataset Review, One by One

### Dataset Option 1: vedicscriptures/bhagavad-gita

Source:
- GitHub: vedicscriptures/bhagavad-gita
- Also mirrored by saurabh2k1/bhagavad-gita-dataset.

Observed structure:
- `chapter/` contains 18 chapter JSON files.
- `slok/` contains individual verse JSON files.
- Verse JSON files are large because they include translations/commentaries from multiple authors.

Strengths:
- Rich dataset.
- Has chapters, verses, translations, transliterations, commentaries, explanations.
- Good for future multi-commentary support.
- API exists through vedicscriptures.github.io.

Weaknesses:
- More complex than needed for MVP.
- Multiple commentators can create interpretation mixing if not handled carefully.
- Need source attribution per translation/commentary.

Recommendation:
- Use as primary candidate for v1 ingestion, but select one translation/commentary path first.
- Do not load every commentary into generation immediately.

### Dataset Option 2: ravisiyer/gita-data

Source:
- GitHub: ravisiyer/gita-data.

Observed structure:
- `data/v1/`
- `verse_recitation/`
- `split-commentary/`

Strengths:
- Appears structured for static JSON usage.
- Has tooling around commentary splitting.
- Potentially useful if we want cleaner generated static data.

Weaknesses:
- Needs deeper inspection before choosing.
- Commentary tooling may be unnecessary for MVP.

Recommendation:
- Inspect after Option 1.
- Treat as secondary source or cross-check source.

### Dataset Option 3: AdiyogiArts/gita-json

Source:
- GitHub: AdiyogiArts/gita-json.

Observed structure:
- `base.json`
- `en.json`
- `hi.json`

Strengths:
- Single JSON files may be easy for ingestion.
- English and Hindi support could be useful later.
- Simple structure may suit MVP.

Weaknesses:
- Need license and schema review.
- Need confirm translation provenance.
- If source attribution is weak, not ideal for a serious grounded app.

Recommendation:
- Consider for MVP only if schema is clean and license/provenance are acceptable.

### Dataset Option 4: Mercity/bhagavad_gita-embeddings on Hugging Face

Source:
- Hugging Face dataset.
- Existing embedding dataset.

Strengths:
- Already embedding-oriented.
- Could accelerate semantic search experiments.

Weaknesses:
- Very small, under 1k rows.
- Low usage signal.
- Embedding method and source assumptions need verification.
- Depending on precomputed embeddings weakens our portfolio story.

Recommendation:
- Do not use as core dataset.
- Use only as reference/inspiration.

### Dataset Option 5: PDFs / scraped books

Strengths:
- Can include detailed commentary.
- May improve answer richness.

Weaknesses:
- PDF extraction noise.
- Copyright risk.
- Harder citation.
- Naive chunking breaks verse/commentary relationships.

Recommendation:
- Avoid for MVP.
- Add commentary later only from clearly licensed and attributable sources.

## 12. Data Strategy

Do not chunk the book word-by-word.

Use verse-aware records:

```json
{
  "id": "2.47",
  "chapter": 2,
  "verse_start": 47,
  "verse_end": 47,
  "sanskrit": "...",
  "transliteration": "...",
  "translation": "...",
  "short_meaning": "...",
  "themes": ["action", "detachment", "duty"],
  "source": "...",
  "text_for_embedding": "..."
}
```

Chunk levels:
- Verse chunk: one verse.
- Verse group chunk: 2-4 adjacent verses for continuity.
- Chapter theme chunk: short chapter summary, optional v2.
- Commentary chunk: tied to exact verse, optional v2.

MVP decision:
- Use verse chunks and small adjacent verse-group chunks.
- Add manual theme tags for high-value verses.

## 13. Retrieval Strategy

MVP retrieval:
1. Embed user query.
2. Semantic search over verse and verse-group chunks.
3. Apply metadata/theme boosts.
4. Return top 5 chunks.
5. Generate answer only from retrieved chunks.

Preferred embedding model:
- `BAAI/bge-small-en-v1.5`, if Hugging Face Spaces handles it well.
- fallback: `sentence-transformers/all-MiniLM-L6-v2`.

Preferred vector store:
- FAISS for simple local vector search.
- Chroma only if metadata filtering becomes easier than FAISS.

Future retrieval improvements:
- Hybrid BM25 + vector search.
- Reranker model.
- Query classifier for emotion/theme extraction.
- Verse map explaining why each verse was selected.

## 14. Manual Steps

Before coding:
- Choose primary dataset.
- Confirm license/provenance.
- Pick one English translation for MVP.
- Define theme taxonomy.
- Create 20 evaluation questions.

Before public launch:
- Test sensitive questions.
- Review answer style.
- Confirm app does not store user Q&A.
- Review README language to avoid overclaiming.

## 15. Automation Opportunities

- Script to download and normalize dataset.
- Script to build embeddings and FAISS index.
- Script to run retrieval tests.
- Gradio app auto-loads vector index at startup.
- CI later: run ingestion checks and tests on push.

## 16. Approval Points

Require SK approval before:
- Final dataset selection.
- Adding commentary sources.
- Creating GitHub repo content.
- Publishing to GitHub.
- Deploying Hugging Face Space.
- Adding storage of user questions/answers.

## 17. Risks

Technical risks:
- Retrieval returns irrelevant verses.
- LLM uses knowledge outside retrieved context.
- Hugging Face free Space sleeps or has slow cold starts.
- Embedding model adds startup time.

Content risks:
- Translation/commentary licensing issues.
- Mixed interpretations without attribution.
- Overconfident spiritual advice.
- Sensitive questions about harm, depression, abuse, or self-harm.

Portfolio risks:
- Project looks like another basic Gita chatbot.
- Weak README hides the engineering work.

Mitigations:
- Verse-aware retrieval.
- Strict citation prompt.
- Refusal/uncertainty behavior.
- Clear limitations.
- Evaluation questions and retrieval score table.

## 18. Security and Privacy

MVP:
- No user login.
- No database for user Q&A.
- No analytics storing prompts.
- API key must be stored in Hugging Face Spaces secrets, not committed.
- If using OpenRouter, read API key from environment variable.

Prompt safety:
- Do not provide medical, legal, or emergency guidance.
- For self-harm or immediate danger, advise contacting emergency/local support.
- For abuse or safety issues, do not spiritualize staying in harm.

## 19. Architecture

```text
User
  ↓
Gradio UI
  ↓
Question preprocessor / Dharma Lens reframer
  ↓
Retriever
  ├── semantic vector search
  ├── theme metadata boost
  └── adjacent verse expansion
  ↓
Context builder
  ↓
LLM answer generator
  ↓
Citation validator
  ↓
Grounded answer in UI
```

## 20. Folder Structure

```text
dharma-lens/
  PRD.md
  README.md
  requirements.txt
  app.py
  data/
    raw/
    processed/
    dharma_lens_verses.json
  indexes/
    faiss.index
    metadata.json
  src/
    __init__.py
    config.py
    ingest.py
    normalize.py
    chunking.py
    embeddings.py
    retrieval.py
    prompt.py
    answer.py
    safety.py
    evaluation.py
  tests/
    test_ingest.py
    test_chunking.py
    test_retrieval.py
    test_prompt_grounding.py
  eval/
    questions.json
    retrieval_results.md
  docs/
    architecture.md
    dataset_review.md
```

## 21. Build Phases

### Phase 0: Research and dataset selection

Deliverables:
- `docs/dataset_review.md`
- selected source
- license notes
- selected translation/commentary policy

### Phase 1: Dataset ingestion

Deliverables:
- `src/ingest.py`
- `data/processed/dharma_lens_verses.json`
- ingestion tests

### Phase 2: Chunking and embeddings

Deliverables:
- verse-aware chunks
- FAISS index
- metadata file
- retrieval sanity tests

### Phase 3: Retrieval evaluation

Deliverables:
- 20 manually designed questions
- expected theme/verse hints
- retrieval report

### Phase 4: Answer generation

Deliverables:
- strict grounded prompt
- citation validator
- answer format
- weak-evidence response

### Phase 5: Gradio UI

Deliverables:
- `app.py`
- clean input/output UI
- source/citation display
- no Q&A persistence

### Phase 6: Hugging Face deployment

Deliverables:
- Spaces-compatible repo structure
- `requirements.txt`
- environment variable docs
- public demo link

### Phase 7: GitHub/portfolio polish

Deliverables:
- README
- architecture diagram
- screenshots
- CV bullets
- limitations section

## 22. Testing Plan

Unit tests:
- Dataset loads correctly.
- Every record has chapter/verse/source fields.
- Chunking preserves verse boundaries.
- Retrieval returns metadata and citations.
- Prompt builder includes only retrieved context.

Manual evaluation:
- 20 questions across anxiety, duty, anger, attachment, relationship conflict, workplace stress, discipline, grief, ego, jealousy, purpose.
- Record top retrieved verses.
- Mark retrieval quality: good / partial / poor.

Safety tests:
- Self-harm query.
- Abuse query.
- Medical/legal query.
- Manipulative relationship query.
- Question asking the app to ignore scripture and invent answer.

## 23. Rollback Plan

If dataset source causes license/provenance issues:
- Remove dataset files.
- Switch to another structured source.
- Rebuild processed JSON and index.

If answer quality is poor:
- Disable generation temporarily.
- Show retrieved verses only.
- Improve retrieval and prompt before re-enabling LLM answers.

If Hugging Face deployment fails:
- Run local Gradio demo.
- Simplify dependencies.
- Prebuild index and commit index files if license allows.

## 24. Maintenance Plan

Weekly during active development:
- Add failed questions to evaluation set.
- Review poor retrieval cases.
- Improve theme tags and chunking.
- Check Hugging Face app health.

Before portfolio sharing:
- Freeze v1 release tag.
- Verify README setup works from clean clone.
- Confirm no secrets are committed.
- Confirm no user Q&A storage.

## 25. Open Questions

1. Which exact English translation should MVP use?
2. Should Sanskrit/transliteration be shown in UI by default or behind an expand button?
3. Should commentary be excluded from v1 or included as optional retrieved context?
4. Which LLM provider should be used for public demo, OpenRouter or Hugging Face-hosted model?
5. Should app display confidence score numerically or as high/medium/low?

## 26. Current Recommendation

Start with:
- Gradio on Hugging Face Spaces.
- No Q&A storage.
- One reliable structured Bhagavad Gita dataset.
- Verse-aware chunks.
- `BAAI/bge-small-en-v1.5` embeddings, fallback MiniLM.
- FAISS index.
- OpenRouter generation via environment secret.
- Strict answer format and citation validator.

Avoid for v1:
- Fine-tuning.
- Word-by-word chunking.
- Full commentary ingestion.
- User accounts.
- Saved chat history.
