from psycopg import Connection

from backend.app.inventory.models import (
    AdminAvailability,
    InventorySnapshot,
)


class PostgresInventoryRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def get_inventory_snapshot(
        self,
        product_id: str,
    ) -> InventorySnapshot | None:
        sql = """
            SELECT
                p.product_id,
                p.stock_quantity,
                COALESCE(h.reserved_quantity, 0)::INTEGER,
                p.availability
            FROM products p
            LEFT JOIN (
                SELECT
                    product_id,
                    SUM(quantity) AS reserved_quantity
                FROM product_holds
                WHERE status = 'Active'
                GROUP BY product_id
            ) h
                ON h.product_id = p.product_id
            WHERE p.product_id = %s
        """

        with self.connection.cursor() as cursor:
            cursor.execute(sql, (product_id,))
            row = cursor.fetchone()

        if row is None:
            return None

        return InventorySnapshot(
            product_id=row[0],
            stock_quantity=row[1],
            reserved_quantity=row[2],
            admin_availability=AdminAvailability(row[3]),
        )
