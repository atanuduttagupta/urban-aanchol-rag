from unittest.mock import MagicMock

import pytest

from backend.app.inventory.inventory_service import InventoryService
from backend.app.inventory.models import (
    AdminAvailability,
    InventorySnapshot,
    ReservationReason,
)


@pytest.fixture
def repository():
    return MagicMock()


@pytest.fixture
def service(repository):
    return InventoryService(repository)


def test_get_inventory_returns_snapshot(service, repository):
    snapshot = InventorySnapshot(
        product_id="UA-0001",
        stock_quantity=12,
        reserved_quantity=0,
        admin_availability=AdminAvailability.AVAILABLE,
    )
    repository.get_inventory_snapshot.return_value = snapshot

    result = service.get_inventory("UA-0001")

    assert result == snapshot
    repository.get_inventory_snapshot.assert_called_once_with("UA-0001")


def test_get_inventory_returns_none_for_unknown_product(service, repository):
    repository.get_inventory_snapshot.return_value = None

    result = service.get_inventory("UA-9999")

    assert result is None


def test_can_reserve_when_quantity_is_available(service, repository):
    repository.get_inventory_snapshot.return_value = InventorySnapshot(
        product_id="UA-0001",
        stock_quantity=12,
        reserved_quantity=2,
        admin_availability=AdminAvailability.AVAILABLE,
    )

    assert service.can_reserve("UA-0001", 5) is True


def test_cannot_reserve_when_quantity_exceeds_available(service, repository):
    repository.get_inventory_snapshot.return_value = InventorySnapshot(
        product_id="UA-0001",
        stock_quantity=12,
        reserved_quantity=10,
        admin_availability=AdminAvailability.AVAILABLE,
    )

    assert service.can_reserve("UA-0001", 3) is False


def test_cannot_reserve_when_admin_status_is_reserved(service, repository):
    repository.get_inventory_snapshot.return_value = InventorySnapshot(
        product_id="UA-0016",
        stock_quantity=4,
        reserved_quantity=2,
        admin_availability=AdminAvailability.RESERVED,
    )

    assert service.can_reserve("UA-0016", 1) is False


def test_cannot_reserve_unknown_product(service, repository):
    repository.get_inventory_snapshot.return_value = None

    assert service.can_reserve("UA-9999", 1) is False


@pytest.mark.parametrize("quantity", [0, -1])
def test_rejects_non_positive_quantity(service, quantity):
    with pytest.raises(ValueError, match="greater than zero"):
        service.can_reserve("UA-0001", quantity)


@pytest.mark.parametrize("quantity", [True, 1.5, "2"])
def test_rejects_non_integer_quantity(service, quantity):
    with pytest.raises(ValueError, match="must be an integer"):
        service.can_reserve("UA-0001", quantity)


@pytest.mark.parametrize("product_id", ["", "   "])
def test_rejects_empty_product_id(service, product_id):
    with pytest.raises(ValueError, match="Product ID cannot be empty"):
        service.get_inventory(product_id)


def test_reservation_decision_allowed(service, repository):
    repository.get_inventory_snapshot.return_value = InventorySnapshot(
        product_id="UA-0001",
        stock_quantity=12,
        reserved_quantity=2,
        admin_availability=AdminAvailability.AVAILABLE,
    )

    decision = service.check_reservation("UA-0001", 5)

    assert decision.allowed is True
    assert decision.product_id == "UA-0001"
    assert decision.requested_quantity == 5
    assert decision.available_quantity == 10
    assert decision.reason == ReservationReason.RESERVATION_ALLOWED


def test_reservation_decision_insufficient_stock(service, repository):
    repository.get_inventory_snapshot.return_value = InventorySnapshot(
        product_id="UA-0001",
        stock_quantity=12,
        reserved_quantity=10,
        admin_availability=AdminAvailability.AVAILABLE,
    )

    decision = service.check_reservation("UA-0001", 3)

    assert decision.allowed is False
    assert decision.available_quantity == 2
    assert decision.reason == ReservationReason.INSUFFICIENT_STOCK


def test_reservation_decision_admin_reserved(service, repository):
    repository.get_inventory_snapshot.return_value = InventorySnapshot(
        product_id="UA-0016",
        stock_quantity=4,
        reserved_quantity=2,
        admin_availability=AdminAvailability.RESERVED,
    )

    decision = service.check_reservation("UA-0016", 1)

    assert decision.allowed is False
    assert decision.available_quantity == 2
    assert decision.reason == ReservationReason.PRODUCT_NOT_AVAILABLE


def test_reservation_decision_out_of_stock(service, repository):
    repository.get_inventory_snapshot.return_value = InventorySnapshot(
        product_id="UA-0003",
        stock_quantity=0,
        reserved_quantity=0,
        admin_availability=AdminAvailability.AVAILABLE,
    )

    decision = service.check_reservation("UA-0003", 1)

    assert decision.allowed is False
    assert decision.available_quantity == 0
    assert decision.reason == ReservationReason.OUT_OF_STOCK


def test_reservation_decision_product_not_found(service, repository):
    repository.get_inventory_snapshot.return_value = None

    decision = service.check_reservation("UA-9999", 1)

    assert decision.allowed is False
    assert decision.available_quantity is None
    assert decision.customer_availability is None
    assert decision.reason == ReservationReason.PRODUCT_NOT_FOUND
