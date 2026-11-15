
import pytest

from backend.app.database.connection import get_database_connection
from backend.app.inventory.inventory_repository import (
    PostgresInventoryRepository,
)
from backend.app.inventory.models import (
    HoldReleaseReason,
    HoldStatus,
    ReservationReason,
)


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


def test_list_active_holds_and_filter_by_product(isolated_repository):
    repository, _ = isolated_repository

    result = repository.create_hold(
        product_id="UA-0001",
        quantity=1,
        customer_reference="TEST-IM-3B-LIST",
    )

    assert result.created is True

    all_holds = repository.list_active_holds()

    assert any(hold.hold_id == result.hold_id for hold in all_holds)

    product_holds = repository.list_active_holds(
        product_id="UA-0001"
    )

    matching_hold = next(
        hold for hold in product_holds
        if hold.hold_id == result.hold_id
    )

    assert matching_hold.product_id == "UA-0001"
    assert matching_hold.quantity == 1
    assert matching_hold.customer_reference == "TEST-IM-3B-LIST"
    assert matching_hold.status == HoldStatus.ACTIVE


def test_release_active_hold_and_preserve_physical_stock(
    isolated_repository,
):
    repository, connection = isolated_repository

    initial_inventory = repository.get_inventory_snapshot("UA-0001")

    assert initial_inventory is not None

    creation = repository.create_hold(
        product_id="UA-0001",
        quantity=2,
        customer_reference="TEST-IM-3B-RELEASE",
    )

    assert creation.created is True

    result = repository.release_hold(creation.hold_id)

    assert result.released is True
    assert result.hold_id == creation.hold_id
    assert result.product_id == "UA-0001"
    assert result.reason == HoldReleaseReason.HOLD_RELEASED

    updated_inventory = repository.get_inventory_snapshot("UA-0001")

    assert updated_inventory is not None
    assert updated_inventory.stock_quantity == initial_inventory.stock_quantity
    assert updated_inventory.available_quantity == initial_inventory.available_quantity

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT status
            FROM product_holds
            WHERE hold_id = %s
            """,
            (creation.hold_id,),
        )
        row = cursor.fetchone()

    assert row == ("Released",)

    active_holds = repository.list_active_holds("UA-0001")

    assert not any(
        hold.hold_id == creation.hold_id
        for hold in active_holds
    )


def test_release_unknown_hold(isolated_repository):
    repository, _ = isolated_repository

    result = repository.release_hold(-1)

    assert result.released is False
    assert result.hold_id == -1
    assert result.product_id is None
    assert result.reason == HoldReleaseReason.HOLD_NOT_FOUND


def test_release_already_released_hold(isolated_repository):
    repository, _ = isolated_repository

    creation = repository.create_hold(
        product_id="UA-0001",
        quantity=1,
        customer_reference="TEST-IM-3B-REPEAT",
    )

    assert creation.created is True

    first_release = repository.release_hold(creation.hold_id)
    second_release = repository.release_hold(creation.hold_id)

    assert first_release.released is True
    assert second_release.released is False
    assert second_release.reason == HoldReleaseReason.HOLD_NOT_ACTIVE


def test_release_converted_hold_is_rejected(isolated_repository):
    repository, connection = isolated_repository

    creation = repository.create_hold(
        product_id="UA-0001",
        quantity=1,
        customer_reference="TEST-IM-3B-CONVERTED",
    )

    assert creation.created is True

    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE product_holds
            SET status = 'Converted'
            WHERE hold_id = %s
            """,
            (creation.hold_id,),
        )

    result = repository.release_hold(creation.hold_id)

    assert result.released is False
    assert result.reason == HoldReleaseReason.HOLD_NOT_ACTIVE