from dataclasses import fields
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from backend.app.orders.models import Order, OrderItem, OrderStatus
from backend.app.orders.order_repository import (
    PostgresOrderRepository,
    ProductOrderSnapshot,
    order_from_row,
    order_item_from_row,
)


@pytest.fixture
def connection():
    return MagicMock()


@pytest.fixture
def repository(connection):
    return PostgresOrderRepository(connection)


@pytest.fixture
def now():
    return datetime.now(UTC)


@pytest.fixture
def order(now):
    return Order(
        order_id=1,
        order_number="UA-ORD-000001",
        customer_id=1,
        order_date=now,
        order_status=OrderStatus.PLACED,
        subtotal=Decimal("5000.00"),
        discount_amount=Decimal("200.00"),
        delivery_charge=Decimal("100.00"),
        grand_total=Decimal("4900.00"),
        created_at=now,
        updated_at=now,
        payment_due_at=now + timedelta(hours=24),
    )


@pytest.fixture
def order_item(now):
    return OrderItem(
        order_item_id=1,
        order_id=1,
        product_id="UA-0001",
        product_name="Bengal Cotton Saree",
        category="Saree",
        quantity=2,
        unit_price=Decimal("2500.00"),
        line_discount=Decimal("100.00"),
        line_total=Decimal("4900.00"),
        created_at=now,
        updated_at=now,
    )


@pytest.fixture
def cursor(connection):
    return connection.cursor.return_value.__enter__.return_value


def order_row(order):
    values = [getattr(order, field.name) for field in fields(Order)]
    values[5] = values[5].value
    return tuple(values)


def order_item_row(item):
    return tuple(getattr(item, field.name) for field in fields(OrderItem))


def test_order_from_row(order):
    result = order_from_row(order_row(order))

    assert result == order
    assert result.order_status == OrderStatus.PLACED
    assert result.payment_due_at == order.payment_due_at


def test_order_item_from_row(order_item):
    result = order_item_from_row(order_item_row(order_item))

    assert result == order_item


def test_get_order_success(repository, cursor, order):
    cursor.fetchone.return_value = order_row(order)

    result = repository.get_order(1)

    assert result == order
    cursor.execute.assert_called_once()
    assert cursor.execute.call_args.args[1] == (1,)


def test_get_order_not_found(repository, cursor):
    cursor.fetchone.return_value = None

    result = repository.get_order(999)

    assert result is None


def test_get_order_items_success(repository, cursor, order_item):
    cursor.fetchall.return_value = [order_item_row(order_item)]

    result = repository.get_order_items(1)

    assert result == [order_item]
    cursor.execute.assert_called_once()
    assert cursor.execute.call_args.args[1] == (1,)


def test_get_order_items_empty(repository, cursor):
    cursor.fetchall.return_value = []

    result = repository.get_order_items(1)

    assert result == []


def test_list_orders_without_filters(repository, cursor, order):
    cursor.fetchall.return_value = [order_row(order)]

    result = repository.list_orders()

    assert result == [order]

    sql, params = cursor.execute.call_args.args
    assert "FROM orders" in sql
    assert "ORDER BY order_date DESC, order_id DESC" in sql
    assert params == (20, 0)


def test_list_orders_by_customer(repository, cursor, order):
    cursor.fetchall.return_value = [order_row(order)]

    result = repository.list_orders(customer_id=1)

    assert result == [order]

    sql, params = cursor.execute.call_args.args
    assert "customer_id = %s" in sql
    assert params == (1, 20, 0)


def test_list_orders_by_status(repository, cursor, order):
    cursor.fetchall.return_value = [order_row(order)]

    result = repository.list_orders(order_status=OrderStatus.PLACED)

    assert result == [order]

    sql, params = cursor.execute.call_args.args
    assert "order_status = %s" in sql
    assert params == ("Placed", 20, 0)


def test_list_orders_by_customer_and_status(repository, cursor, order):
    cursor.fetchall.return_value = [order_row(order)]

    result = repository.list_orders(
        customer_id=1,
        order_status=OrderStatus.PLACED,
        limit=10,
        offset=5,
    )

    assert result == [order]

    sql, params = cursor.execute.call_args.args
    assert "customer_id = %s" in sql
    assert "order_status = %s" in sql
    assert params == (1, "Placed", 10, 5)


def test_list_orders_empty(repository, cursor):
    cursor.fetchall.return_value = []

    result = repository.list_orders(customer_id=999)

    assert result == []


def test_get_next_order_number_first_value(repository, cursor):
    cursor.fetchone.return_value = (1,)

    result = repository.get_next_order_number()

    assert result == "UA-ORD-000001"
    cursor.execute.assert_called_once_with("SELECT nextval('order_number_seq')")


def test_get_next_order_number_large_value(repository, cursor):
    cursor.fetchone.return_value = (1234567,)

    result = repository.get_next_order_number()

    assert result == "UA-ORD-1234567"


def test_get_products_for_order_success(repository, cursor):
    cursor.fetchall.return_value = [
        (
            "UA-0001",
            "Bengal Cotton Saree",
            "Saree",
            "Urban Aanchol",
            Decimal("2500.00"),
            "Available",
            12,
        ),
        ("UA-0002", "Silk Saree", "Saree", None, Decimal("4500.00"), "Available", 8),
    ]

    result = repository.get_products_for_order(("UA-0001", "UA-0002"))

    assert len(result) == 2
    assert result["UA-0001"] == ProductOrderSnapshot(
        product_id="UA-0001",
        product_name="Bengal Cotton Saree",
        category="Saree",
        brand="Urban Aanchol",
        price=Decimal("2500.00"),
        availability="Available",
        stock_quantity=12,
    )

    assert result["UA-0002"].brand is None
    cursor.execute.assert_called_once()


def test_get_products_for_order_locks_in_sorted_order(repository, cursor):
    cursor.fetchall.return_value = []

    repository.get_products_for_order(("UA-0002", "UA-0001"))

    sql, params = cursor.execute.call_args.args

    assert "ORDER BY product_id" in sql
    assert "FOR UPDATE" in sql
    assert params == (["UA-0001", "UA-0002"],)


def test_get_products_for_order_omits_missing_products(repository, cursor):
    cursor.fetchall.return_value = [
        ("UA-0001", "Cotton Saree", "Saree", None, Decimal("2000.00"), "Available", 12),
    ]

    result = repository.get_products_for_order(("UA-0001", "UA-9999"))

    assert "UA-0001" in result
    assert "UA-9999" not in result


def test_get_products_for_order_preserves_null_price(repository, cursor):
    cursor.fetchall.return_value = [
        ("UA-0001", "Unpriced Saree", "Saree", None, None, "Available", 12),
    ]

    result = repository.get_products_for_order(("UA-0001",))

    assert result["UA-0001"].price is None


def test_get_products_for_order_rejects_duplicate_ids(repository, cursor):
    with pytest.raises(ValueError, match="Duplicate"):
        repository.get_products_for_order(("UA-0001", "UA-0001"))

    cursor.execute.assert_not_called()


@pytest.mark.parametrize(
    "product_ids",
    [
        (),
        ("",),
        ("   ",),
        (None,),
        ("UA-0001", "  "),
    ],
)
def test_get_products_for_order_rejects_invalid_ids(repository, cursor, product_ids):
    with pytest.raises(ValueError):
        repository.get_products_for_order(product_ids)

    cursor.execute.assert_not_called()


def test_get_products_for_order_rejects_non_tuple_ids(repository, cursor):
    with pytest.raises(ValueError):
        repository.get_products_for_order(["UA-0001"])

    cursor.execute.assert_not_called()
