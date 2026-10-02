from backend.app.conversation.resolution import ResolutionStatus
from backend.app.query_understanding.llm_resolution_policy import (
    decide_llm_resolution,
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


def test_safe_intent_is_not_llm_eligible() -> None:
    result = decide_llm_resolution(
        intent=_intent(retrieval_safe=True),
        resolution_status=ResolutionStatus.RESOLVED,
    )

    assert result.eligible is False
    assert result.reason == "intent_is_not_ambiguous"


def test_resolved_intent_is_not_llm_eligible() -> None:
    intent = _intent(
        retrieval_safe=False,
        signals=("comparison_detected",),
    )

    result = decide_llm_resolution(
        intent=intent,
        resolution_status=ResolutionStatus.RESOLVED,
    )

    assert result.eligible is False
    assert result.reason == "intent_is_not_ambiguous"


def test_comparison_is_llm_eligible() -> None:
    intent = _intent(
        retrieval_safe=False,
        signals=("comparison_detected",),
    )

    result = decide_llm_resolution(
        intent=intent,
        resolution_status=ResolutionStatus.AMBIGUOUS,
    )

    assert result.eligible is True
    assert result.reason == "llm_eligible_retrieval_ambiguity"


def test_conversational_reference_is_llm_eligible() -> None:
    intent = _intent(
        retrieval_safe=False,
        signals=("conversational_reference_detected",),
    )

    result = decide_llm_resolution(
        intent=intent,
        resolution_status=ResolutionStatus.AMBIGUOUS,
    )

    assert result.eligible is True


def test_approximate_constraint_is_llm_eligible() -> None:
    intent = _intent(
        retrieval_safe=False,
        signals=("approximate_constraint_detected",),
    )

    result = decide_llm_resolution(
        intent=intent,
        resolution_status=ResolutionStatus.AMBIGUOUS,
    )

    assert result.eligible is True


def test_negation_is_not_currently_llm_eligible() -> None:
    intent = _intent(
        retrieval_safe=False,
        signals=("negation_detected",),
    )

    result = decide_llm_resolution(
        intent=intent,
        resolution_status=ResolutionStatus.AMBIGUOUS,
    )

    assert result.eligible is False
    assert result.reason == "no_llm_eligible_signal"


def test_missing_safety_information_is_not_llm_eligible() -> None:
    intent = RetrievalIntent(
        original_query="test query",
        semantic_query="test query",
        retrieval_safety=None,
    )

    result = decide_llm_resolution(
        intent=intent,
        resolution_status=ResolutionStatus.AMBIGUOUS,
    )

    assert result.eligible is False
    assert result.reason == "retrieval_safety_information_missing"
