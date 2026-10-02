import pytest

from backend.app.query_understanding.retrieval_safety import (
    detect_retrieval_safety,
)

TEST_VOCABULARY = {
    "colour": ["Red", "Blue", "Green"],
    "fabric": ["Silk", "Cotton"],
    "border": ["Zari"],
}


MULTI_WORD_TEST_VOCABULARY = {
    "colour": ["Red", "Blue", "Dark Blue"],
    "fabric": ["Silk", "Pure Silk"],
    "border": ["Zari", "Temple Border"],
}


@pytest.mark.parametrize(
    "query",
    [
        "Show me 5 blue silk sarees under ₹3000",
        "I want something graceful for a wedding",
        "Show me festive sarees",
        "I want something elegant and joyful",
        "Show me traditional sarees for Durga Puja",
    ],
)
def test_normal_queries_are_retrieval_safe(query: str) -> None:
    result = detect_retrieval_safety(
        query=query,
        vocabulary=TEST_VOCABULARY,
    )

    assert result.retrieval_safe is True
    assert result.signals == ()


@pytest.mark.parametrize(
    ("query", "expected_signal"),
    [
        (
            "Show me something cheaper than the saree you showed earlier",
            "comparison_detected",
        ),
        (
            "Show me the one you showed earlier",
            "conversational_reference_detected",
        ),
        (
            "Show me something like that one",
            "conversational_reference_detected",
        ),
        (
            "I don't want red sarees",
            "negation_detected",
        ),
        (
            "Show me sarees without zari",
            "negation_detected",
        ),
        (
            "Show me something around ₹3000",
            "approximate_constraint_detected",
        ),
        (
            "I want something affordable",
            "approximate_constraint_detected",
        ),
    ],
)
def test_retrieval_critical_ambiguity_is_not_safe(
    query: str,
    expected_signal: str,
) -> None:
    result = detect_retrieval_safety(
        query=query,
        vocabulary=TEST_VOCABULARY,
    )

    assert result.retrieval_safe is False
    assert expected_signal in result.signals


@pytest.mark.parametrize(
    "query",
    [
        "I don't want red sarees",
        "I do not want red sarees",
        "I don't want anything red",
        "Show me sarees without zari",
        "Avoid silk",
        "Show me sarees except cotton",
    ],
)
def test_catalogue_value_negation_is_not_safe(query: str) -> None:
    result = detect_retrieval_safety(
        query=query,
        vocabulary=TEST_VOCABULARY,
    )

    assert result.retrieval_safe is False
    assert "negation_detected" in result.signals


@pytest.mark.parametrize(
    "query",
    [
        "I don't want to buy anything today",
        "I want a beautiful red saree",
        "I want something elegant",
        "Show me blue silk sarees",
    ],
)
def test_non_critical_language_does_not_make_query_unsafe(
    query: str,
) -> None:
    result = detect_retrieval_safety(
        query=query,
        vocabulary=TEST_VOCABULARY,
    )

    assert result.retrieval_safe is True
    assert result.signals == ()


@pytest.mark.parametrize(
    "query",
    [
        "I don't want dark blue sarees",
        "I don't want pure silk",
        "Show me sarees without temple border",
    ],
)
def test_multi_word_catalogue_value_negation_is_not_safe(
    query: str,
) -> None:
    result = detect_retrieval_safety(
        query=query,
        vocabulary=MULTI_WORD_TEST_VOCABULARY,
    )

    assert result.retrieval_safe is False
    assert "negation_detected" in result.signals


@pytest.mark.parametrize(
    "query",
    [
        "I don't want anything dark",
        "I don't want anything pure",
        "I don't want anything temple",
    ],
)
def test_partial_catalogue_value_does_not_trigger_negation(
    query: str,
) -> None:
    result = detect_retrieval_safety(
        query=query,
        vocabulary=MULTI_WORD_TEST_VOCABULARY,
    )

    assert result.retrieval_safe is True
    assert result.signals == ()


def test_multiple_retrieval_critical_signals_are_reported() -> None:
    result = detect_retrieval_safety(
        query=(
            "Show me something cheaper than the one you showed earlier, but not red."
        ),
        vocabulary=TEST_VOCABULARY,
    )

    assert result.retrieval_safe is False
    assert result.signals == (
        "conversational_reference_detected",
        "comparison_detected",
        "negation_detected",
    )
