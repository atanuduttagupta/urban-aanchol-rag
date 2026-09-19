from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RetrievalRequest:
    query: str
    limit: int = 5
    filters: dict[str, Any] | None = None


@dataclass(frozen=True)
class ProductResult:
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