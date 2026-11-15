from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from backend.app.api.routes.customers import get_customer_service
from backend.app.customers.models import Customer
from backend.app.main import app


@pytest.fixture
def service():
    return MagicMock()


@pytest.fixture
def client(service):
    app.dependency_overrides[get_customer_service] = lambda: service

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def customer():
    now = datetime.now(UTC)

    return Customer(
        customer_id=1,
        full_name="Test Customer",
        mobile_number="9876543210",
        whatsapp_number="9876543211",
        email="test@example.com",
        bill_to_contact_name="Test Customer",
        bill_to_phone="9876543210",
        bill_to_address="Kolkata",
        ship_to_contact_name=None,
        ship_to_phone=None,
        ship_to_address=None,
        notes="Test customer",
        attribute1=None,
        attribute2=None,
        attribute3=None,
        attribute4=None,
        attribute5=None,
        created_at=now,
        updated_at=now,
    )


def test_create_customer_success(client, service, customer):
    service.create_customer.return_value = customer

    response = client.post(
        "/api/customers",
        json={
            "full_name": "Test Customer",
            "mobile_number": "9876543210",
        },
    )

    assert response.status_code == 201
    assert response.json()["customer_id"] == 1
    assert response.json()["full_name"] == "Test Customer"

    service.create_customer.assert_called_once()


def test_create_customer_rejects_missing_name(client, service):
    response = client.post(
        "/api/customers",
        json={"mobile_number": "9876543210"},
    )

    assert response.status_code == 422
    service.create_customer.assert_not_called()


def test_create_customer_rejects_missing_mobile(client, service):
    response = client.post(
        "/api/customers",
        json={"full_name": "Test Customer"},
    )

    assert response.status_code == 422
    service.create_customer.assert_not_called()


def test_create_customer_rejects_unknown_fields(client, service):
    response = client.post(
        "/api/customers",
        json={
            "full_name": "Test Customer",
            "mobile_number": "9876543210",
            "unexpected": "value",
        },
    )

    assert response.status_code == 422
    service.create_customer.assert_not_called()


def test_create_customer_service_validation_error(client, service):
    service.create_customer.side_effect = ValueError(
        "Invalid email address."
    )

    response = client.post(
        "/api/customers",
        json={
            "full_name": "Test Customer",
            "mobile_number": "9876543210",
            "email": "invalid-email",
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Invalid email address."


def test_get_customer_success(client, service, customer):
    service.get_customer.return_value = customer

    response = client.get("/api/customers/1")

    assert response.status_code == 200
    assert response.json()["customer_id"] == 1
    assert response.json()["mobile_number"] == "9876543210"

    service.get_customer.assert_called_once_with(1)


def test_get_unknown_customer(client, service):
    service.get_customer.return_value = None

    response = client.get("/api/customers/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Customer not found."


def test_get_customer_rejects_invalid_id(client, service):
    response = client.get("/api/customers/invalid")

    assert response.status_code == 422
    service.get_customer.assert_not_called()


def test_list_customers(client, service, customer):
    service.list_customers.return_value = [customer]

    response = client.get("/api/customers")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["customer_id"] == 1

    service.list_customers.assert_called_once_with(
        search=None,
        limit=20,
        offset=0,
    )


def test_list_customers_with_search_and_pagination(
    client, service, customer
):
    service.list_customers.return_value = [customer]

    response = client.get(
        "/api/customers",
        params={
            "search": "Test",
            "limit": 10,
            "offset": 5,
        },
    )

    assert response.status_code == 200

    service.list_customers.assert_called_once_with(
        search="Test",
        limit=10,
        offset=5,
    )


def test_list_customers_rejects_invalid_limit(client, service):
    response = client.get(
        "/api/customers",
        params={"limit": 101},
    )

    assert response.status_code == 422
    service.list_customers.assert_not_called()


def test_update_customer_partial_success(client, service, customer):
    service.update_customer.return_value = customer

    response = client.patch(
        "/api/customers/1",
        json={"whatsapp_number": "9876543211"},
    )

    assert response.status_code == 200
    assert response.json()["customer_id"] == 1

    service.update_customer.assert_called_once_with(
        1,
        {"whatsapp_number": "9876543211"},
    )


def test_update_customer_can_clear_optional_field(
    client, service, customer
):
    service.update_customer.return_value = customer

    response = client.patch(
        "/api/customers/1",
        json={"email": None},
    )

    assert response.status_code == 200

    service.update_customer.assert_called_once_with(
        1,
        {"email": None},
    )


def test_update_customer_rejects_unknown_fields(client, service):
    response = client.patch(
        "/api/customers/1",
        json={"unknown_field": "value"},
    )

    assert response.status_code == 422
    service.update_customer.assert_not_called()


def test_update_customer_rejects_empty_request(client, service):
    service.update_customer.side_effect = ValueError(
        "At least one update field is required."
    )

    response = client.patch(
        "/api/customers/1",
        json={},
    )

    assert response.status_code == 422
    assert "At least one update field" in response.json()["detail"]


def test_update_customer_rejects_clearing_required_field(
    client, service
):
    service.update_customer.side_effect = ValueError(
        "full_name is required."
    )

    response = client.patch(
        "/api/customers/1",
        json={"full_name": None},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "full_name is required."


def test_update_unknown_customer(client, service):
    service.update_customer.return_value = None

    response = client.patch(
        "/api/customers/999",
        json={"notes": "Updated notes"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Customer not found."