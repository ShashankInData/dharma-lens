# Dharma Lens Dataset Review

Date: 2026-06-28
Status: Draft v0.1
Purpose: choose the cleanest Bhagavad Gita dataset for Dharma Lens MVP.

## Short Recommendation

Use `ravisiyer/gita-data` as the first MVP dataset candidate, with selected English translation fields only.

Reason:
- Unlicense, simplest for portfolio/public GitHub use.
- Clean static JSON structure.
- Verse metadata, Sanskrit, transliteration, word meanings, translations, authors, languages.
- Easy to normalize into verse-aware RAG records.

Use `vedicscriptures/bhagavad-gita` as a cross-reference and fallback, not the default MVP source.

Avoid PDFs/scraped books for v1.

## Decision Table

| Dataset | License | Structure | Strength | Risk | MVP Decision |
|---|---:|---|---|---|---|
| `ravisiyer/gita-data` | Unlicense | Static JSON API files | Clean, permissive, easy ingestion | 701 verse convention, needs normalization | Best MVP candidate |
| `vedicscriptures/bhagavad-gita` | GPL-3.0 | Chapter JSON + per-verse JSON | Rich translations/commentaries | GPL implications, complex author fields | Cross-check / v2 source |
| `AdiyogiArts/gita-json` | MIT-like text, GitHub reports NOASSERTION | `base.json`, `en.json`, `hi.json` | Simple, explanations included | Provenance weaker, no stars/forks, generated-sounding explanations | Possible fallback, not first choice |
| `Mercity/bhagavad_gita-embeddings` | MIT | HF precomputed embeddings | Quick experiment | Weak portfolio value, low usage, opaque embedding assumptions | Do not use core |
| PDFs/scraped books | Varies | Unstructured | Rich commentary | Copyright/noise/citation problems | Avoid v1 |

## Dataset 1: ravisiyer/gita-data

Source:
- GitHub: `https://github.com/ravisiyer/gita-data`
- Static JSON API base: `https://ravisiyer.github.io/gita-data/v1/`

License:
- Unlicense.
- README says data is taken from the open-source `gita/gita` project and this project uses the same Unlicense license.

Repository signal:
- Stars: 0
- Forks: 1
- Last pushed: 2026-01-14
- Description: Bhagavad Gita Static JSON files API

Observed files:
- `data/v1/authors.json`
- `data/v1/languages.json`
- `data/v1/chapters.json`
- `data/v1/verse.json`
- `data/v1/translation.json`
- `data/v1/commentary.json`
- `data/v1/commentaries/author{author_id}/lang{lang}/chapter{chapter_number}.json`

Observed schema:

`verse.json` contains 701 records. Each verse has:
- `chapter_id`
- `chapter_number`
- `externalId`
- `id`
- `text`, Sanskrit verse
- `title`
- `verse_number`
- `verse_order`
- `transliteration`
- `word_meanings`

`translation.json` contains 4,907 records:
- 7 translation authors x 701 verses.
- English authors found:
  - Swami Adidevananda
  - Swami Gambirananda
  - Swami Sivananda
  - Dr. S. Sankaranarayan
  - Shri Purohit Swami
- Hindi authors found:
  - Swami Ramsukhdas
  - Swami Tejomayananda

Example 2.47 translations:
- Swami Adidevananda: "You have the right to work alone, but not to the fruits of it..."
- Swami Gambirananda: "Your right is only to act, not to the results..."
- Swami Sivananda: "Your right is only to work, but not to its results..."
- Dr. S. Sankaranarayan: "Let your claim rest on action alone and never on the fruits..."
- Shri Purohit Swami: "But you have only the right to work, but none to the fruit of it..."

Chapter count convention:
- Total verses: 701.
- Chapter 13 has 35 verses.
- This is a known edition convention. Some editions count Chapter 13 as 34 verses and total as 700.

Strengths:
- Best licensing posture for public GitHub and Hugging Face portfolio project.
- Clean files can be downloaded once and committed or cached depending on final choice.
- Separates verses, translations, authors, languages, and commentaries.
- Easier to select only one translation for MVP.

Weaknesses:
- Low repository popularity, so we should not rely on social proof.
- Needs normalization to hide internal global IDs and expose proper `chapter.verse` IDs.
- Commentary split has some confusing fields. Example Swami Sivananda chapter 2 file shows global `verseNumber` offset while description text starts with chapter-local verse. We should not use commentary in MVP until tested.

MVP use:
- Use `verse.json` for Sanskrit, transliteration, word meanings.
- Use `translation.json` for one selected English translation.
- Do not use commentary in v1 answer generation.
- Store source attribution in every normalized record.

Recommended initial translation:
- Swami Sivananda, because the wording is clear, concise, and widely used.
- Alternative: Swami Gambirananda for a more literal/neutral tone.

Implementation note:
- Normalize each verse as `chapter.verse`, not the dataset's global `id`.
- Preserve original dataset IDs in metadata for traceability.

## Dataset 2: vedicscriptures/bhagavad-gita

Source:
- GitHub: `https://github.com/vedicscriptures/bhagavad-gita`
- API: `https://vedicscriptures.github.io/`

License:
- GPL-3.0.

Repository signal:
- Stars: 39
- Forks: 19
- Last pushed: 2025-11-18

Observed files:
- `chapter/bhagavadgita_chapter_2.json`
- `slok/bhagavadgita_chapter_2_slok_47.json`

Chapter schema:
- `chapter_number`
- `verses_count`
- `name`
- `translation`
- `transliteration`
- `meaning`
- `summary`

Verse schema:
- `_id`
- `chapter`
- `verse`
- `speaker`
- `slok`
- `transliteration`
- author-coded fields such as `siva`, `purohit`, `san`, `adi`, `gambir`, `sankar`, `prabhu`.

Example 2.47 English fields:
- `siva`: Swami Sivananda, translation + commentary.
- `purohit`: Shri Purohit Swami, translation.
- `san`: Dr. S. Sankaranarayan, translation.
- `adi`: Swami Adidevananda, translation.
- `gambir`: Swami Gambirananda, translation.
- `sankar`: Sri Shankaracharya, translation/interpretation.
- `prabhu`: A.C. Bhaktivedanta Swami Prabhupada, translation + commentary.

Strengths:
- Very rich per-verse file.
- Multiple commentaries and translation traditions.
- Strong candidate for v2 comparison mode.
- Useful for cross-checking fields against `ravisiyer/gita-data`.

Weaknesses:
- GPL-3.0 creates stronger obligations if dataset files or derivative normalized files are distributed in the repo.
- Per-verse JSON files are large and noisy for MVP.
- Multiple author codes increase ingestion complexity.
- Loading everything risks mixing theological interpretations without clear attribution.

MVP use:
- Do not use as primary dataset for v1.
- Use as reference/cross-check only.
- Consider v2 feature: compare interpretations from Sivananda, Gambirananda, Prabhupada, Shankara, etc., each clearly labeled.

## Dataset 3: AdiyogiArts/gita-json

Source:
- GitHub: `https://github.com/AdiyogiArts/gita-json`

License:
- LICENSE file uses MIT text plus a sacred-use note.
- GitHub API reports license as `NOASSERTION`, likely because of the additional note.

Repository signal:
- Stars: 0
- Forks: 0
- Last pushed: 2026-04-10

Observed files:
- `base.json`
- `en.json`
- `hi.json`

Observed schema:

`base.json` keyed by `chapter-verse`, e.g. `2-47`:
- `chapter`
- `verse`
- `sanskrit`
- `transliteration`
- `chapterName`
- `chapterNameTranslation`
- `chapterVerseCount`
- video URLs

`en.json` keyed by `chapter-verse`:
- `translation`
- `explanation`
- `wordMeanings`

Example 2.47 explanation includes modern framing:
- It calls 2.47 "arguably the most famous verse".
- It maps the verse to "process focus vs outcome focus".

Strengths:
- Very easy to ingest.
- Simple `chapter-verse` keys.
- Includes explanation and word meanings.
- English and Hindi support could be useful later.

Weaknesses:
- Translation/explanation provenance is not as clear as named classical translators.
- Explanations are already interpretive and modernized, which may bias the AI answer.
- Low repo signal.
- Video URLs are irrelevant for MVP.

MVP use:
- Possible fallback if we need quick prototyping.
- Do not use as canonical source unless provenance is clarified.

## Dataset 4: Mercity/bhagavad_gita-embeddings

Source:
- Hugging Face: `Mercity/bhagavad_gita-embeddings`

License:
- MIT listed on Hugging Face.

Observed metadata:
- Size category: `n<1K`
- Languages: Sanskrit and English.
- Downloads: 7
- Likes: 1
- Last modified: 2025-05-13
- Source mentions VedaBase/ISKCON.

Strengths:
- Already designed for semantic search.
- Might help for quick baseline comparison.

Weaknesses:
- Very low adoption signal.
- Precomputed embeddings make the project less transparent.
- Unknown embedding model and preprocessing choices need verification.
- We need our own ingestion + embedding pipeline for portfolio credibility.

MVP use:
- Do not use as core.
- Optional reference only.

## Dataset 5: PDFs or scraped books

Examples:
- Commentary PDFs.
- Websites with book text.
- Random scraped pages.

Strengths:
- More detailed commentary.
- Can improve answer richness later.

Weaknesses:
- Copyright risk.
- PDF extraction noise.
- Poor citation granularity.
- Hard to preserve verse-commentary relationship.
- Scraping can break or violate website terms.

MVP use:
- Avoid.

## Final MVP Dataset Recommendation

Use `ravisiyer/gita-data` first.

MVP normalized record should look like:

```json
{
  "id": "2.47",
  "chapter": 2,
  "verse": 47,
  "verse_order": 94,
  "sanskrit": "...",
  "transliteration": "...",
  "word_meanings": "...",
  "translation": "Your right is only to work...",
  "translation_author": "Swami Sivananda",
  "source_dataset": "ravisiyer/gita-data",
  "source_license": "Unlicense",
  "source_url": "https://github.com/ravisiyer/gita-data",
  "themes": [],
  "text_for_embedding": "Bhagavad Gita 2.47..."
}
```

## Recommended MVP Data Pipeline

1. Download `verse.json`, `translation.json`, `authors.json`, `languages.json`.
2. Select English translation author.
3. Join verse + translation by global `verse_id`.
4. Convert global IDs into `chapter.verse` IDs.
5. Clean whitespace and remove duplicate line breaks.
6. Add theme tags for high-value verses manually in a separate `themes.yaml` or `themes.json`.
7. Create verse chunks.
8. Create adjacent verse group chunks.
9. Build embeddings.
10. Store FAISS index + metadata.

## Translation Choice

Initial recommendation:
- Use Swami Sivananda for v1.

Why:
- Clear English.
- Concise enough for retrieval context.
- Available for all 701 verse records in `ravisiyer/gita-data`.

Alternative:
- Swami Gambirananda if we want more literal/neutral language.

Do not mix multiple translations in answer generation v1.

## 701 vs 700 Verse Issue

Some editions count Bhagavad Gita as 700 verses; these datasets contain 701 records because Chapter 13 has 35 verses in that convention.

Decision:
- Preserve source convention internally.
- In README, say "about 700 verses" or "701 verse records depending on edition convention".
- Avoid false claim if using 701 records.

## Risks and Mitigations

Risk: source contains 701 records while users expect 700.
- Mitigation: explain edition convention in README.

Risk: translation choice influences answer tone.
- Mitigation: label author and source in metadata and UI.

Risk: retrieval based only on translation misses Sanskrit/word meaning nuance.
- Mitigation: embed translation + word meanings + theme tags, not Sanskrit alone.

Risk: answers overclaim spiritual authority.
- Mitigation: prompt says "Based on these verses, one possible reflection is..." and citation validator blocks uncited claims.

## Next Build Step

Create the ingestion script for `ravisiyer/gita-data` and produce a normalized local JSON file from:
- `verse.json`
- `translation.json`

Then run checks:
- record count is 701.
- every record has `id`, `chapter`, `verse`, Sanskrit, transliteration, translation, author, source.
- selected author translation count is 701.
- sample verses 2.47, 2.48, 3.19, 6.5, 12.15 exist.
