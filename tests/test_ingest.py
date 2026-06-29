from src.ingest import normalize_records


def test_normalize_records_selects_requested_english_translation_and_preserves_verse_metadata():
    verses = [
        {
            "chapter_number": 2,
            "verse_number": 47,
            "verse_order": 94,
            "id": 94,
            "text": "कर्मण्येवाधिकारस्ते...",
            "transliteration": "karmaṇy evādhikāras te...",
            "word_meanings": "karmaṇi — in action; phaleṣu — fruits",
        }
    ]
    translations = [
        {
            "verse_id": 94,
            "lang": "english",
            "authorName": "Swami Sivananda",
            "description": "Your right is only to work, but not to its results.",
        },
        {
            "verse_id": 94,
            "lang": "english",
            "authorName": "Swami Gambirananda",
            "description": "Your right is only to act, not to the results.",
        },
    ]

    records = normalize_records(verses, translations, translation_author="Swami Sivananda")

    assert records == [
        {
            "id": "2.47",
            "chapter": 2,
            "verse": 47,
            "verse_order": 94,
            "source_verse_id": 94,
            "sanskrit": "कर्मण्येवाधिकारस्ते...",
            "transliteration": "karmaṇy evādhikāras te...",
            "word_meanings": "karmaṇi — in action; phaleṣu — fruits",
            "translation": "Your right is only to work, but not to its results.",
            "translation_author": "Swami Sivananda",
            "source_dataset": "ravisiyer/gita-data",
            "source_license": "Unlicense",
            "source_url": "https://github.com/ravisiyer/gita-data",
            "themes": [],
            "text_for_embedding": "Bhagavad Gita 2.47\nSanskrit: कर्मण्येवाधिकारस्ते...\nTransliteration: karmaṇy evādhikāras te...\nTranslation (Swami Sivananda): Your right is only to work, but not to its results.\nWord meanings: karmaṇi — in action; phaleṣu — fruits",
        }
    ]


def test_normalize_records_raises_when_selected_translation_missing():
    verses = [
        {
            "chapter_number": 2,
            "verse_number": 47,
            "verse_order": 94,
            "id": 94,
            "text": "कर्मण्येवाधिकारस्ते...",
            "transliteration": "karmaṇy evādhikāras te...",
            "word_meanings": "karmaṇi — in action",
        }
    ]
    translations = []

    try:
        normalize_records(verses, translations, translation_author="Swami Sivananda")
    except ValueError as exc:
        assert "Missing Swami Sivananda English translations for verse ids: [94]" in str(exc)
    else:
        raise AssertionError("Expected ValueError for missing translation")
