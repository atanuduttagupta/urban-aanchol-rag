from backend.app.conversation.models import ConversationContext


def test_default_conversation_context_is_empty() -> None:
    context = ConversationContext()

    assert context.previous_query is None
    assert context.last_result_ids == ()
    assert context.selected_product_id is None


def test_conversation_context_stores_retrieval_references() -> None:
    context = ConversationContext(
        previous_query="Show me blue silk sarees",
        last_result_ids=(
            "UA-0024",
            "UA-0018",
            "UA-0012",
        ),
        selected_product_id="UA-0024",
    )

    assert context.previous_query == "Show me blue silk sarees"
    assert context.last_result_ids == (
        "UA-0024",
        "UA-0018",
        "UA-0012",
    )
    assert context.selected_product_id == "UA-0024"
