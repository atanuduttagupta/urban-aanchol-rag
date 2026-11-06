from unittest.mock import MagicMock

from backend.app.retrieval.models import (
    ProductResult,
    RetrievalPolicy,
    RetrievalRequest,
)
from backend.app.retrieval.semantic_retriever import SemanticProductRetriever


def test_semantic_retriever_forwards_product_exclusions(monkeypatch):
    connection = MagicMock()
    embedding_generator = MagicMock()
    embedding_generator.generate.return_value = [0.1, 0.2, 0.3]

    search_mock = MagicMock(
        return_value=[
            {
                "product_id": "UA-0003",
                "product_name": "Blue Silk Saree",
                "category": "Saree",
                "price": 2500,
                "availability": "Available",
                "similarity": 0.92,
            }
        ]
    )

    monkeypatch.setattr(
        "backend.app.retrieval.semantic_retriever.search_similar_products",
        search_mock,
    )

    retriever = SemanticProductRetriever(
        connection=connection,
        embedding_generator=embedding_generator,
    )

    request = RetrievalRequest(
        query="blue silk sarees",
        limit=5,
        filters={"colour": "Blue"},
        exclude_product_ids=("UA-0001", "UA-0002"),
    )

    policy = RetrievalPolicy(
        fusion_window=10,
        rrf_k=60,
    )

    results = retriever.retrieve(request, policy)

    assert len(results) == 1
    assert isinstance(results[0], ProductResult)
    assert results[0].product_id == "UA-0003"

    search_mock.assert_called_once_with(
        connection,
        [0.1, 0.2, 0.3],
        limit=10,
        filters={"colour": "Blue"},
        exclude_product_ids=("UA-0001", "UA-0002"),
    )