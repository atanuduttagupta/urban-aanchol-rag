
import pytest

from backend.app.catalogue.validator import validate_product


def sample_product(stock_quantity):
    return {
        "product_id": "UA-TEST-001",
        "product_name": "Test Saree",
        "category": "Saree",
        "availability": "Available",
        "stock_quantity": stock_quantity,
        "price": 2500,
    }


@pytest.mark.parametrize("quantity", [0, 1, 10, 100])
def test_valid_stock_quantities_are_accepted(quantity):
    errors = validate_product(sample_product(quantity), 1)

    assert not any("stock_quantity" in error for error in errors)


@pytest.mark.parametrize(
    "quantity",
    [None, "", "   ", -1, -10, 1.5, -1.5, "abc", True, float("nan"), float("inf")],
)
def test_invalid_stock_quantities_are_rejected(quantity):
    errors = validate_product(sample_product(quantity), 1)

    assert any("stock_quantity" in error for error in errors)


def test_integral_float_stock_quantity_is_accepted():
    errors = validate_product(sample_product(5.0), 1)

    assert not any("stock_quantity" in error for error in errors)
