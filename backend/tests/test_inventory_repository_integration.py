
import pytest

from backend.app.database.connection import get_database_connection
from backend.app.inventory.inventory_repository import (
    PostgresInventoryRepository,
)
from backend.app.inventory.models import ReservationReason


class RollbackTestTransaction(Exception):
    pass


@pytest.fixture
def isolated_repository():
    connection = get_database_connection()

    try:
        try:
            with connection.transaction():
                repository = PostgresInventoryRepository(connection)
                yield repository, connection

                # Roll back every test write, even when assertions pass.
                raise RollbackTestTransaction()
        except RollbackTestTransaction:
            pass
    finally:
        connection.close()


def test_create_hold_success_and_commit_to_outer_transaction(
    isolated_repository,
):
    repository, connection = isolated_repository

    result = repository.create_hold(
        product_id="UA-0001",
        quantity=2,
        customer_reference="TEST-CUSTOMER-IM-3A",
        notes="Integration test",
    )

    assert result.created is True
    assert result.hold_id is not None
    assert result.product_id == "UA-0001"
    assert result.requested_quantity == 2
    assert result.available_quantity == 10
    assert result.reason == ReservationReason.RESERVATION_ALLOWED

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT quantity, status, customer_reference
            FROM product_holds
            WHERE hold_id = %s
            """,
            (result.hold_id,),
        )
        row = cursor.fetchone()

    assert row == (2, "Active", "TEST-CUSTOMER-IM-3A")


def test_create_hold_rejects_insufficient_stock(
    isolated_repository,
):
    repository, connection = isolated_repository

    result = repository.create_hold(
        product_id="UA-0001",
        quantity=13,
        customer_reference="TEST-CUSTOMER-IM-3A",
    )

    assert result.created is False
    assert result.hold_id is None
    assert result.available_quantity == 12
    assert result.reason == ReservationReason.INSUFFICIENT_STOCK

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM product_holds
            WHERE product_id = 'UA-0001'
              AND customer_reference = 'TEST-CUSTOMER-IM-3A'
            """
        )
        count = cursor.fetchone()[0]

    assert count == 0


def test_create_hold_rejects_unknown_product(
    isolated_repository,
):
    repository, _ = isolated_repository

    result = repository.create_hold(
        product_id="UA-9999",
        quantity=1,
        customer_reference="TEST-CUSTOMER-IM-3A",
    )

    assert result.created is False
    assert result.hold_id is None
    assert result.available_quantity is None
    assert result.reason == ReservationReason.PRODUCT_NOT_FOUND
