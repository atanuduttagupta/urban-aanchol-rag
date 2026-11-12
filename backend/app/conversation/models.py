from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.app.retrieval.models import RetrievalIntent


@dataclass(frozen=True)
class ConversationContext:
    """
    Retrieval-focused conversation context.

    previous_query stores the customer's immediately preceding query.
    last_result_ids stores the ordered IDs from the latest displayed batch.
    shown_product_ids stores unique IDs already displayed.
    selected_product_id stores an explicitly selected product.
    last_retrieval_intent stores the last successful structured search.
    """

    previous_query: str | None = None
    last_result_ids: tuple[str, ...] = ()
    shown_product_ids: tuple[str, ...] = ()
    selected_product_id: str | None = None
    last_retrieval_intent: RetrievalIntent | None = None
