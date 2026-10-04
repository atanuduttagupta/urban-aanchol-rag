from backend.app.recommendation.scorer import score_product
from backend.app.retrieval.models import ProductResult


def test_score_product_preserves_hybrid_score():
    product = ProductResult(
        product_id="UA-0001",
        product_name="Test Saree",
        category="Saree",
        price=2500,
        availability="Available",
        score=0.032,
        retrieval_method="hybrid",
    )

    recommendation = score_product(product)

    assert recommendation.product.product_id == "UA-0001"
    assert recommendation.recommendation_score == 0.032
    assert recommendation.explanation_signals == (
        "hybrid_retrieval_match",
        "availability:Available",
    )


def test_score_product_handles_missing_score():
    product = ProductResult(
        product_id="UA-0002",
        product_name="Another Saree",
        category="Saree",
        price=3000,
        availability="Available",
        score=None,
        retrieval_method="hybrid",
    )

    recommendation = score_product(product)

    assert recommendation.recommendation_score == 0.0