from backend.app.conversation.models import ConversationContext
from backend.app.conversation.resolver import resolve_product_reference


def test_resolves_first_result() -> None:
    context = ConversationContext(
        last_result_ids=("UA-0024", "UA-0018", "UA-0012"),
    )

    result = resolve_product_reference(
        query="Show me something cheaper than the first one",
        context=context,
    )

    assert result.resolved is True
    assert result.resolved_product_id == "UA-0024"


def test_resolves_second_result() -> None:
    context = ConversationContext(
        last_result_ids=("UA-0024", "UA-0018", "UA-0012"),
    )

    result = resolve_product_reference(
        query="I like the second one",
        context=context,
    )

    assert result.resolved is True
    assert result.resolved_product_id == "UA-0018"


def test_resolves_selected_product() -> None:
    context = ConversationContext(
        last_result_ids=("UA-0024", "UA-0018"),
        selected_product_id="UA-0018",
    )

    result = resolve_product_reference(
        query="Show me this saree",
        context=context,
    )

    assert result.resolved is True
    assert result.resolved_product_id == "UA-0018"


def test_does_not_resolve_without_context() -> None:
    context = ConversationContext()

    result = resolve_product_reference(
        query="Show me the first one",
        context=context,
    )

    assert result.resolved is False
    assert result.resolved_product_id is None


def test_does_not_resolve_missing_second_result() -> None:
    context = ConversationContext(
        last_result_ids=("UA-0024",),
    )

    result = resolve_product_reference(
        query="Show me the second one",
        context=context,
    )

    assert result.resolved is False
    assert result.resolved_product_id is None


def test_does_not_invent_reference() -> None:
    context = ConversationContext(
        last_result_ids=("UA-0024", "UA-0018"),
    )

    result = resolve_product_reference(
        query="Show me something like my sister's saree",
        context=context,
    )

    assert result.resolved is False
    assert result.resolved_product_id is None
