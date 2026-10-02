import re
from dataclasses import dataclass

from backend.app.conversation.models import ConversationContext


@dataclass(frozen=True)
class ReferenceResolution:
    """
    Result of attempting to resolve a product reference
    from trusted conversation context.

    `resolved_product_id` is populated only when the reference
    can be resolved deterministically.
    """

    resolved_product_id: str | None = None
    resolved: bool = False


def resolve_product_reference(
    query: str,
    context: ConversationContext,
) -> ReferenceResolution:
    """
    Resolve simple product references using conversation context.

    This resolver never invents product IDs. If the required
    context is unavailable or the reference cannot be resolved,
    the result remains unresolved.
    """
    normalized = re.sub(r"\s+", " ", query.strip().casefold())

    if not context.last_result_ids:
        return ReferenceResolution()

    if re.search(r"\b(first|1st)\s+one\b", normalized):
        return ReferenceResolution(
            resolved_product_id=context.last_result_ids[0],
            resolved=True,
        )

    if re.search(r"\b(second|2nd)\s+one\b", normalized):
        if len(context.last_result_ids) >= 2:
            return ReferenceResolution(
                resolved_product_id=context.last_result_ids[1],
                resolved=True,
            )
        return ReferenceResolution()

    if re.search(r"\b(third|3rd)\s+one\b", normalized):
        if len(context.last_result_ids) >= 3:
            return ReferenceResolution(
                resolved_product_id=context.last_result_ids[2],
                resolved=True,
            )
        return ReferenceResolution()

    if (
        re.search(r"\b(this|that)\s+(?:saree|one)\b", normalized)
        and context.selected_product_id
    ):
        return ReferenceResolution(
            resolved_product_id=context.selected_product_id,
            resolved=True,
        )

    return ReferenceResolution()
