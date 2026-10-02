from unittest.mock import MagicMock

from backend.app.catalogue.postgres_product_repository import (
    PostgresProductRepository,
)


def test_get_product_returns_product() -> None:
    connection = MagicMock()
    cursor = connection.cursor.return_value.__enter__.return_value

    cursor.fetchone.return_value = (
        "UA-0024",
        "Test Saree",
        "Saree",
        2999,
        "Available",
    )

    repository = PostgresProductRepository(connection)

    result = repository.get_product("UA-0024")

    assert result is not None
    assert result.product_id == "UA-0024"
    assert result.product_name == "Test Saree"
    assert result.category == "Saree"
    assert result.price == 2999
    assert result.availability == "Available"
    assert result.retrieval_method == "direct"


def test_get_product_returns_none_when_not_found() -> None:
    connection = MagicMock()
    cursor = connection.cursor.return_value.__enter__.return_value

    cursor.fetchone.return_value = None

    repository = PostgresProductRepository(connection)

    result = repository.get_product("UA-9999")

    assert result is None
