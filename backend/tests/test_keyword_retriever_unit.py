from unittest.mock import MagicMock

from backend.app.retrieval.keyword_retriever import KeywordProductRetriever
from backend.app.retrieval.models import (
    RetrievalPolicy,
    RetrievalRequest,
)


def test_keyword_retriever_excludes_previously_displayed_products():
    connection = MagicMock()

    cursor = connection.cursor.return_value.__enter__.return_value
    cursor.fetchall.return_value = [
        ("UA-0003", "Blue Silk Saree", "Saree", 2500, "Available", 0.85),
    ]

    retriever = KeywordProductRetriever(connection)

    request = RetrievalRequest(
        query="blue silk saree",
        filters={"colour": "Blue"},
        exclude_product_ids=("UA-0001", "UA-0002"),
    )

    policy = RetrievalPolicy(fusion_window=10, rrf_k=60)

    results = retriever.retrieve(request, policy)

    assert len(results) == 1
    assert results[0].product_id == "UA-0003"
    assert results[0].retrieval_method == "keyword"

    query, parameters = cursor.execute.call_args.args

    assert "p.colour ILIKE %s" in query
    assert "p.product_id NOT IN (%s, %s)" in query
    assert query.index("NOT IN") < query.index("LIMIT")

    assert parameters == [
        "blue silk saree",
        "blue silk saree",
        "%Blue%",
        "UA-0001",
        "UA-0002",
        10,
    ]


def test_keyword_retriever_without_exclusions():
    connection = MagicMock()

    cursor = connection.cursor.return_value.__enter__.return_value
    cursor.fetchall.return_value = []

    retriever = KeywordProductRetriever(connection)

    request = RetrievalRequest(query="red saree")

    policy = RetrievalPolicy(fusion_window=10, rrf_k=60)

    results = retriever.retrieve(request, policy)

    assert results == []

    query, parameters = cursor.execute.call_args.args

    assert "NOT IN" not in query

    assert parameters == [
        "red saree",
        "red saree",
        10,
    ]