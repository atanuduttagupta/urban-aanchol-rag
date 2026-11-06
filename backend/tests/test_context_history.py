from backend.app.conversation.context_history import (
    MAX_SHOWN_PRODUCT_IDS,
    update_displayed_products,
)
from backend.app.conversation.models import ConversationContext


def test_updates_latest_displayed_product_ids() -> None:
    context = ConversationContext()

    updated = update_displayed_products(
        context,
        ("UA-0001", "UA-0002"),
    )

    assert updated.last_result_ids == ("UA-0001", "UA-0002")
    assert updated.shown_product_ids == ("UA-0001", "UA-0002")


def test_appends_new_products_to_display_history() -> None:
    context = ConversationContext(
        last_result_ids=("UA-0001", "UA-0002"),
        shown_product_ids=("UA-0001", "UA-0002"),
    )

    updated = update_displayed_products(
        context,
        ("UA-0003", "UA-0004"),
    )

    assert updated.last_result_ids == ("UA-0003", "UA-0004")
    assert updated.shown_product_ids == (
        "UA-0001",
        "UA-0002",
        "UA-0003",
        "UA-0004",
    )


def test_refreshes_repeated_ids_to_latest_display_position() -> None:
    context = ConversationContext(
        shown_product_ids=("UA-0001", "UA-0002"),
    )

    updated = update_displayed_products(
        context,
        ("UA-0002", "UA-0003", "UA-0001"),
    )

    assert updated.last_result_ids == (
        "UA-0002",
        "UA-0003",
        "UA-0001",
    )
    assert updated.shown_product_ids == (
        "UA-0002",
        "UA-0003",
        "UA-0001",
    )


def test_preserves_other_conversation_context_fields() -> None:
    context = ConversationContext(
        previous_query="Show blue silk sarees",
        last_result_ids=("UA-0001",),
        shown_product_ids=("UA-0001",),
        selected_product_id="UA-0001",
    )

    updated = update_displayed_products(
        context,
        ("UA-0002",),
    )

    assert updated.previous_query == "Show blue silk sarees"
    assert updated.selected_product_id == "UA-0001"


def test_history_is_capped_at_maximum_size() -> None:
    existing_ids = tuple(
        f"UA-{number:04d}"
        for number in range(1, MAX_SHOWN_PRODUCT_IDS + 1)
    )

    context = ConversationContext(
        shown_product_ids=existing_ids,
    )

    updated = update_displayed_products(
        context,
        ("UA-0101", "UA-0102"),
    )

    assert len(updated.shown_product_ids) == MAX_SHOWN_PRODUCT_IDS
    assert updated.shown_product_ids[0] == "UA-0003"
    assert updated.shown_product_ids[-2:] == ("UA-0101", "UA-0102")


def test_repeated_products_refresh_history_order_without_duplicates() -> None:
    context = ConversationContext(
        shown_product_ids=(
            "UA-0001",
            "UA-0002",
            "UA-0003",
        ),
    )

    updated = update_displayed_products(
        context,
        ("UA-0002", "UA-0004"),
    )

    assert updated.shown_product_ids == (
        "UA-0001",
        "UA-0003",
        "UA-0002",
        "UA-0004",
    )

    assert len(updated.shown_product_ids) == len(
        set(updated.shown_product_ids)
    )