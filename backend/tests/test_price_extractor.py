from backend.app.query_understanding.price_extractor import (
    extract_price_filters,
)


def test_extracts_max_price():
    assert extract_price_filters(
        "Show me cotton sarees under 3000"
    ) == {
        "max_price": 3000.0,
    }


def test_extracts_rupee_max_price():
    assert extract_price_filters(
        "Show me sarees below ₹3,000"
    ) == {
        "max_price": 3000.0,
    }


def test_extracts_min_price():
    assert extract_price_filters(
        "I want sarees above Rs 2000"
    ) == {
        "min_price": 2000.0,
    }


def test_extracts_price_range():
    assert extract_price_filters(
        "Show sarees between 2000 and 3000"
    ) == {
        "min_price": 2000.0,
        "max_price": 3000.0,
    }


def test_extracts_price_range_with_rupee_symbol():
    assert extract_price_filters(
        "Show sarees between ₹2,000 and ₹3,500"
    ) == {
        "min_price": 2000.0,
        "max_price": 3500.0,
    }


def test_bare_number_is_not_treated_as_price():
    assert extract_price_filters(
        "Show me 3 sarees"
    ) == {}


def test_no_price_constraint():
    assert extract_price_filters(
        "I want something elegant for a wedding"
    ) == {}

def test_extracts_not_exceeding_max_price():
    result = extract_price_filters(
        "Show me sarees not exceeding ₹3000"
    )

    assert result == {
        "max_price": 3000.0,
    }


def test_extracts_below_price_with_comma():
    result = extract_price_filters(
        "Show me sarees below ₹3,000"
    )

    assert result == {
        "max_price": 3000.0,
    }


def test_extracts_up_to_price_with_comma():
    result = extract_price_filters(
        "Show me sarees up to ₹3,000"
    )

    assert result == {
        "max_price": 3000.0,
    }


def test_extracts_between_price_with_currency_symbols():
    result = extract_price_filters(
        "Show me sarees between ₹2,000 and ₹4,000"
    )

    assert result == {
        "min_price": 2000.0,
        "max_price": 4000.0,
    }

def test_extracts_not_exceeding_without_currency_symbol():
    result = extract_price_filters(
        "Show me sarees not exceeding 3000"
    )

    assert result == {
        "max_price": 3000.0,
    }