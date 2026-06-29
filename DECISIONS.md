# Dharma Lens Decisions

## 2026-06-28 - Dataset source

Decision: use `ravisiyer/gita-data` as the MVP dataset source.

Reason:
- Unlicense is safest for a public GitHub/portfolio project.
- Static JSON files are easy to ingest.
- Contains Sanskrit, transliteration, word meanings, translations, authors, and languages.

Notes:
- Dataset contains 701 verse records because of edition convention, Chapter 13 has 35 verses.
- README should say "about 700 verses" or explain the convention.

## 2026-06-28 - MVP translation

Decision: start with Swami Sivananda English translation.

Reason:
- Available for all 701 records.
- Clear and concise enough for retrieval context.

Fallback:
- Swami Gambirananda if we want a more literal/neutral tone.

## 2026-06-28 - No commentary in v1

Decision: exclude commentary from v1 answer generation.

Reason:
- Commentary schema needs deeper validation.
- Mixing commentaries risks interpretation drift.
- Verse-grounded retrieval should work first.

## 2026-06-28 - No user Q&A storage in v1

Decision: do not persist user questions, answers, sessions, analytics, or chat history in v1.

Reason:
- Public spiritual/life questions can be sensitive.
- MVP should only store static scripture data, metadata, embeddings, and vector index.
