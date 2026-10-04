from collections.abc import Sequence

from backend.app.recommendation.models import Recommendation


def rank_recommendations(
    recommendations: Sequence[Recommendation],
    limit: int,
) -> list[Recommendation]:
    ranked = sorted(
        recommendations,
        key=lambda recommendation: (
            recommendation.recommendation_score,
            recommendation.product.product_id,
        ),
        reverse=True,
    )

    return ranked[:limit]