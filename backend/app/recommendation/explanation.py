from backend.app.recommendation.models import Recommendation


def explain_recommendation(
    recommendation: Recommendation,
) -> tuple[str, ...]:
    explanations: list[str] = []

    if "hybrid_retrieval_match" in recommendation.explanation_signals:
        explanations.append(
            "Matches your search criteria.",
        )

    for signal in recommendation.explanation_signals:
        if signal.startswith("availability:"):
            availability = signal.split(
                ":",
                1,
            )[1]

            explanations.append(
                f"Availability: {availability}.",
            )

    return tuple(explanations)