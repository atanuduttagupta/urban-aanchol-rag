from backend.app.query_understanding.limit_extractor import (
    extract_requested_limit,
)


VOCABULARY = {
    "category": ["Saree", "Blouse"],
}


def test_extracts_show_me_limit():
    assert extract_requested_limit(
        "Show me 3 sarees"
    ) == 3


def test_extracts_show_limit():
    assert extract_requested_limit(
        "Show 5 sarees"
    ) == 5


def test_extracts_give_me_limit():
    assert extract_requested_limit(
        "Give me 4 options"
    ) == 4


def test_extracts_find_limit():
    assert extract_requested_limit(
        "Find 6 sarees"
    ) == 6


def test_extracts_top_limit():
    assert extract_requested_limit(
        "Show top 10 sarees"
    ) == 10


def test_extracts_number_before_catalogue_item():
    assert extract_requested_limit(
        "I want 3 sarees",
        vocabulary=VOCABULARY,
    ) == 3


def test_extracts_number_before_new_catalogue_item():
    vocabulary = {
        "category": ["Dupatta"],
    }

    assert extract_requested_limit(
        "I want 7 dupattas",
        vocabulary=vocabulary,
    ) == 7


def test_does_not_treat_price_as_limit():
    assert extract_requested_limit(
        "Sarees under 3000"
    ) is None


def test_no_explicit_limit():
    assert extract_requested_limit(
        "I want an elegant saree for a wedding"
    ) is None