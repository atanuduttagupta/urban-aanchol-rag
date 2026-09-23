from backend.app.retrieval.models import RetrievalIntent


def test_retrieval_intent_preserves_original_and_semantic_query():
    intent = RetrievalIntent(
        original_query=(
            "I want something elegant for my sister's wedding, "
            "preferably blue cotton under 3000"
        ),
        semantic_query="something elegant for my sister's wedding",
        filters={
            "colour": "Blue",
            "fabric": "Cotton",
            "max_price": 3000,
        },
    )

    assert intent.original_query == (
        "I want something elegant for my sister's wedding, "
        "preferably blue cotton under 3000"
    )
    assert intent.semantic_query == (
        "something elegant for my sister's wedding"
    )
    assert intent.filters == {
        "colour": "Blue",
        "fabric": "Cotton",
        "max_price": 3000,
    }
    assert intent.requested_limit is None


def test_retrieval_intent_preserves_explicit_requested_limit():
    intent = RetrievalIntent(
        original_query="Show me 3 blue cotton sarees",
        semantic_query="blue cotton sarees",
        filters={
            "colour": "Blue",
            "fabric": "Cotton",
        },
        requested_limit=3,
    )

    assert intent.requested_limit == 3