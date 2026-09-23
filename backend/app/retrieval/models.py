from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RetrievalIntent:
    """
    Structured interpretation of a customer's product-search request.

    `original_query` preserves the customer's original message.

    `semantic_query` contains the natural-language portion intended
    for keyword and semantic retrieval.

    `filters` contains structured constraints extracted from the request.

    `requested_limit` contains an explicit number requested by the
    customer, if one was provided. It is not a default display limit.
    """

    original_query: str
    semantic_query: str
    filters: dict[str, Any] | None = None
    requested_limit: int | None = None


@dataclass(frozen=True)
class RetrievalRequest:
    """
    User-facing retrieval request.

    `limit` is the maximum number of products returned to the user.
    It must not be used as an internal retrieval or fusion depth.
    """

    query: str
    limit: int = 5
    filters: dict[str, Any] | None = None


@dataclass(frozen=True)
class RetrievalPolicy:
    """
    Internal retrieval configuration.

    `fusion_window` controls how many candidates from each retrieval
    backend may participate in hybrid fusion.

    `rrf_k` controls the Reciprocal Rank Fusion calculation.

    These values are intentionally separate from RetrievalRequest.limit.
    """

    fusion_window: int
    rrf_k: int = 60


@dataclass(frozen=True)
class ProductCandidate:
    """
    Ranked candidate produced by an individual retrieval backend.
    """

    product_id: str
    product_name: str
    category: str | None = None
    price: Any = None
    availability: str | None = None
    score: float | None = None
    rank: int | None = None
    retrieval_method: str | None = None


@dataclass(frozen=True)
class ProductResult:
    """
    Product returned by the retrieval pipeline.
    """

    product_id: str
    product_name: str
    category: str | None = None
    price: Any = None
    availability: str | None = None
    score: float | None = None
    retrieval_method: str | None = None


@dataclass(frozen=True)
class KnowledgeResult:
    chunk_id: str
    document_id: str
    section_title: str | None = None
    chunk_text: str = ""
    score: float | None = None
    retrieval_method: str | None = None
