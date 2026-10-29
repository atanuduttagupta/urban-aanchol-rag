from backend.app.conversation.models import ConversationContext
from backend.app.conversation.resolution import (
    ResolutionStatus,
    resolve_retrieval_ambiguity,
)
from backend.app.query_understanding.retrieval_safety import (
    RetrievalSafety,
)
from backend.app.retrieval.models import RetrievalIntent


def _intent(
    *,
    retrieval_safe: bool,
    signals: tuple[str, ...] = (),
) -> RetrievalIntent:
    return RetrievalIntent(
        original_query="test query",
        semantic_query="test query",
        retrieval_safety=RetrievalSafety(
            retrieval_safe=retrieval_safe,
            signals=signals,
        ),
    )


def test_safe_intent_is_resolved() -> None:
    result = resolve_retrieval_ambiguity(
        intent=_intent(retrieval_safe=True),
        context=ConversationContext(),
    )

    assert result.status == ResolutionStatus.RESOLVED
    assert result.resolved_product_id is None


def test_first_result_reference_is_resolved() -> None:
    intent = _intent(
        retrieval_safe=False,
        signals=("conversational_reference_detected",),
    )
    intent = RetrievalIntent(
        original_query="Show me the first one",
        semantic_query="Show me the first one",
        retrieval_safety=intent.retrieval_safety,
    )

    context = ConversationContext(
        last_result_ids=("UA-0024", "UA-0018"),
    )

    result = resolve_retrieval_ambiguity(
        intent=intent,
        context=context,
    )

    assert result.status == ResolutionStatus.RESOLVED
    assert result.resolved_product_id == "UA-0024"


def test_unresolved_reference_is_ambiguous() -> None:
    intent = RetrievalIntent(
        original_query="Show me the one you showed earlier",
        semantic_query="Show me the one you showed earlier",
        retrieval_safety=RetrievalSafety(
            retrieval_safe=False,
            signals=("conversational_reference_detected",),
        ),
    )

    result = resolve_retrieval_ambiguity(
        intent=intent,
        context=ConversationContext(),
    )

    assert result.status == ResolutionStatus.AMBIGUOUS
    assert result.resolved_product_id is None


def test_comparison_without_resolvable_reference_is_ambiguous() -> None:
    intent = RetrievalIntent(
        original_query="Show me something cheaper",
        semantic_query="Show me something cheaper",
        retrieval_safety=RetrievalSafety(
            retrieval_safe=False,
            signals=("comparison_detected",),
        ),
    )

    result = resolve_retrieval_ambiguity(
        intent=intent,
        context=ConversationContext(),
    )

    assert result.status == ResolutionStatus.AMBIGUOUS
    assert result.resolved_product_id is None


def test_missing_safety_information_is_ambiguous() -> None:
    intent = RetrievalIntent(
        original_query="Show me something",
        semantic_query="Show me something",
        retrieval_safety=None,
    )

    result = resolve_retrieval_ambiguity(
        intent=intent,
        context=ConversationContext(),
    )

    assert result.status == ResolutionStatus.AMBIGUOUS



def test_second_result_follow_up_is_resolved() -> None:
    intent = RetrievalIntent(
        original_query="Show me the second one",
        semantic_query="Show me the second one",
        retrieval_safety=RetrievalSafety(
            retrieval_safe=False,
            signals=("conversational_reference_detected",),
        ),
    )
    context = ConversationContext(
        last_result_ids=("UA-0024", "UA-0018", "UA-0012"),
    )

    result = resolve_retrieval_ambiguity(
        intent=intent,
        context=context,
    )

    assert result.status == ResolutionStatus.RESOLVED
    assert result.resolved_product_id == "UA-0018"


def test_missing_third_result_remains_ambiguous() -> None:
    intent = RetrievalIntent(
        original_query="Show me the third one",
        semantic_query="Show me the third one",
        retrieval_safety=RetrievalSafety(
            retrieval_safe=False,
            signals=("conversational_reference_detected",),
        ),
    )
    context = ConversationContext(
        last_result_ids=("UA-0024", "UA-0018"),
    )

    result = resolve_retrieval_ambiguity(
        intent=intent,
        context=context,
    )

    assert result.status == ResolutionStatus.AMBIGUOUS
    assert result.resolved_product_id is None


def test_combined_price_comparison_is_not_simplified() -> None:
    intent = RetrievalIntent(
        original_query="Something cheaper than the second one",
        semantic_query="Something cheaper than the second one",
        retrieval_safety=RetrievalSafety(
            retrieval_safe=False,
            signals=(
                "conversational_reference_detected",
                "comparison_detected",
            ),
        ),
    )
    context = ConversationContext(
        last_result_ids=("UA-0024", "UA-0018"),
    )

    result = resolve_retrieval_ambiguity(
        intent=intent,
        context=context,
    )

    assert result.status == ResolutionStatus.AMBIGUOUS
    assert result.resolved_product_id is None
