from psycopg import Connection

from backend.app.inventory.models import (
    AdminAvailability,
    HoldCreationResult,
    HoldRecord,
    HoldReleaseReason,
    HoldReleaseResult,
    HoldStatus,
    InventorySnapshot,
    ReservationReason,
)
from backend.app.inventory.reservation import get_inventory_snapshots


class PostgresInventoryRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def get_inventory_snapshot(
        self,
        product_id: str,
    ) -> InventorySnapshot | None:
        with self.connection.cursor() as cursor:
            snapshots = get_inventory_snapshots(
                cursor=cursor,
                product_ids=(product_id,),
            )

        return snapshots.get(product_id.strip())

    def list_active_holds(
        self,
        product_id: str | None = None,
    ) -> list[HoldRecord]:
        sql = """
            SELECT
                hold_id,
                product_id,
                customer_reference,
                quantity,
                status,
                notes,
                created_at,
                updated_at
            FROM product_holds
            WHERE status = 'Active'
        """

        params: tuple[str, ...] = ()

        if product_id is not None:
            sql += " AND product_id = %s"
            params = (product_id,)

        sql += " ORDER BY created_at DESC, hold_id DESC"

        with self.connection.cursor() as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchall()

        return [
            HoldRecord(
                hold_id=row[0],
                product_id=row[1],
                customer_reference=row[2],
                quantity=row[3],
                status=HoldStatus(row[4]),
                notes=row[5],
                created_at=row[6],
                updated_at=row[7],
            )
            for row in rows
        ]

    def release_hold(self, hold_id: int) -> HoldReleaseResult:
        with self.connection.transaction():
            with self.connection.cursor() as cursor:
                # Find the product without locking the hold first.
                cursor.execute(
                    """
                    SELECT product_id
                    FROM product_holds
                    WHERE hold_id = %s
                    """,
                    (hold_id,),
                )
                hold = cursor.fetchone()

                if hold is None:
                    return HoldReleaseResult(
                        released=False,
                        hold_id=hold_id,
                        product_id=None,
                        reason=HoldReleaseReason.HOLD_NOT_FOUND,
                    )

                product_id = hold[0]

                # Follow the same product-first lock order as create_hold().
                cursor.execute(
                    """
                    SELECT product_id
                    FROM products
                    WHERE product_id = %s
                    FOR UPDATE
                    """,
                    (product_id,),
                )

                # Lock and recheck the hold after acquiring the product lock.
                cursor.execute(
                    """
                    SELECT status
                    FROM product_holds
                    WHERE hold_id = %s
                    FOR UPDATE
                    """,
                    (hold_id,),
                )
                current_hold = cursor.fetchone()

                if current_hold is None:
                    return HoldReleaseResult(
                        released=False,
                        hold_id=hold_id,
                        product_id=None,
                        reason=HoldReleaseReason.HOLD_NOT_FOUND,
                    )

                if current_hold[0] != HoldStatus.ACTIVE.value:
                    return HoldReleaseResult(
                        released=False,
                        hold_id=hold_id,
                        product_id=product_id,
                        reason=HoldReleaseReason.HOLD_NOT_ACTIVE,
                    )

                cursor.execute(
                    """
                    UPDATE product_holds
                    SET
                        status = 'Released',
                        updated_at = CURRENT_TIMESTAMP
                    WHERE hold_id = %s
                    """,
                    (hold_id,),
                )

                return HoldReleaseResult(
                    released=True,
                    hold_id=hold_id,
                    product_id=product_id,
                    reason=HoldReleaseReason.HOLD_RELEASED,
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

                # Recalculate inventory after acquiring the product lock.
                snapshots = get_inventory_snapshots(
                    cursor=cursor,
                    product_ids=(product_id,),
                )

                inventory = snapshots.get(product_id)

                if inventory is None:
                    return HoldCreationResult(
                        created=False,
                        hold_id=None,
                        product_id=product_id,
                        requested_quantity=quantity,
                        available_quantity=None,
                        customer_availability=None,
                        reason=ReservationReason.PRODUCT_NOT_FOUND,
                    )

                if not inventory.can_reserve:
                    reason = (
                        ReservationReason.OUT_OF_STOCK
                        if inventory.admin_availability == AdminAvailability.AVAILABLE
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
                    held_quantity=inventory.held_quantity + quantity,
                    ordered_quantity=inventory.ordered_quantity,
                    admin_availability=inventory.admin_availability,
                )

                return HoldCreationResult(
                    created=True,
                    hold_id=hold_id,
                    product_id=product_id,
                    requested_quantity=quantity,
                    available_quantity=updated_inventory.available_quantity,
                    customer_availability=(updated_inventory.customer_availability),
                    reason=ReservationReason.RESERVATION_ALLOWED,
                )
