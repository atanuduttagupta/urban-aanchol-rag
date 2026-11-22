
from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from backend.app.api.routes.orders import get_order_service
from backend.app.main import app
from backend.app.orders.delivery_charge import (
    DeliveryChargeConfigurationError,
)
from backend.app.orders.exceptions import (
    CustomerNotFoundError,
    HoldConflictError,
    HoldNotFoundError,
    InsufficientInventoryError,
    ProductNotFoundError,
    ProductPriceNotConfiguredError,
    ProductUnavailableError,
)
from backend.app.orders.idempotency import IdempotencyConflictError
from backend.app.orders.models import (
    Order,
    OrderCreationResult,
    OrderItem,
    OrderStatus,
)


@pytest.fixture
def service():
    return MagicMock()


@pytest.fixture
def client(service):
    app.dependency_overrides[get_order_service] = lambda: service

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def order_creation_result():
    now = datetime.now(UTC)

    order = Order(
        order_id=101,
        order_number="UA-ORD-00101",
        customer_id=1,
        order_date=now,
        payment_due_at=now.replace(
            year=now.year + 1,
        ),
        order_status=OrderStatus.PLACED,
        subtotal=Decimal("2500.00"),
        discount_amount=Decimal("0.00"),
        delivery_charge=Decimal("100.00"),
        grand_total=Decimal("2600.00"),
        created_at=now,
        updated_at=now,
    )

    item = OrderItem(
        order_item_id=201,
        order_id=101,
        product_id="UA-0001",
        product_name="Bengal Cotton Saree",
        category="Saree",
        quantity=1,
        unit_price=Decimal("2500.00"),
        line_discount=Decimal("0.00"),
        line_total=Decimal("2500.00"),
        created_at=now,
        updated_at=now,
        brand="Urban Aanchol",
        notes=None,
    )

    return OrderCreationResult(
        order=order,
        items=(item,),
    )


@pytest.fixture
def valid_order_payload():
    return {
        "customer_id": 1,
        "items": [
            {
                "product_id": "UA-0001",
                "quantity": 1,
            }
        ],
    }


def test_create_order_success(
    client,
    service,
    order_creation_result,
    valid_order_payload,
):
    idempotency_key = str(uuid4())
    service.create_order.return_value = order_creation_result

    response = client.post(
        "/api/orders",
        json=valid_order_payload,
        headers={"Idempotency-Key": idempotency_key},
    )

    assert response.status_code == 201

    data = response.json()

    assert data["order"]["order_id"] == 101
    assert data["order"]["order_number"] == "UA-ORD-00101"
    assert data["order"]["grand_total"] == "2600.00"

    assert len(data["items"]) == 1
    assert data["items"][0]["product_id"] == "UA-0001"

    service.create_order.assert_called_once()

    domain_request = service.create_order.call_args.kwargs["request"]

    assert domain_request.customer_id == 1
    assert isinstance(domain_request.items, tuple)
    assert domain_request.items[0].product_id == "UA-0001"
    assert domain_request.items[0].quantity == 1
    assert service.create_order.call_args.kwargs[
        "idempotency_key"
    ].__str__() == idempotency_key


def test_create_order_rejects_missing_idempotency_key(
    client,
    service,
    valid_order_payload,
):
    response = client.post(
        "/api/orders",
        json=valid_order_payload,
    )

    assert response.status_code == 422
    service.create_order.assert_not_called()


def test_create_order_rejects_invalid_idempotency_key(
    client,
    service,
    valid_order_payload,
):
    response = client.post(
        "/api/orders",
        json=valid_order_payload,
        headers={"Idempotency-Key": "not-a-uuid"},
    )

    assert response.status_code == 422
    service.create_order.assert_not_called()


def test_create_order_rejects_missing_customer_id(
    client,
    service,
):
    response = client.post(
        "/api/orders",
        json={
            "items": [
                {
                    "product_id": "UA-0001",
                    "quantity": 1,
                }
            ]
        },
        headers={"Idempotency-Key": str(uuid4())},
    )

    assert response.status_code == 422
    service.create_order.assert_not_called()


def test_create_order_rejects_empty_items(
    client,
    service,
):
    response = client.post(
        "/api/orders",
        json={
            "customer_id": 1,
            "items": [],
        },
        headers={"Idempotency-Key": str(uuid4())},
    )

    assert response.status_code == 422
    service.create_order.assert_not_called()


def test_create_order_rejects_client_supplied_price(
    client,
    service,
):
    response = client.post(
        "/api/orders",
        json={
            "customer_id": 1,
            "items": [
                {
                    "product_id": "UA-0001",
                    "quantity": 1,
                    "unit_price": 100,
                }
            ],
        },
        headers={"Idempotency-Key": str(uuid4())},
    )

    assert response.status_code == 422
    service.create_order.assert_not_called()



@pytest.mark.parametrize(
    ("exception", "expected_status"),
    [
        (CustomerNotFoundError("Customer not found"), 404),
        (ProductNotFoundError("Product not found"), 404),
        (HoldNotFoundError("Hold not found"), 404),
        (HoldConflictError("Hold conflict"), 409),
        (ProductUnavailableError("Product unavailable"), 409),
        (InsufficientInventoryError("Insufficient stock"), 409),
        (IdempotencyConflictError("Idempotency conflict"), 409),
        (ProductPriceNotConfiguredError("Price not configured"), 503),
        (
            DeliveryChargeConfigurationError("Configuration missing"),
            503,
        ),
    ],
)
def test_create_order_business_exception_mapping(
    client,
    service,
    valid_order_payload,
    exception,
    expected_status,
):
    service.create_order.side_effect = exception

    response = client.post(
        "/api/orders",
        json=valid_order_payload,
        headers={"Idempotency-Key": str(uuid4())},
    )

    assert response.status_code == expected_status


def test_create_order_does_not_expose_configuration_details(
    client,
    service,
    valid_order_payload,
):
    service.create_order.side_effect = DeliveryChargeConfigurationError(
        "Sensitive internal configuration information"
    )

    response = client.post(
        "/api/orders",
        json=valid_order_payload,
        headers={"Idempotency-Key": str(uuid4())},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "Order placement is temporarily unavailable."
    )
    assert "Sensitive internal" not in response.text



def test_create_order_rejects_duplicate_product_ids(
    client,
    service,
):
    response = client.post(
        "/api/orders",
        json={
            "customer_id": 1,
            "items": [
                {"product_id": "UA-0001", "quantity": 1},
                {"product_id": "UA-0001", "quantity": 2},
            ],
        },
        headers={"Idempotency-Key": str(uuid4())},
    )

    assert response.status_code == 422
    assert "Duplicate product IDs" in response.json()["detail"]
    service.create_order.assert_not_called()


def test_create_order_rejects_duplicate_hold_ids(
    client,
    service,
):
    response = client.post(
        "/api/orders",
        json={
            "customer_id": 1,
            "items": [
                {
                    "product_id": "UA-0001",
                    "quantity": 1,
                    "hold_id": 101,
                },
                {
                    "product_id": "UA-0002",
                    "quantity": 1,
                    "hold_id": 101,
                },
            ],
        },
        headers={"Idempotency-Key": str(uuid4())},
    )

    assert response.status_code == 422
    assert "Duplicate hold IDs" in response.json()["detail"]
    service.create_order.assert_not_called()



def test_get_order_success(
    client,
    service,
    order_creation_result,
):
    service.get_order.return_value = order_creation_result.order

    response = client.get("/api/orders/101")

    assert response.status_code == 200
    assert response.json()["order_id"] == 101
    assert response.json()["order_number"] == "UA-ORD-00101"
    assert response.json()["order_status"] == "Placed"

    service.get_order.assert_called_once_with(101)


def test_get_unknown_order(client, service):
    service.get_order.return_value = None

    response = client.get("/api/orders/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found."

    service.get_order.assert_called_once_with(999)


@pytest.mark.parametrize(
    "order_id",
    ["invalid", "0", "-1"],
)
def test_get_order_rejects_invalid_id(
    client,
    service,
    order_id,
):
    response = client.get(f"/api/orders/{order_id}")

    assert response.status_code == 422
    service.get_order.assert_not_called()



def test_get_order_items_success(
    client,
    service,
    order_creation_result,
):
    service.get_order.return_value = order_creation_result.order
    service.get_order_items.return_value = list(
        order_creation_result.items
    )

    response = client.get("/api/orders/101/items")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["order_item_id"] == 201
    assert response.json()[0]["product_id"] == "UA-0001"

    service.get_order.assert_called_once_with(101)
    service.get_order_items.assert_called_once_with(101)


def test_get_order_items_returns_empty_list(
    client,
    service,
    order_creation_result,
):
    service.get_order.return_value = order_creation_result.order
    service.get_order_items.return_value = []

    response = client.get("/api/orders/101/items")

    assert response.status_code == 200
    assert response.json() == []

    service.get_order_items.assert_called_once_with(101)


def test_get_order_items_for_unknown_order(
    client,
    service,
):
    service.get_order.return_value = None

    response = client.get("/api/orders/999/items")

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found."

    service.get_order.assert_called_once_with(999)
    service.get_order_items.assert_not_called()


@pytest.mark.parametrize(
    "order_id",
    ["invalid", "0", "-1"],
)
def test_get_order_items_rejects_invalid_id(
    client,
    service,
    order_id,
):
    response = client.get(f"/api/orders/{order_id}/items")

    assert response.status_code == 422
    service.get_order.assert_not_called()
    service.get_order_items.assert_not_called()



def test_list_orders_success(
    client,
    service,
    order_creation_result,
):
    service.list_orders.return_value = [
        order_creation_result.order
    ]

    response = client.get("/api/orders")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["order_id"] == 101

    service.list_orders.assert_called_once_with(
        customer_id=None,
        order_status=None,
        limit=20,
        offset=0,
    )


def test_list_orders_with_filters(
    client,
    service,
    order_creation_result,
):
    service.list_orders.return_value = [
        order_creation_result.order
    ]

    response = client.get(
        "/api/orders",
        params={
            "customer_id": 1,
            "order_status": "Placed",
            "limit": 10,
            "offset": 5,
        },
    )

    assert response.status_code == 200
    assert len(response.json()) == 1

    service.list_orders.assert_called_once_with(
        customer_id=1,
        order_status=OrderStatus.PLACED,
        limit=10,
        offset=5,
    )


def test_list_orders_returns_empty_list(client, service):
    service.list_orders.return_value = []

    response = client.get("/api/orders")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize(
    ("params", "expected_status"),
    [
        ({"limit": 0}, 422),
        ({"limit": 101}, 422),
        ({"offset": -1}, 422),
        ({"customer_id": "invalid"}, 422),
        ({"order_status": "InvalidStatus"}, 422),
    ],
)
def test_list_orders_rejects_invalid_parameters(
    client,
    service,
    params,
    expected_status,
):
    response = client.get("/api/orders", params=params)

    assert response.status_code == expected_status
    service.list_orders.assert_not_called()


def test_list_orders_rejects_nonexistent_customer_id_value(
    client,
    service,
):
    service.list_orders.side_effect = ValueError(
        "customer_id must be greater than zero"
    )

    response = client.get(
        "/api/orders",
        params={"customer_id": 0},
    )

    assert response.status_code == 422
    service.list_orders.assert_called_once()
