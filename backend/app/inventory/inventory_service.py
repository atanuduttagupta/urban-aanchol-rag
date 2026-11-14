from backend.app.inventory.inventory_repository import (
    PostgresInventoryRepository,
)
from backend.app.inventory.models import (
    InventorySnapshot,
    ReservationDecision,
    ReservationReason,
)


class InventoryService:
    def __init__(
        self,
        repository: PostgresInventoryRepository,
    ) -> None:
        self.repository = repository

    def get_inventory(
        self,
        product_id: str,
    ) -> InventorySnapshot | None:
        if not product_id or not product_id.strip():
            raise ValueError("Product ID cannot be empty.")

        return self.repository.get_inventory_snapshot(product_id)

    def can_reserve(
        self,
        product_id: str,
        quantity: int,
    ) -> bool:
        return self.check_reservation(product_id, quantity).allowed

    def check_reservation(
        self,
        product_id: str,
        quantity: int,
    ) -> ReservationDecision:
        if isinstance(quantity, bool) or not isinstance(quantity, int):
            raise ValueError("Reservation quantity must be an integer.")

        if quantity <= 0:
            raise ValueError("Reservation quantity must be greater than zero.")

        inventory = self.get_inventory(product_id)

        if inventory is None:
            return ReservationDecision(
                allowed=False,
                product_id=product_id,
                requested_quantity=quantity,
                available_quantity=None,
                customer_availability=None,
                reason=ReservationReason.PRODUCT_NOT_FOUND,
            )

        if not inventory.can_reserve:
            if inventory.admin_availability.value == "Available":
                reason = ReservationReason.OUT_OF_STOCK
            else:
                reason = ReservationReason.PRODUCT_NOT_AVAILABLE

            return ReservationDecision(
                allowed=False,
                product_id=product_id,
                requested_quantity=quantity,
                available_quantity=inventory.available_quantity,
                customer_availability=inventory.customer_availability,
                reason=reason,
            )

        if quantity > inventory.available_quantity:
            return ReservationDecision(
                allowed=False,
                product_id=product_id,
                requested_quantity=quantity,
                available_quantity=inventory.available_quantity,
                customer_availability=inventory.customer_availability,
                reason=ReservationReason.INSUFFICIENT_STOCK,
            )

        return ReservationDecision(
            allowed=True,
            product_id=product_id,
            requested_quantity=quantity,
            available_quantity=inventory.available_quantity,
            customer_availability=inventory.customer_availability,
            reason=ReservationReason.RESERVATION_ALLOWED,
        )
