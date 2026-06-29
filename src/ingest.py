"""Dataset ingestion and normalization for Dharma Lens."""

from __future__ import annotations

import argparse
import json
import re
import urllib.request
from pathlib import Path
from typing import Any

SOURCE_DATASET = "ravisiyer/gita-data"
SOURCE_LICENSE = "Unlicense"
SOURCE_URL = "https://github.com/ravisiyer/gita-data"
VERSE_URL = "https://raw.githubusercontent.com/ravisiyer/gita-data/main/data/v1/verse.json"
TRANSLATION_URL = "https://raw.githubusercontent.com/ravisiyer/gita-data/main/data/v1/translation.json"
DEFAULT_TRANSLATION_AUTHOR = "Swami Sivananda"


def clean_text(value: str | None) -> str:
    """Normalize dataset whitespace without changing wording."""
    if not value:
        return ""
    return re.sub(r"\s+", " ", value.replace("\xa0", " ")).strip()


def normalize_records(
    verses: list[dict[str, Any]],
    translations: list[dict[str, Any]],
    *,
    translation_author: str = DEFAULT_TRANSLATION_AUTHOR,
) -> list[dict[str, Any]]:
    """Join raw verse and translation JSON into verse-aware Dharma Lens records."""
    selected_translations = {
        item["verse_id"]: clean_text(item.get("description"))
        for item in translations
        if item.get("lang") == "english" and item.get("authorName") == translation_author
    }

    missing = [verse["id"] for verse in verses if verse["id"] not in selected_translations]
    if missing:
        raise ValueError(
            f"Missing {translation_author} English translations for verse ids: {missing[:10]}"
        )

    records: list[dict[str, Any]] = []
    for verse in sorted(verses, key=lambda item: item["verse_order"]):
        chapter = int(verse["chapter_number"])
        verse_number = int(verse["verse_number"])
        record_id = f"{chapter}.{verse_number}"
        sanskrit = clean_text(verse.get("text"))
        transliteration = clean_text(verse.get("transliteration"))
        word_meanings = clean_text(verse.get("word_meanings"))
        translation = selected_translations[verse["id"]]

        text_for_embedding_parts = [
            f"Bhagavad Gita {record_id}",
            f"Sanskrit: {sanskrit}",
            f"Transliteration: {transliteration}",
            f"Translation ({translation_author}): {translation}",
        ]
        if word_meanings:
            text_for_embedding_parts.append(f"Word meanings: {word_meanings}")

        records.append(
            {
                "id": record_id,
                "chapter": chapter,
                "verse": verse_number,
                "verse_order": int(verse["verse_order"]),
                "source_verse_id": int(verse["id"]),
                "sanskrit": sanskrit,
                "transliteration": transliteration,
                "word_meanings": word_meanings,
                "translation": translation,
                "translation_author": translation_author,
                "source_dataset": SOURCE_DATASET,
                "source_license": SOURCE_LICENSE,
                "source_url": SOURCE_URL,
                "themes": [],
                "text_for_embedding": "\n".join(text_for_embedding_parts),
            }
        )

    return records


def fetch_json(url: str) -> Any:
    with urllib.request.urlopen(url, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def build_normalized_dataset(
    *,
    output_path: Path,
    translation_author: str = DEFAULT_TRANSLATION_AUTHOR,
) -> list[dict[str, Any]]:
    verses = fetch_json(VERSE_URL)
    translations = fetch_json(TRANSLATION_URL)
    records = normalize_records(
        verses, translations, translation_author=translation_author
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(records, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Dharma Lens normalized Gita data")
    parser.add_argument(
        "--output",
        default="data/processed/dharma_lens_verses.json",
        help="Output JSON path",
    )
    parser.add_argument(
        "--translation-author",
        default=DEFAULT_TRANSLATION_AUTHOR,
        help="English translation author to select",
    )
    args = parser.parse_args()

    records = build_normalized_dataset(
        output_path=Path(args.output), translation_author=args.translation_author
    )
    print(f"Wrote {len(records)} normalized records to {args.output}")


if __name__ == "__main__":
    main()
