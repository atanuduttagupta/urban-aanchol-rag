
from dataclasses import dataclass
from enum import StrEnum


class AdminAvailability(StrEnum):
    PLANNED = "Planned"
    COMING_SOON = "Coming Soon"
    AVAILABLE = "Available"
    RESERVED = "Reserved"
    SOLD = "Sold"
    INACTIVE = "Inactive"
    DISCONTINUED = "Discontinued"


class CustomerAvailability(StrEnum):
    PLANNED = "Planned"
    COMING_SOON = "Coming Soon"
    AVAILABLE = "Available"
    OUT_OF_STOCK = "Out of Stock"
    RESERVED = "Reserved"
    SOLD = "Sold"
    INACTIVE = "Inactive"
    DISCONTINUED = "Discontinued"


@dataclass(frozen=True)
class InventorySnapshot:
    product_id: str
    stock_quantity: int
    reserved_quantity: int
    admin_availability: AdminAvailability

    def __post_init__(self) -> None:
        if not self.product_id.strip():
            raise ValueError("Product ID cannot be empty.")

        for field_name, value in (
            ("stock_quantity", self.stock_quantity),
            ("reserved_quantity", self.reserved_quantity),
        ):
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(f"{field_name} must be an integer.")

            if value < 0:
                raise ValueError(f"{field_name} cannot be negative.")

        if self.reserved_quantity > self.stock_quantity:
            raise ValueError(
                "Reserved quantity cannot exceed physical stock."
            )

        if not isinstance(self.admin_availability, AdminAvailability):
            raise ValueError("Invalid admin availability status.")

    @property
    def available_quantity(self) -> int:
        return self.stock_quantity - self.reserved_quantity

    @property
    def customer_availability(self) -> CustomerAvailability:
        status = self.admin_availability

        if status == AdminAvailability.PLANNED:
            return CustomerAvailability.PLANNED

        if status == AdminAvailability.COMING_SOON:
            return CustomerAvailability.COMING_SOON

        if status == AdminAvailability.RESERVED:
            return CustomerAvailability.RESERVED

        if status == AdminAvailability.SOLD:
            return CustomerAvailability.SOLD

        if status == AdminAvailability.INACTIVE:
            return CustomerAvailability.INACTIVE

        if status == AdminAvailability.DISCONTINUED:
            return CustomerAvailability.DISCONTINUED

        if self.available_quantity == 0:
            return CustomerAvailability.OUT_OF_STOCK

        return CustomerAvailability.AVAILABLE

    @property
    def can_reserve(self) -> bool:
        return (
            self.admin_availability == AdminAvailability.AVAILABLE
            and self.available_quantity > 0
        )
