from backend.app.conversation.follow_up_detector import (
    detect_follow_up_intent,
)
from backend.app.conversation.follow_up_models import (
    FollowUpIntentType,
)


def test_detects_reference_to_second_result():
    intent = detect_follow_up_intent("What about the second one?")

    assert intent is not None
    assert intent.intent_type == FollowUpIntentType.REFERENCE
    assert intent.reference_position == 2


def test_detects_more_results_with_requested_count():
    intent = detect_follow_up_intent("Show me 3 more")

    assert intent is not None
    assert intent.intent_type == FollowUpIntentType.MORE_RESULTS
    assert intent.requested_limit == 3


def test_detects_change_limit():
    intent = detect_follow_up_intent("Show me 5 instead")

    assert intent is not None
    assert intent.intent_type == FollowUpIntentType.CHANGE_LIMIT
    assert intent.requested_limit == 5


def test_detects_cheaper_follow_up():
    intent = detect_follow_up_intent("Show something cheaper")

    assert intent is not None
    assert intent.intent_type == FollowUpIntentType.REFINE_PRICE


def test_detects_attribute_refinement():
    intent = detect_follow_up_intent("Same style in red")

    assert intent is not None
    assert intent.intent_type == FollowUpIntentType.REFINE_ATTRIBUTE


def test_detects_similar_products():
    intent = detect_follow_up_intent("Show similar sarees")

    assert intent is not None
    assert intent.intent_type == FollowUpIntentType.SIMILAR_TO


def test_unrecognized_query_returns_none():
    intent = detect_follow_up_intent(
        "I am looking for a cotton saree for a wedding"
    )

    assert intent is None


def test_empty_query_returns_none():
    assert detect_follow_up_intent("") is None


def test_zero_count_is_not_accepted():
    assert detect_follow_up_intent("Show me 0 more") is None


def test_detects_reference_to_first_result():
    intent = detect_follow_up_intent("What about the first one?")

    assert intent is not None
    assert intent.intent_type == FollowUpIntentType.REFERENCE
    assert intent.reference_position == 1


def test_detects_reference_to_third_result():
    intent = detect_follow_up_intent("Show me the third one")

    assert intent is not None
    assert intent.intent_type == FollowUpIntentType.REFERENCE
    assert intent.reference_position == 3


def test_detects_ten_more_results():
    intent = detect_follow_up_intent("Show me 10 more")

    assert intent is not None
    assert intent.intent_type == FollowUpIntentType.MORE_RESULTS
    assert intent.requested_limit == 10


def test_new_red_saree_request_is_not_attribute_follow_up():
    intent = detect_follow_up_intent("I want a red saree")

    assert intent is None


def test_new_wedding_saree_request_is_not_follow_up():
    intent = detect_follow_up_intent("Show me a red saree for a wedding")

    assert intent is None


def test_combined_price_and_reference_query_is_not_silently_simplified():
    intent = detect_follow_up_intent(
        "Something cheaper than the second one"
    )

    assert intent is None
