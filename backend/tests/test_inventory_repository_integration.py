from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import uuid4

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


def create_test_order(connection, product_id, quantity, order_number):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO customers (full_name, mobile_number)
            VALUES ('Inventory Integration Test', '9999990001')
            RETURNING customer_id
            """
        )
        customer_id = cursor.fetchone()[0]

        total = quantity * 100

        cursor.execute(
            """
            INSERT INTO orders (
                order_number,
                customer_id,
                payment_due_at,
                order_status,
                subtotal,
                grand_total
            )
            VALUES (
                %s,
                %s,
                CURRENT_TIMESTAMP + INTERVAL '24 hours',
                'Placed',
                %s,
                %s
            )
            RETURNING order_id
            """,
            (order_number, customer_id, total, total),
        )
        order_id = cursor.fetchone()[0]

        cursor.execute(
            """
            INSERT INTO order_items (
                order_id,
                product_id,
                product_name,
                category,
                quantity,
                unit_price,
                line_total
            )
            VALUES (%s, %s, 'Integration Test Saree', 'Saree', %s, 100, %s)
            RETURNING order_item_id
            """,
            (order_id, product_id, quantity, total),
        )
        order_item_id = cursor.fetchone()[0]

    return order_id, order_item_id


def test_order_commitment_reduces_available_stock(isolated_repository):
    repository, connection = isolated_repository

    initial = repository.get_inventory_snapshot("UA-0001")

    assert initial is not None
    assert initial.stock_quantity == 12

    create_test_order(
        connection=connection,
        product_id="UA-0001",
        quantity=5,
        order_number="TEST-IM-4B-ORDER-001",
    )

    inventory = repository.get_inventory_snapshot("UA-0001")

    assert inventory is not None
    assert inventory.stock_quantity == 12
    assert inventory.held_quantity == 0
    assert inventory.ordered_quantity == 5
    assert inventory.reserved_quantity == 5
    assert inventory.available_quantity == 7


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

    product_holds = repository.list_active_holds(product_id="UA-0001")

    matching_hold = next(
        hold for hold in product_holds if hold.hold_id == result.hold_id
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

    assert not any(hold.hold_id == creation.hold_id for hold in active_holds)


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


def test_partial_dispatch_transfers_order_commitment_to_physical_stock(
    isolated_repository,
):
    repository, connection = isolated_repository

    order_id, order_item_id = create_test_order(
        connection=connection,
        product_id="UA-0001",
        quantity=5,
        order_number="TEST-IM-4B-ORDER-002",
    )

    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO shipments (
                order_id,
                shipment_number,
                shipment_status,
                dispatched_at
            )
            VALUES (%s, %s, 'Dispatched', CURRENT_TIMESTAMP)
            RETURNING shipment_id
            """,
            (order_id, "TEST-IM-4B-SHIPMENT-002"),
        )
        shipment_id = cursor.fetchone()[0]

        cursor.execute(
            """
            INSERT INTO shipment_items (
                shipment_id,
                order_id,
                order_item_id,
                quantity
            )
            VALUES (%s, %s, %s, 2)
            """,
            (shipment_id, order_id, order_item_id),
        )

        # Simulate the physical stock deduction that the future
        # shipment dispatch service must perform atomically.
        cursor.execute(
            """
            UPDATE products
            SET stock_quantity = stock_quantity - 2
            WHERE product_id = %s
            """,
            ("UA-0001",),
        )

    inventory = repository.get_inventory_snapshot("UA-0001")

    assert inventory is not None
    assert inventory.stock_quantity == 10
    assert inventory.ordered_quantity == 3
    assert inventory.reserved_quantity == 3
    assert inventory.available_quantity == 7


def test_cancelled_order_does_not_reserve_inventory(isolated_repository):
    repository, connection = isolated_repository

    order_id, _ = create_test_order(
        connection=connection,
        product_id="UA-0001",
        quantity=5,
        order_number="TEST-IM-4B-ORDER-003",
    )

    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE orders
            SET order_status = 'Cancelled'
            WHERE order_id = %s
            """,
            (order_id,),
        )

    inventory = repository.get_inventory_snapshot("UA-0001")

    assert inventory is not None
    assert inventory.stock_quantity == 12
    assert inventory.held_quantity == 0
    assert inventory.ordered_quantity == 0
    assert inventory.reserved_quantity == 0
    assert inventory.available_quantity == 12


def test_create_hold_respects_existing_order_commitments(
    isolated_repository,
):
    repository, connection = isolated_repository

    create_test_order(
        connection=connection,
        product_id="UA-0001",
        quantity=5,
        order_number="TEST-IM-4B-ORDER-004",
    )

    # Physical stock 12 - order commitment 5 = 7 available.
    rejected = repository.create_hold(
        product_id="UA-0001",
        quantity=8,
        customer_reference="TEST-ORDER-COMMITMENT",
    )

    assert rejected.created is False
    assert rejected.hold_id is None
    assert rejected.available_quantity == 7
    assert rejected.reason == ReservationReason.INSUFFICIENT_STOCK

    # A hold for the remaining 7 units should succeed.
    accepted = repository.create_hold(
        product_id="UA-0001",
        quantity=7,
        customer_reference="TEST-ORDER-COMMITMENT",
    )

    assert accepted.created is True
    assert accepted.hold_id is not None
    assert accepted.available_quantity == 0

    inventory = repository.get_inventory_snapshot("UA-0001")

    assert inventory is not None
    assert inventory.stock_quantity == 12
    assert inventory.held_quantity == 7
    assert inventory.ordered_quantity == 5
    assert inventory.reserved_quantity == 12
    assert inventory.available_quantity == 0


def test_inventory_snapshot_includes_holds_and_order_commitments(
    isolated_repository,
):
    repository, connection = isolated_repository

    create_test_order(
        connection=connection,
        product_id="UA-0001",
        quantity=5,
        order_number="TEST-IM-4B-ORDER-005",
    )

    hold = repository.create_hold(
        product_id="UA-0001",
        quantity=3,
        customer_reference="TEST-COMBINED-COMMITMENT",
    )

    assert hold.created is True

    inventory = repository.get_inventory_snapshot("UA-0001")

    assert inventory is not None
    assert inventory.stock_quantity == 12
    assert inventory.held_quantity == 3
    assert inventory.ordered_quantity == 5
    assert inventory.reserved_quantity == 8
    assert inventory.available_quantity == 4


@pytest.mark.parametrize(
    "shipment_status",
    ["In Transit", "Delivered", "Failed", "Returned"],
)
def test_post_dispatch_statuses_reduce_order_commitment(
    isolated_repository,
    shipment_status,
):
    repository, connection = isolated_repository

    order_id, order_item_id = create_test_order(
        connection=connection,
        product_id="UA-0001",
        quantity=5,
        order_number=(f"TEST-IM-4B-STATUS-{shipment_status.upper().replace(' ', '-')}"),
    )

    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO shipments (
                order_id,
                shipment_number,
                shipment_status,
                dispatched_at,
                delivered_at
            )
            VALUES (
                %s, %s, %s, CURRENT_TIMESTAMP,
                CASE WHEN %s = 'Delivered'
                     THEN CURRENT_TIMESTAMP ELSE NULL END
            )
            RETURNING shipment_id
            """,
            (
                order_id,
                f"TEST-SHIP-{shipment_status.upper().replace(' ', '-')}",
                shipment_status,
                shipment_status,
            ),
        )
        shipment_id = cursor.fetchone()[0]

        cursor.execute(
            """
            INSERT INTO shipment_items (
                shipment_id,
                order_id,
                order_item_id,
                quantity
            )
            VALUES (%s, %s, %s, 2)
            """,
            (shipment_id, order_id, order_item_id),
        )

        # Simulate the physical-stock deduction performed at dispatch.
        cursor.execute(
            """
            UPDATE products
            SET stock_quantity = stock_quantity - 2
            WHERE product_id = 'UA-0001'
            """
        )

    inventory = repository.get_inventory_snapshot("UA-0001")

    assert inventory is not None
    assert inventory.stock_quantity == 10
    assert inventory.ordered_quantity == 3
    assert inventory.reserved_quantity == 3
    assert inventory.available_quantity == 7


@pytest.mark.parametrize(
    "shipment_status",
    ["Planned", "Ready", "Cancelled"],
)
def test_pre_dispatch_statuses_do_not_reduce_order_commitment(
    isolated_repository,
    shipment_status,
):
    repository, connection = isolated_repository

    order_id, order_item_id = create_test_order(
        connection=connection,
        product_id="UA-0001",
        quantity=5,
        order_number=(f"TEST-IM-4B-PRE-{shipment_status.upper()}"),
    )

    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO shipments (
                order_id,
                shipment_number,
                shipment_status
            )
            VALUES (%s, %s, %s)
            RETURNING shipment_id
            """,
            (
                order_id,
                f"TEST-SHIP-PRE-{shipment_status.upper()}",
                shipment_status,
            ),
        )
        shipment_id = cursor.fetchone()[0]

        cursor.execute(
            """
            INSERT INTO shipment_items (
                shipment_id,
                order_id,
                order_item_id,
                quantity
            )
            VALUES (%s, %s, %s, 2)
            """,
            (shipment_id, order_id, order_item_id),
        )

    inventory = repository.get_inventory_snapshot("UA-0001")

    assert inventory is not None
    assert inventory.stock_quantity == 12
    assert inventory.ordered_quantity == 5
    assert inventory.reserved_quantity == 5
    assert inventory.available_quantity == 7


def test_concurrent_holds_do_not_oversell_inventory():
    product_id = "UA-0001"
    test_token = uuid4().hex
    references = [
        f"CONCURRENCY-{test_token}-A",
        f"CONCURRENCY-{test_token}-B",
    ]
    barrier = Barrier(2)

    def reserve_inventory(customer_reference):
        connection = get_database_connection()

        try:
            repository = PostgresInventoryRepository(connection)

            # Both workers wait here before attempting reservation.
            barrier.wait(timeout=10)

            result = repository.create_hold(
                product_id=product_id,
                quantity=7,
                customer_reference=customer_reference,
            )

            return result
        finally:
            connection.close()

    cleanup_connection = get_database_connection()

    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(reserve_inventory, reference)
                for reference in references
            ]

            results = [future.result(timeout=30) for future in futures]

        successful = [result for result in results if result.created]
        rejected = [result for result in results if not result.created]

        assert len(successful) == 1
        assert len(rejected) == 1

        assert rejected[0].reason == ReservationReason.INSUFFICIENT_STOCK

        with cleanup_connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT COALESCE(SUM(quantity), 0)
                FROM product_holds
                WHERE product_id = %s
                  AND customer_reference = ANY(%s)
                  AND status = 'Active'
                """,
                (product_id, references),
            )
            active_quantity = cursor.fetchone()[0]

            assert active_quantity == 7

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM product_holds
                WHERE product_id = %s
                  AND customer_reference = ANY(%s)
                """,
                (product_id, references),
            )
            hold_count = cursor.fetchone()[0]

            assert hold_count == 1

    finally:
        cleanup_connection.rollback()

        with cleanup_connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM product_holds
                WHERE product_id = %s
                  AND customer_reference = ANY(%s)
                """,
                (product_id, references),
            )

        cleanup_connection.commit()
        cleanup_connection.close()
