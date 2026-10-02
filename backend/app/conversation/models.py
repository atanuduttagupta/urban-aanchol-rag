from dataclasses import dataclass


@dataclass(frozen=True)
class ConversationContext:
    """
    Retrieval-focused conversation context.

    `previous_query` stores the customer's immediately preceding query.

    `last_result_ids` stores the ordered product IDs from the most
    recently displayed retrieval result set.

    `selected_product_id` stores the product explicitly selected by
    the customer, when available.

    Product details are intentionally not stored here. Product IDs
    remain the reference, and current product data should be retrieved
    from the catalogue database when needed.
    """

    previous_query: str | None = None
    last_result_ids: tuple[str, ...] = ()
    selected_product_id: str | None = None
