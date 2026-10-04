from backend.app.recommendation.models import Recommendation
from backend.app.retrieval.models import ProductResult


def score_product(product: ProductResult) -> Recommendation:
    recommendation_score = product.score or 0.0

    explanation_signals = ["hybrid_retrieval_match"]

    if product.availability:
        explanation_signals.append(
            f"availability:{product.availability}",
        )

    return Recommendation(
        product=product,
        recommendation_score=recommendation_score,
        explanation_signals=tuple(explanation_signals),
    )