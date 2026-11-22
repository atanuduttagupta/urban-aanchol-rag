from dataclasses import replace
from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from backend.app.orders.idempotency import (
    calculate_advisory_lock_id,
    calculate_order_request_hash,
)
from backend.app.orders.models import (
    CreateOrderRequest,
    OrderItemRequest,
)


@pytest.fixture
def order_request():
    return CreateOrderRequest(
        customer_id=1,
        items=(
            OrderItemRequest(
                product_id="UA-0001",
                quantity=2,
                line_discount=Decimal("100.00"),
                notes="Red border preference",
                hold_id=10,
            ),
        ),
        discount_amount=Decimal("200.00"),
        expected_delivery_date=date(2026, 12, 15),
        ship_to_contact_name="Customer One",
        ship_to_phone="9876543210",
        ship_to_address="Kolkata, West Bengal",
        notes="Festival delivery",
    )


def test_identical_requests_generate_same_hash(order_request):
    first_hash = calculate_order_request_hash(order_request)
    second_hash = calculate_order_request_hash(order_request)

    assert first_hash == second_hash


def test_hash_is_64_character_sha256(order_request):
    result = calculate_order_request_hash(order_request)

    assert len(result) == 64
    assert all(character in "0123456789abcdef" for character in result)


def test_different_customer_generates_different_hash(order_request):
    changed = replace(order_request, customer_id=2)

    assert calculate_order_request_hash(order_request) != (
        calculate_order_request_hash(changed)
    )


@pytest.mark.parametrize(
    "field,value",
    [
        ("discount_amount", Decimal("250.00")),
        ("expected_delivery_date", date(2026, 12, 20)),
        ("ship_to_contact_name", "Customer Two"),
        ("ship_to_phone", "9999999999"),
        ("ship_to_address", "Howrah, West Bengal"),
        ("notes", "Urgent delivery"),
    ],
)
def test_order_level_changes_generate_different_hash(
    order_request,
    field,
    value,
):
    changed = replace(order_request, **{field: value})

    assert calculate_order_request_hash(order_request) != (
        calculate_order_request_hash(changed)
    )


@pytest.mark.parametrize(
    "field,value",
    [
        ("product_id", "UA-0002"),
        ("quantity", 3),
        ("line_discount", Decimal("150.00")),
        ("notes", "Different item preference"),
        ("hold_id", 11),
    ],
)
def test_order_item_changes_generate_different_hash(
    order_request,
    field,
    value,
):
    changed_item = replace(
        order_request.items[0],
        **{field: value},
    )

    changed = replace(
        order_request,
        items=(changed_item,),
    )

    assert calculate_order_request_hash(order_request) != (
        calculate_order_request_hash(changed)
    )


def test_item_order_affects_hash():
    first_item = OrderItemRequest(
        product_id="UA-0001",
        quantity=1,
    )

    second_item = OrderItemRequest(
        product_id="UA-0002",
        quantity=1,
    )

    first_request = CreateOrderRequest(
        customer_id=1,
        items=(first_item, second_item),
    )

    second_request = CreateOrderRequest(
        customer_id=1,
        items=(second_item, first_item),
    )

    assert calculate_order_request_hash(first_request) != (
        calculate_order_request_hash(second_request)
    )


def test_advisory_lock_id_is_deterministic():
    key = uuid4()

    first = calculate_advisory_lock_id(101, key)
    second = calculate_advisory_lock_id(101, key)

    assert first == second


def test_advisory_lock_id_differs_for_different_customers():
    key = uuid4()

    first = calculate_advisory_lock_id(101, key)
    second = calculate_advisory_lock_id(102, key)

    assert first != second


def test_advisory_lock_id_differs_for_different_keys():
    first = calculate_advisory_lock_id(101, uuid4())
    second = calculate_advisory_lock_id(101, uuid4())

    assert first != second


def test_advisory_lock_id_fits_signed_64_bit_integer():
    lock_id = calculate_advisory_lock_id(101, uuid4())

    assert -(2**63) <= lock_id < 2**63


@pytest.mark.parametrize(
    "value",
    [
        Decimal("200"),
        Decimal("200.0"),
        Decimal("200.000"),
    ],
)
def test_equivalent_order_discounts_generate_same_hash(order_request, value):
    changed = replace(order_request, discount_amount=value)

    assert calculate_order_request_hash(order_request) == (
        calculate_order_request_hash(changed)
    )


@pytest.mark.parametrize(
    "value",
    [
        Decimal("100"),
        Decimal("100.0"),
        Decimal("100.000"),
    ],
)
def test_equivalent_line_discounts_generate_same_hash(order_request, value):
    changed_item = replace(
        order_request.items[0],
        line_discount=value,
    )
    changed = replace(order_request, items=(changed_item,))

    assert calculate_order_request_hash(order_request) == (
        calculate_order_request_hash(changed)
    )
