from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from threading import Barrier

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
    )

    assert result.order.order_id > 0
    assert result.order.order_number.startswith("UA-ORD-")
    assert result.order.customer_id == customer.customer_id
    assert result.order.order_status == OrderStatus.PLACED

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

    with pytest.raises(ValueError, match="Customer not found"):
        repository.create_order(
            request=request,
            delivery_charge=Decimal("100.00"),
            customer_repository=customer_repository,
        )

    # Verify that no order or order items were created.
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM orders")
        final_order_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM order_items")
        final_item_count = cursor.fetchone()[0]

    assert final_order_count == initial_order_count
    assert final_item_count == initial_item_count


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
        ValueError,
        match=f"Product {product_id} is not available for ordering",
    ):
        repository.create_order(
            request=request,
            delivery_charge=Decimal("100.00"),
            customer_repository=customer_repository,
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
        ValueError,
        match=f"Product {product_id} has no configured price",
    ):
        repository.create_order(
            request=request,
            delivery_charge=Decimal("100.00"),
            customer_repository=customer_repository,
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
        ValueError,
        match="Insufficient available stock",
    ):
        repository.create_order(
            request=request,
            delivery_charge=Decimal("100.00"),
            customer_repository=customer_repository,
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
        ValueError,
        match=f"Hold {hold_id} does not belong to this customer",
    ):
        repository.create_order(
            request=request,
            delivery_charge=Decimal("100.00"),
            customer_repository=customer_repository,
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
        ValueError,
        match=f"Hold {hold_id} does not belong to this customer",
    ):
        repository.create_order(
            request=request,
            delivery_charge=Decimal("100.00"),
            customer_repository=customer_repository,
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
        ValueError,
        match=f"Hold {hold_id} is not active",
    ):
        repository.create_order(
            request=request,
            delivery_charge=Decimal("100.00"),
            customer_repository=customer_repository,
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
    with pytest.raises(
        RaiseException,
        match="simulated hold conversion failure",
    ):
        repository.create_order(
            request=request,
            delivery_charge=Decimal("100.00"),
            customer_repository=customer_repository,
        )

    # Verify that the entire order transaction was rolled back.
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM orders")
        final_order_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM order_items")
        final_item_count = cursor.fetchone()[0]

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

    assert final_hold == (
        customer.customer_id,
        "Active",
        None,
    )
