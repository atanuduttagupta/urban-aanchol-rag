from datetime import date
from decimal import Decimal

import pytest

from backend.app.orders.models import (
    CreateOrderRequest,
    OrderItemRequest,
)


@pytest.fixture
def valid_item():
    return OrderItemRequest(
        product_id="UA-0001",
        quantity=2,
    )


@pytest.fixture
def valid_request(valid_item):
    return CreateOrderRequest(
        customer_id=1,
        items=(valid_item,),
    )


def test_order_item_request_success(valid_item):
    assert valid_item.product_id == "UA-0001"
    assert valid_item.quantity == 2
    assert valid_item.line_discount == Decimal("0.00")


def test_order_item_request_with_discount():
    item = OrderItemRequest(
        product_id="UA-0001",
        quantity=2,
        line_discount=Decimal("100.00"),
        notes="Customer requested discount",
    )

    assert item.line_discount == Decimal("100.00")


@pytest.mark.parametrize(
    "product_id",
    ["", "   ", None, 123],
)
def test_order_item_request_invalid_product_id(product_id):
    with pytest.raises(ValueError):
        OrderItemRequest(product_id, 1)


@pytest.mark.parametrize("quantity", [0, -1, True, 1.5])
def test_order_item_request_invalid_quantity(quantity):
    with pytest.raises(ValueError):
        OrderItemRequest("UA-0001", quantity)


@pytest.mark.parametrize(
    "discount",
    [Decimal("-1"), Decimal("NaN"), Decimal("Infinity"), 100],
)
def test_order_item_request_invalid_discount(discount):
    with pytest.raises(ValueError):
        OrderItemRequest(
            product_id="UA-0001",
            quantity=1,
            line_discount=discount,
        )


def test_order_request_success(valid_request):
    assert valid_request.customer_id == 1
    assert len(valid_request.items) == 1
    assert valid_request.discount_amount == Decimal("0.00")


def test_order_request_multiple_products():
    request = CreateOrderRequest(
        customer_id=1,
        items=(
            OrderItemRequest("UA-0001", 2),
            OrderItemRequest("UA-0002", 1),
        ),
        discount_amount=Decimal("100.00"),
    )

    assert len(request.items) == 2


def test_order_request_rejects_duplicate_products():
    with pytest.raises(ValueError, match="Duplicate"):
        CreateOrderRequest(
            customer_id=1,
            items=(
                OrderItemRequest("UA-0001", 1),
                OrderItemRequest("UA-0001", 2),
            ),
        )


def test_order_request_rejects_duplicate_products_with_whitespace():
    with pytest.raises(ValueError, match="Duplicate"):
        CreateOrderRequest(
            customer_id=1,
            items=(
                OrderItemRequest("UA-0001", 1),
                OrderItemRequest(" UA-0001 ", 2),
            ),
        )


@pytest.mark.parametrize("customer_id", [0, -1, True, "1"])
def test_order_request_invalid_customer_id(customer_id):
    with pytest.raises(ValueError):
        CreateOrderRequest(
            customer_id=customer_id,
            items=(OrderItemRequest("UA-0001", 1),),
        )


@pytest.mark.parametrize(
    "items",
    [(), [], None],
)
def test_order_request_rejects_empty_or_invalid_items(items):
    with pytest.raises(ValueError):
        CreateOrderRequest(
            customer_id=1,
            items=items,
        )


def test_order_request_rejects_invalid_item_type():
    with pytest.raises(ValueError):
        CreateOrderRequest(
            customer_id=1,
            items=("UA-0001",),
        )


@pytest.mark.parametrize(
    "discount",
    [Decimal("-1"), Decimal("NaN"), Decimal("Infinity"), 100],
)
def test_order_request_invalid_order_discount(discount):
    with pytest.raises(ValueError):
        CreateOrderRequest(
            customer_id=1,
            items=(OrderItemRequest("UA-0001", 1),),
            discount_amount=discount,
        )


def test_order_request_shipping_address_override():
    request = CreateOrderRequest(
        customer_id=1,
        items=(OrderItemRequest("UA-0001", 1),),
        ship_to_contact_name="Test Customer",
        ship_to_phone="9999999999",
        ship_to_address="Different delivery address, Kolkata",
    )

    assert request.ship_to_contact_name == "Test Customer"
    assert request.ship_to_phone == "9999999999"
    assert request.ship_to_address == "Different delivery address, Kolkata"


def test_order_request_expected_delivery_date():
    expected_date = date(2026, 12, 25)

    request = CreateOrderRequest(
        customer_id=1,
        items=(OrderItemRequest("UA-0001", 1),),
        expected_delivery_date=expected_date,
    )

    assert request.expected_delivery_date == expected_date


def test_order_request_rejects_invalid_shipping_field():
    with pytest.raises(ValueError):
        CreateOrderRequest(
            customer_id=1,
            items=(OrderItemRequest("UA-0001", 1),),
            ship_to_phone=9999999999,
        )


def test_order_item_request_without_hold():
    item = OrderItemRequest(
        product_id="UA-0001",
        quantity=2,
    )

    assert item.hold_id is None


def test_order_item_request_with_hold():
    item = OrderItemRequest(
        product_id="UA-0001",
        quantity=2,
        hold_id=101,
    )

    assert item.hold_id == 101


@pytest.mark.parametrize(
    "hold_id",
    [0, -1, True, False, "101", 1.5],
)
def test_order_item_request_invalid_hold_id(hold_id):
    with pytest.raises(ValueError, match="hold_id"):
        OrderItemRequest(
            product_id="UA-0001",
            quantity=2,
            hold_id=hold_id,
        )


def test_order_request_rejects_reused_hold_id():
    with pytest.raises(ValueError, match="Duplicate hold IDs"):
        CreateOrderRequest(
            customer_id=1,
            items=(
                OrderItemRequest("UA-0001", 1, hold_id=101),
                OrderItemRequest("UA-0002", 1, hold_id=101),
            ),
        )


def test_order_item_request_normalizes_product_id():
    item = OrderItemRequest(
        product_id=" UA-0001 ",
        quantity=2,
    )

    assert item.product_id == "UA-0001"
