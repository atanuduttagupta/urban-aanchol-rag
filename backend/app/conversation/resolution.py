from dataclasses import dataclass
from enum import StrEnum

from backend.app.conversation.follow_up_detector import (
    detect_follow_up_intent,
)
from backend.app.conversation.follow_up_models import FollowUpIntentType
from backend.app.conversation.models import ConversationContext
from backend.app.conversation.resolver import resolve_product_reference
from backend.app.retrieval.models import RetrievalIntent


class ResolutionStatus(StrEnum):
    RESOLVED = "resolved"
    AMBIGUOUS = "ambiguous"
    UNRESOLVED = "unresolved"


@dataclass(frozen=True)
class ResolutionResult:
    """
    Outcome of attempting to resolve retrieval-critical ambiguity.

    RESOLVED:
        The ambiguity was resolved deterministically from trusted
        conversation context.

    AMBIGUOUS:
        The query contains a retrieval-critical ambiguity that may
        require additional interpretation.

    UNRESOLVED:
        Required reference information is unavailable and must not
        be guessed.
    """

    status: ResolutionStatus
    resolved_product_id: str | None = None



def resolve_retrieval_ambiguity(
    intent: RetrievalIntent,
    context: ConversationContext,
) -> ResolutionResult:
    """
    Resolve retrieval-critical ambiguity using trusted conversation
    context before considering additional interpretation.

    This function does not call an LLM and does not perform database
    retrieval.
    """
    if intent.retrieval_safety is None:
        return ResolutionResult(
            status=ResolutionStatus.AMBIGUOUS,
        )

    if intent.retrieval_safety.retrieval_safe:
        return ResolutionResult(
            status=ResolutionStatus.RESOLVED,
        )

    follow_up = detect_follow_up_intent(intent.original_query)

    if (
        follow_up is not None
        and follow_up.intent_type == FollowUpIntentType.REFERENCE
    ):
        reference = resolve_product_reference(
            query=intent.original_query,
            context=context,
        )

        if reference.resolved:
            return ResolutionResult(
                status=ResolutionStatus.RESOLVED,
                resolved_product_id=reference.resolved_product_id,
            )

    # Do not fall back to reference-only resolution when the query
    # combines a price comparison with a positional reference.
    combined_comparison = (
        "comparison_detected" in intent.retrieval_safety.signals
        and "conversational_reference_detected"
        in intent.retrieval_safety.signals
    )

    if not combined_comparison:
        reference = resolve_product_reference(
            query=intent.original_query,
            context=context,
        )

        if reference.resolved:
            return ResolutionResult(
                status=ResolutionStatus.RESOLVED,
                resolved_product_id=reference.resolved_product_id,
            )

    # A retrieval-critical ambiguity exists, but we could not
    # resolve it deterministically. Do not guess.
    if intent.retrieval_safety.signals:
        return ResolutionResult(
            status=ResolutionStatus.AMBIGUOUS,
        )

    return ResolutionResult(
        status=ResolutionStatus.UNRESOLVED,
    )
