from collections.abc import Sequence

from backend.app.recommendation.models import Recommendation
from backend.app.recommendation.ranker import rank_recommendations
from backend.app.recommendation.scorer import score_product
from backend.app.retrieval.models import ProductResult


class RecommendationService:
    """Rank retrieved products into grounded recommendations."""

    def recommend(
        self,
        products: Sequence[ProductResult],
        limit: int,
    ) -> list[Recommendation]:
        recommendations = [
            score_product(product)
            for product in products
        ]

        return rank_recommendations(
            recommendations,
            limit=limit,
        )