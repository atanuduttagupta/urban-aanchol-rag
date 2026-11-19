from decimal import Decimal

import pytest

from backend.app.orders.models import OrderItemRequest
from backend.app.orders.order_pricing import calculate_order_pricing


@pytest.fixture
def items():
    return (
        OrderItemRequest(
            product_id="UA-0001",
            quantity=2,
            line_discount=Decimal("100.00"),
        ),
        OrderItemRequest(
            product_id="UA-0002",
            quantity=1,
        ),
    )


@pytest.fixture
def unit_prices():
    return {
        "UA-0001": Decimal("2500.00"),
        "UA-0002": Decimal("1500.00"),
    }


def test_calculate_order_pricing_success(items, unit_prices):
    result = calculate_order_pricing(
        items=items,
        unit_prices=unit_prices,
        discount_amount=Decimal("200.00"),
        delivery_charge=Decimal("100.00"),
    )

    assert result.subtotal == Decimal("6400.00")
    assert result.discount_amount == Decimal("200.00")
    assert result.delivery_charge == Decimal("100.00")
    assert result.grand_total == Decimal("6300.00")


def test_calculate_line_pricing(items, unit_prices):
    result = calculate_order_pricing(
        items=items,
        unit_prices=unit_prices,
        discount_amount=Decimal("0.00"),
        delivery_charge=Decimal("0.00"),
    )

    first_line = result.lines[0]

    assert first_line.gross_total == Decimal("5000.00")
    assert first_line.line_discount == Decimal("100.00")
    assert first_line.line_total == Decimal("4900.00")


def test_calculate_pricing_without_discounts():
    items = (OrderItemRequest("UA-0001", 2),)

    result = calculate_order_pricing(
        items=items,
        unit_prices={"UA-0001": Decimal("1000.00")},
        discount_amount=Decimal("0.00"),
        delivery_charge=Decimal("0.00"),
    )

    assert result.subtotal == Decimal("2000.00")
    assert result.grand_total == Decimal("2000.00")


def test_calculate_pricing_rounds_to_two_decimal_places():
    items = (OrderItemRequest("UA-0001", 1),)

    result = calculate_order_pricing(
        items=items,
        unit_prices={"UA-0001": Decimal("100.555")},
        discount_amount=Decimal("0"),
        delivery_charge=Decimal("10.555"),
    )

    assert result.lines[0].unit_price == Decimal("100.56")
    assert result.subtotal == Decimal("100.56")
    assert result.delivery_charge == Decimal("10.56")
    assert result.grand_total == Decimal("111.12")


def test_rejects_line_discount_exceeding_gross_amount():
    items = (
        OrderItemRequest(
            product_id="UA-0001",
            quantity=1,
            line_discount=Decimal("1500.00"),
        ),
    )

    with pytest.raises(ValueError, match="Line discount exceeds"):
        calculate_order_pricing(
            items=items,
            unit_prices={"UA-0001": Decimal("1000.00")},
            discount_amount=Decimal("0.00"),
            delivery_charge=Decimal("0.00"),
        )


def test_rejects_order_discount_exceeding_subtotal():
    items = (OrderItemRequest("UA-0001", 1),)

    with pytest.raises(ValueError, match="Order discount"):
        calculate_order_pricing(
            items=items,
            unit_prices={"UA-0001": Decimal("1000.00")},
            discount_amount=Decimal("1000.01"),
            delivery_charge=Decimal("0.00"),
        )


def test_rejects_missing_product_price():
    items = (OrderItemRequest("UA-0001", 1),)

    with pytest.raises(ValueError, match="Product prices"):
        calculate_order_pricing(
            items=items,
            unit_prices={},
            discount_amount=Decimal("0.00"),
            delivery_charge=Decimal("0.00"),
        )


def test_rejects_extra_product_price():
    items = (OrderItemRequest("UA-0001", 1),)

    with pytest.raises(ValueError, match="Product prices"):
        calculate_order_pricing(
            items=items,
            unit_prices={
                "UA-0001": Decimal("1000.00"),
                "UA-0002": Decimal("2000.00"),
            },
            discount_amount=Decimal("0.00"),
            delivery_charge=Decimal("0.00"),
        )


@pytest.mark.parametrize(
    "discount",
    [
        Decimal("-1.00"),
        Decimal("NaN"),
        Decimal("Infinity"),
        100,
    ],
)
def test_rejects_invalid_order_discount(discount):
    items = (OrderItemRequest("UA-0001", 1),)

    with pytest.raises(ValueError):
        calculate_order_pricing(
            items=items,
            unit_prices={"UA-0001": Decimal("1000.00")},
            discount_amount=discount,
            delivery_charge=Decimal("0.00"),
        )


@pytest.mark.parametrize(
    "delivery_charge",
    [
        Decimal("-1.00"),
        Decimal("NaN"),
        Decimal("Infinity"),
        100,
    ],
)
def test_rejects_invalid_delivery_charge(delivery_charge):
    items = (OrderItemRequest("UA-0001", 1),)

    with pytest.raises(ValueError):
        calculate_order_pricing(
            items=items,
            unit_prices={"UA-0001": Decimal("1000.00")},
            discount_amount=Decimal("0.00"),
            delivery_charge=delivery_charge,
        )


def test_rejects_duplicate_product_ids():
    items = (
        OrderItemRequest("UA-0001", 1),
        OrderItemRequest("UA-0001", 2),
    )

    with pytest.raises(ValueError, match="Duplicate"):
        calculate_order_pricing(
            items=items,
            unit_prices={"UA-0001": Decimal("1000.00")},
            discount_amount=Decimal("0.00"),
            delivery_charge=Decimal("0.00"),
        )
