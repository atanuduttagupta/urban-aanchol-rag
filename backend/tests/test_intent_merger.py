from backend.app.query_understanding.intent_merger import (
    merge_llm_intent,
)
from backend.app.query_understanding.llm_models import (
    LLMIntentProposal,
)
from backend.app.query_understanding.retrieval_safety import (
    RetrievalSafety,
)
from backend.app.retrieval.models import RetrievalIntent


def _intent(
    *,
    filters: dict[str, object] | None = None,
    requested_limit: int | None = None,
) -> RetrievalIntent:
    return RetrievalIntent(
        original_query="Show me blue silk sarees",
        semantic_query="Show me blue silk sarees",
        filters=filters,
        requested_limit=requested_limit,
        retrieval_safety=RetrievalSafety(
            retrieval_safe=False,
            signals=("comparison_detected",),
        ),
    )


def test_llm_can_add_missing_filter() -> None:
    deterministic = _intent(
        filters={"colour": "Blue"},
        requested_limit=5,
    )

    proposal = LLMIntentProposal(
        filters={"max_price": 2800},
    )

    result = merge_llm_intent(
        deterministic_intent=deterministic,
        proposal=proposal,
    )

    assert result.merged is True
    assert result.intent is not None
    assert result.intent.filters == {
        "colour": "Blue",
        "max_price": 2800,
    }
    assert result.intent.requested_limit == 5


def test_deterministic_filter_cannot_be_overwritten() -> None:
    deterministic = _intent(
        filters={"colour": "Blue"},
    )

    proposal = LLMIntentProposal(
        filters={"colour": "Red"},
    )

    result = merge_llm_intent(
        deterministic_intent=deterministic,
        proposal=proposal,
    )

    assert result.merged is False
    assert result.intent is None
    assert result.errors == ("filter_conflict:colour",)


def test_deterministic_limit_cannot_be_overwritten() -> None:
    deterministic = _intent(
        requested_limit=5,
    )

    proposal = LLMIntentProposal(
        requested_limit=10,
    )

    result = merge_llm_intent(
        deterministic_intent=deterministic,
        proposal=proposal,
    )

    assert result.merged is False
    assert result.intent is None
    assert result.errors == ("requested_limit_conflict",)


def test_llm_can_supply_missing_limit() -> None:
    deterministic = _intent()

    proposal = LLMIntentProposal(
        requested_limit=7,
    )

    result = merge_llm_intent(
        deterministic_intent=deterministic,
        proposal=proposal,
    )

    assert result.merged is True
    assert result.intent is not None
    assert result.intent.requested_limit == 7


def test_existing_deterministic_values_are_preserved() -> None:
    deterministic = _intent(
        filters={
            "colour": "Blue",
            "fabric": "Silk",
        },
        requested_limit=5,
    )

    proposal = LLMIntentProposal(
        filters={
            "max_price": 2800,
        },
        requested_limit=10,
        semantic_query="cheaper blue silk sarees",
    )

    result = merge_llm_intent(
        deterministic_intent=deterministic,
        proposal=proposal,
    )

    assert result.merged is False
    assert result.intent is None
    assert result.errors == ("requested_limit_conflict",)


def test_semantic_query_can_be_refined_by_llm() -> None:
    deterministic = _intent()

    proposal = LLMIntentProposal(
        semantic_query="cheaper festive sarees",
    )

    result = merge_llm_intent(
        deterministic_intent=deterministic,
        proposal=proposal,
    )

    assert result.merged is True
    assert result.intent is not None
    assert result.intent.semantic_query == "cheaper festive sarees"


def test_retrieval_safety_is_preserved() -> None:
    deterministic = _intent()

    proposal = LLMIntentProposal(
        filters={"max_price": 2800},
    )

    result = merge_llm_intent(
        deterministic_intent=deterministic,
        proposal=proposal,
    )

    assert result.intent is not None
    assert result.intent.retrieval_safety == (deterministic.retrieval_safety)
