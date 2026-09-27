from backend.app.query_understanding.attribute_matcher import (
    match_catalogue_attributes,
)

VOCABULARY = {
    "occasion": [
        "Wedding",
        "Festival",
        "Party",
    ],
    "style": [
        "Traditional",
        "Contemporary",
    ],
    "mood": [
        "Elegant",
        "Vibrant",
    ],
    "tag": [
        "Handloom",
        "Festive",
    ],
}


def test_matches_attributes_case_insensitively():
    matches = match_catalogue_attributes(
        "I want something ELEGANT for a wedding",
        VOCABULARY,
    )

    assert matches == {
        "occasion": ["Wedding"],
        "mood": ["Elegant"],
    }


def test_matches_multiple_values_within_same_attribute():
    matches = match_catalogue_attributes(
        "I want something elegant and vibrant",
        VOCABULARY,
    )

    assert matches == {
        "mood": ["Elegant", "Vibrant"],
    }


def test_matches_multiple_attribute_types():
    matches = match_catalogue_attributes(
        "traditional handloom saree for festival",
        VOCABULARY,
    )

    assert matches == {
        "occasion": ["Festival"],
        "style": ["Traditional"],
        "tag": ["Handloom"],
    }


def test_does_not_match_partial_words():
    matches = match_catalogue_attributes(
        "I want something elegantness",
        VOCABULARY,
    )

    assert matches == {}


def test_unknown_language_is_left_unmatched():
    matches = match_catalogue_attributes(
        "I want something beautiful and graceful",
        VOCABULARY,
    )

    assert matches == {}


def test_empty_vocabulary_returns_no_matches():
    matches = match_catalogue_attributes(
        "I want something elegant for a wedding",
        {},
    )

    assert matches == {}


def test_matches_new_catalogue_values_without_code_changes():
    vocabulary = {
        "colour": ["Blue", "Wine"],
        "mood": ["Elegant", "Romantic"],
    }

    result = match_catalogue_attributes(
        "I want a wine saree with a romantic mood",
        vocabulary,
    )

    assert result == {
        "colour": ["Wine"],
        "mood": ["Romantic"],
    }


def test_prefers_specific_catalogue_value_when_matches_overlap():
    vocabulary = {
        "colour": [
            "Blue",
            "Light Blue",
            "Dark Blue",
        ],
    }

    result = match_catalogue_attributes(
        "Show me light blue sarees",
        vocabulary,
    )

    assert result == {
        "colour": ["Light Blue"],
    }


def test_preserves_distinct_non_overlapping_catalogue_values():
    vocabulary = {
        "colour": [
            "Blue",
            "Light Blue",
            "Red",
        ],
    }

    result = match_catalogue_attributes(
        "Show me blue and light blue sarees",
        vocabulary,
    )

    assert result == {
        "colour": ["Blue", "Light Blue"],
    }


def test_prefers_specific_catalogue_value_for_another_overlapping_phrase():
    vocabulary = {
        "colour": [
            "Blue",
            "Light Blue",
            "Dark Blue",
        ],
    }

    result = match_catalogue_attributes(
        "I want a dark blue saree",
        vocabulary,
    )

    assert result == {
        "colour": ["Dark Blue"],
    }
