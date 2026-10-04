from dataclasses import dataclass

from backend.app.retrieval.models import ProductResult


@dataclass(frozen=True)
class Recommendation:
    product: ProductResult
    recommendation_score: float
    explanation_signals: tuple[str, ...] = ()