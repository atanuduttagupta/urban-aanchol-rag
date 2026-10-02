from dataclasses import dataclass

from backend.app.conversation.resolution import ResolutionStatus
from backend.app.retrieval.models import RetrievalIntent


@dataclass(frozen=True)
class LLMResolutionDecision:
    """
    Describes whether an ambiguous retrieval intent is eligible
    for LLM-based interpretation.

    This policy does not call an LLM.
    """

    eligible: bool
    reason: str | None = None


LLM_ELIGIBLE_SIGNALS = frozenset(
    {
        "conversational_reference_detected",
        "comparison_detected",
        "approximate_constraint_detected",
    }
)


def decide_llm_resolution(
    intent: RetrievalIntent,
    resolution_status: ResolutionStatus,
) -> LLMResolutionDecision:
    """
    Decide whether an unresolved retrieval ambiguity may be sent
    to an LLM.

    The policy is intentionally narrow:
    only known retrieval-critical ambiguity types are eligible.

    Safe or already-resolved intents must not be sent to an LLM.
    """

    if resolution_status != ResolutionStatus.AMBIGUOUS:
        return LLMResolutionDecision(
            eligible=False,
            reason="intent_is_not_ambiguous",
        )

    if intent.retrieval_safety is None:
        return LLMResolutionDecision(
            eligible=False,
            reason="retrieval_safety_information_missing",
        )

    signals = set(intent.retrieval_safety.signals)

    eligible_signals = signals & LLM_ELIGIBLE_SIGNALS

    if not eligible_signals:
        return LLMResolutionDecision(
            eligible=False,
            reason="no_llm_eligible_signal",
        )

    return LLMResolutionDecision(
        eligible=True,
        reason="llm_eligible_retrieval_ambiguity",
    )
