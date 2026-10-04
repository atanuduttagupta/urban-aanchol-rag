from backend.app.recommendation.models import Recommendation
from backend.app.recommendation.ranker import rank_recommendations
from backend.app.retrieval.models import ProductResult


def recommendation(
    product_id: str,
    score: float,
) -> Recommendation:
    product = ProductResult(
        product_id=product_id,
        product_name=f"Product {product_id}",
        category="Saree",
        price=2500,
        availability="Available",
        score=score,
        retrieval_method="hybrid",
    )

    return Recommendation(
        product=product,
        recommendation_score=score,
    )


def test_rank_recommendations_orders_by_score():
    recommendations = [
        recommendation("UA-0001", 0.02),
        recommendation("UA-0002", 0.05),
        recommendation("UA-0003", 0.03),
    ]

    ranked = rank_recommendations(
        recommendations,
        limit=3,
    )

    assert [
        item.product.product_id
        for item in ranked
    ] == [
        "UA-0002",
        "UA-0003",
        "UA-0001",
    ]


def test_rank_recommendations_applies_limit():
    recommendations = [
        recommendation("UA-0001", 0.05),
        recommendation("UA-0002", 0.04),
        recommendation("UA-0003", 0.03),
    ]

    ranked = rank_recommendations(
        recommendations,
        limit=2,
    )

    assert len(ranked) == 2

    assert [
        item.product.product_id
        for item in ranked
    ] == [
        "UA-0001",
        "UA-0002",
    ]


def test_rank_recommendations_uses_product_id_as_tie_breaker():
    recommendations = [
        recommendation("UA-0003", 0.05),
        recommendation("UA-0001", 0.05),
        recommendation("UA-0002", 0.05),
    ]

    ranked = rank_recommendations(
        recommendations,
        limit=3,
    )

    assert [
        item.product.product_id
        for item in ranked
    ] == [
        "UA-0003",
        "UA-0002",
        "UA-0001",
    ]