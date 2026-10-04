from backend.app.recommendation.models import Recommendation
from backend.app.retrieval.models import ProductResult


def test_recommendation_contains_product_and_score():
    product = ProductResult(
        product_id="UA-0001",
        product_name="Test Saree",
        category="Saree",
        price=2500,
        availability="Available",
        score=0.02,
        retrieval_method="hybrid",
    )

    recommendation = Recommendation(
        product=product,
        recommendation_score=0.95,
        explanation_signals=("strong_hybrid_relevance",),
    )

    assert recommendation.product.product_id == "UA-0001"
    assert recommendation.recommendation_score == 0.95
    assert recommendation.explanation_signals == (
        "strong_hybrid_relevance",
    )