import pytest

from backend.app.inventory.models import (
    AdminAvailability,
    CustomerAvailability,
    InventorySnapshot,
)


@pytest.mark.parametrize(
    "admin_status, expected_customer_status",
    [
        (AdminAvailability.PLANNED, CustomerAvailability.PLANNED),
        (AdminAvailability.COMING_SOON, CustomerAvailability.COMING_SOON),
        (AdminAvailability.RESERVED, CustomerAvailability.RESERVED),
        (AdminAvailability.SOLD, CustomerAvailability.SOLD),
        (AdminAvailability.INACTIVE, CustomerAvailability.INACTIVE),
        (AdminAvailability.DISCONTINUED, CustomerAvailability.DISCONTINUED),
    ],
)
def test_admin_status_mapping(admin_status, expected_customer_status):
    inventory = InventorySnapshot(
        product_id="UA-TEST",
        stock_quantity=10,
        reserved_quantity=2,
        admin_availability=admin_status,
    )

    assert inventory.customer_availability == expected_customer_status
    assert inventory.can_reserve is False


def test_available_product_with_remaining_stock():
    inventory = InventorySnapshot(
        product_id="UA-TEST",
        stock_quantity=5,
        reserved_quantity=2,
        admin_availability=AdminAvailability.AVAILABLE,
    )

    assert inventory.available_quantity == 3
    assert inventory.customer_availability == CustomerAvailability.AVAILABLE
    assert inventory.can_reserve is True


def test_available_product_with_all_stock_reserved():
    inventory = InventorySnapshot(
        product_id="UA-TEST",
        stock_quantity=2,
        reserved_quantity=2,
        admin_availability=AdminAvailability.AVAILABLE,
    )

    assert inventory.available_quantity == 0
    assert inventory.customer_availability == CustomerAvailability.OUT_OF_STOCK
    assert inventory.can_reserve is False


def test_available_product_with_zero_stock():
    inventory = InventorySnapshot(
        product_id="UA-TEST",
        stock_quantity=0,
        reserved_quantity=0,
        admin_availability=AdminAvailability.AVAILABLE,
    )

    assert inventory.customer_availability == CustomerAvailability.OUT_OF_STOCK
    assert inventory.can_reserve is False


@pytest.mark.parametrize(
    "product_id, stock, reserved",
    [
        ("UA-TEST", -1, 0),
        ("UA-TEST", 5, -1),
        ("UA-TEST", 2, 3),
        ("UA-TEST", 2.5, 0),
        ("UA-TEST", 5, True),
        ("", 5, 0),
    ],
)
def test_invalid_inventory_values_are_rejected(product_id, stock, reserved):
    with pytest.raises(ValueError):
        InventorySnapshot(
            product_id=product_id,
            stock_quantity=stock,
            reserved_quantity=reserved,
            admin_availability=AdminAvailability.AVAILABLE,
        )


def test_reserved_status_blocks_new_reservations_with_remaining_stock():
    inventory = InventorySnapshot(
        product_id="UA-0016",
        stock_quantity=4,
        reserved_quantity=2,
        admin_availability=AdminAvailability.RESERVED,
    )

    assert inventory.available_quantity == 2
    assert inventory.customer_availability == CustomerAvailability.RESERVED
    assert inventory.can_reserve is False
