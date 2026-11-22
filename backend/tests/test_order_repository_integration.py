from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from threading import Barrier
from uuid import uuid4

import pytest
from psycopg.errors import RaiseException

from backend.app.customers.customer_repository import (
    PostgresCustomerRepository,
)
from backend.app.database.connection import get_database_connection
from backend.app.inventory.inventory_repository import (
    PostgresInventoryRepository,
)
from backend.app.inventory.models import AdminAvailability
from backend.app.inventory.reservation import get_inventory_snapshots
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
    CreateOrderRequest,
    OrderItemRequest,
    OrderStatus,
)
from backend.app.orders.order_repository import PostgresOrderRepository


class RollbackTestTransaction(Exception):
    pass


@pytest.fixture
def isolated_repository():
    connection = get_database_connection()

    try:
        try:
            with connection.transaction():
                repository = PostgresOrderRepository(connection)
                yield repository, connection

                # Roll back all test activity.
                raise RollbackTestTransaction()
        except RollbackTestTransaction:
            pass
    finally:
        connection.close()


def test_get_products_for_order_retrieves_real_database_products(
    isolated_repository,
):
    repository, connection = isolated_repository

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                product_id,
                product_name,
                category,
                brand,
                price,
                availability,
                stock_quantity
            FROM products
            WHERE product_id = 'UA-0001'
            """
        )
        expected = cursor.fetchone()

    assert expected is not None

    result = repository.get_products_for_order(("UA-0001",))

    assert "UA-0001" in result

    product = result["UA-0001"]

    assert product.product_id == expected[0]
    assert product.product_name == expected[1]
    assert product.category == expected[2]
    assert product.brand == expected[3]
    assert product.price == expected[4]
    assert product.availability == expected[5]
    assert product.stock_quantity == expected[6]


def test_get_products_for_order_omits_unknown_product(
    isolated_repository,
):
    repository, _ = isolated_repository

    result = repository.get_products_for_order(("UA-0001", "UA-NONEXISTENT-TEST"))

    assert "UA-0001" in result
    assert "UA-NONEXISTENT-TEST" not in result


def test_concurrent_product_locks_use_consistent_order():
    setup_connection = get_database_connection()

    try:
        with setup_connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT product_id
                FROM products
                ORDER BY product_id
                LIMIT 2
                """
            )
            rows = cursor.fetchall()

        assert len(rows) == 2
        product_ids = tuple(row[0] for row in rows)

    finally:
        setup_connection.close()

    barrier = Barrier(2)

    def lock_products(requested_ids):
        connection = get_database_connection()

        try:
            with connection.transaction():
                repository = PostgresOrderRepository(connection)

                barrier.wait(timeout=10)

                result = repository.get_products_for_order(requested_ids)

                return result

        finally:
            connection.close()

    with ThreadPoolExecutor(max_workers=2) as executor:
        future_a = executor.submit(lock_products, product_ids)
        future_b = executor.submit(
            lock_products,
            tuple(reversed(product_ids)),
        )

        result_a = future_a.result(timeout=20)
        result_b = future_b.result(timeout=20)

    assert set(result_a) == set(product_ids)
    assert set(result_b) == set(product_ids)


def test_create_order_success(isolated_repository):
    repository, connection = isolated_repository
    customer_repository = PostgresCustomerRepository(connection)

    customer = customer_repository.create_customer(
        {
            "full_name": "Order Integration Customer",
            "mobile_number": "9999991234",
            "email": "order-integration@example.com",
            "bill_to_address": "Kolkata",
        }
    )

    product_id = "UA-0001"

    # Capture the product's database price and initial inventory.
    products = repository.get_products_for_order((product_id,))
    product = products[product_id]

    assert product.price is not None
    assert product.availability == AdminAvailability.AVAILABLE.value

    with connection.cursor() as cursor:
        initial_inventory = get_inventory_snapshots(
            cursor,
            (product_id,),
        )[product_id]

    assert initial_inventory.available_quantity >= 1

    request = CreateOrderRequest(
        customer_id=customer.customer_id,
        items=(
            OrderItemRequest(
                product_id=product_id,
                quantity=1,
            ),
        ),
    )

    result = repository.create_order(
        request=request,
        delivery_charge=Decimal("100.00"),
        customer_repository=customer_repository,
        idempotency_key=uuid4(),
    )

    assert result.order.order_id > 0
    assert result.order.order_number.startswith("UA-ORD-")
    assert result.order.customer_id == customer.customer_id
    assert result.order.order_status == OrderStatus.PLACED
    # Verify the 24-hour payment deadline.
    assert result.order.payment_due_at.tzinfo is not None

    assert (
        result.order.payment_due_at - result.order.order_date
    ).total_seconds() == 24 * 60 * 60

    # Verify the timestamps persisted in PostgreSQL.
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT order_date, payment_due_at
            FROM orders
            WHERE order_id = %s
            """,
            (result.order.order_id,),
        )
        persisted_deadline = cursor.fetchone()

    assert persisted_deadline is not None
    assert persisted_deadline[0] == result.order.order_date
    assert persisted_deadline[1] == result.order.payment_due_at

    assert (
        persisted_deadline[1] - persisted_deadline[0]
    ).total_seconds() == 24 * 60 * 60

    assert result.order.subtotal == product.price
    assert result.order.discount_amount == Decimal("0.00")
    assert result.order.delivery_charge == Decimal("100.00")
    assert result.order.grand_total == product.price + Decimal("100.00")

    assert len(result.items) == 1

    item = result.items[0]

    assert item.order_id == result.order.order_id
    assert item.product_id == product_id
    assert item.product_name == product.product_name
    assert item.category == product.category
    assert item.brand == product.brand
    assert item.quantity == 1
    assert item.unit_price == product.price

    # Verify billing and shipping snapshots.
    assert result.order.bill_to_contact_name == customer.full_name
    assert result.order.bill_to_phone == customer.mobile_number
    assert result.order.bill_to_address == "Kolkata"

    assert result.order.ship_to_contact_name == customer.full_name
    assert result.order.ship_to_phone == customer.mobile_number
    assert result.order.ship_to_address == "Kolkata"

    # Order placement reserves inventory but does not deduct physical stock.
    with connection.cursor() as cursor:
        updated_inventory = get_inventory_snapshots(
            cursor,
            (product_id,),
        )[product_id]

    assert updated_inventory.stock_quantity == initial_inventory.stock_quantity
    assert updated_inventory.ordered_quantity == initial_inventory.ordered_quantity + 1
    assert (
        updated_inventory.available_quantity == initial_inventory.available_quantity - 1
    )


def test_create_order_rejects_unknown_customer(isolated_repository):
    repository, connection = isolated_repository
    customer_repository = PostgresCustomerRepository(connection)

    # Find a positive customer ID that does not exist.
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT COALESCE(MAX(customer_id), 0) + 1
            FROM customers
            """
        )
        unknown_customer_id = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM orders")
        initial_order_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM order_items")
        initial_item_count = cursor.fetchone()[0]

    request = CreateOrderRequest(
        customer_id=unknown_customer_id,
        items=(
            OrderItemRequest(
                product_id="UA-0001",
                quantity=1,
            ),
        ),
    )

    with pytest.raises(CustomerNotFoundError, match="Customer not found"):
        repository.create_order(
            request=request,
            delivery_charge=Decimal("100.00"),
            customer_repository=customer_repository,
            idempotency_key=uuid4(),
        )

    # Verify that no order or order items were created.
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM orders")
        final_order_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM order_items")
        final_item_count = cursor.fetchone()[0]

    assert final_order_count == initial_order_count
    assert final_item_count == initial_item_count


def test_create_order_rejects_unknown_product(isolated_repository):
    repository, connection = isolated_repository
    customer_repository = PostgresCustomerRepository(connection)

    customer = customer_repository.create_customer(
        {
            "full_name": "Unknown Product Customer",
            "mobile_number": "9999991242",
            "email": "unknown-product@example.com",
        }
    )

    request = CreateOrderRequest(
        customer_id=customer.customer_id,
        items=(
            OrderItemRequest(
                product_id="UA-NONEXISTENT-ORDER-TEST",
                quantity=1,
            ),
        ),
    )

    with pytest.raises(
        ProductNotFoundError,
        match="Products not found",
    ):
        repository.create_order(
            request=request,
            delivery_charge=Decimal("100.00"),
            customer_repository=customer_repository,
            idempotency_key=uuid4(),
        )

    # Verify that no order was created.
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) FROM orders WHERE customer_id = %s",
            (customer.customer_id,),
        )
        assert cursor.fetchone()[0] == 0


def test_create_order_rejects_unknown_hold(isolated_repository):
    repository, connection = isolated_repository
    customer_repository = PostgresCustomerRepository(connection)

    customer = customer_repository.create_customer(
        {
            "full_name": "Unknown Hold Customer",
            "mobile_number": "9999991243",
            "email": "unknown-hold@example.com",
        }
    )

    # Find a positive hold ID that does not exist.
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT COALESCE(MAX(hold_id), 0) + 1
            FROM product_holds
            """
        )
        unknown_hold_id = cursor.fetchone()[0]

    request = CreateOrderRequest(
        customer_id=customer.customer_id,
        items=(
            OrderItemRequest(
                product_id="UA-0001",
                quantity=1,
                hold_id=unknown_hold_id,
            ),
        ),
    )

    with pytest.raises(
        HoldNotFoundError,
        match="Holds not found",
    ):
        repository.create_order(
            request=request,
            delivery_charge=Decimal("100.00"),
            customer_repository=customer_repository,
            idempotency_key=uuid4(),
        )

    # Verify that no order was created.
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) FROM orders WHERE customer_id = %s",
            (customer.customer_id,),
        )
        assert cursor.fetchone()[0] == 0


def test_create_order_rejects_unavailable_product(isolated_repository):
    repository, connection = isolated_repository
    customer_repository = PostgresCustomerRepository(connection)

    customer = customer_repository.create_customer(
        {
            "full_name": "Unavailable Product Customer",
            "mobile_number": "9999991235",
            "email": "unavailable-product@example.com",
        }
    )

    product_id = "UA-0001"

    # Temporarily mark the product as discontinued.
    # The outer test transaction will roll this back.
    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE products
            SET availability = 'Discontinued'
            WHERE product_id = %s
            """,
            (product_id,),
        )

        assert cursor.rowcount == 1

    request = CreateOrderRequest(
        customer_id=customer.customer_id,
        items=(
            OrderItemRequest(
                product_id=product_id,
                quantity=1,
            ),
        ),
    )

    with pytest.raises(
        ProductUnavailableError,
        match=f"Product {product_id} is not available for ordering",
    ):
        repository.create_order(
            request=request,
            delivery_charge=Decimal("100.00"),
            customer_repository=customer_repository,
            idempotency_key=uuid4(),
        )


def test_create_order_rejects_product_without_price(isolated_repository):
    repository, connection = isolated_repository
    customer_repository = PostgresCustomerRepository(connection)

    customer = customer_repository.create_customer(
        {
            "full_name": "Missing Price Customer",
            "mobile_number": "9999991236",
            "email": "missing-price@example.com",
        }
    )

    product_id = "UA-0001"

    # Temporarily remove the product price.
    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE products
            SET price = NULL
            WHERE product_id = %s
            """,
            (product_id,),
        )

        assert cursor.rowcount == 1

    request = CreateOrderRequest(
        customer_id=customer.customer_id,
        items=(
            OrderItemRequest(
                product_id=product_id,
                quantity=1,
            ),
        ),
    )

    with pytest.raises(
        ProductPriceNotConfiguredError,
        match=f"Product {product_id} has no configured price",
    ):
        repository.create_order(
            request=request,
            delivery_charge=Decimal("100.00"),
            customer_repository=customer_repository,
            idempotency_key=uuid4(),
        )


def test_create_order_rejects_insufficient_inventory(isolated_repository):
    repository, connection = isolated_repository
    customer_repository = PostgresCustomerRepository(connection)

    customer = customer_repository.create_customer(
        {
            "full_name": "Insufficient Stock Customer",
            "mobile_number": "9999991237",
            "email": "insufficient-stock@example.com",
        }
    )

    product_id = "UA-0001"

    products = repository.get_products_for_order((product_id,))
    product = products[product_id]

    assert product.availability == AdminAvailability.AVAILABLE.value
    assert product.price is not None

    with connection.cursor() as cursor:
        initial_inventory = get_inventory_snapshots(
            cursor,
            (product_id,),
        )[product_id]

    requested_quantity = initial_inventory.available_quantity + 1

    request = CreateOrderRequest(
        customer_id=customer.customer_id,
        items=(
            OrderItemRequest(
                product_id=product_id,
                quantity=requested_quantity,
            ),
        ),
    )

    with pytest.raises(
        InsufficientInventoryError,
        match="Insufficient available stock",
    ):
        repository.create_order(
            request=request,
            delivery_charge=Decimal("100.00"),
            customer_repository=customer_repository,
            idempotency_key=uuid4(),
        )

    # Verify that inventory remains unchanged.
    with connection.cursor() as cursor:
        final_inventory = get_inventory_snapshots(
            cursor,
            (product_id,),
        )[product_id]

    assert final_inventory.stock_quantity == initial_inventory.stock_quantity
    assert final_inventory.held_quantity == initial_inventory.held_quantity
    assert final_inventory.ordered_quantity == initial_inventory.ordered_quantity
    assert final_inventory.available_quantity == initial_inventory.available_quantity


def test_create_order_validates_inventory_for_every_product(
    isolated_repository,
):
    repository, connection = isolated_repository
    customer_repository = PostgresCustomerRepository(connection)

    customer = customer_repository.create_customer(
        {
            "full_name": "Multi Product Stock Customer",
            "mobile_number": "9999991241",
            "email": "multi-product-stock@example.com",
        }
    )

    # The first product will have insufficient stock.
    # The second product will have sufficient stock.
    product_ids = ("UA-0002", "UA-0001")

    products = repository.get_products_for_order(product_ids)

    for product_id in product_ids:
        product = products[product_id]
        assert product.availability == AdminAvailability.AVAILABLE.value
        assert product.price is not None

    with connection.cursor() as cursor:
        initial_inventory = get_inventory_snapshots(
            cursor,
            product_ids,
        )

    insufficient_quantity = initial_inventory["UA-0002"].available_quantity + 1

    assert initial_inventory["UA-0001"].available_quantity >= 1

    request = CreateOrderRequest(
        customer_id=customer.customer_id,
        items=(
            OrderItemRequest(
                product_id="UA-0002",
                quantity=insufficient_quantity,
            ),
            OrderItemRequest(
                product_id="UA-0001",
                quantity=1,
            ),
        ),
    )

    with pytest.raises(
        InsufficientInventoryError,
        match="Insufficient available stock",
    ):
        repository.create_order(
            request=request,
            delivery_charge=Decimal("100.00"),
            customer_repository=customer_repository,
            idempotency_key=uuid4(),
        )

    # Verify that neither product's inventory was changed.
    with connection.cursor() as cursor:
        final_inventory = get_inventory_snapshots(
            cursor,
            product_ids,
        )

    for product_id in product_ids:
        assert (
            final_inventory[product_id].stock_quantity
            == initial_inventory[product_id].stock_quantity
        )
        assert (
            final_inventory[product_id].held_quantity
            == initial_inventory[product_id].held_quantity
        )
        assert (
            final_inventory[product_id].ordered_quantity
            == initial_inventory[product_id].ordered_quantity
        )
        assert (
            final_inventory[product_id].available_quantity
            == initial_inventory[product_id].available_quantity
        )


def test_create_order_rejects_hold_owned_by_another_customer(
    isolated_repository,
):
    repository, connection = isolated_repository

    customer_repository = PostgresCustomerRepository(connection)
    inventory_repository = PostgresInventoryRepository(connection)

    # Register two different customers.
    customer_a = customer_repository.create_customer(
        {
            "full_name": "Hold Owner Customer",
            "mobile_number": "9999991238",
            "email": "hold-owner@example.com",
        }
    )

    customer_b = customer_repository.create_customer(
        {
            "full_name": "Different Customer",
            "mobile_number": "9999991239",
            "email": "different-customer@example.com",
        }
    )

    product_id = "UA-0001"

    # Customer A creates a hold.
    hold_result = inventory_repository.create_hold(
        product_id=product_id,
        quantity=1,
        customer_reference="HOLD-OWNER-TEST",
    )

    assert hold_result.created is True
    assert hold_result.hold_id is not None

    hold_id = hold_result.hold_id

    # Explicitly associate the hold with registered customer A.
    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE product_holds
            SET customer_id = %s
            WHERE hold_id = %s
            """,
            (customer_a.customer_id, hold_id),
        )

    # Customer B attempts to convert customer A's hold.
    request = CreateOrderRequest(
        customer_id=customer_b.customer_id,
        items=(
            OrderItemRequest(
                product_id=product_id,
                quantity=1,
                hold_id=hold_id,
            ),
        ),
    )

    with pytest.raises(
        HoldConflictError,
        match=f"Hold {hold_id} does not belong to this customer",
    ):
        repository.create_order(
            request=request,
            delivery_charge=Decimal("100.00"),
            customer_repository=customer_repository,
            idempotency_key=uuid4(),
        )

    # Verify the hold remains active and belongs to customer A.
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT customer_id, status, order_id
            FROM product_holds
            WHERE hold_id = %s
            """,
            (hold_id,),
        )
        hold = cursor.fetchone()

    assert hold is not None
    assert hold[0] == customer_a.customer_id
    assert hold[1] == "Active"
    assert hold[2] is None


def test_create_order_rejects_unlinked_hold(isolated_repository):
    repository, connection = isolated_repository

    customer_repository = PostgresCustomerRepository(connection)
    inventory_repository = PostgresInventoryRepository(connection)

    customer = customer_repository.create_customer(
        {
            "full_name": "Unlinked Hold Customer",
            "mobile_number": "9999991240",
            "email": "unlinked-hold@example.com",
        }
    )

    product_id = "UA-0001"

    hold_result = inventory_repository.create_hold(
        product_id=product_id,
        quantity=1,
        customer_reference="UNLINKED-HOLD-TEST",
    )

    assert hold_result.created is True
    assert hold_result.hold_id is not None

    hold_id = hold_result.hold_id

    # Confirm the hold is not linked to a registered customer.
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT customer_id, status
            FROM product_holds
            WHERE hold_id = %s
            """,
            (hold_id,),
        )
        hold = cursor.fetchone()

    assert hold == (None, "Active")

    request = CreateOrderRequest(
        customer_id=customer.customer_id,
        items=(
            OrderItemRequest(
                product_id=product_id,
                quantity=1,
                hold_id=hold_id,
            ),
        ),
    )

    with pytest.raises(
        HoldConflictError,
        match=f"Hold {hold_id} does not belong to this customer",
    ):
        repository.create_order(
            request=request,
            delivery_charge=Decimal("100.00"),
            customer_repository=customer_repository,
            idempotency_key=uuid4(),
        )

    # The failed conversion must not modify the hold.
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT customer_id, status, order_id
            FROM product_holds
            WHERE hold_id = %s
            """,
            (hold_id,),
        )
        final_hold = cursor.fetchone()

    assert final_hold == (None, "Active", None)


def test_create_order_rejects_released_hold(isolated_repository):
    repository, connection = isolated_repository

    customer_repository = PostgresCustomerRepository(connection)
    inventory_repository = PostgresInventoryRepository(connection)

    customer = customer_repository.create_customer(
        {
            "full_name": "Released Hold Customer",
            "mobile_number": "9999991241",
            "email": "released-hold@example.com",
        }
    )

    product_id = "UA-0001"

    # Create a hold.
    hold_result = inventory_repository.create_hold(
        product_id=product_id,
        quantity=1,
        customer_reference="RELEASED-HOLD-TEST",
    )

    assert hold_result.created is True
    assert hold_result.hold_id is not None

    hold_id = hold_result.hold_id

    # Link the hold to the registered customer.
    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE product_holds
            SET customer_id = %s
            WHERE hold_id = %s
            """,
            (customer.customer_id, hold_id),
        )

    # Release the hold.
    release_result = inventory_repository.release_hold(hold_id)

    assert release_result.released is True

    request = CreateOrderRequest(
        customer_id=customer.customer_id,
        items=(
            OrderItemRequest(
                product_id=product_id,
                quantity=1,
                hold_id=hold_id,
            ),
        ),
    )

    with pytest.raises(
        HoldConflictError,
        match=f"Hold {hold_id} is not active",
    ):
        repository.create_order(
            request=request,
            delivery_charge=Decimal("100.00"),
            customer_repository=customer_repository,
            idempotency_key=uuid4(),
        )

    # Verify that the hold remains Released and unconverted.
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT customer_id, status, order_id
            FROM product_holds
            WHERE hold_id = %s
            """,
            (hold_id,),
        )
        final_hold = cursor.fetchone()

    assert final_hold == (customer.customer_id, "Released", None)


def test_create_order_successfully_converts_customer_hold(
    isolated_repository,
):
    repository, connection = isolated_repository

    customer_repository = PostgresCustomerRepository(connection)
    inventory_repository = PostgresInventoryRepository(connection)

    customer = customer_repository.create_customer(
        {
            "full_name": "Successful Hold Conversion Customer",
            "mobile_number": "9999991242",
            "email": "successful-hold@example.com",
        }
    )

    product_id = "UA-0001"

    # Create a hold for one unit.
    hold_result = inventory_repository.create_hold(
        product_id=product_id,
        quantity=1,
        customer_reference="SUCCESSFUL-HOLD-TEST",
    )

    assert hold_result.created is True
    assert hold_result.hold_id is not None

    hold_id = hold_result.hold_id

    # Link the hold to the registered customer.
    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE product_holds
            SET customer_id = %s
            WHERE hold_id = %s
            """,
            (customer.customer_id, hold_id),
        )

        cursor.execute(
            """
            SELECT status
            FROM product_holds
            WHERE hold_id = %s
            """,
            (hold_id,),
        )
        assert cursor.fetchone()[0] == "Active"

        inventory_before = get_inventory_snapshots(
            cursor,
            (product_id,),
        )[product_id]

    # Place an order using the exact hold.
    request = CreateOrderRequest(
        customer_id=customer.customer_id,
        items=(
            OrderItemRequest(
                product_id=product_id,
                quantity=1,
                hold_id=hold_id,
            ),
        ),
    )

    result = repository.create_order(
        request=request,
        delivery_charge=Decimal("100.00"),
        customer_repository=customer_repository,
        idempotency_key=uuid4(),
    )

    assert result.order.order_status == OrderStatus.PLACED
    assert len(result.items) == 1
    assert result.items[0].product_id == product_id
    assert result.items[0].quantity == 1

    # Verify that the hold is converted and linked to the order.
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT customer_id, status, order_id
            FROM product_holds
            WHERE hold_id = %s
            """,
            (hold_id,),
        )
        converted_hold = cursor.fetchone()

        inventory_after = get_inventory_snapshots(
            cursor,
            (product_id,),
        )[product_id]

    assert converted_hold == (
        customer.customer_id,
        "Converted",
        result.order.order_id,
    )

    # The active hold is replaced by an order commitment.
    assert inventory_after.stock_quantity == inventory_before.stock_quantity
    assert inventory_after.held_quantity == inventory_before.held_quantity - 1
    assert inventory_after.ordered_quantity == inventory_before.ordered_quantity + 1
    assert inventory_after.available_quantity == inventory_before.available_quantity


def test_create_order_rolls_back_when_hold_conversion_fails(
    isolated_repository,
):
    repository, connection = isolated_repository

    customer_repository = PostgresCustomerRepository(connection)
    inventory_repository = PostgresInventoryRepository(connection)

    customer = customer_repository.create_customer(
        {
            "full_name": "Rollback Test Customer",
            "mobile_number": "9999991243",
            "email": "rollback-test@example.com",
        }
    )

    product_id = "UA-0001"

    # Create an active hold.
    hold_result = inventory_repository.create_hold(
        product_id=product_id,
        quantity=1,
        customer_reference="ROLLBACK-TEST",
    )

    assert hold_result.created is True
    assert hold_result.hold_id is not None

    hold_id = hold_result.hold_id

    # Link the hold to the registered customer.
    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE product_holds
            SET customer_id = %s
            WHERE hold_id = %s
            """,
            (customer.customer_id, hold_id),
        )

        cursor.execute("SELECT COUNT(*) FROM orders")
        initial_order_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM order_items")
        initial_item_count = cursor.fetchone()[0]

    # Create a temporary trigger that deliberately fails
    # when the order repository attempts to convert this hold.
    with connection.cursor() as cursor:
        cursor.execute(
            """
            CREATE FUNCTION test_fail_hold_conversion()
            RETURNS TRIGGER AS $$
            BEGIN
                RAISE EXCEPTION 'simulated hold conversion failure';
            END;
            $$ LANGUAGE plpgsql
            """
        )

        cursor.execute(
            """
            CREATE TRIGGER test_fail_hold_conversion_trigger
            BEFORE UPDATE ON product_holds
            FOR EACH ROW
            EXECUTE FUNCTION test_fail_hold_conversion()
            """
        )

    request = CreateOrderRequest(
        customer_id=customer.customer_id,
        items=(
            OrderItemRequest(
                product_id=product_id,
                quantity=1,
                hold_id=hold_id,
            ),
        ),
    )

    # The order header and items are inserted before this failure.
    idempotency_key = uuid4()

    with pytest.raises(
        RaiseException,
        match="simulated hold conversion failure",
    ):
        repository.create_order(
            request=request,
            delivery_charge=Decimal("100.00"),
            customer_repository=customer_repository,
            idempotency_key=idempotency_key,
        )

    # Verify that the entire order transaction was rolled back.
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM orders")
        final_order_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM order_items")
        final_item_count = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM order_idempotency
            WHERE customer_id = %s
              AND idempotency_key = %s
            """,
            (customer.customer_id, idempotency_key),
        )
        final_idempotency_count = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT customer_id, status, order_id
            FROM product_holds
            WHERE hold_id = %s
            """,
            (hold_id,),
        )
        final_hold = cursor.fetchone()

    assert final_order_count == initial_order_count
    assert final_item_count == initial_item_count
    assert final_idempotency_count == 0

    assert final_hold == (
        customer.customer_id,
        "Active",
        None,
    )


def test_create_order_replays_original_order_for_same_idempotency_key(
    isolated_repository,
):
    repository, connection = isolated_repository
    customer_repository = PostgresCustomerRepository(connection)

    customer = customer_repository.create_customer(
        {
            "full_name": "Idempotency Replay Customer",
            "mobile_number": "9999991235",
            "email": "idempotency-replay@example.com",
            "bill_to_address": "Kolkata",
        }
    )

    product_id = "UA-0001"
    products = repository.get_products_for_order((product_id,))
    product = products[product_id]

    assert product.price is not None
    assert product.availability == AdminAvailability.AVAILABLE.value

    with connection.cursor() as cursor:
        initial_inventory = get_inventory_snapshots(
            cursor,
            (product_id,),
        )[product_id]

    assert initial_inventory.available_quantity >= 1

    request = CreateOrderRequest(
        customer_id=customer.customer_id,
        items=(
            OrderItemRequest(
                product_id=product_id,
                quantity=1,
            ),
        ),
    )

    idempotency_key = uuid4()

    first_result = repository.create_order(
        request=request,
        delivery_charge=Decimal("100.00"),
        customer_repository=customer_repository,
        idempotency_key=idempotency_key,
    )

    with connection.cursor() as cursor:
        inventory_after_first = get_inventory_snapshots(
            cursor,
            (product_id,),
        )[product_id]

    second_result = repository.create_order(
        request=request,
        delivery_charge=Decimal("100.00"),
        customer_repository=customer_repository,
        idempotency_key=idempotency_key,
    )

    with connection.cursor() as cursor:
        inventory_after_second = get_inventory_snapshots(
            cursor,
            (product_id,),
        )[product_id]

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM orders
            WHERE customer_id = %s
            """,
            (customer.customer_id,),
        )
        order_count = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM order_idempotency
            WHERE customer_id = %s
              AND idempotency_key = %s
            """,
            (customer.customer_id, idempotency_key),
        )
        idempotency_count = cursor.fetchone()[0]

    assert first_result.order.order_id == second_result.order.order_id
    assert first_result.order.order_number == second_result.order.order_number
    assert first_result.items == second_result.items

    assert order_count == 1
    assert idempotency_count == 1

    assert (
        inventory_after_first.available_quantity
        == inventory_after_second.available_quantity
    )
    assert inventory_after_first.stock_quantity == inventory_after_second.stock_quantity


def test_create_order_rejects_different_request_with_same_idempotency_key(
    isolated_repository,
):
    repository, connection = isolated_repository
    customer_repository = PostgresCustomerRepository(connection)

    customer = customer_repository.create_customer(
        {
            "full_name": "Idempotency Conflict Customer",
            "mobile_number": "9999991236",
            "email": "idempotency-conflict@example.com",
            "bill_to_address": "Kolkata",
        }
    )

    request = CreateOrderRequest(
        customer_id=customer.customer_id,
        items=(
            OrderItemRequest(
                product_id="UA-0001",
                quantity=1,
            ),
        ),
        notes="Original request",
    )

    idempotency_key = uuid4()

    first_result = repository.create_order(
        request=request,
        delivery_charge=Decimal("100.00"),
        customer_repository=customer_repository,
        idempotency_key=idempotency_key,
    )

    modified_request = CreateOrderRequest(
        customer_id=customer.customer_id,
        items=(
            OrderItemRequest(
                product_id="UA-0001",
                quantity=1,
            ),
        ),
        notes="Modified request",
    )

    with pytest.raises(IdempotencyConflictError):
        repository.create_order(
            request=modified_request,
            delivery_charge=Decimal("100.00"),
            customer_repository=customer_repository,
            idempotency_key=idempotency_key,
        )

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM orders
            WHERE customer_id = %s
            """,
            (customer.customer_id,),
        )
        order_count = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT order_id
            FROM order_idempotency
            WHERE customer_id = %s
              AND idempotency_key = %s
            """,
            (customer.customer_id, idempotency_key),
        )
        idempotency_record = cursor.fetchone()

    assert order_count == 1
    assert idempotency_record is not None
    assert idempotency_record[0] == first_result.order.order_id


def test_create_order_with_different_keys_creates_separate_orders(
    isolated_repository,
):
    repository, connection = isolated_repository
    customer_repository = PostgresCustomerRepository(connection)

    customer = customer_repository.create_customer(
        {
            "full_name": "Different Keys Customer",
            "mobile_number": "9999991237",
            "email": "different-keys@example.com",
            "bill_to_address": "Kolkata",
        }
    )

    request = CreateOrderRequest(
        customer_id=customer.customer_id,
        items=(
            OrderItemRequest(
                product_id="UA-0001",
                quantity=1,
            ),
        ),
    )

    first_result = repository.create_order(
        request=request,
        delivery_charge=Decimal("100.00"),
        customer_repository=customer_repository,
        idempotency_key=uuid4(),
    )

    second_result = repository.create_order(
        request=request,
        delivery_charge=Decimal("100.00"),
        customer_repository=customer_repository,
        idempotency_key=uuid4(),
    )

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM orders
            WHERE customer_id = %s
            """,
            (customer.customer_id,),
        )
        order_count = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM order_idempotency
            WHERE customer_id = %s
            """,
            (customer.customer_id,),
        )
        idempotency_count = cursor.fetchone()[0]

    assert first_result.order.order_id != second_result.order.order_id
    assert first_result.order.order_number != second_result.order.order_number
    assert order_count == 2
    assert idempotency_count == 2


def test_idempotency_key_is_scoped_to_customer(isolated_repository):
    repository, connection = isolated_repository
    customer_repository = PostgresCustomerRepository(connection)

    customer_one = customer_repository.create_customer(
        {
            "full_name": "Idempotency Customer One",
            "mobile_number": "9999991238",
            "email": "idempotency-customer-one@example.com",
            "bill_to_address": "Kolkata",
        }
    )

    customer_two = customer_repository.create_customer(
        {
            "full_name": "Idempotency Customer Two",
            "mobile_number": "9999991239",
            "email": "idempotency-customer-two@example.com",
            "bill_to_address": "Kolkata",
        }
    )

    idempotency_key = uuid4()

    request_one = CreateOrderRequest(
        customer_id=customer_one.customer_id,
        items=(OrderItemRequest(product_id="UA-0001", quantity=1),),
    )

    request_two = CreateOrderRequest(
        customer_id=customer_two.customer_id,
        items=(OrderItemRequest(product_id="UA-0001", quantity=1),),
    )

    first_result = repository.create_order(
        request=request_one,
        delivery_charge=Decimal("100.00"),
        customer_repository=customer_repository,
        idempotency_key=idempotency_key,
    )

    second_result = repository.create_order(
        request=request_two,
        delivery_charge=Decimal("100.00"),
        customer_repository=customer_repository,
        idempotency_key=idempotency_key,
    )

    assert first_result.order.order_id != second_result.order.order_id
    assert first_result.order.customer_id == customer_one.customer_id
    assert second_result.order.customer_id == customer_two.customer_id

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM order_idempotency
            WHERE idempotency_key = %s
            """,
            (idempotency_key,),
        )
        idempotency_count = cursor.fetchone()[0]

    assert idempotency_count == 2


def test_concurrent_same_key_submissions_create_only_one_order():
    setup_connection = get_database_connection()

    try:
        customer_repository = PostgresCustomerRepository(setup_connection)

        customer = customer_repository.create_customer(
            {
                "full_name": "Concurrent Idempotency Customer",
                "mobile_number": "9999991240",
                "email": "concurrent-idempotency@example.com",
                "bill_to_address": "Kolkata",
            }
        )
    finally:
        setup_connection.close()

    customer_id = customer.customer_id
    idempotency_key = uuid4()

    request = CreateOrderRequest(
        customer_id=customer_id,
        items=(
            OrderItemRequest(
                product_id="UA-0001",
                quantity=1,
            ),
        ),
    )

    barrier = Barrier(2)

    def submit_order():
        connection = get_database_connection()

        try:
            repository = PostgresOrderRepository(connection)
            customer_repo = PostgresCustomerRepository(connection)

            barrier.wait(timeout=10)

            return repository.create_order(
                request=request,
                delivery_charge=Decimal("100.00"),
                customer_repository=customer_repo,
                idempotency_key=idempotency_key,
            )
        finally:
            connection.close()

    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_one = executor.submit(submit_order)
            future_two = executor.submit(submit_order)

            result_one = future_one.result(timeout=30)
            result_two = future_two.result(timeout=30)

        assert result_one.order.order_id == result_two.order.order_id
        assert result_one.order.order_number == result_two.order.order_number
        assert result_one.items == result_two.items

        verification_connection = get_database_connection()

        try:
            with verification_connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM orders
                    WHERE customer_id = %s
                    """,
                    (customer_id,),
                )
                order_count = cursor.fetchone()[0]

                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM order_idempotency
                    WHERE customer_id = %s
                      AND idempotency_key = %s
                    """,
                    (customer_id, idempotency_key),
                )
                idempotency_count = cursor.fetchone()[0]

            assert order_count == 1
            assert idempotency_count == 1
        finally:
            verification_connection.close()

    finally:
        cleanup_connection = get_database_connection()

        try:
            with cleanup_connection.transaction():
                with cleanup_connection.cursor() as cursor:
                    cursor.execute(
                        """
                        DELETE FROM order_idempotency
                        WHERE customer_id = %s
                        """,
                        (customer_id,),
                    )

                    cursor.execute(
                        """
                        DELETE FROM order_items
                        WHERE order_id IN (
                            SELECT order_id
                            FROM orders
                            WHERE customer_id = %s
                        )
                        """,
                        (customer_id,),
                    )

                    cursor.execute(
                        """
                        DELETE FROM orders
                        WHERE customer_id = %s
                        """,
                        (customer_id,),
                    )

                    cursor.execute(
                        """
                        DELETE FROM customers
                        WHERE customer_id = %s
                        """,
                        (customer_id,),
                    )
        finally:
            cleanup_connection.close()
