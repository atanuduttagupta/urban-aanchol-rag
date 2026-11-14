from unittest.mock import MagicMock

import pytest

from backend.app.inventory.inventory_repository import (
    PostgresInventoryRepository,
)
from backend.app.inventory.models import CustomerAvailability


def create_repository(result):
    connection = MagicMock()
    cursor = connection.cursor.return_value.__enter__.return_value
    cursor.fetchone.return_value = result

    repository = PostgresInventoryRepository(connection)

    return repository, connection, cursor


def test_get_inventory_snapshot_with_active_holds():
    repository, _, cursor = create_repository(("UA-0016", 4, 2, "Reserved"))

    result = repository.get_inventory_snapshot("UA-0016")

    assert result is not None
    assert result.product_id == "UA-0016"
    assert result.stock_quantity == 4
    assert result.reserved_quantity == 2
    assert result.available_quantity == 2
    assert result.customer_availability == CustomerAvailability.RESERVED
    assert result.can_reserve is False

    cursor.execute.assert_called_once()
    assert cursor.execute.call_args.args[1] == ("UA-0016",)


def test_get_inventory_snapshot_without_holds():
    repository, _, _ = create_repository(("UA-0001", 12, 0, "Available"))

    result = repository.get_inventory_snapshot("UA-0001")

    assert result is not None
    assert result.stock_quantity == 12
    assert result.reserved_quantity == 0
    assert result.available_quantity == 12
    assert result.customer_availability == CustomerAvailability.AVAILABLE
    assert result.can_reserve is True


def test_get_inventory_snapshot_returns_none_for_missing_product():
    repository, _, _ = create_repository(None)

    result = repository.get_inventory_snapshot("UA-9999")

    assert result is None


@pytest.mark.parametrize(
    "product_id, stock, reserved, admin_status, expected_available, expected_status",
    [
        (
            "UA-0016",
            4,
            2,
            "Reserved",
            2,
            CustomerAvailability.RESERVED,
        ),
        (
            "UA-0017",
            2,
            1,
            "Reserved",
            1,
            CustomerAvailability.RESERVED,
        ),
        (
            "UA-0018",
            0,
            0,
            "Reserved",
            0,
            CustomerAvailability.RESERVED,
        ),
    ],
)
def test_demo_inventory_scenarios(
    product_id,
    stock,
    reserved,
    admin_status,
    expected_available,
    expected_status,
):
    repository, _, _ = create_repository((product_id, stock, reserved, admin_status))

    result = repository.get_inventory_snapshot(product_id)

    assert result is not None
    assert result.stock_quantity == stock
    assert result.reserved_quantity == reserved
    assert result.available_quantity == expected_available
    assert result.customer_availability == expected_status
    assert result.can_reserve is False


def test_query_uses_only_active_holds():
    repository, _, cursor = create_repository(("UA-0016", 4, 2, "Reserved"))

    repository.get_inventory_snapshot("UA-0016")

    executed_sql = cursor.execute.call_args.args[0]

    assert "status = 'Active'" in executed_sql
    assert "SUM(quantity)" in executed_sql
    assert "LEFT JOIN" in executed_sql
    assert "GROUP BY product_id" in executed_sql
