from src.chunking import apply_theme_tags, build_adjacent_chunks, build_verse_chunks


def sample_records():
    return [
        {
            "id": "2.47",
            "chapter": 2,
            "verse": 47,
            "verse_order": 94,
            "translation": "Your right is only to work, but not to its results.",
            "sanskrit": "कर्मण्येवाधिकारस्ते...",
            "transliteration": "karmaṇy evādhikāras te...",
            "word_meanings": "karmaṇi — in action; phaleṣu — fruits",
            "translation_author": "Swami Sivananda",
            "source_dataset": "ravisiyer/gita-data",
            "source_license": "Unlicense",
            "source_url": "https://github.com/ravisiyer/gita-data",
            "themes": [],
            "text_for_embedding": "Bhagavad Gita 2.47\nTranslation: Your right is only to work, but not to its results.",
        },
        {
            "id": "2.48",
            "chapter": 2,
            "verse": 48,
            "verse_order": 95,
            "translation": "Perform action, O Arjuna, being steadfast in Yoga.",
            "sanskrit": "योगस्थः कुरु कर्माणि...",
            "transliteration": "yogasthaḥ kuru karmāṇi...",
            "word_meanings": "yoga-sthaḥ — steadfast in Yoga",
            "translation_author": "Swami Sivananda",
            "source_dataset": "ravisiyer/gita-data",
            "source_license": "Unlicense",
            "source_url": "https://github.com/ravisiyer/gita-data",
            "themes": [],
            "text_for_embedding": "Bhagavad Gita 2.48\nTranslation: Perform action, O Arjuna, being steadfast in Yoga.",
        },
        {
            "id": "3.19",
            "chapter": 3,
            "verse": 19,
            "verse_order": 135,
            "translation": "Therefore, without attachment, always perform the action that should be done.",
            "sanskrit": "तस्मादसक्तः सततं...",
            "transliteration": "tasmād asaktaḥ satataṁ...",
            "word_meanings": "asaktaḥ — without attachment",
            "translation_author": "Swami Sivananda",
            "source_dataset": "ravisiyer/gita-data",
            "source_license": "Unlicense",
            "source_url": "https://github.com/ravisiyer/gita-data",
            "themes": [],
            "text_for_embedding": "Bhagavad Gita 3.19\nTranslation: Therefore, without attachment, always perform the action that should be done.",
        },
    ]


def test_apply_theme_tags_adds_known_themes_without_mutating_input():
    records = sample_records()
    tagged = apply_theme_tags(records, {"2.47": ["action", "detachment", "duty"]})

    assert records[0]["themes"] == []
    assert tagged[0]["themes"] == ["action", "detachment", "duty"]
    assert tagged[1]["themes"] == []


def test_build_verse_chunks_preserves_citation_and_metadata():
    tagged = apply_theme_tags(sample_records(), {"2.47": ["action", "detachment", "duty"]})

    chunks = build_verse_chunks(tagged)

    assert chunks[0] == {
        "chunk_id": "verse:2.47",
        "chunk_type": "verse",
        "chapter": 2,
        "verse_start": 47,
        "verse_end": 47,
        "verse_ids": ["2.47"],
        "citation": "Bhagavad Gita 2.47",
        "themes": ["action", "detachment", "duty"],
        "translation_author": "Swami Sivananda",
        "source_dataset": "ravisiyer/gita-data",
        "source_license": "Unlicense",
        "text": "Bhagavad Gita 2.47\nThemes: action, detachment, duty\nTranslation (Swami Sivananda): Your right is only to work, but not to its results.\nWord meanings: karmaṇi — in action; phaleṣu — fruits",
    }


def test_build_adjacent_chunks_groups_only_contiguous_verses_in_same_chapter():
    tagged = apply_theme_tags(
        sample_records(),
        {
            "2.47": ["action", "detachment"],
            "2.48": ["equanimity", "discipline"],
            "3.19": ["duty"],
        },
    )

    chunks = build_adjacent_chunks(tagged, window_size=2)

    assert [chunk["chunk_id"] for chunk in chunks] == ["group:2.47-2.48"]
    assert chunks[0]["verse_ids"] == ["2.47", "2.48"]
    assert chunks[0]["citation"] == "Bhagavad Gita 2.47-2.48"
    assert chunks[0]["themes"] == ["action", "detachment", "discipline", "equanimity"]
    assert "Bhagavad Gita 2.47" in chunks[0]["text"]
    assert "Bhagavad Gita 2.48" in chunks[0]["text"]
    assert "3.19" not in chunks[0]["citation"]
