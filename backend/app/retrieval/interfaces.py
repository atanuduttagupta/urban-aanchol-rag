from typing import Protocol

from backend.app.retrieval.models import (
    KnowledgeResult,
    ProductResult,
    RetrievalRequest,
)


class ProductRetriever(Protocol):
    """Contract for product retrieval implementations."""

    def retrieve(
        self,
        request: RetrievalRequest,
    ) -> list[ProductResult]:
        ...


class KnowledgeRetriever(Protocol):
    """Contract for knowledge retrieval implementations."""

    def retrieve(
        self,
        request: RetrievalRequest,
    ) -> list[KnowledgeResult]:
        ...