from typing import Protocol

from backend.app.retrieval.models import (
    KnowledgeResult,
    ProductResult,
    RetrievalPolicy,
    RetrievalRequest,
)


class EligibilityProvider(Protocol):
    """Contract for determining which products are eligible for retrieval."""

    def get_eligible_product_ids(
        self,
        request: RetrievalRequest,
    ) -> set[str]:
        ...


class ProductRetriever(Protocol):
    """Contract for ranked product retrieval."""

    def retrieve(
        self,
        request: RetrievalRequest,
        policy: RetrievalPolicy,
    ) -> list[ProductResult]:
        ...


class KnowledgeRetriever(Protocol):
    """Contract for knowledge retrieval."""

    def retrieve(
        self,
        request: RetrievalRequest,
        policy: RetrievalPolicy,
    ) -> list[KnowledgeResult]:
        ...