"""Verse-aware chunking for Dharma Lens retrieval."""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path
from typing import Any


def load_theme_tags(path: Path) -> dict[str, list[str]]:
    """Load verse-id to theme-list mapping from JSON."""
    data = json.loads(path.read_text(encoding="utf-8"))
    return {str(key): list(value) for key, value in data.items()}


def apply_theme_tags(
    records: list[dict[str, Any]], theme_tags: dict[str, list[str]]
) -> list[dict[str, Any]]:
    """Return copied records with deterministic theme tags applied by verse id."""
    tagged = deepcopy(records)
    for record in tagged:
        themes = theme_tags.get(record["id"], record.get("themes", []))
        record["themes"] = sorted(dict.fromkeys(themes))
    return tagged


def _format_themes(themes: list[str]) -> str:
    return ", ".join(themes) if themes else "none"


def _verse_text(record: dict[str, Any]) -> str:
    lines = [
        f"Bhagavad Gita {record['id']}",
        f"Themes: {_format_themes(record.get('themes', []))}",
        f"Translation ({record['translation_author']}): {record['translation']}",
    ]
    if record.get("word_meanings"):
        lines.append(f"Word meanings: {record['word_meanings']}")
    return "\n".join(lines)


def build_verse_chunks(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build one retrieval chunk per verse while preserving citation metadata."""
    chunks: list[dict[str, Any]] = []
    for record in sorted(records, key=lambda item: item["verse_order"]):
        chunks.append(
            {
                "chunk_id": f"verse:{record['id']}",
                "chunk_type": "verse",
                "chapter": record["chapter"],
                "verse_start": record["verse"],
                "verse_end": record["verse"],
                "verse_ids": [record["id"]],
                "citation": f"Bhagavad Gita {record['id']}",
                "themes": record.get("themes", []),
                "translation_author": record["translation_author"],
                "source_dataset": record["source_dataset"],
                "source_license": record["source_license"],
                "text": _verse_text(record),
            }
        )
    return chunks


def build_adjacent_chunks(
    records: list[dict[str, Any]], *, window_size: int = 2
) -> list[dict[str, Any]]:
    """Build same-chapter adjacent verse group chunks for contextual continuity."""
    if window_size < 2:
        raise ValueError("window_size must be at least 2")

    ordered = sorted(records, key=lambda item: item["verse_order"])
    chunks: list[dict[str, Any]] = []
    for index in range(0, len(ordered) - window_size + 1):
        window = ordered[index : index + window_size]
        first = window[0]
        last = window[-1]
        same_chapter = all(record["chapter"] == first["chapter"] for record in window)
        contiguous = all(
            window[i + 1]["verse"] == window[i]["verse"] + 1
            for i in range(len(window) - 1)
        )
        if not same_chapter or not contiguous:
            continue

        themes = sorted(
            dict.fromkeys(theme for record in window for theme in record.get("themes", []))
        )
        verse_ids = [record["id"] for record in window]
        chunk_id = f"group:{first['id']}-{last['id']}"
        citation = f"Bhagavad Gita {first['id']}-{last['id']}"
        text = "\n\n".join(_verse_text(record) for record in window)

        chunks.append(
            {
                "chunk_id": chunk_id,
                "chunk_type": "adjacent_verses",
                "chapter": first["chapter"],
                "verse_start": first["verse"],
                "verse_end": last["verse"],
                "verse_ids": verse_ids,
                "citation": citation,
                "themes": themes,
                "translation_author": first["translation_author"],
                "source_dataset": first["source_dataset"],
                "source_license": first["source_license"],
                "text": text,
            }
        )
    return chunks


def build_chunks(
    records: list[dict[str, Any]], theme_tags: dict[str, list[str]]
) -> list[dict[str, Any]]:
    tagged_records = apply_theme_tags(records, theme_tags)
    return build_verse_chunks(tagged_records) + build_adjacent_chunks(
        tagged_records, window_size=2
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Dharma Lens retrieval chunks")
    parser.add_argument(
        "--records",
        default="data/processed/dharma_lens_verses.json",
        help="Normalized records JSON path",
    )
    parser.add_argument(
        "--themes",
        default="data/themes/core_themes.json",
        help="Theme tags JSON path",
    )
    parser.add_argument(
        "--output",
        default="data/processed/dharma_lens_chunks.json",
        help="Output chunks JSON path",
    )
    args = parser.parse_args()

    records = json.loads(Path(args.records).read_text(encoding="utf-8"))
    themes = load_theme_tags(Path(args.themes))
    chunks = build_chunks(records, themes)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(chunks, ensure_ascii=False, indent=2) + "\n")
    print(f"Wrote {len(chunks)} chunks to {output_path}")


if __name__ == "__main__":
    main()
