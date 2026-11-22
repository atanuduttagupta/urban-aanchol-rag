from unittest.mock import MagicMock

import pytest

from backend.app.inventory.models import (
    CustomerAvailability,
)
from backend.app.inventory.reservation import get_inventory_snapshots


def create_cursor():
    return MagicMock()


def test_get_inventory_snapshots_for_multiple_products():
    cursor = create_cursor()

    cursor.fetchall.return_value = [
        ("UA-0001", 12, 2, 3, "Available"),
        ("UA-0002", 8, 1, 0, "Available"),
    ]

    result = get_inventory_snapshots(
        cursor,
        ("UA-0001", "UA-0002"),
    )

    assert len(result) == 2

    first = result["UA-0001"]
    assert first.stock_quantity == 12
    assert first.held_quantity == 2
    assert first.ordered_quantity == 3
    assert first.available_quantity == 7
    assert first.customer_availability == CustomerAvailability.AVAILABLE

    second = result["UA-0002"]
    assert second.stock_quantity == 8
    assert second.held_quantity == 1
    assert second.ordered_quantity == 0
    assert second.available_quantity == 7

    cursor.execute.assert_called_once()


def test_missing_products_are_omitted():
    cursor = create_cursor()
    cursor.fetchall.return_value = [
        ("UA-0001", 12, 0, 0, "Available"),
    ]

    result = get_inventory_snapshots(
        cursor,
        ("UA-0001", "UA-9999"),
    )

    assert "UA-0001" in result
    assert "UA-9999" not in result


def test_locking_occurs_before_inventory_calculation():
    cursor = create_cursor()

    cursor.fetchall.side_effect = [
        [("UA-0001",), ("UA-0002",)],
        [
            ("UA-0001", 12, 0, 0, "Available"),
            ("UA-0002", 8, 0, 0, "Available"),
        ],
    ]

    result = get_inventory_snapshots(
        cursor,
        ("UA-0002", "UA-0001"),
        lock_products=True,
    )

    assert len(result) == 2
    assert cursor.execute.call_count == 2

    lock_sql = cursor.execute.call_args_list[0].args[0]
    inventory_sql = cursor.execute.call_args_list[1].args[0]

    assert "ORDER BY product_id" in lock_sql
    assert "FOR UPDATE" in lock_sql
    assert "shipment_items" in inventory_sql


def test_products_are_locked_in_sorted_order():
    cursor = create_cursor()
    cursor.fetchall.side_effect = [
        [("UA-0001",), ("UA-0002",)],
        [
            ("UA-0001", 12, 0, 0, "Available"),
            ("UA-0002", 8, 0, 0, "Available"),
        ],
    ]

    get_inventory_snapshots(
        cursor,
        ("UA-0002", "UA-0001"),
        lock_products=True,
    )

    lock_parameters = cursor.execute.call_args_list[0].args[1]

    assert lock_parameters == (["UA-0001", "UA-0002"],)


def test_duplicate_product_ids_are_rejected():
    cursor = create_cursor()

    with pytest.raises(ValueError, match="Duplicate"):
        get_inventory_snapshots(
            cursor,
            ("UA-0001", "UA-0001"),
        )

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
def test_invalid_product_ids_are_rejected(product_ids):
    cursor = create_cursor()

    with pytest.raises(ValueError):
        get_inventory_snapshots(cursor, product_ids)

    cursor.execute.assert_not_called()


def test_non_tuple_product_ids_are_rejected():
    cursor = create_cursor()

    with pytest.raises(ValueError):
        get_inventory_snapshots(
            cursor,
            ["UA-0001"],
        )

    cursor.execute.assert_not_called()


def test_inventory_calculation_does_not_acquire_locks_by_default():
    cursor = create_cursor()
    cursor.fetchall.return_value = [
        ("UA-0001", 12, 0, 0, "Available"),
    ]

    get_inventory_snapshots(
        cursor,
        ("UA-0001",),
    )

    assert cursor.execute.call_count == 1

    executed_sql = cursor.execute.call_args.args[0]

    assert "FOR UPDATE" not in executed_sql


def test_invalid_availability_is_rejected():
    cursor = create_cursor()
    cursor.fetchall.return_value = [
        ("UA-0001", 12, 0, 0, "Unknown"),
    ]

    with pytest.raises(ValueError):
        get_inventory_snapshots(
            cursor,
            ("UA-0001",),
        )
