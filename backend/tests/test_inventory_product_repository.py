
from unittest.mock import MagicMock

from backend.app.database.product_repository import insert_products


def sample_product() -> dict:
    return {
        "product_id": "UA-TEST-001",
        "product_name": "Test Saree",
        "category": "Saree",
        "brand": "Urban Aanchol",
        "collection": "Test Collection",
        "fabric": "Cotton",
        "colour": "Red",
        "secondary_colour": None,
        "pattern": "Traditional",
        "border": "Gold",
        "price": 2500,
        "availability": "Available",
        "stock_quantity": 10,
        "description": "Test product",
        "product_url": None,
        "remarks": None,
        "additional_attributes": {},
        "launch_date": None,
        "created_at": None,
        "updated_at": None,
    }


def test_new_product_insert_includes_stock_quantity() -> None:
    connection = MagicMock()
    cursor = connection.cursor.return_value.__enter__.return_value

    product = sample_product()

    count = insert_products(connection, [product])

    assert count == 1

    executed_sql = cursor.execute.call_args.args[0]
    executed_parameters = cursor.execute.call_args.args[1]

    assert "stock_quantity" in executed_sql
    assert executed_parameters["stock_quantity"] == 10
    assert "availability" in executed_parameters


def test_existing_product_update_preserves_stock_and_availability() -> None:
    connection = MagicMock()
    cursor = connection.cursor.return_value.__enter__.return_value

    insert_products(connection, [sample_product()])

    executed_sql = cursor.execute.call_args.args[0]
    update_clause = executed_sql.split("ON CONFLICT")[1]

    assert "stock_quantity =" not in update_clause
    assert "availability =" not in update_clause


def test_repository_returns_number_of_processed_products() -> None:
    connection = MagicMock()

    products = [
        sample_product(),
        {**sample_product(), "product_id": "UA-TEST-002"},
        {**sample_product(), "product_id": "UA-TEST-003"},
    ]

    count = insert_products(connection, products)

    assert count == 3
    assert connection.cursor.return_value.__enter__.return_value.execute.call_count == 3
