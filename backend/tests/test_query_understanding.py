from backend.app.query_understanding.query_understanding import (
    understand_query,
)


VOCABULARY = {
    "category": ["Saree", "Blouse"],
    "brand": ["Brand A", "Brand B"],
    "collection": ["Festive Collection"],
    "fabric": ["Cotton", "Silk"],
    "colour": ["Blue", "Red", "Wine"],
    "secondary_colour": ["Gold"],
    "pattern": ["Floral"],
    "border": ["Zari"],
    "occasion": ["Wedding", "Party"],
    "style": ["Traditional", "Contemporary"],
    "mood": ["Elegant", "Vibrant", "Romantic"],
    "tag": ["Handloom", "Festive"],
}


def test_understand_query_extracts_attributes_and_price():
    query = "I want an elegant blue cotton saree for a wedding under 3000"

    intent = understand_query(
        query=query,
        vocabulary=VOCABULARY,
    )

    assert intent.original_query == query

    assert intent.semantic_query == query

    assert intent.filters == {
        "category": "Saree",
        "fabric": "Cotton",
        "colour": "Blue",
        "occasion": "Wedding",
        "mood": "Elegant",
        "max_price": 3000.0,
    }

    assert intent.requested_limit is None


def test_understand_query_extracts_multiple_values():
    query = "Show me blue or red sarees for a wedding or party"

    intent = understand_query(
        query=query,
        vocabulary=VOCABULARY,
    )

    assert intent.filters == {
        "category": "Saree",
        "colour": ["Blue", "Red"],
        "occasion": ["Wedding", "Party"],
    }


def test_understand_query_extracts_requested_limit():
    query = "Show me 3 blue cotton sarees"

    intent = understand_query(
        query=query,
        vocabulary=VOCABULARY,
    )

    assert intent.filters == {
        "category": "Saree",
        "colour": "Blue",
        "fabric": "Cotton",
    }

    assert intent.requested_limit == 3


def test_understand_query_extracts_new_catalogue_values():
    query = "Show me romantic wine sarees"

    intent = understand_query(
        query=query,
        vocabulary=VOCABULARY,
    )

    assert intent.filters == {
        "category": "Saree",
        "colour": "Wine",
        "mood": "Romantic",
    }


def test_understand_query_preserves_semantic_query():
    query = "Something graceful and festive for my sister's wedding"

    intent = understand_query(
        query=query,
        vocabulary=VOCABULARY,
    )

    assert intent.original_query == query
    assert intent.semantic_query == query
    assert intent.filters == {
        "occasion": "Wedding",
        "tag": "Festive",
    }
    assert intent.requested_limit is None


def test_understand_query_returns_empty_filters_when_nothing_is_detected():
    query = "I want something beautiful for my sister"

    intent = understand_query(
        query=query,
        vocabulary=VOCABULARY,
    )

    assert intent.original_query == query
    assert intent.semantic_query == query
    assert intent.filters is None
    assert intent.requested_limit is None

def test_understand_query_extracts_all_constraints_from_realistic_request():
    query = "Show me 5 elegant blue cotton sarees under 3000"

    intent = understand_query(
        query=query,
        vocabulary=VOCABULARY,
    )

    assert intent.original_query == query

    assert intent.semantic_query == query

    assert intent.filters == {
        "category": "Saree",
        "colour": "Blue",
        "fabric": "Cotton",
        "mood": "Elegant",
        "max_price": 3000.0,
    }

    assert intent.requested_limit == 5