
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from backend.app.api.routes.inventory import get_inventory_service
from backend.app.inventory.models import (
    CustomerAvailability,
    HoldCreationResult,
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
