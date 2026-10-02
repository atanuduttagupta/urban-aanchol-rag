from unittest.mock import MagicMock

from backend.app.conversation.models import ConversationContext
from backend.app.query_understanding.llm_models import LLMIntentProposal
from backend.app.retrieval.models import (
    ProductResult,
    RetrievalPolicy,
)
from backend.app.retrieval.service import (
    RetrievalExecutionStatus,
    RetrievalService,
)

VOCABULARY = {
    "colour": ["Red", "Blue"],
    "fabric": ["Silk", "Cotton"],
    "occasion": ["Wedding"],
}


def build_service(
    llm_resolver: MagicMock | None = None,
    ) -> tuple[RetrievalService, MagicMock, MagicMock]:
    hybrid_retriever = MagicMock()
    product_repository = MagicMock()

    service = RetrievalService(
        hybrid_retriever=hybrid_retriever,
        product_repository=product_repository,
        policy=RetrievalPolicy(
            fusion_window=10,
        ),
        default_limit=5,
        llm_resolver=llm_resolver,
    )

    return service, hybrid_retriever, product_repository


def test_normal_query_uses_hybrid_retriever() -> None:
    service, hybrid_retriever, product_repository = build_service()

    hybrid_retriever.retrieve.return_value = [
        ProductResult(
            product_id="UA-0001",
            product_name="Blue Silk Saree",
        ),
    ]

    result = service.retrieve(
        query="blue silk sarees",
        context=ConversationContext(),
        vocabulary=VOCABULARY,
    )

    assert result.status == RetrievalExecutionStatus.COMPLETED
    assert [item.product_id for item in result.results] == ["UA-0001"]

    hybrid_retriever.retrieve.assert_called_once()
    product_repository.get_product.assert_not_called()


def test_resolved_reference_uses_product_repository() -> None:
    service, hybrid_retriever, product_repository = build_service()

    product_repository.get_product.return_value = ProductResult(
        product_id="UA-0024",
        product_name="Selected Saree",
        retrieval_method="direct",
    )

    result = service.retrieve(
        query="show me the first one",
        context=ConversationContext(
            last_result_ids=("UA-0024", "UA-0018"),
        ),
        vocabulary=VOCABULARY,
    )

    assert result.status == RetrievalExecutionStatus.COMPLETED
    assert [item.product_id for item in result.results] == ["UA-0024"]

    product_repository.get_product.assert_called_once_with("UA-0024")
    hybrid_retriever.retrieve.assert_not_called()


def test_missing_resolved_product_needs_clarification() -> None:
    service, hybrid_retriever, product_repository = build_service()

    product_repository.get_product.return_value = None

    result = service.retrieve(
        query="show me the first one",
        context=ConversationContext(
            last_result_ids=("UA-0024",),
        ),
        vocabulary=VOCABULARY,
    )

    assert result.status == RetrievalExecutionStatus.NEEDS_CLARIFICATION
    assert result.reason == "resolved_product_not_found"

    hybrid_retriever.retrieve.assert_not_called()


def test_customer_requested_limit_is_sent_to_hybrid_retriever() -> None:
    service, hybrid_retriever, _ = build_service()

    hybrid_retriever.retrieve.return_value = []

    result = service.retrieve(
        query="show me 8 blue sarees",
        context=ConversationContext(),
        vocabulary=VOCABULARY,
    )

    assert result.status == RetrievalExecutionStatus.COMPLETED

    request = hybrid_retriever.retrieve.call_args.kwargs["request"]

    assert request.limit == 8
    assert request.query == "show me 8 blue sarees"


def test_ambiguous_query_uses_injected_llm_resolver() -> None:
    llm_resolver = MagicMock()

    llm_resolver.resolve.return_value = LLMIntentProposal(
        semantic_query="blue silk sarees",
    )

    service, hybrid_retriever, _ = build_service(
        llm_resolver=llm_resolver,
    )

    hybrid_retriever.retrieve.return_value = [
        ProductResult(
            product_id="UA-0001",
            product_name="Blue Silk Saree",
        ),
    ]

    result = service.retrieve(
        query="show me something cheaper than the one you showed earlier",
        context=ConversationContext(
            last_result_ids=("UA-0024",),
        ),
        vocabulary=VOCABULARY,
    )

    assert result.status == RetrievalExecutionStatus.COMPLETED
    assert [item.product_id for item in result.results] == ["UA-0001"]

    llm_resolver.resolve.assert_called_once()
    hybrid_retriever.retrieve.assert_called_once()