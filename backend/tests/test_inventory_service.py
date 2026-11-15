from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from backend.app.inventory.inventory_service import InventoryService
from backend.app.inventory.models import (
    AdminAvailability,
    CustomerAvailability,
    HoldCreationResult,
    HoldRecord,
    HoldReleaseReason,
    HoldReleaseResult,
    HoldStatus,
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


def test_create_hold_success(service, repository):
    expected = HoldCreationResult(
        created=True,
        hold_id=101,
        product_id="UA-0001",
        requested_quantity=2,
        available_quantity=8,
        customer_availability=CustomerAvailability.AVAILABLE,
        reason=ReservationReason.RESERVATION_ALLOWED,
    )
    repository.create_hold.return_value = expected

    result = service.create_hold(
        product_id=" UA-0001 ",
        quantity=2,
        customer_reference="  CUSTOMER-001  ",
        notes="Customer confirmed on WhatsApp",
    )

    assert result == expected
    repository.create_hold.assert_called_once_with(
        product_id="UA-0001",
        quantity=2,
        customer_reference="CUSTOMER-001",
        notes="Customer confirmed on WhatsApp",
    )


def test_create_hold_returns_insufficient_stock(service, repository):
    expected = HoldCreationResult(
        created=False,
        hold_id=None,
        product_id="UA-0001",
        requested_quantity=5,
        available_quantity=2,
        customer_availability=CustomerAvailability.AVAILABLE,
        reason=ReservationReason.INSUFFICIENT_STOCK,
    )
    repository.create_hold.return_value = expected

    result = service.create_hold(
        "UA-0001", 5, "CUSTOMER-001"
    )

    assert result == expected
    assert result.created is False


def test_create_hold_returns_product_not_found(service, repository):
    expected = HoldCreationResult(
        created=False,
        hold_id=None,
        product_id="UA-9999",
        requested_quantity=1,
        available_quantity=None,
        customer_availability=None,
        reason=ReservationReason.PRODUCT_NOT_FOUND,
    )
    repository.create_hold.return_value = expected

    result = service.create_hold(
        "UA-9999", 1, "CUSTOMER-001"
    )

    assert result == expected


def test_create_hold_returns_product_not_available(service, repository):
    expected = HoldCreationResult(
        created=False,
        hold_id=None,
        product_id="UA-0016",
        requested_quantity=1,
        available_quantity=2,
        customer_availability=CustomerAvailability.RESERVED,
        reason=ReservationReason.PRODUCT_NOT_AVAILABLE,
    )
    repository.create_hold.return_value = expected

    result = service.create_hold(
        "UA-0016", 1, "CUSTOMER-001"
    )

    assert result == expected


@pytest.mark.parametrize("quantity", [0, -1])
def test_create_hold_rejects_non_positive_quantity(
    service, repository, quantity
):
    with pytest.raises(ValueError, match="greater than zero"):
        service.create_hold("UA-0001", quantity, "CUSTOMER-001")

    repository.create_hold.assert_not_called()


@pytest.mark.parametrize("quantity", [True, 1.5, "2"])
def test_create_hold_rejects_non_integer_quantity(
    service, repository, quantity
):
    with pytest.raises(ValueError, match="must be an integer"):
        service.create_hold("UA-0001", quantity, "CUSTOMER-001")

    repository.create_hold.assert_not_called()


@pytest.mark.parametrize("product_id", ["", "   "])
def test_create_hold_rejects_empty_product_id(
    service, repository, product_id
):
    with pytest.raises(ValueError, match="Product ID cannot be empty"):
        service.create_hold(product_id, 1, "CUSTOMER-001")

    repository.create_hold.assert_not_called()


@pytest.mark.parametrize("customer_reference", ["", "   ", None])
def test_create_hold_rejects_missing_customer_reference(
    service, repository, customer_reference
):
    with pytest.raises(ValueError, match="Customer reference is required"):
        service.create_hold("UA-0001", 1, customer_reference)

    repository.create_hold.assert_not_called()


def test_create_hold_rejects_long_customer_reference(service, repository):
    with pytest.raises(ValueError, match="100 characters"):
        service.create_hold("UA-0001", 1, "C" * 101)

    repository.create_hold.assert_not_called()


def test_list_active_holds(service, repository):
    expected = [
        HoldRecord(
            hold_id=101,
            product_id="UA-0001",
            customer_reference="CUSTOMER-001",
            quantity=2,
            status=HoldStatus.ACTIVE,
            notes=None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
    ]
    repository.list_active_holds.return_value = expected

    result = service.list_active_holds()

    assert result == expected
    repository.list_active_holds.assert_called_once_with(None)


def test_list_active_holds_filters_by_product(service, repository):
    repository.list_active_holds.return_value = []

    result = service.list_active_holds(" UA-0001 ")

    assert result == []
    repository.list_active_holds.assert_called_once_with("UA-0001")


@pytest.mark.parametrize("product_id", ["", "   ", 123])
def test_list_active_holds_rejects_invalid_product_id(
    service, repository, product_id
):
    with pytest.raises(ValueError, match="Product ID cannot be empty"):
        service.list_active_holds(product_id)

    repository.list_active_holds.assert_not_called()


def test_release_hold_success(service, repository):
    expected = HoldReleaseResult(
        released=True,
        hold_id=101,
        product_id="UA-0001",
        reason=HoldReleaseReason.HOLD_RELEASED,
    )
    repository.release_hold.return_value = expected

    result = service.release_hold(101)

    assert result == expected
    repository.release_hold.assert_called_once_with(101)


@pytest.mark.parametrize("hold_id", [0, -1])
def test_release_hold_rejects_non_positive_id(
    service, repository, hold_id
):
    with pytest.raises(ValueError, match="greater than zero"):
        service.release_hold(hold_id)

    repository.release_hold.assert_not_called()


@pytest.mark.parametrize("hold_id", [True, 1.5, "101", None])
def test_release_hold_rejects_non_integer_id(
    service, repository, hold_id
):
    with pytest.raises(ValueError, match="must be an integer"):
        service.release_hold(hold_id)

    repository.release_hold.assert_not_called()