
from dataclasses import dataclass, field, replace

from backend.app.conversation.context_history import (
    update_displayed_products,
)
from backend.app.conversation.models import ConversationContext
from backend.app.recommendation.models import Recommendation
from backend.app.recommendation.service import RecommendationService
from backend.app.retrieval.service import (
    RetrievalExecutionStatus,
    RetrievalService,
)


@dataclass(frozen=True)
class ConversationExecutionResult:
    """Customer-facing result of one conversation turn."""

    status: RetrievalExecutionStatus
    recommendations: tuple[Recommendation, ...] = ()
    context: ConversationContext = field(
        default_factory=ConversationContext,
    )
    reason: str | None = None


class ConversationService:
    """
    Coordinate product retrieval, recommendation and conversation history.

    Query understanding and retrieval remain the responsibility of
    RetrievalService. This service manages the customer conversation.
    """

    def __init__(
        self,
        retrieval_service: RetrievalService,
        recommendation_service: RecommendationService,
    ) -> None:
        self.retrieval_service = retrieval_service
        self.recommendation_service = recommendation_service

    def handle_message(
        self,
        message: str,
        context: ConversationContext,
        vocabulary: dict[str, list[str]],
    ) -> ConversationExecutionResult:
        """Process one customer message and return the updated conversation."""

        retrieval_result = self.retrieval_service.retrieve(
            query=message,
            context=context,
            vocabulary=vocabulary,
        )

        if retrieval_result.status != RetrievalExecutionStatus.COMPLETED:
            return ConversationExecutionResult(
                status=retrieval_result.status,
                context=context,
                reason=retrieval_result.reason,
            )

        recommendations = self.recommendation_service.recommend(
            products=retrieval_result.results,
            limit=len(retrieval_result.results),
        )

        displayed_ids = tuple(
            item.product.product_id
            for item in recommendations
        )

        updated_context = replace(
            context,
            previous_query=message,
        )

        updated_context = update_displayed_products(
            context=updated_context,
            displayed_product_ids=displayed_ids,
        )

        return ConversationExecutionResult(
            status=RetrievalExecutionStatus.COMPLETED,
            recommendations=tuple(recommendations),
            context=updated_context,
        )
