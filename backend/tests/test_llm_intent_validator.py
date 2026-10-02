from backend.app.conversation.models import ConversationContext
from backend.app.query_understanding.llm_intent_validator import (
    validate_llm_intent_proposal,
)
from backend.app.query_understanding.llm_models import (
    LLMIntentProposal,
)

TEST_VOCABULARY = {
    "colour": ["Red", "Blue", "Green"],
    "fabric": ["Silk", "Cotton"],
    "occasion": ["Wedding", "Durga Puja"],
    "style": ["Traditional", "Elegant"],
}


def test_valid_catalogue_values_are_accepted() -> None:
    proposal = LLMIntentProposal(
        filters={
            "colour": "Blue",
            "fabric": "Silk",
            "occasion": "Wedding",
        },
        requested_limit=5,
    )

    result = validate_llm_intent_proposal(
        proposal=proposal,
        vocabulary=TEST_VOCABULARY,
        context=ConversationContext(),
    )

    assert result.valid is True
    assert result.errors == ()


def test_unknown_catalogue_value_is_rejected() -> None:
    proposal = LLMIntentProposal(
        filters={
            "colour": "Unicorn Pink",
        },
    )

    result = validate_llm_intent_proposal(
        proposal=proposal,
        vocabulary=TEST_VOCABULARY,
        context=ConversationContext(),
    )

    assert result.valid is False
    assert "unknown_catalogue_value:colour:Unicorn Pink" in result.errors


def test_unsupported_filter_is_rejected() -> None:
    proposal = LLMIntentProposal(
        filters={
            "saree_quality": "premium",
        },
    )

    result = validate_llm_intent_proposal(
        proposal=proposal,
        vocabulary=TEST_VOCABULARY,
        context=ConversationContext(),
    )

    assert result.valid is False
    assert "unsupported_filter:saree_quality" in result.errors


def test_invalid_requested_limit_is_rejected() -> None:
    proposal = LLMIntentProposal(
        requested_limit=0,
    )

    result = validate_llm_intent_proposal(
        proposal=proposal,
        vocabulary=TEST_VOCABULARY,
        context=ConversationContext(),
    )

    assert result.valid is False
    assert "invalid_requested_limit" in result.errors


def test_negative_price_is_rejected() -> None:
    proposal = LLMIntentProposal(
        filters={
            "min_price": -100,
        },
    )

    result = validate_llm_intent_proposal(
        proposal=proposal,
        vocabulary=TEST_VOCABULARY,
        context=ConversationContext(),
    )

    assert result.valid is False
    assert "invalid_price:min_price" in result.errors


def test_resolved_product_must_be_from_trusted_context() -> None:
    proposal = LLMIntentProposal(
        resolved_product_id="UA-9999",
    )

    context = ConversationContext(
        last_result_ids=("UA-0024", "UA-0018"),
    )

    result = validate_llm_intent_proposal(
        proposal=proposal,
        vocabulary=TEST_VOCABULARY,
        context=context,
    )

    assert result.valid is False
    assert "untrusted_resolved_product" in result.errors


def test_resolved_product_from_context_is_accepted() -> None:
    proposal = LLMIntentProposal(
        resolved_product_id="UA-0024",
    )

    context = ConversationContext(
        last_result_ids=("UA-0024", "UA-0018"),
    )

    result = validate_llm_intent_proposal(
        proposal=proposal,
        vocabulary=TEST_VOCABULARY,
        context=context,
    )

    assert result.valid is True
    assert result.errors == ()


def test_selected_product_is_trusted() -> None:
    proposal = LLMIntentProposal(
        resolved_product_id="UA-0018",
    )

    context = ConversationContext(
        selected_product_id="UA-0018",
    )

    result = validate_llm_intent_proposal(
        proposal=proposal,
        vocabulary=TEST_VOCABULARY,
        context=context,
    )

    assert result.valid is True
