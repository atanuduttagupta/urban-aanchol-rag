import pytest

from backend.app.customers.customer_repository import (
    PostgresCustomerRepository,
)
from backend.app.database.connection import get_database_connection


class RollbackTestTransaction(Exception):
    pass


@pytest.fixture
def isolated_repository():
    connection = get_database_connection()

    try:
        try:
            with connection.transaction():
                repository = PostgresCustomerRepository(connection)
                yield repository, connection

                # Roll back every test write.
                raise RollbackTestTransaction()
        except RollbackTestTransaction:
            pass
    finally:
        connection.close()


def create_test_customer(
    repository,
    suffix="001",
):
    return repository.create_customer({
        "full_name": f"Integration Test Customer {suffix}",
        "mobile_number": "9876543210",
        "whatsapp_number": "9876543211",
        "email": f"customer{suffix}@example.com",
        "bill_to_address": "Kolkata",
        "notes": "Integration test",
    })


def test_create_customer(isolated_repository):
    repository, _ = isolated_repository

    customer = create_test_customer(repository)

    assert customer.customer_id > 0
    assert customer.full_name == "Integration Test Customer 001"
    assert customer.mobile_number == "9876543210"
    assert customer.whatsapp_number == "9876543211"
    assert customer.email == "customer001@example.com"
    assert customer.bill_to_address == "Kolkata"
    assert customer.notes == "Integration test"
    assert customer.created_at is not None
    assert customer.updated_at is not None


def test_create_customer_with_optional_fields_omitted(
    isolated_repository,
):
    repository, _ = isolated_repository

    customer = repository.create_customer({
        "full_name": "Minimal Test Customer",
        "mobile_number": "9876543210",
    })

    assert customer.full_name == "Minimal Test Customer"
    assert customer.whatsapp_number is None
    assert customer.email is None
    assert customer.bill_to_address is None
    assert customer.notes is None
    assert customer.attribute1 is None
    assert customer.attribute5 is None


def test_get_customer_by_id(isolated_repository):
    repository, _ = isolated_repository

    created = create_test_customer(repository)

    retrieved = repository.get_customer(created.customer_id)

    assert retrieved == created


def test_get_unknown_customer_returns_none(isolated_repository):
    repository, _ = isolated_repository

    assert repository.get_customer(-1) is None


def test_list_customers(isolated_repository):
    repository, _ = isolated_repository

    first = create_test_customer(repository, "LIST-A")
    second = create_test_customer(repository, "LIST-B")

    customers = repository.list_customers(limit=100)

    customer_ids = {customer.customer_id for customer in customers}

    assert first.customer_id in customer_ids
    assert second.customer_id in customer_ids


def test_list_customers_search_by_name(isolated_repository):
    repository, _ = isolated_repository

    customer = create_test_customer(repository, "SEARCH-NAME")

    results = repository.list_customers(
        search="SEARCH-NAME",
    )

    assert any(
        item.customer_id == customer.customer_id
        for item in results
    )


def test_list_customers_search_by_mobile(isolated_repository):
    repository, _ = isolated_repository

    customer = create_test_customer(repository, "SEARCH-MOBILE")

    results = repository.list_customers(
        search="9876543210",
    )

    assert any(
        item.customer_id == customer.customer_id
        for item in results
    )


def test_list_customers_search_by_email(isolated_repository):
    repository, _ = isolated_repository

    customer = create_test_customer(repository, "SEARCH-EMAIL")

    results = repository.list_customers(
        search="customerSEARCH-EMAIL@example.com",
    )

    assert any(
        item.customer_id == customer.customer_id
        for item in results
    )


def test_list_customers_pagination(isolated_repository):
    repository, _ = isolated_repository

    first = create_test_customer(repository, "PAGE-A")
    second = create_test_customer(repository, "PAGE-B")
    third = create_test_customer(repository, "PAGE-C")

    customers = repository.list_customers(
        limit=2,
        offset=0,
    )

    customer_ids = {customer.customer_id for customer in customers}

    assert len(customers) == 2
    assert first.customer_id not in customer_ids
    assert second.customer_id in customer_ids
    assert third.customer_id in customer_ids


def test_update_customer(isolated_repository):
    repository, _ = isolated_repository

    created = create_test_customer(repository)

    updated = repository.update_customer(
        created.customer_id,
        {
            "full_name": "Updated Integration Customer",
            "whatsapp_number": "9876543212",
            "notes": "Updated notes",
        },
    )

    assert updated is not None
    assert updated.customer_id == created.customer_id
    assert updated.full_name == "Updated Integration Customer"
    assert updated.whatsapp_number == "9876543212"
    assert updated.notes == "Updated notes"
    assert updated.mobile_number == created.mobile_number


def test_update_customer_can_clear_optional_field(
    isolated_repository,
):
    repository, _ = isolated_repository

    created = create_test_customer(repository)

    updated = repository.update_customer(
        created.customer_id,
        {"email": None},
    )

    assert updated is not None
    assert updated.email is None


def test_update_unknown_customer_returns_none(isolated_repository):
    repository, _ = isolated_repository

    result = repository.update_customer(
        -1,
        {"notes": "Unknown customer"},
    )

    assert result is None


def test_update_customer_rejects_unknown_fields(
    isolated_repository,
):
    repository, _ = isolated_repository

    with pytest.raises(ValueError, match="Invalid customer update fields"):
        repository.update_customer(
            1,
            {"customer_id": 999},
        )


def test_update_customer_with_no_fields_returns_existing_record(
    isolated_repository,
):
    repository, _ = isolated_repository

    created = create_test_customer(repository)

    result = repository.update_customer(
        created.customer_id,
        {},
    )

    assert result == created