
import pytest
from pydantic import ValidationError

from backend.app.api.schemas.orders import OrderCreateRequest


@pytest.fixture
def valid_order_payload():
    return {
        "customer_id": 1,
        "items": [
            {
                "product_id": "UA-0001",
                "quantity": 2,
            }
        ],
    }


def test_valid_order_request(valid_order_payload):
    request = OrderCreateRequest.model_validate(valid_order_payload)

    assert request.customer_id == 1
    assert len(request.items) == 1
    assert request.items[0].product_id == "UA-0001"
    assert request.items[0].quantity == 2


def test_order_request_accepts_shipping_details(valid_order_payload):
    valid_order_payload.update(
        {
            "ship_to_contact_name": "Test Customer",
            "ship_to_phone": "9876543210",
            "ship_to_address": "Kolkata",
            "notes": "Deliver carefully",
        }
    )

    request = OrderCreateRequest.model_validate(valid_order_payload)

    assert request.ship_to_contact_name == "Test Customer"
    assert request.ship_to_phone == "9876543210"
    assert request.ship_to_address == "Kolkata"


def test_order_request_rejects_missing_customer_id(valid_order_payload):
    del valid_order_payload["customer_id"]

    with pytest.raises(ValidationError):
        OrderCreateRequest.model_validate(valid_order_payload)


def test_order_request_rejects_missing_items(valid_order_payload):
    del valid_order_payload["items"]

    with pytest.raises(ValidationError):
        OrderCreateRequest.model_validate(valid_order_payload)


def test_order_request_rejects_empty_items(valid_order_payload):
    valid_order_payload["items"] = []

    with pytest.raises(ValidationError):
        OrderCreateRequest.model_validate(valid_order_payload)


@pytest.mark.parametrize("quantity", [0, -1, True, "2", 1.5])
def test_order_request_rejects_invalid_quantity(
    valid_order_payload,
    quantity,
):
    valid_order_payload["items"][0]["quantity"] = quantity

    with pytest.raises(ValidationError):
        OrderCreateRequest.model_validate(valid_order_payload)


@pytest.mark.parametrize("customer_id", [0, -1, True, "1"])
def test_order_request_rejects_invalid_customer_id(
    valid_order_payload,
    customer_id,
):
    valid_order_payload["customer_id"] = customer_id

    with pytest.raises(ValidationError):
        OrderCreateRequest.model_validate(valid_order_payload)


def test_order_request_rejects_unknown_top_level_fields(
    valid_order_payload,
):
    valid_order_payload["grand_total"] = "1000.00"

    with pytest.raises(ValidationError):
        OrderCreateRequest.model_validate(valid_order_payload)


def test_order_request_rejects_client_supplied_order_status(
    valid_order_payload,
):
    valid_order_payload["order_status"] = "Placed"

    with pytest.raises(ValidationError):
        OrderCreateRequest.model_validate(valid_order_payload)


@pytest.mark.parametrize(
    "field,value",
    [
        ("unit_price", "500.00"),
        ("line_total", "1000.00"),
        ("stock_quantity", 10),
        ("line_discount", "0.00"),
    ],
)
def test_order_item_request_rejects_unauthorized_fields(
    valid_order_payload,
    field,
    value,
):
    valid_order_payload["items"][0][field] = value

    with pytest.raises(ValidationError):
        OrderCreateRequest.model_validate(valid_order_payload)


def test_order_request_accepts_valid_hold_id(valid_order_payload):
    valid_order_payload["items"][0]["hold_id"] = 10

    request = OrderCreateRequest.model_validate(valid_order_payload)

    assert request.items[0].hold_id == 10


@pytest.mark.parametrize("hold_id", [0, -1, True, "10"])
def test_order_request_rejects_invalid_hold_id(
    valid_order_payload,
    hold_id,
):
    valid_order_payload["items"][0]["hold_id"] = hold_id

    with pytest.raises(ValidationError):
        OrderCreateRequest.model_validate(valid_order_payload)
