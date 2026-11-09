
from unittest.mock import MagicMock

from backend.app.conversation.models import ConversationContext
from backend.app.conversation.service import ConversationService
from backend.app.recommendation.service import RecommendationService
from backend.app.retrieval.models import ProductResult
from backend.app.retrieval.service import RetrievalExecutionStatus

VOCABULARY = {
    "colour": ["Red", "Blue"],
    "fabric": ["Silk", "Cotton"],
    "occasion": ["Wedding"],
}


def build_service():
    retrieval_service = MagicMock()
    recommendation_service = RecommendationService()

    service = ConversationService(
        retrieval_service=retrieval_service,
        recommendation_service=recommendation_service,
    )

    return service, retrieval_service


def test_successful_message_returns_ranked_recommendations():
    service, retrieval_service = build_service()

    retrieval_service.retrieve.return_value.status = (
        RetrievalExecutionStatus.COMPLETED
    )
    retrieval_service.retrieve.return_value.results = (
        ProductResult(
            product_id="UA-0001",
            product_name="Red Silk Saree",
            score=0.03,
        ),
        ProductResult(
            product_id="UA-0002",
            product_name="Blue Silk Saree",
            score=0.05,
        ),
    )

    result = service.handle_message(
        message="show me silk sarees",
        context=ConversationContext(),
        vocabulary=VOCABULARY,
    )

    assert result.status == RetrievalExecutionStatus.COMPLETED
    assert [
        item.product.product_id
        for item in result.recommendations
    ] == ["UA-0002", "UA-0001"]


def test_successful_message_updates_conversation_history():
    service, retrieval_service = build_service()

    retrieval_service.retrieve.return_value.status = (
        RetrievalExecutionStatus.COMPLETED
    )
    retrieval_service.retrieve.return_value.results = (
        ProductResult(
            product_id="UA-0001",
            product_name="Red Silk Saree",
            score=0.05,
        ),
    )

    result = service.handle_message(
        message="show me red silk sarees",
        context=ConversationContext(),
        vocabulary=VOCABULARY,
    )

    assert result.context.previous_query == "show me red silk sarees"
    assert result.context.last_result_ids == ("UA-0001",)
    assert result.context.shown_product_ids == ("UA-0001",)


def test_successful_message_preserves_previous_display_history():
    service, retrieval_service = build_service()

    retrieval_service.retrieve.return_value.status = (
        RetrievalExecutionStatus.COMPLETED
    )
    retrieval_service.retrieve.return_value.results = (
        ProductResult(
            product_id="UA-0003",
            product_name="Cotton Saree",
            score=0.05,
        ),
    )

    context = ConversationContext(
        previous_query="show me silk sarees",
        last_result_ids=("UA-0001", "UA-0002"),
        shown_product_ids=("UA-0001", "UA-0002"),
    )

    result = service.handle_message(
        message="show me cotton sarees",
        context=context,
        vocabulary=VOCABULARY,
    )

    assert result.context.last_result_ids == ("UA-0003",)
    assert result.context.shown_product_ids == (
        "UA-0001",
        "UA-0002",
        "UA-0003",
    )


def test_needs_llm_status_is_propagated():
    service, retrieval_service = build_service()

    retrieval_service.retrieve.return_value.status = (
        RetrievalExecutionStatus.NEEDS_LLM
    )
    retrieval_service.retrieve.return_value.reason = "llm_required"

    context = ConversationContext(
        previous_query="previous query",
    )

    result = service.handle_message(
        message="something similar",
        context=context,
        vocabulary=VOCABULARY,
    )

    assert result.status == RetrievalExecutionStatus.NEEDS_LLM
    assert result.reason == "llm_required"
    assert result.context == context
    assert result.recommendations == ()


def test_needs_clarification_status_is_propagated():
    service, retrieval_service = build_service()

    retrieval_service.retrieve.return_value.status = (
        RetrievalExecutionStatus.NEEDS_CLARIFICATION
    )
    retrieval_service.retrieve.return_value.reason = "ambiguous_query"

    result = service.handle_message(
        message="show me that one",
        context=ConversationContext(),
        vocabulary=VOCABULARY,
    )

    assert result.status == RetrievalExecutionStatus.NEEDS_CLARIFICATION
    assert result.reason == "ambiguous_query"
    assert result.recommendations == ()


def test_rejected_status_is_propagated():
    service, retrieval_service = build_service()

    retrieval_service.retrieve.return_value.status = (
        RetrievalExecutionStatus.REJECTED
    )
    retrieval_service.retrieve.return_value.reason = "unsafe_request"

    result = service.handle_message(
        message="invalid request",
        context=ConversationContext(),
        vocabulary=VOCABULARY,
    )

    assert result.status == RetrievalExecutionStatus.REJECTED
    assert result.reason == "unsafe_request"


def test_empty_results_update_query_without_displaying_products():
    service, retrieval_service = build_service()

    retrieval_service.retrieve.return_value.status = (
        RetrievalExecutionStatus.COMPLETED
    )
    retrieval_service.retrieve.return_value.results = ()

    context = ConversationContext(
        shown_product_ids=("UA-0001",),
    )

    result = service.handle_message(
        message="show me purple silk sarees",
        context=context,
        vocabulary=VOCABULARY,
    )

    assert result.status == RetrievalExecutionStatus.COMPLETED
    assert result.recommendations == ()
    assert result.context.previous_query == "show me purple silk sarees"
    assert result.context.last_result_ids == ()
    assert result.context.shown_product_ids == ("UA-0001",)
