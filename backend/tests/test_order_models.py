from dataclasses import FrozenInstanceError
from datetime import UTC, date, datetime
from decimal import Decimal

import pytest

from backend.app.orders.models import (
    Order,
    OrderCreationResult,
    OrderItem,
    OrderStatus,
)


@pytest.fixture
def now():
    return datetime.now(UTC)


@pytest.fixture
def order_data(now):
    return {
        "order_id": 1,
        "order_number": "UA-ORD-000001",
        "customer_id": 1,
        "order_date": now,
        "order_status": OrderStatus.PLACED,
        "subtotal": Decimal("5000.00"),
        "discount_amount": Decimal("200.00"),
        "delivery_charge": Decimal("100.00"),
        "grand_total": Decimal("4900.00"),
        "created_at": now,
        "updated_at": now,
    }


@pytest.fixture
def order_item_data(now):
    return {
        "order_item_id": 1,
        "order_id": 1,
        "product_id": "UA-0001",
        "product_name": "Bengal Cotton Saree",
        "category": "Saree",
        "quantity": 2,
        "unit_price": Decimal("2500.00"),
        "line_discount": Decimal("100.00"),
        "line_total": Decimal("4900.00"),
        "created_at": now,
        "updated_at": now,
    }


def test_create_valid_order(order_data):
    order = Order(**order_data)

    assert order.order_id == 1
    assert order.order_status == OrderStatus.PLACED
    assert order.grand_total == Decimal("4900.00")
    assert order.currency == "INR"


def test_create_valid_order_item(order_item_data):
    item = OrderItem(**order_item_data)

    assert item.product_id == "UA-0001"
    assert item.quantity == 2
    assert item.line_total == Decimal("4900.00")


@pytest.mark.parametrize(
    "field,value",
    [
        ("order_id", 0),
        ("order_id", -1),
        ("order_id", True),
        ("customer_id", 0),
        ("customer_id", -1),
        ("customer_id", True),
    ],
)
def test_order_rejects_invalid_ids(order_data, field, value):
    order_data[field] = value

    with pytest.raises(ValueError):
        Order(**order_data)


def test_order_rejects_empty_order_number(order_data):
    order_data["order_number"] = " "

    with pytest.raises(ValueError, match="order_number"):
        Order(**order_data)


def test_order_rejects_invalid_status(order_data):
    order_data["order_status"] = "Placed"

    with pytest.raises(ValueError, match="order_status"):
        Order(**order_data)


@pytest.mark.parametrize(
    "field,value",
    [
        ("subtotal", Decimal("-1.00")),
        ("discount_amount", Decimal("-1.00")),
        ("delivery_charge", Decimal("-1.00")),
        ("grand_total", Decimal("-1.00")),
        ("subtotal", 100.0),
        ("grand_total", float("nan")),
        ("delivery_charge", Decimal("Infinity")),
    ],
)
def test_order_rejects_invalid_money(order_data, field, value):
    order_data[field] = value

    with pytest.raises(ValueError):
        Order(**order_data)


def test_order_rejects_discount_greater_than_subtotal(order_data):
    order_data["discount_amount"] = Decimal("5001.00")

    with pytest.raises(ValueError, match="discount_amount"):
        Order(**order_data)


def test_order_rejects_incorrect_grand_total(order_data):
    order_data["grand_total"] = Decimal("5000.00")

    with pytest.raises(ValueError, match="grand_total"):
        Order(**order_data)


@pytest.mark.parametrize("currency", ["inr", "IN", "INR1", "123", ""])
def test_order_rejects_invalid_currency(order_data, currency):
    order_data["currency"] = currency

    with pytest.raises(ValueError, match="currency"):
        Order(**order_data)


def test_order_accepts_complete_invoice_details(order_data):
    order_data.update(
        {
            "invoice_number": "UA-INV-000001",
            "invoice_date": date(2026, 11, 18),
            "invoice_issued_at": datetime.now(UTC),
        }
    )

    order = Order(**order_data)

    assert order.invoice_number == "UA-INV-000001"


@pytest.mark.parametrize(
    "invoice_values",
    [
        ("UA-INV-000001", None, None),
        (None, date(2026, 11, 18), None),
        (None, None, datetime.now(UTC)),
        ("UA-INV-000001", date(2026, 11, 18), None),
    ],
)
def test_order_rejects_incomplete_invoice_details(order_data, invoice_values):
    (
        order_data["invoice_number"],
        order_data["invoice_date"],
        order_data["invoice_issued_at"],
    ) = invoice_values

    with pytest.raises(ValueError, match="Invoice fields"):
        Order(**order_data)


def test_order_rejects_empty_invoice_number(order_data):
    order_data.update(
        {
            "invoice_number": " ",
            "invoice_date": date(2026, 11, 18),
            "invoice_issued_at": datetime.now(UTC),
        }
    )

    with pytest.raises(ValueError, match="invoice_number"):
        Order(**order_data)


def test_order_rejects_invalid_order_date(order_data):
    order_data["order_date"] = "2026-11-18"

    with pytest.raises(ValueError, match="order_date"):
        Order(**order_data)


def test_order_rejects_invalid_expected_delivery_date(order_data):
    order_data["expected_delivery_date"] = datetime.now(UTC)

    with pytest.raises(ValueError, match="expected_delivery_date"):
        Order(**order_data)


def test_order_rejects_invalid_invoice_date(order_data):
    order_data.update(
        {
            "invoice_number": "UA-INV-000001",
            "invoice_date": "2026-11-18",
            "invoice_issued_at": datetime.now(UTC),
        }
    )

    with pytest.raises(ValueError, match="invoice_date"):
        Order(**order_data)


def test_order_is_immutable(order_data):
    order = Order(**order_data)

    with pytest.raises(FrozenInstanceError):
        order.grand_total = Decimal("100.00")


@pytest.mark.parametrize(
    "field,value",
    [
        ("order_item_id", 0),
        ("order_item_id", True),
        ("order_id", -1),
        ("quantity", 0),
        ("quantity", -1),
        ("quantity", True),
    ],
)
def test_order_item_rejects_invalid_ids_and_quantity(order_item_data, field, value):
    order_item_data[field] = value

    with pytest.raises(ValueError):
        OrderItem(**order_item_data)


@pytest.mark.parametrize(
    "field,value",
    [
        ("product_id", ""),
        ("product_name", " "),
        ("category", ""),
    ],
)
def test_order_item_rejects_empty_product_fields(order_item_data, field, value):
    order_item_data[field] = value

    with pytest.raises(ValueError):
        OrderItem(**order_item_data)


@pytest.mark.parametrize(
    "field,value",
    [
        ("unit_price", Decimal("-1.00")),
        ("line_discount", Decimal("-1.00")),
        ("line_total", Decimal("-1.00")),
        ("unit_price", 2500.0),
        ("line_total", Decimal("NaN")),
    ],
)
def test_order_item_rejects_invalid_money(order_item_data, field, value):
    order_item_data[field] = value

    with pytest.raises(ValueError):
        OrderItem(**order_item_data)


def test_order_item_rejects_discount_greater_than_gross_amount(
    order_item_data,
):
    order_item_data["line_discount"] = Decimal("5001.00")

    with pytest.raises(ValueError, match="line_discount"):
        OrderItem(**order_item_data)


def test_order_item_rejects_incorrect_line_total(order_item_data):
    order_item_data["line_total"] = Decimal("5000.00")

    with pytest.raises(ValueError, match="line_total"):
        OrderItem(**order_item_data)


def test_order_item_rejects_invalid_created_at(order_item_data):
    order_item_data["created_at"] = "2026-11-18"

    with pytest.raises(ValueError, match="created_at"):
        OrderItem(**order_item_data)


def test_order_item_is_immutable(order_item_data):
    item = OrderItem(**order_item_data)

    with pytest.raises(FrozenInstanceError):
        item.quantity = 5


def test_create_valid_order_creation_result(order_data, order_item_data):
    order = Order(**order_data)
    item = OrderItem(**order_item_data)

    result = OrderCreationResult(
        order=order,
        items=(item,),
    )

    assert result.order == order
    assert result.items == (item,)
    assert len(result.items) == 1


def test_order_creation_result_is_immutable(order_data, order_item_data):
    order = Order(**order_data)
    item = OrderItem(**order_item_data)

    result = OrderCreationResult(
        order=order,
        items=(item,),
    )

    with pytest.raises(FrozenInstanceError):
        result.order = order
