from decimal import Decimal
from uuid import UUID

from psycopg import Connection, Cursor

from backend.app.customers.customer_repository import (
    PostgresCustomerRepository,
)
from backend.app.inventory.models import AdminAvailability
from backend.app.inventory.reservation import get_inventory_snapshots
from backend.app.orders.idempotency import (
    IdempotencyConflictError,
    calculate_advisory_lock_id,
    calculate_order_request_hash,
)
from backend.app.orders.models import (
    CreateOrderRequest,
    Order,
    OrderCreationResult,
    OrderItem,
    OrderStatus,
    ProductOrderSnapshot,
)
from backend.app.orders.order_pricing import calculate_order_pricing

ORDER_COLUMNS = """
    order_id,
    order_number,
    customer_id,
    order_date,
    payment_due_at,
    order_status,
    subtotal,
    discount_amount,
    delivery_charge,
    grand_total,
    created_at,
    updated_at,
    expected_delivery_date,
    invoice_number,
    invoice_date,
    invoice_issued_at,
    currency,
    bill_to_contact_name,
    bill_to_phone,
    bill_to_address,
    ship_to_contact_name,
    ship_to_phone,
    ship_to_address,
    notes,
    attribute1,
    attribute2,
    attribute3,
    attribute4,
    attribute5
"""


ORDER_ITEM_COLUMNS = """
    order_item_id,
    order_id,
    product_id,
    product_name,
    category,
    quantity,
    unit_price,
    line_discount,
    line_total,
    created_at,
    updated_at,
    brand,
    notes,
    attribute1,
    attribute2,
    attribute3,
    attribute4,
    attribute5
"""


def order_from_row(row: tuple) -> Order:
    values = list(row)
    values[5] = OrderStatus(values[5])
    return Order(*values)


def order_item_from_row(row: tuple) -> OrderItem:
    return OrderItem(*row)


class PostgresOrderRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def get_order(self, order_id: int) -> Order | None:
        sql = f"""
            SELECT {ORDER_COLUMNS}
            FROM orders
            WHERE order_id = %s
        """

        with self.connection.cursor() as cursor:
            cursor.execute(sql, (order_id,))
            row = cursor.fetchone()

        if row is None:
            return None

        return order_from_row(row)

    def get_order_items(self, order_id: int) -> list[OrderItem]:
        sql = f"""
            SELECT {ORDER_ITEM_COLUMNS}
            FROM order_items
            WHERE order_id = %s
            ORDER BY order_item_id
        """

        with self.connection.cursor() as cursor:
            cursor.execute(sql, (order_id,))
            rows = cursor.fetchall()

        return [order_item_from_row(row) for row in rows]

    def list_orders(
        self,
        customer_id: int | None = None,
        order_status: OrderStatus | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Order]:
        sql = f"""
            SELECT {ORDER_COLUMNS}
            FROM orders
        """

        conditions = []
        params = []

        if customer_id is not None:
            conditions.append("customer_id = %s")
            params.append(customer_id)

        if order_status is not None:
            conditions.append("order_status = %s")
            params.append(order_status.value)

        if conditions:
            sql += " WHERE " + " AND ".join(conditions)

        sql += """
            ORDER BY order_date DESC, order_id DESC
            LIMIT %s OFFSET %s
        """

        params.extend([limit, offset])

        with self.connection.cursor() as cursor:
            cursor.execute(sql, tuple(params))
            rows = cursor.fetchall()

        return [order_from_row(row) for row in rows]

    def _get_products_for_order(
        self,
        cursor: Cursor,
        product_ids: tuple[str, ...],
    ) -> dict[str, ProductOrderSnapshot]:
        """Retrieve and lock products using the caller's cursor."""

        if not isinstance(product_ids, tuple) or not product_ids:
            raise ValueError("product_ids must be a non-empty tuple")

        if not all(
            isinstance(product_id, str) and product_id.strip()
            for product_id in product_ids
        ):
            raise ValueError("All product IDs must be non-empty strings")

        normalized_ids = tuple(sorted(product_id.strip() for product_id in product_ids))

        if len(normalized_ids) != len(set(normalized_ids)):
            raise ValueError("Duplicate product IDs are not allowed")

        sql = """
            SELECT
                product_id,
                product_name,
                category,
                brand,
                price,
                availability,
                stock_quantity
            FROM products
            WHERE product_id = ANY(%s)
            ORDER BY product_id
            FOR UPDATE
        """

        cursor.execute(sql, (list(normalized_ids),))
        rows = cursor.fetchall()

        return {
            row[0]: ProductOrderSnapshot(
                product_id=row[0],
                product_name=row[1],
                category=row[2],
                brand=row[3],
                price=row[4],
                availability=row[5],
                stock_quantity=row[6],
            )
            for row in rows
        }

    def get_products_for_order(
        self,
        product_ids: tuple[str, ...],
    ) -> dict[str, ProductOrderSnapshot]:
        """Public product retrieval operation."""

        with self.connection.cursor() as cursor:
            return self._get_products_for_order(cursor, product_ids)

    @staticmethod
    def _get_next_order_number(cursor: Cursor) -> str:
        """Generate an order number using the caller's cursor."""

        cursor.execute("SELECT nextval('order_number_seq')")
        sequence_value = cursor.fetchone()[0]

        return f"UA-ORD-{sequence_value:06d}"

    def get_next_order_number(self) -> str:
        """Generate a unique order number."""

        with self.connection.cursor() as cursor:
            return self._get_next_order_number(cursor)

    def create_order(
        self,
        request: CreateOrderRequest,
        delivery_charge: Decimal,
        customer_repository: PostgresCustomerRepository,
        idempotency_key: UUID,
    ) -> OrderCreationResult:
        """Create an order and reserve inventory atomically."""

        if customer_repository.connection is not self.connection:
            raise ValueError(
                "Order and customer repositories must share the same connection"
            )

        if not isinstance(idempotency_key, UUID):
            raise ValueError("idempotency_key must be a UUID")

        request_hash = calculate_order_request_hash(request)
        lock_id = calculate_advisory_lock_id(
            request.customer_id,
            idempotency_key,
        )

        product_ids = tuple(item.product_id for item in request.items)

        hold_items = {
            item.hold_id: item for item in request.items if item.hold_id is not None
        }
        hold_ids = tuple(hold_items)

        with self.connection.transaction():
            with self.connection.cursor() as cursor:
                # Step 0: Serialize requests using the same customer/key.
                cursor.execute(
                    "SELECT pg_advisory_xact_lock(%s)",
                    (lock_id,),
                )

                # Step 0.1: Check whether this request was already processed.
                cursor.execute(
                    """
                    SELECT request_hash, order_id
                    FROM order_idempotency
                    WHERE customer_id = %s
                      AND idempotency_key = %s
                    """,
                    (request.customer_id, idempotency_key),
                )

                existing_idempotency = cursor.fetchone()

                if existing_idempotency is not None:
                    existing_hash, existing_order_id = existing_idempotency

                    if existing_hash.strip() != request_hash:
                        raise IdempotencyConflictError(
                            "Idempotency key was already used "
                            "with a different order request"
                        )

                    # Return the original order and its items.
                    cursor.execute(
                        f"""
                        SELECT {ORDER_COLUMNS}
                        FROM orders
                        WHERE order_id = %s
                        """,
                        (existing_order_id,),
                    )
                    existing_order_row = cursor.fetchone()

                    if existing_order_row is None:
                        raise RuntimeError(
                            "Idempotency record references a missing order"
                        )

                    cursor.execute(
                        f"""
                        SELECT {ORDER_ITEM_COLUMNS}
                        FROM order_items
                        WHERE order_id = %s
                        ORDER BY order_item_id
                        """,
                        (existing_order_id,),
                    )
                    existing_item_rows = cursor.fetchall()

                    return OrderCreationResult(
                        order=order_from_row(existing_order_row),
                        items=tuple(
                            order_item_from_row(row) for row in existing_item_rows
                        ),
                    )
                # Step 1: Read hold metadata without locking.
                # This lets us identify the associated products first.
                if hold_ids:
                    cursor.execute(
                        """
                        SELECT hold_id, product_id, customer_id, quantity, status
                        FROM product_holds
                        WHERE hold_id = ANY(%s)
                        ORDER BY product_id, hold_id
                        """,
                        (list(hold_ids),),
                    )
                    initial_hold_rows = cursor.fetchall()

                    initial_holds = {row[0]: row for row in initial_hold_rows}

                    missing_holds = set(hold_ids) - set(initial_holds)

                    if missing_holds:
                        raise ValueError(
                            "Holds not found: "
                            f"{', '.join(map(str, sorted(missing_holds)))}"
                        )

                    for hold_id, item in hold_items.items():
                        hold = initial_holds[hold_id]

                        if hold[1] != item.product_id:
                            raise ValueError(
                                f"Hold {hold_id} does not match "
                                f"product {item.product_id}"
                            )

                        if hold[3] != item.quantity:
                            raise ValueError(
                                f"Hold {hold_id} quantity does not match the order item"
                            )

                # Step 2: Lock products in sorted order.
                products = self._get_products_for_order(cursor, product_ids)

                missing_products = set(product_ids) - set(products)

                if missing_products:
                    raise ValueError(
                        f"Products not found: {', '.join(sorted(missing_products))}"
                    )

                # Step 3: Lock the customer row.
                customer = customer_repository.get_customer_for_order(
                    cursor,
                    request.customer_id,
                )

                if customer is None:
                    raise ValueError("Customer not found")

                # Step 4: Lock and revalidate holds.
                locked_holds = {}

                if hold_ids:
                    cursor.execute(
                        """
                        SELECT hold_id, product_id, customer_id, quantity, status
                        FROM product_holds
                        WHERE hold_id = ANY(%s)
                        ORDER BY product_id, hold_id
                        FOR UPDATE
                        """,
                        (list(hold_ids),),
                    )

                    locked_hold_rows = cursor.fetchall()
                    locked_holds = {row[0]: row for row in locked_hold_rows}

                    if set(locked_holds) != set(hold_ids):
                        raise ValueError("One or more requested holds no longer exist")

                    for hold_id, item in hold_items.items():
                        hold = locked_holds[hold_id]

                        if hold[4] != "Active":
                            raise ValueError(f"Hold {hold_id} is not active")

                        if hold[2] != request.customer_id:
                            raise ValueError(
                                f"Hold {hold_id} does not belong to this customer"
                            )

                        if hold[1] != item.product_id:
                            raise ValueError(
                                f"Hold {hold_id} product does not match the order item"
                            )

                        if hold[3] != item.quantity:
                            raise ValueError(
                                f"Hold {hold_id} quantity does not match the order item"
                            )

                # Step 5: Retrieve authoritative inventory snapshots.
                inventory_snapshots = get_inventory_snapshots(
                    cursor,
                    product_ids,
                    lock_products=False,
                )

                # Step 6: Validate product availability, price and stock.
                for item in request.items:
                    product = products[item.product_id]
                    inventory = inventory_snapshots[item.product_id]

                    if product.availability != AdminAvailability.AVAILABLE.value:
                        raise ValueError(
                            f"Product {item.product_id} is not available for ordering"
                        )

                    if product.price is None:
                        raise ValueError(
                            f"Product {item.product_id} has no configured price"
                        )

                    # An active hold belonging to this customer is
                    # already included in held_quantity. Credit it back
                    # for this order after successful hold validation.
                    own_hold_quantity = item.quantity if item.hold_id is not None else 0

                    effective_available = (
                        inventory.available_quantity + own_hold_quantity
                    )

                    if item.quantity > effective_available:
                        raise ValueError(
                            f"Insufficient available stock for product "
                            f"{item.product_id}. Requested: {item.quantity}, "
                            f"available: {effective_available}"
                        )

                # Step 7: Calculate authoritative order pricing.
                unit_prices = {
                    product_id: product.price
                    for product_id, product in products.items()
                }

                pricing = calculate_order_pricing(
                    items=request.items,
                    unit_prices=unit_prices,
                    discount_amount=request.discount_amount,
                    delivery_charge=delivery_charge,
                )

                # Step 8: Resolve billing and shipping snapshots.
                bill_to_contact_name = (
                    customer.bill_to_contact_name or customer.full_name
                )
                bill_to_phone = customer.bill_to_phone or customer.mobile_number
                bill_to_address = customer.bill_to_address

                ship_to_contact_name = (
                    request.ship_to_contact_name
                    if request.ship_to_contact_name is not None
                    else customer.ship_to_contact_name or bill_to_contact_name
                )

                ship_to_phone = (
                    request.ship_to_phone
                    if request.ship_to_phone is not None
                    else customer.ship_to_phone or bill_to_phone
                )

                ship_to_address = (
                    request.ship_to_address
                    if request.ship_to_address is not None
                    else customer.ship_to_address or bill_to_address
                )

                # Step 9: Generate the order number.
                order_number = self._get_next_order_number(cursor)

                # Step 10: Insert the order header.
                cursor.execute(
                    f"""
                    INSERT INTO orders (
                        order_number,
                        customer_id,
                        order_status,
                        subtotal,
                        discount_amount,
                        delivery_charge,
                        grand_total,
                        expected_delivery_date,
                        currency,
                        bill_to_contact_name,
                        bill_to_phone,
                        bill_to_address,
                        ship_to_contact_name,
                        ship_to_phone,
                        ship_to_address,
                        notes,
                        payment_due_at
                    )
                    VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s,
                        CURRENT_TIMESTAMP + INTERVAL '24 hours'
                    )
                    RETURNING {ORDER_COLUMNS}
                    """,
                    (
                        order_number,
                        request.customer_id,
                        OrderStatus.PLACED.value,
                        pricing.subtotal,
                        pricing.discount_amount,
                        pricing.delivery_charge,
                        pricing.grand_total,
                        request.expected_delivery_date,
                        "INR",
                        bill_to_contact_name,
                        bill_to_phone,
                        bill_to_address,
                        ship_to_contact_name,
                        ship_to_phone,
                        ship_to_address,
                        request.notes,
                    ),
                )

                order_row = cursor.fetchone()

                # Step 11: Insert order items.
                pricing_by_product_id = {
                    line.product_id: line for line in pricing.lines
                }

                created_items = []

                for item in request.items:
                    product = products[item.product_id]
                    line = pricing_by_product_id[item.product_id]

                    cursor.execute(
                        f"""
                        INSERT INTO order_items (
                            order_id,
                            product_id,
                            product_name,
                            category,
                            brand,
                            quantity,
                            unit_price,
                            line_discount,
                            line_total,
                            notes
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING {ORDER_ITEM_COLUMNS}
                        """,
                        (
                            order_row[0],
                            item.product_id,
                            product.product_name,
                            product.category,
                            product.brand,
                            item.quantity,
                            line.unit_price,
                            line.line_discount,
                            line.line_total,
                            item.notes,
                        ),
                    )

                    item_row = cursor.fetchone()

                    if item_row is None:
                        raise RuntimeError(
                            f"Order item insertion failed for {item.product_id}"
                        )

                    created_items.append(order_item_from_row(item_row))

                # Step 12: Convert active holds into this order.
                for hold_id, item in hold_items.items():
                    cursor.execute(
                        """
                        UPDATE product_holds
                        SET
                            status = 'Converted',
                            order_id = %s,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE
                            hold_id = %s
                            AND status = 'Active'
                            AND customer_id = %s
                            AND product_id = %s
                            AND quantity = %s
                        RETURNING hold_id
                        """,
                        (
                            order_row[0],
                            hold_id,
                            request.customer_id,
                            item.product_id,
                            item.quantity,
                        ),
                    )

                    converted_hold = cursor.fetchone()

                    if converted_hold is None:
                        raise ValueError(
                            f"Could not convert hold {hold_id}. "
                            "Its status or details have changed."
                        )

                # Step 13: Save the idempotency record.
                cursor.execute(
                    """
                    INSERT INTO order_idempotency (
                        customer_id,
                        idempotency_key,
                        request_hash,
                        order_id
                    )
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        request.customer_id,
                        idempotency_key,
                        request_hash,
                        order_row[0],
                    ),
                )

                # Step 14: Return the completed order.
                return OrderCreationResult(
                    order=order_from_row(order_row),
                    items=tuple(created_items),
                )
