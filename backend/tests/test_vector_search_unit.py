from unittest.mock import MagicMock

from backend.app.database.embedding_config import MODEL_NAME, MODEL_VERSION
from backend.app.database.vector_search import search_similar_products


def test_vector_search_excludes_previously_displayed_products():
    connection = MagicMock()

    cursor = connection.cursor.return_value.__enter__.return_value
    cursor.fetchall.return_value = [
        ("UA-0003", "Blue Silk Saree", "Saree", 2500, "Available", 0.92),
    ]

    results = search_similar_products(
        connection=connection,
        query_embedding=[0.1, 0.2, 0.3],
        limit=5,
        filters={"colour": "Blue"},
        exclude_product_ids=("UA-0001", "UA-0002"),
    )

    assert len(results) == 1
    assert results[0]["product_id"] == "UA-0003"

    query, parameters = cursor.execute.call_args.args

    assert "p.colour ILIKE %s" in query
    assert "p.product_id NOT IN (%s, %s)" in query
    assert query.index("NOT IN") < query.index("LIMIT")

    assert parameters == [
        [0.1, 0.2, 0.3],
        MODEL_NAME,
        MODEL_VERSION,
        "%Blue%",
        "UA-0001",
        "UA-0002",
        [0.1, 0.2, 0.3],
        5,
    ]


def test_vector_search_without_exclusions():
    connection = MagicMock()

    cursor = connection.cursor.return_value.__enter__.return_value
    cursor.fetchall.return_value = []

    results = search_similar_products(
        connection=connection,
        query_embedding=[0.1, 0.2, 0.3],
        limit=5,
    )

    assert results == []

    query, parameters = cursor.execute.call_args.args

    assert "NOT IN" not in query

    assert parameters == [
        [0.1, 0.2, 0.3],
        MODEL_NAME,
        MODEL_VERSION,
        [0.1, 0.2, 0.3],
        5,
    ]