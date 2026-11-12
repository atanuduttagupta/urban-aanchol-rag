from unittest.mock import MagicMock

from backend.app.retrieval.eligibility_provider import (
    MetadataEligibilityProvider,
)
from backend.app.retrieval.models import RetrievalRequest


def test_metadata_eligibility_returns_product_ids():
    connection = MagicMock()

    cursor = connection.cursor.return_value.__enter__.return_value
    cursor.fetchall.return_value = [
        ("UA-0001",),
        ("UA-0002",),
        ("UA-0003",),
    ]

    provider = MetadataEligibilityProvider(connection)

    request = RetrievalRequest(
        query="blue saree",
        filters={
            "colour": "Blue",
            "availability": "Available",
        },
    )

    eligible_ids = provider.get_eligible_product_ids(request)

    assert eligible_ids == {
        "UA-0001",
        "UA-0002",
        "UA-0003",
    }

    cursor.execute.assert_called_once()


def test_metadata_eligibility_excludes_previously_displayed_products():
    connection = MagicMock()

    cursor = connection.cursor.return_value.__enter__.return_value
    cursor.fetchall.return_value = [
        ("UA-0003",),
    ]

    provider = MetadataEligibilityProvider(connection)

    request = RetrievalRequest(
        query="blue saree",
        filters={"colour": "Blue"},
        exclude_product_ids=("UA-0001", "UA-0002"),
    )

    eligible_ids = provider.get_eligible_product_ids(request)

    assert eligible_ids == {"UA-0003"}

    query, parameters = cursor.execute.call_args.args

    assert "p.colour ILIKE %s" in query
    assert "p.product_id NOT IN (%s, %s)" in query
    assert parameters == [
        "%Blue%",
        "UA-0001",
        "UA-0002",
    ]


def test_metadata_eligibility_without_exclusions():
    connection = MagicMock()

    cursor = connection.cursor.return_value.__enter__.return_value
    cursor.fetchall.return_value = [("UA-0001",)]

    provider = MetadataEligibilityProvider(connection)

    request = RetrievalRequest(
        query="red saree",
    )

    eligible_ids = provider.get_eligible_product_ids(request)

    assert eligible_ids == {"UA-0001"}

    query, parameters = cursor.execute.call_args.args

    assert "NOT IN" not in query
    assert parameters == []


def test_metadata_eligibility_excludes_sold_products_by_default():
    connection = MagicMock()

    cursor = connection.cursor.return_value.__enter__.return_value
    cursor.fetchall.return_value = [
        ("UA-0001",),
        ("UA-0002",),
    ]

    provider = MetadataEligibilityProvider(connection)

    request = RetrievalRequest(
        query="cotton sarees",
    )

    eligible_ids = provider.get_eligible_product_ids(request)

    assert eligible_ids == {"UA-0001", "UA-0002"}

    query, parameters = cursor.execute.call_args.args

    assert "p.availability = 'Available'" in query
    assert parameters == []