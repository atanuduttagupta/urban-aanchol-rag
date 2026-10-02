from dataclasses import dataclass
from typing import Any

from backend.app.conversation.models import ConversationContext
from backend.app.query_understanding.llm_models import LLMIntentProposal


@dataclass(frozen=True)
class LLMValidationResult:
    """
    Result of validating an untrusted LLM intent proposal.
    """

    valid: bool
    errors: tuple[str, ...] = ()


SUPPORTED_FILTERS = frozenset(
    {
        "category",
        "availability",
        "brand",
        "collection",
        "fabric",
        "colour",
        "secondary_colour",
        "pattern",
        "border",
        "occasion",
        "style",
        "mood",
        "tag",
        "min_price",
        "max_price",
    }
)


def _normalise(value: str) -> str:
    return " ".join(value.strip().casefold().split())


def _validate_filter_names(
    filters: dict[str, Any],
    errors: list[str],
) -> None:
    for name in filters:
        if name not in SUPPORTED_FILTERS:
            errors.append(f"unsupported_filter:{name}")


def _validate_filter_values(
    filters: dict[str, Any],
    vocabulary: dict[str, list[str]],
    errors: list[str],
) -> None:
    catalogue_attributes = set(vocabulary)

    for name, value in filters.items():
        if name not in catalogue_attributes:
            continue

        allowed_values = {_normalise(item) for item in vocabulary[name]}

        values = value if isinstance(value, list) else [value]

        for item in values:
            if not isinstance(item, str):
                errors.append(f"invalid_filter_value_type:{name}")
                continue

            if _normalise(item) not in allowed_values:
                errors.append(f"unknown_catalogue_value:{name}:{item}")


def _validate_price_filters(
    filters: dict[str, Any],
    errors: list[str],
) -> None:
    for name in ("min_price", "max_price"):
        if name not in filters:
            continue

        value = filters[name]

        if not isinstance(value, (int, float)):
            errors.append(f"invalid_price:{name}")
            continue

        if value < 0:
            errors.append(f"invalid_price:{name}")


def _validate_requested_limit(
    requested_limit: int | None,
    errors: list[str],
) -> None:
    if requested_limit is None:
        return

    if not isinstance(requested_limit, int):
        errors.append("invalid_requested_limit")
        return

    if requested_limit <= 0:
        errors.append("invalid_requested_limit")


def _validate_resolved_product(
    resolved_product_id: str | None,
    context: ConversationContext,
    errors: list[str],
) -> None:
    if resolved_product_id is None:
        return

    trusted_ids = set(context.last_result_ids)

    if context.selected_product_id:
        trusted_ids.add(context.selected_product_id)

    if resolved_product_id not in trusted_ids:
        errors.append("untrusted_resolved_product")


def validate_llm_intent_proposal(
    proposal: LLMIntentProposal,
    vocabulary: dict[str, list[str]],
    context: ConversationContext,
) -> LLMValidationResult:
    """
    Validate an untrusted LLM retrieval-intent proposal.

    Catalogue values must come from the supplied vocabulary.
    Product references must come from trusted conversation context.

    No database access or LLM calls occur here.
    """
    errors: list[str] = []

    if proposal.filters is not None:
        _validate_filter_names(
            filters=proposal.filters,
            errors=errors,
        )
        _validate_filter_values(
            filters=proposal.filters,
            vocabulary=vocabulary,
            errors=errors,
        )
        _validate_price_filters(
            filters=proposal.filters,
            errors=errors,
        )

    _validate_requested_limit(
        requested_limit=proposal.requested_limit,
        errors=errors,
    )

    _validate_resolved_product(
        resolved_product_id=proposal.resolved_product_id,
        context=context,
        errors=errors,
    )

    return LLMValidationResult(
        valid=not errors,
        errors=tuple(errors),
    )
