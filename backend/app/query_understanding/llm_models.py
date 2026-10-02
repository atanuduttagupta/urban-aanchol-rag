from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class LLMIntentProposal:
    """
    Untrusted retrieval-intent proposal produced by an LLM.

    This model represents a proposed interpretation only.
    It must be validated before it can become a RetrievalIntent.

    The LLM must never be treated as the source of truth for
    catalogue values, product details, prices, availability, or
    database operations.
    """

    semantic_query: str | None = None
    filters: dict[str, Any] | None = None
    requested_limit: int | None = None
    resolved_product_id: str | None = None
