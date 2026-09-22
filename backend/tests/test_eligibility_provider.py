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