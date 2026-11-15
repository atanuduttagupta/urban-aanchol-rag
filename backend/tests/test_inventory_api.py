
from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from backend.app.api.routes.inventory import get_inventory_service
from backend.app.inventory.models import (
    CustomerAvailability,
    HoldCreationResult,
    HoldRecord,
    HoldReleaseReason,
    HoldReleaseResult,
    HoldStatus,
    ReservationReason,
)
from backend.app.main import app


@pytest.fixture
def service():
    return MagicMock()


@pytest.fixture
def client(service):
    app.dependency_overrides[get_inventory_service] = lambda: service

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_create_hold_success(client, service):
    service.create_hold.return_value = HoldCreationResult(
        created=True,
        hold_id=101,
        product_id="UA-0001",
        requested_quantity=2,
        available_quantity=10,
        customer_availability=CustomerAvailability.AVAILABLE,
        reason=ReservationReason.RESERVATION_ALLOWED,
    )

    response = client.post(
        "/api/inventory/create-hold",
        json={
            "product_id": "UA-0001",
            "quantity": 2,
            "customer_reference": "CUSTOMER-001",
            "notes": "WhatsApp customer",
        },
    )

    assert response.status_code == 201
    assert response.json()["created"] is True
    assert response.json()["hold_id"] == 101
    assert response.json()["available_quantity"] == 10

    service.create_hold.assert_called_once()


def test_create_hold_insufficient_stock(client, service):
    service.create_hold.return_value = HoldCreationResult(
        created=False,
        hold_id=None,
        product_id="UA-0001",
        requested_quantity=5,
        available_quantity=2,
        customer_availability=CustomerAvailability.AVAILABLE,
        reason=ReservationReason.INSUFFICIENT_STOCK,
    )

    response = client.post(
        "/api/inventory/create-hold",
        json={
            "product_id": "UA-0001",
            "quantity": 5,
            "customer_reference": "CUSTOMER-001",
        },
    )

    assert response.status_code == 409
    assert response.json()["created"] is False
    assert response.json()["reason"] == "INSUFFICIENT_STOCK"


def test_create_hold_unknown_product(client, service):
    service.create_hold.return_value = HoldCreationResult(
        created=False,
        hold_id=None,
        product_id="UA-9999",
        requested_quantity=1,
        available_quantity=None,
        customer_availability=None,
        reason=ReservationReason.PRODUCT_NOT_FOUND,
    )

    response = client.post(
        "/api/inventory/create-hold",
        json={
            "product_id": "UA-9999",
            "quantity": 1,
            "customer_reference": "CUSTOMER-001",
        },
    )

    assert response.status_code == 404
    assert response.json()["reason"] == "PRODUCT_NOT_FOUND"


def test_create_hold_rejects_missing_customer_reference(
    client, service
):
    response = client.post(
        "/api/inventory/create-hold",
        json={
            "product_id": "UA-0001",
            "quantity": 1,
        },
    )

    assert response.status_code == 422
    service.create_hold.assert_not_called()


def test_create_hold_rejects_invalid_quantity(client, service):
    response = client.post(
        "/api/inventory/create-hold",
        json={
            "product_id": "UA-0001",
            "quantity": 0,
            "customer_reference": "CUSTOMER-001",
        },
    )

    assert response.status_code == 422
    service.create_hold.assert_not_called()


def test_list_active_holds(client, service):
    now = datetime.now(UTC)

    service.list_active_holds.return_value = [
        HoldRecord(
            hold_id=101,
            product_id="UA-0001",
            customer_reference="CUSTOMER-001",
            quantity=2,
            status=HoldStatus.ACTIVE,
            notes="WhatsApp customer",
            created_at=now,
            updated_at=now,
        )
    ]

    response = client.get("/api/inventory/holds")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["hold_id"] == 101
    assert response.json()[0]["product_id"] == "UA-0001"
    assert response.json()[0]["status"] == "Active"

    service.list_active_holds.assert_called_once_with(None)


def test_list_active_holds_filtered_by_product(client, service):
    service.list_active_holds.return_value = []

    response = client.get(
        "/api/inventory/holds",
        params={"product_id": "UA-0001"},
    )

    assert response.status_code == 200
    assert response.json() == []

    service.list_active_holds.assert_called_once_with("UA-0001")


def test_release_hold_success(client, service):
    service.release_hold.return_value = HoldReleaseResult(
        released=True,
        hold_id=101,
        product_id="UA-0001",
        reason=HoldReleaseReason.HOLD_RELEASED,
    )

    response = client.post("/api/inventory/holds/101/release")

    assert response.status_code == 200
    assert response.json()["released"] is True
    assert response.json()["hold_id"] == 101
    assert response.json()["reason"] == "HOLD_RELEASED"

    service.release_hold.assert_called_once_with(101)


def test_release_unknown_hold(client, service):
    service.release_hold.return_value = HoldReleaseResult(
        released=False,
        hold_id=999,
        product_id=None,
        reason=HoldReleaseReason.HOLD_NOT_FOUND,
    )

    response = client.post("/api/inventory/holds/999/release")

    assert response.status_code == 404
    assert response.json()["detail"] == "Hold not found."


def test_release_inactive_hold_returns_conflict(client, service):
    service.release_hold.return_value = HoldReleaseResult(
        released=False,
        hold_id=101,
        product_id="UA-0001",
        reason=HoldReleaseReason.HOLD_NOT_ACTIVE,
    )

    response = client.post("/api/inventory/holds/101/release")

    assert response.status_code == 409
    assert response.json()["detail"] == "Hold is no longer active."