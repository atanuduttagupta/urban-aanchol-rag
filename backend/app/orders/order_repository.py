from psycopg import Connection

from backend.app.orders.models import (
    Order,
    OrderItem,
    OrderStatus,
    ProductOrderSnapshot,
)

ORDER_COLUMNS = """
    order_id,
    order_number,
    customer_id,
    order_date,
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
    values[4] = OrderStatus(values[4])
    return Order(*values)


def order_item_from_row(row: tuple) -> OrderItem:
    return OrderItem(*row)


class PostgresOrderRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def get_products_for_order(
        self,
        product_ids: tuple[str, ...],
    ) -> dict[str, ProductOrderSnapshot]:
        """
        Lock product rows in sorted order and retrieve their order details.

        The caller owns the database transaction.
        Missing products are omitted from the returned dictionary.
        """

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

        with self.connection.cursor() as cursor:
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

    def get_next_order_number(self) -> str:
        """Generate a unique order number using the PostgreSQL sequence."""
        sql = "SELECT nextval('order_number_seq')"

        with self.connection.cursor() as cursor:
            cursor.execute(sql)
            sequence_value = cursor.fetchone()[0]

        return f"UA-ORD-{sequence_value:06d}"

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
