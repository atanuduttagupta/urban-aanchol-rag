from unittest.mock import MagicMock

from backend.app.recommendation.service import RecommendationService
from backend.app.retrieval.models import ProductResult


def test_retrieval_results_can_flow_into_recommendation_service():
    hybrid_retriever = MagicMock()

    hybrid_retriever.retrieve.return_value = [
        ProductResult(
            product_id="UA-0001",
            product_name="Blue Silk Saree",
            category="Saree",
            price=2500,
            availability="Available",
            score=0.02,
            retrieval_method="hybrid",
        ),
        ProductResult(
            product_id="UA-0002",
            product_name="Red Silk Saree",
            category="Saree",
            price=2800,
            availability="Available",
            score=0.05,
            retrieval_method="hybrid",
        ),
        ProductResult(
            product_id="UA-0003",
            product_name="Cotton Saree",
            category="Saree",
            price=1800,
            availability="Available",
            score=0.03,
            retrieval_method="hybrid",
        ),
    ]

    retrieval_results = hybrid_retriever.retrieve()

    recommendation_service = RecommendationService()

    recommendations = recommendation_service.recommend(
        products=retrieval_results,
        limit=2,
    )

    assert [
        item.product.product_id
        for item in recommendations
    ] == [
        "UA-0002",
        "UA-0003",
    ]

    assert recommendations[0].recommendation_score == 0.05
    assert recommendations[1].recommendation_score == 0.03