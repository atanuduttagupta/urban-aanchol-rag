from backend.app.query_understanding.plural_variants import (
    generate_plural_variants,
)


def test_generates_regular_plural():
    assert generate_plural_variants("Saree") == {"sarees"}


def test_generates_plural_for_words_ending_in_y():
    assert generate_plural_variants("Party") == {"parties"}


def test_generates_plural_for_words_ending_in_s():
    assert generate_plural_variants("Blouse") == {"blouses"}


def test_generates_plural_for_words_ending_in_ch():
    assert generate_plural_variants("Match") == {"matches"}


def test_is_case_insensitive():
    assert generate_plural_variants("SAREE") == {"sarees"}


def test_empty_value_returns_no_variants():
    assert generate_plural_variants("") == set()


def test_multi_word_value_returns_no_variants():
    assert generate_plural_variants("Festive Collection") == set()