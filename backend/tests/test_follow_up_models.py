from backend.app.conversation.follow_up_models import (
    FollowUpIntent,
    FollowUpIntentType,
)


def test_reference_intent():
    intent = FollowUpIntent(
        intent_type=FollowUpIntentType.REFERENCE,
        reference_position=2,
    )

    assert intent.intent_type == FollowUpIntentType.REFERENCE
    assert intent.reference_position == 2


def test_more_results_intent():
    intent = FollowUpIntent(
        intent_type=FollowUpIntentType.MORE_RESULTS,
        requested_limit=3,
    )

    assert intent.intent_type == FollowUpIntentType.MORE_RESULTS
    assert intent.requested_limit == 3


def test_change_limit_intent():
    intent = FollowUpIntent(
        intent_type=FollowUpIntentType.CHANGE_LIMIT,
        requested_limit=5,
    )

    assert intent.intent_type == FollowUpIntentType.CHANGE_LIMIT
    assert intent.requested_limit == 5


def test_refine_price_intent():
    intent = FollowUpIntent(
        intent_type=FollowUpIntentType.REFINE_PRICE,
        semantic_query="something cheaper",
    )

    assert intent.intent_type == FollowUpIntentType.REFINE_PRICE
    assert intent.semantic_query == "something cheaper"


def test_refine_attribute_intent():
    intent = FollowUpIntent(
        intent_type=FollowUpIntentType.REFINE_ATTRIBUTE,
        semantic_query="same style in red",
    )

    assert intent.intent_type == FollowUpIntentType.REFINE_ATTRIBUTE
    assert intent.semantic_query == "same style in red"


def test_similar_to_intent():
    intent = FollowUpIntent(
        intent_type=FollowUpIntentType.SIMILAR_TO,
        semantic_query="similar sarees",
    )

    assert intent.intent_type == FollowUpIntentType.SIMILAR_TO
    assert intent.semantic_query == "similar sarees"


def test_optional_fields_default_to_none():
    intent = FollowUpIntent(
        intent_type=FollowUpIntentType.REFERENCE,
    )

    assert intent.requested_limit is None
    assert intent.reference_position is None
    assert intent.semantic_query is None


def test_follow_up_intent_is_immutable():
    intent = FollowUpIntent(
        intent_type=FollowUpIntentType.MORE_RESULTS,
        requested_limit=3,
    )

    try:
        intent.requested_limit = 5
    except AttributeError:
        pass
    else:
        raise AssertionError("FollowUpIntent should be immutable")