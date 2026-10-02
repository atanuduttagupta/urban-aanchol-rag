from dataclasses import dataclass
from enum import StrEnum

from backend.app.catalogue.product_repository import ProductRepository
from backend.app.conversation.models import ConversationContext
from backend.app.query_understanding.llm_interface import (
    LLMIntentResolver,
)
from backend.app.query_understanding.retrieval_orchestrator import (
    OrchestrationStatus,
    prepare_retrieval,
)
from backend.app.retrieval.hybrid_retriever import HybridProductRetriever
from backend.app.retrieval.models import (
    ProductResult,
    RetrievalPolicy,
    RetrievalRequest,
)


class RetrievalExecutionStatus(StrEnum):
    COMPLETED = "completed"
    NEEDS_LLM = "needs_llm"
    NEEDS_CLARIFICATION = "needs_clarification"
    REJECTED = "rejected"


@dataclass(frozen=True)
class RetrievalExecutionResult:
    """Result returned by the retrieval service."""

    status: RetrievalExecutionStatus
    results: tuple[ProductResult, ...] = ()
    reason: str | None = None


class RetrievalService:
    """
    Execute retrieval after query understanding and orchestration.

    This service coordinates retrieval components but does not contain
    query parsing, ranking, or LLM logic.
    """

    def __init__(
        self,
        hybrid_retriever: HybridProductRetriever,
        product_repository: ProductRepository,
        policy: RetrievalPolicy,
        default_limit: int = 5,
        llm_resolver: LLMIntentResolver | None = None,
    ) -> None:
        self.hybrid_retriever = hybrid_retriever
        self.product_repository = product_repository
        self.policy = policy
        self.default_limit = default_limit
        self.llm_resolver = llm_resolver

    def retrieve(
        self,
        query: str,
        context: ConversationContext,
        vocabulary: dict[str, list[str]],
    ) -> RetrievalExecutionResult:
        decision = prepare_retrieval(
            query=query,
            context=context,
            vocabulary=vocabulary,
            llm_resolver=self.llm_resolver,
        )

        if decision.status == OrchestrationStatus.NEEDS_LLM:
            return RetrievalExecutionResult(
                status=RetrievalExecutionStatus.NEEDS_LLM,
                reason=decision.reason,
            )

        if decision.status == OrchestrationStatus.NEEDS_CLARIFICATION:
            return RetrievalExecutionResult(
                status=RetrievalExecutionStatus.NEEDS_CLARIFICATION,
                reason=decision.reason,
            )

        if decision.status == OrchestrationStatus.REJECTED:
            return RetrievalExecutionResult(
                status=RetrievalExecutionStatus.REJECTED,
                reason=decision.reason,
            )

        if decision.resolved_product_id is not None:
            product = self.product_repository.get_product(
                decision.resolved_product_id,
            )

            if product is None:
                return RetrievalExecutionResult(
                    status=RetrievalExecutionStatus.NEEDS_CLARIFICATION,
                    reason="resolved_product_not_found",
                )

            return RetrievalExecutionResult(
                status=RetrievalExecutionStatus.COMPLETED,
                results=(product,),
            )

        if decision.intent is None:
            return RetrievalExecutionResult(
                status=RetrievalExecutionStatus.REJECTED,
                reason="retrieval_intent_missing",
            )

        resolved_limit = decision.intent.requested_limit or self.default_limit

        request = RetrievalRequest(
            query=decision.intent.semantic_query,
            limit=resolved_limit,
            filters=decision.intent.filters,
        )

        results = self.hybrid_retriever.retrieve(
            request=request,
            policy=self.policy,
        )

        return RetrievalExecutionResult(
            status=RetrievalExecutionStatus.COMPLETED,
            results=tuple(results),
        )
