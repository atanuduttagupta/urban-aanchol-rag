from backend.app.conversation.models import ConversationContext

MAX_SHOWN_PRODUCT_IDS = 100


def update_displayed_products(
    context: ConversationContext,
    displayed_product_ids: tuple[str, ...],
) -> ConversationContext:
    """
    Return an updated context after products are displayed.

    Only products actually displayed to the customer should be supplied.

    The latest result IDs preserve their display order.
    The accumulated history contains unique IDs in display order,
    retaining at most the most recent 100 unique IDs.
    """
    latest_ids = tuple(dict.fromkeys(displayed_product_ids))

    accumulated_ids = tuple(
        product_id
        for product_id in context.shown_product_ids
        if product_id not in latest_ids
    ) + latest_ids

    bounded_ids = accumulated_ids[-MAX_SHOWN_PRODUCT_IDS:]

    return ConversationContext(
        previous_query=context.previous_query,
        last_result_ids=latest_ids,
        shown_product_ids=bounded_ids,
        selected_product_id=context.selected_product_id,
        last_retrieval_intent=context.last_retrieval_intent,
    )