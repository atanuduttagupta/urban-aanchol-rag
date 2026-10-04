from backend.app.recommendation.service import (
    RecommendationService,
)
from backend.app.retrieval.models import ProductResult


def product(
    product_id: str,
    score: float,
) -> ProductResult:
    return ProductResult(
        product_id=product_id,
        product_name=f"Product {product_id}",
        category="Saree",
        price=2500,
        availability="Available",
        score=score,
        retrieval_method="hybrid",
    )


def test_recommendation_service_scores_and_ranks_products():
    service = RecommendationService()

    products = [
        product("UA-0001", 0.02),
        product("UA-0002", 0.05),
        product("UA-0003", 0.03),
    ]

    recommendations = service.recommend(
        products,
        limit=3,
    )

    assert [
        item.product.product_id
        for item in recommendations
    ] == [
        "UA-0002",
        "UA-0003",
        "UA-0001",
    ]

    assert recommendations[0].recommendation_score == 0.05


def test_recommendation_service_applies_limit():
    service = RecommendationService()

    products = [
        product("UA-0001", 0.05),
        product("UA-0002", 0.04),
        product("UA-0003", 0.03),
    ]

    recommendations = service.recommend(
        products,
        limit=2,
    )

    assert len(recommendations) == 2

    assert [
        item.product.product_id
        for item in recommendations
    ] == [
        "UA-0001",
        "UA-0002",
    ]


def test_recommendation_service_preserves_explanation_signals():
    service = RecommendationService()

    products = [
        product("UA-0001", 0.05),
    ]

    recommendations = service.recommend(
        products,
        limit=1,
    )

    assert recommendations[0].explanation_signals == (
        "hybrid_retrieval_match",
        "availability:Available",
    )