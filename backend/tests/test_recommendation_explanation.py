from backend.app.recommendation.explanation import (
    explain_recommendation,
)
from backend.app.recommendation.models import Recommendation
from backend.app.retrieval.models import ProductResult


def test_explanation_uses_grounded_hybrid_signal():
    product = ProductResult(
        product_id="UA-0001",
        product_name="Test Saree",
        category="Saree",
        price=2500,
        availability="Available",
        score=0.03,
        retrieval_method="hybrid",
    )

    recommendation = Recommendation(
        product=product,
        recommendation_score=0.03,
        explanation_signals=(
            "hybrid_retrieval_match",
            "availability:Available",
        ),
    )

    explanations = explain_recommendation(
        recommendation,
    )

    assert explanations == (
        "Matches your search criteria.",
        "Availability: Available.",
    )


def test_explanation_does_not_invent_unknown_product_attributes():
    product = ProductResult(
        product_id="UA-0002",
        product_name="Another Saree",
        category="Saree",
        price=3000,
        availability="Available",
        score=0.02,
        retrieval_method="hybrid",
    )

    recommendation = Recommendation(
        product=product,
        recommendation_score=0.02,
        explanation_signals=(
            "hybrid_retrieval_match",
        ),
    )

    explanations = explain_recommendation(
        recommendation,
    )

    assert explanations == (
        "Matches your search criteria.",
    )

    assert not any(
        "wedding" in explanation.casefold()
        for explanation in explanations
    )