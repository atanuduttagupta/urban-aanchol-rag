from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from backend.app.customers.customer_service import CustomerService
from backend.app.customers.models import Customer


@pytest.fixture
def repository():
    return MagicMock()


@pytest.fixture
def service(repository):
    return CustomerService(repository)


@pytest.fixture
def customer():
    now = datetime.now(UTC)
    return Customer(
        customer_id=1,
        full_name="Test Customer",
        mobile_number="9876543210",
        whatsapp_number=None,
        email=None,
        bill_to_contact_name=None,
        bill_to_phone=None,
        bill_to_address=None,
        ship_to_contact_name=None,
        ship_to_phone=None,
        ship_to_address=None,
        notes=None,
        attribute1=None,
        attribute2=None,
        attribute3=None,
        attribute4=None,
        attribute5=None,
        created_at=now,
        updated_at=now,
    )


def test_create_customer_success(service, repository, customer):
    repository.create_customer.return_value = customer

    result = service.create_customer({
        "full_name": " Test Customer ",
        "mobile_number": " 9876543210 ",
    })

    assert result == customer

    data = repository.create_customer.call_args.args[0]
    assert data["full_name"] == "Test Customer"
    assert data["mobile_number"] == "9876543210"


@pytest.mark.parametrize(
    "data",
    [
        {"mobile_number": "9876543210"},
        {"full_name": "Test Customer"},
        {"full_name": " ", "mobile_number": "9876543210"},
        {"full_name": "Test Customer", "mobile_number": " "},
    ],
)
def test_create_customer_rejects_missing_required_fields(
    service, repository, data
):
    with pytest.raises(ValueError):
        service.create_customer(data)

    repository.create_customer.assert_not_called()


def test_create_customer_rejects_invalid_email(service, repository):
    with pytest.raises(ValueError, match="Invalid email"):
        service.create_customer({
            "full_name": "Test Customer",
            "mobile_number": "9876543210",
            "email": "invalid-email",
        })

    repository.create_customer.assert_not_called()


@pytest.mark.parametrize(
    "field",
    ["mobile_number", "whatsapp_number", "bill_to_phone", "ship_to_phone"],
)
def test_create_customer_rejects_invalid_phone_characters(
    service, repository, field
):
    with pytest.raises(ValueError, match="invalid characters"):
        service.create_customer({
            "full_name": "Test Customer",
            "mobile_number": "9876543210",
            field: "phone@invalid",
        })

    repository.create_customer.assert_not_called()


@pytest.mark.parametrize(
    "phone",
    [
        "91+9876543210",
        "++91 9876543210",
    ],
)
def test_create_customer_rejects_misplaced_or_repeated_plus(
    service, repository, phone
):
    with pytest.raises(ValueError, match="invalid characters"):
        service.create_customer({
            "full_name": "Test Customer",
            "mobile_number": phone,
        })

    repository.create_customer.assert_not_called()


@pytest.mark.parametrize(
    "phone",
    [
        "9876543210",
        "+91 9876543210",
        "+91-9876543210",
        "(033) 2345-6789",
    ],
)
def test_create_customer_accepts_valid_phone_formats(
    service, repository, phone
):
    service.create_customer({
        "full_name": "Test Customer",
        "mobile_number": phone,
    })

    repository.create_customer.assert_called_once()


    @pytest.mark.parametrize(
        "field",
        ["mobile_number", "whatsapp_number", "bill_to_phone", "ship_to_phone"],
    )
    @pytest.mark.parametrize("phone", ["++++", "---", "()"])
    def test_create_customer_rejects_phone_without_digits(
        service, repository, field, phone
    ):
        with pytest.raises(ValueError, match="at least one digit"):
            service.create_customer({
                "full_name": "Test Customer",
                "mobile_number": "9876543210",
                field: phone,
            })

        repository.create_customer.assert_not_called()


def test_create_customer_accepts_optional_fields(service, repository, customer):
    repository.create_customer.return_value = customer

    service.create_customer({
        "full_name": "Test Customer",
        "mobile_number": "9876543210",
        "whatsapp_number": None,
        "email": None,
        "notes": "  WhatsApp customer  ",
    })

    data = repository.create_customer.call_args.args[0]
    assert data["whatsapp_number"] is None
    assert data["email"] is None
    assert data["notes"] == "WhatsApp customer"


def test_create_customer_rejects_unknown_fields(service, repository):
    with pytest.raises(ValueError, match="Unknown customer fields"):
        service.create_customer({
            "full_name": "Test Customer",
            "mobile_number": "9876543210",
            "unexpected": "value",
        })

    repository.create_customer.assert_not_called()


def test_get_customer_success(service, repository, customer):
    repository.get_customer.return_value = customer

    assert service.get_customer(1) == customer
    repository.get_customer.assert_called_once_with(1)


@pytest.mark.parametrize("customer_id", [0, -1, True, "1", None])
def test_get_customer_rejects_invalid_id(service, repository, customer_id):
    with pytest.raises(ValueError):
        service.get_customer(customer_id)

    repository.get_customer.assert_not_called()


def test_list_customers_success(service, repository, customer):
    repository.list_customers.return_value = [customer]

    result = service.list_customers(
        search="  Test  ",
        limit=10,
        offset=5,
    )

    assert result == [customer]
    repository.list_customers.assert_called_once_with(
        search="Test",
        limit=10,
        offset=5,
    )


@pytest.mark.parametrize("limit", [0, -1, 101, True, "10"])
def test_list_customers_rejects_invalid_limit(service, repository, limit):
    with pytest.raises(ValueError):
        service.list_customers(limit=limit)

    repository.list_customers.assert_not_called()


@pytest.mark.parametrize("offset", [-1, True, "5"])
def test_list_customers_rejects_invalid_offset(service, repository, offset):
    with pytest.raises(ValueError):
        service.list_customers(offset=offset)

    repository.list_customers.assert_not_called()


def test_update_customer_partial_success(service, repository, customer):
    repository.update_customer.return_value = customer

    result = service.update_customer(
        1,
        {"whatsapp_number": "9876543211"},
    )

    assert result == customer
    repository.update_customer.assert_called_once_with(
        1,
        {"whatsapp_number": "9876543211"},
    )


@pytest.mark.parametrize(
    "updates",
    [
        {"full_name": None},
        {"full_name": ""},
        {"mobile_number": None},
        {"mobile_number": " "},
    ],
)
def test_update_customer_rejects_clearing_required_fields(
    service, repository, updates
):
    with pytest.raises(ValueError):
        service.update_customer(1, updates)

    repository.update_customer.assert_not_called()


def test_update_customer_can_clear_optional_field(service, repository, customer):
    repository.update_customer.return_value = customer

    service.update_customer(1, {"email": None})

    repository.update_customer.assert_called_once_with(
        1,
        {"email": None},
    )


def test_update_customer_rejects_empty_updates(service, repository):
    with pytest.raises(ValueError, match="At least one update"):
        service.update_customer(1, {})

    repository.update_customer.assert_not_called()


def test_update_customer_rejects_unknown_fields(service, repository):
    with pytest.raises(ValueError, match="Unknown customer fields"):
        service.update_customer(1, {"customer_id": 2})

    repository.update_customer.assert_not_called()


def test_update_customer_returns_none_for_unknown_customer(
    service, repository
):
    repository.update_customer.return_value = None

    result = service.update_customer(
        999,
        {"notes": "Updated"},
    )

    assert result is None