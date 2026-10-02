from dataclasses import dataclass
from enum import StrEnum

from backend.app.conversation.models import ConversationContext
from backend.app.conversation.resolution import (
    ResolutionStatus,
    resolve_retrieval_ambiguity,
)
from backend.app.query_understanding.intent_merger import (
    merge_llm_intent,
)
from backend.app.query_understanding.llm_intent_validator import (
    validate_llm_intent_proposal,
)
from backend.app.query_understanding.llm_interface import (
    LLMIntentResolver,
)
from backend.app.query_understanding.llm_resolution_policy import (
    decide_llm_resolution,
)
from backend.app.query_understanding.query_understanding import (
    understand_query,
)
from backend.app.retrieval.models import RetrievalIntent


class OrchestrationStatus(StrEnum):
    READY_FOR_RETRIEVAL = "ready_for_retrieval"
    NEEDS_LLM = "needs_llm"
    NEEDS_CLARIFICATION = "needs_clarification"
    REJECTED = "rejected"


@dataclass(frozen=True)
class RetrievalDecision:
    """
    Outcome of retrieval-intent orchestration.

    `intent` is populated only when the intent is ready for retrieval.

    `resolved_product_id` is populated when a conversational product
    reference was resolved from trusted conversation context.
    """

    status: OrchestrationStatus
    intent: RetrievalIntent | None = None
    resolved_product_id: str | None = None
    reason: str | None = None


def prepare_retrieval(
    query: str,
    context: ConversationContext,
    vocabulary: dict[str, list[str]],
    llm_resolver: LLMIntentResolver | None = None,
) -> RetrievalDecision:
    """
    Prepare a customer query for retrieval.

    This function performs query understanding, deterministic
    ambiguity resolution, optional LLM escalation, validation,
    and intent merging.

    It does not perform product retrieval.
    """
    intent = understand_query(
        query=query,
        vocabulary=vocabulary,
    )

    resolution = resolve_retrieval_ambiguity(
        intent=intent,
        context=context,
    )

    if resolution.status == ResolutionStatus.RESOLVED:
        return RetrievalDecision(
            status=OrchestrationStatus.READY_FOR_RETRIEVAL,
            intent=intent,
            resolved_product_id=resolution.resolved_product_id,
        )

    if resolution.status == ResolutionStatus.UNRESOLVED:
        return RetrievalDecision(
            status=OrchestrationStatus.NEEDS_CLARIFICATION,
            reason="required_reference_unavailable",
        )

    llm_decision = decide_llm_resolution(
        intent=intent,
        resolution_status=resolution.status,
    )

    if not llm_decision.eligible:
        return RetrievalDecision(
            status=OrchestrationStatus.NEEDS_CLARIFICATION,
            reason=llm_decision.reason,
        )

    if llm_resolver is None:
        return RetrievalDecision(
            status=OrchestrationStatus.NEEDS_LLM,
            reason="llm_resolver_not_configured",
        )

    proposal = llm_resolver.resolve(
        intent=intent,
        context=context,
    )

    validation = validate_llm_intent_proposal(
        proposal=proposal,
        vocabulary=vocabulary,
        context=context,
    )

    if not validation.valid:
        return RetrievalDecision(
            status=OrchestrationStatus.REJECTED,
            reason="invalid_llm_intent",
        )

    merge_result = merge_llm_intent(
        deterministic_intent=intent,
        proposal=proposal,
    )

    if not merge_result.merged:
        return RetrievalDecision(
            status=OrchestrationStatus.REJECTED,
            reason="llm_intent_conflict",
        )

    return RetrievalDecision(
        status=OrchestrationStatus.READY_FOR_RETRIEVAL,
        intent=merge_result.intent,
    )
