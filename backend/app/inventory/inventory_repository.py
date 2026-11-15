
from psycopg import Connection

from backend.app.inventory.models import (
    AdminAvailability,
    HoldCreationResult,
    InventorySnapshot,
    ReservationReason,
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

    def create_hold(
        self,
        product_id: str,
        quantity: int,
        customer_reference: str,
        notes: str | None = None,
    ) -> HoldCreationResult:
        with self.connection.transaction():
            with self.connection.cursor() as cursor:
                # Lock the product row to serialize reservations
                # for this product.
                cursor.execute(
                    """
                    SELECT product_id, stock_quantity, availability
                    FROM products
                    WHERE product_id = %s
                    FOR UPDATE
                    """,
                    (product_id,),
                )
                product = cursor.fetchone()

                if product is None:
                    return HoldCreationResult(
                        created=False,
                        hold_id=None,
                        product_id=product_id,
                        requested_quantity=quantity,
                        available_quantity=None,
                        customer_availability=None,
                        reason=ReservationReason.PRODUCT_NOT_FOUND,
                    )

                # Recalculate active holds after acquiring the lock.
                cursor.execute(
                    """
                    SELECT COALESCE(SUM(quantity), 0)::INTEGER
                    FROM product_holds
                    WHERE product_id = %s
                      AND status = 'Active'
                    """,
                    (product_id,),
                )
                reserved_quantity = cursor.fetchone()[0]

                inventory = InventorySnapshot(
                    product_id=product[0],
                    stock_quantity=product[1],
                    reserved_quantity=reserved_quantity,
                    admin_availability=AdminAvailability(product[2]),
                )

                if not inventory.can_reserve:
                    reason = (
                        ReservationReason.OUT_OF_STOCK
                        if inventory.admin_availability
                        == AdminAvailability.AVAILABLE
                        else ReservationReason.PRODUCT_NOT_AVAILABLE
                    )

                    return HoldCreationResult(
                        created=False,
                        hold_id=None,
                        product_id=product_id,
                        requested_quantity=quantity,
                        available_quantity=inventory.available_quantity,
                        customer_availability=inventory.customer_availability,
                        reason=reason,
                    )

                if quantity > inventory.available_quantity:
                    return HoldCreationResult(
                        created=False,
                        hold_id=None,
                        product_id=product_id,
                        requested_quantity=quantity,
                        available_quantity=inventory.available_quantity,
                        customer_availability=inventory.customer_availability,
                        reason=ReservationReason.INSUFFICIENT_STOCK,
                    )

                cursor.execute(
                    """
                    INSERT INTO product_holds (
                        product_id,
                        customer_reference,
                        quantity,
                        notes
                    )
                    VALUES (%s, %s, %s, %s)
                    RETURNING hold_id
                    """,
                    (product_id, customer_reference, quantity, notes),
                )
                hold_id = cursor.fetchone()[0]

                updated_inventory = InventorySnapshot(
                    product_id=product_id,
                    stock_quantity=inventory.stock_quantity,
                    reserved_quantity=(
                        inventory.reserved_quantity + quantity
                    ),
                    admin_availability=inventory.admin_availability,
                )

                return HoldCreationResult(
                    created=True,
                    hold_id=hold_id,
                    product_id=product_id,
                    requested_quantity=quantity,
                    available_quantity=updated_inventory.available_quantity,
                    customer_availability=(
                        updated_inventory.customer_availability
                    ),
                    reason=ReservationReason.RESERVATION_ALLOWED,
                )
