from psycopg import Cursor

from backend.app.inventory.models import (
    AdminAvailability,
    InventorySnapshot,
)


def get_inventory_snapshots(
    cursor: Cursor,
    product_ids: tuple[str, ...],
    lock_products: bool = False,
) -> dict[str, InventorySnapshot]:
    """
    Retrieve inventory snapshots for multiple products.

    When lock_products=True, product rows are locked in sorted order
    before inventory quantities are recalculated.

    The caller owns the database transaction.
    """

    if not isinstance(product_ids, tuple) or not product_ids:
        raise ValueError("product_ids must be a non-empty tuple")

    if not all(
        isinstance(product_id, str) and product_id.strip() for product_id in product_ids
    ):
        raise ValueError("All product IDs must be non-empty strings")

    normalized_ids = tuple(sorted(product_id.strip() for product_id in product_ids))

    if len(normalized_ids) != len(set(normalized_ids)):
        raise ValueError("Duplicate product IDs are not allowed")

    if lock_products:
        cursor.execute(
            """
            SELECT product_id
            FROM products
            WHERE product_id = ANY(%s)
            ORDER BY product_id
            FOR UPDATE
            """,
            (list(normalized_ids),),
        )

        # Fetch all lock-query results before running the calculation.
        cursor.fetchall()

    sql = """
        SELECT
            p.product_id,
            p.stock_quantity,

            COALESCE(holds.held_quantity, 0)::INTEGER,

            COALESCE(orders.ordered_quantity, 0)::INTEGER,

            p.availability

        FROM products p

        LEFT JOIN (
            SELECT
                product_id,
                SUM(quantity) AS held_quantity
            FROM product_holds
            WHERE status = 'Active'
              AND product_id = ANY(%s)
            GROUP BY product_id
        ) holds
            ON holds.product_id = p.product_id

        LEFT JOIN (
            SELECT
                oi.product_id,
                SUM(
                    GREATEST(
                        oi.quantity - COALESCE(dispatched.quantity, 0),
                        0
                    )
                ) AS ordered_quantity

            FROM order_items oi

            JOIN orders o
                ON o.order_id = oi.order_id

            LEFT JOIN (
                SELECT
                    si.order_item_id,
                    SUM(si.quantity) AS quantity
                FROM shipment_items si
                JOIN shipments s
                    ON s.shipment_id = si.shipment_id
                WHERE s.shipment_status IN (
                    'Dispatched',
                    'In Transit',
                    'Delivered',
                    'Failed',
                    'Returned'
                )
                GROUP BY si.order_item_id
            ) dispatched
                ON dispatched.order_item_id = oi.order_item_id

            WHERE oi.product_id = ANY(%s)
              AND o.order_status IN (
                  'Placed',
                  'Confirmed',
                  'Processing'
              )

            GROUP BY oi.product_id
        ) orders
            ON orders.product_id = p.product_id

        WHERE p.product_id = ANY(%s)
    """

    params = (
        list(normalized_ids),
        list(normalized_ids),
        list(normalized_ids),
    )

    cursor.execute(sql, params)
    rows = cursor.fetchall()

    return {
        row[0]: InventorySnapshot(
            product_id=row[0],
            stock_quantity=row[1],
            held_quantity=row[2],
            ordered_quantity=row[3],
            admin_availability=AdminAvailability(row[4]),
        )
        for row in rows
    }
