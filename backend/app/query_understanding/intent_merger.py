from dataclasses import dataclass
from typing import Any

from backend.app.query_understanding.llm_models import LLMIntentProposal
from backend.app.retrieval.models import RetrievalIntent


@dataclass(frozen=True)
class IntentMergeResult:
    """
    Result of merging a validated LLM proposal with deterministic intent.

    The deterministic intent remains the source of truth when both
    sources provide the same retrieval field.
    """

    merged: bool
    intent: RetrievalIntent | None = None
    errors: tuple[str, ...] = ()


def _merge_filters(
    deterministic_filters: dict[str, Any] | None,
    llm_filters: dict[str, Any] | None,
) -> tuple[dict[str, Any], list[str]]:
    merged = dict(deterministic_filters or {})
    errors: list[str] = []

    for name, llm_value in (llm_filters or {}).items():
        if name not in merged:
            merged[name] = llm_value
            continue

        deterministic_value = merged[name]

        if deterministic_value != llm_value:
            errors.append(f"filter_conflict:{name}")

    return merged, errors


def merge_llm_intent(
    deterministic_intent: RetrievalIntent,
    proposal: LLMIntentProposal,
) -> IntentMergeResult:
    """
    Merge a validated LLM proposal into deterministic intent.

    Deterministic values always take precedence.

    The proposal is expected to have already passed the dedicated
    LLM intent validator.
    """
    merged_filters, errors = _merge_filters(
        deterministic_filters=deterministic_intent.filters,
        llm_filters=proposal.filters,
    )

    if (
        proposal.requested_limit is not None
        and deterministic_intent.requested_limit is not None
        and proposal.requested_limit != deterministic_intent.requested_limit
    ):
        errors.append("requested_limit_conflict")

    if errors:
        return IntentMergeResult(
            merged=False,
            errors=tuple(errors),
        )

    requested_limit = (
        deterministic_intent.requested_limit
        if deterministic_intent.requested_limit is not None
        else proposal.requested_limit
    )

    semantic_query = (
        proposal.semantic_query
        if proposal.semantic_query is not None
        else deterministic_intent.semantic_query
    )

    return IntentMergeResult(
        merged=True,
        intent=RetrievalIntent(
            original_query=deterministic_intent.original_query,
            semantic_query=semantic_query,
            filters=merged_filters or None,
            requested_limit=requested_limit,
            retrieval_safety=deterministic_intent.retrieval_safety,
        ),
    )
