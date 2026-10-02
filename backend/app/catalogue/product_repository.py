from typing import Protocol

from backend.app.retrieval.models import ProductResult


class ProductRepository(Protocol):
    """Contract for retrieving a current product by product ID."""

    def get_product(
        self,
        product_id: str,
    ) -> ProductResult | None: ...
