from decimal import Decimal
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from backend.app.customers.customer_repository import (
    PostgresCustomerRepository,
)
from backend.app.orders.delivery_charge import (
    DeliveryChargeConfigurationError,
)
from backend.app.orders.models import (
    CreateOrderRequest,
    OrderItemRequest,
    OrderStatus,
)
from backend.app.orders.order_repository import PostgresOrderRepository
from backend.app.orders.order_service import OrderService


@pytest.fixture
def connection():
    return MagicMock()


@pytest.fixture
def idempotency_key():
    return uuid4()


@pytest.fixture
def order_repository(connection):
    repository = PostgresOrderRepository(connection)

    repository.create_order = MagicMock()
    repository.get_order = MagicMock()
    repository.get_order_items = MagicMock()
    repository.list_orders = MagicMock()

    return repository


@pytest.fixture
def customer_repository(connection):
    return PostgresCustomerRepository(connection)


@pytest.fixture
def service(order_repository, customer_repository):
    return OrderService(order_repository, customer_repository)


@pytest.fixture
def order_request():
    return CreateOrderRequest(
        customer_id=1,
        items=(
            OrderItemRequest(
                product_id="UA-0001",
                quantity=2,
            ),
        ),
    )


# ---------------------------------------------------------
# Constructor tests
# ---------------------------------------------------------


def test_order_service_initialization(
    order_repository,
    customer_repository,
):
    service = OrderService(order_repository, customer_repository)

    assert service.order_repository is order_repository
    assert service.customer_repository is customer_repository


@pytest.mark.parametrize(
    "order_repo, customer_repo",
    [
        (None, None),
        (object(), object()),
        (None, PostgresCustomerRepository(MagicMock())),
        (PostgresOrderRepository(MagicMock()), None),
    ],
)
def test_constructor_rejects_invalid_repositories(
    order_repo,
    customer_repo,
):
    with pytest.raises(ValueError):
        OrderService(order_repo, customer_repo)


# ---------------------------------------------------------
# Create order tests
# ---------------------------------------------------------


def test_create_order_success(
    service,
    order_repository,
    customer_repository,
    order_request,
    idempotency_key,
    monkeypatch,
):
    expected_result = object()
    expected_charge = Decimal("80.00")

    get_charge = MagicMock(return_value=expected_charge)

    monkeypatch.setattr(
        "backend.app.orders.order_service.get_flat_delivery_charge",
        get_charge,
    )

    order_repository.create_order = MagicMock(return_value=expected_result)

    result = service.create_order(
        order_request,
        idempotency_key,
    )

    assert result is expected_result

    get_charge.assert_called_once_with()

    order_repository.create_order.assert_called_once_with(
        request=order_request,
        delivery_charge=expected_charge,
        customer_repository=customer_repository,
        idempotency_key=idempotency_key,
    )


def test_create_order_rejects_invalid_request(
    service,
    order_repository,
    idempotency_key,
    monkeypatch,
):
    get_charge = MagicMock()

    monkeypatch.setattr(
        "backend.app.orders.order_service.get_flat_delivery_charge",
        get_charge,
    )

    with pytest.raises(ValueError):
        service.create_order("invalid request", idempotency_key)

    get_charge.assert_not_called()
    order_repository.create_order.assert_not_called()


def test_create_order_rejects_different_database_connections(
    order_repository,
    customer_repository,
    order_request,
    idempotency_key,
    monkeypatch,
):
    other_customer_repository = PostgresCustomerRepository(MagicMock())

    service = OrderService(
        order_repository,
        other_customer_repository,
    )

    get_charge = MagicMock()

    monkeypatch.setattr(
        "backend.app.orders.order_service.get_flat_delivery_charge",
        get_charge,
    )

    with pytest.raises(ValueError, match="same database connection"):
        service.create_order(order_request, idempotency_key)

    get_charge.assert_not_called()


def test_create_order_propagates_delivery_configuration_error(
    service,
    order_repository,
    order_request,
    idempotency_key,
    monkeypatch,
):
    monkeypatch.setattr(
        "backend.app.orders.order_service.get_flat_delivery_charge",
        MagicMock(
            side_effect=DeliveryChargeConfigurationError(
                "Delivery charge is not configured"
            )
        ),
    )

    with pytest.raises(DeliveryChargeConfigurationError):
        service.create_order(order_request, idempotency_key)

    order_repository.create_order.assert_not_called()


# ---------------------------------------------------------
# Get order tests
# ---------------------------------------------------------


def test_get_order_success(service, order_repository):
    expected_order = object()

    order_repository.get_order = MagicMock(return_value=expected_order)

    result = service.get_order(10)

    assert result is expected_order
    order_repository.get_order.assert_called_once_with(10)


def test_get_order_not_found(service, order_repository):
    order_repository.get_order = MagicMock(return_value=None)

    result = service.get_order(999)

    assert result is None


@pytest.mark.parametrize(
    "order_id",
    [0, -1, True, False, "10", None],
)
def test_get_order_rejects_invalid_id(service, order_repository, order_id):
    with pytest.raises(ValueError):
        service.get_order(order_id)

    order_repository.get_order.assert_not_called()


# ---------------------------------------------------------
# Get order items tests
# ---------------------------------------------------------


def test_get_order_items_success(service, order_repository):
    expected_items = [object()]

    order_repository.get_order_items = MagicMock(return_value=expected_items)

    result = service.get_order_items(10)

    assert result is expected_items
    order_repository.get_order_items.assert_called_once_with(10)


@pytest.mark.parametrize(
    "order_id",
    [0, -1, True, "10", None],
)
def test_get_order_items_rejects_invalid_id(
    service,
    order_repository,
    order_id,
):
    with pytest.raises(ValueError):
        service.get_order_items(order_id)

    order_repository.get_order_items.assert_not_called()


# ---------------------------------------------------------
# List orders tests
# ---------------------------------------------------------


def test_list_orders_success(
    service,
    order_repository,
):
    expected_orders = [object()]

    order_repository.list_orders = MagicMock(return_value=expected_orders)

    result = service.list_orders(
        customer_id=10,
        order_status=OrderStatus.PLACED,
        limit=25,
        offset=5,
    )

    assert result is expected_orders

    order_repository.list_orders.assert_called_once_with(
        customer_id=10,
        order_status=OrderStatus.PLACED,
        limit=25,
        offset=5,
    )


def test_list_orders_without_filters(service, order_repository):
    order_repository.list_orders = MagicMock(return_value=[])

    result = service.list_orders()

    assert result == []

    order_repository.list_orders.assert_called_once_with(
        customer_id=None,
        order_status=None,
        limit=20,
        offset=0,
    )


@pytest.mark.parametrize(
    "customer_id",
    [0, -1, True, "10"],
)
def test_list_orders_rejects_invalid_customer_id(
    service,
    order_repository,
    customer_id,
):
    with pytest.raises(ValueError):
        service.list_orders(customer_id=customer_id)

    order_repository.list_orders.assert_not_called()


def test_list_orders_rejects_invalid_status(
    service,
    order_repository,
):
    with pytest.raises(ValueError):
        service.list_orders(order_status="Placed")

    order_repository.list_orders.assert_not_called()


@pytest.mark.parametrize(
    "limit",
    [0, -1, 101, True, "20", 1.5],
)
def test_list_orders_rejects_invalid_limit(
    service,
    order_repository,
    limit,
):
    with pytest.raises(ValueError):
        service.list_orders(limit=limit)

    order_repository.list_orders.assert_not_called()


@pytest.mark.parametrize(
    "offset",
    [-1, True, "5", 1.5],
)
def test_list_orders_rejects_invalid_offset(
    service,
    order_repository,
    offset,
):
    with pytest.raises(ValueError):
        service.list_orders(offset=offset)

    order_repository.list_orders.assert_not_called()


@pytest.mark.parametrize(
    "idempotency_key",
    [None, "", "invalid-uuid", 123, object()],
)
def test_create_order_rejects_invalid_idempotency_key(
    service,
    order_repository,
    order_request,
    idempotency_key,
    monkeypatch,
):
    get_charge = MagicMock()

    monkeypatch.setattr(
        "backend.app.orders.order_service.get_flat_delivery_charge",
        get_charge,
    )

    with pytest.raises(ValueError, match="idempotency_key must be a UUID"):
        service.create_order(order_request, idempotency_key)

    get_charge.assert_not_called()
    order_repository.create_order.assert_not_called()
