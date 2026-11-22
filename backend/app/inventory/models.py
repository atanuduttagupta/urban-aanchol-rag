from dataclasses import dataclass
from datetime import datetime
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


class ReservationReason(StrEnum):
    RESERVATION_ALLOWED = "RESERVATION_ALLOWED"
    PRODUCT_NOT_FOUND = "PRODUCT_NOT_FOUND"
    PRODUCT_NOT_AVAILABLE = "PRODUCT_NOT_AVAILABLE"
    OUT_OF_STOCK = "OUT_OF_STOCK"
    INSUFFICIENT_STOCK = "INSUFFICIENT_STOCK"


@dataclass(frozen=True)
class InventorySnapshot:
    product_id: str
    stock_quantity: int
    held_quantity: int
    ordered_quantity: int
    admin_availability: AdminAvailability

    def __post_init__(self) -> None:
        if not self.product_id.strip():
            raise ValueError("Product ID cannot be empty.")

        for field_name, value in (
            ("stock_quantity", self.stock_quantity),
            ("held_quantity", self.held_quantity),
            ("ordered_quantity", self.ordered_quantity),
        ):
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(f"{field_name} must be an integer.")

            if value < 0:
                raise ValueError(f"{field_name} cannot be negative.")

        if self.reserved_quantity > self.stock_quantity:
            raise ValueError("Reserved quantity cannot exceed physical stock.")

        if not isinstance(self.admin_availability, AdminAvailability):
            raise ValueError("Invalid admin availability status.")

    @property
    def reserved_quantity(self) -> int:
        return self.held_quantity + self.ordered_quantity

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


@dataclass(frozen=True)
class ReservationDecision:
    allowed: bool
    product_id: str
    requested_quantity: int
    available_quantity: int | None
    customer_availability: CustomerAvailability | None
    reason: ReservationReason


@dataclass(frozen=True)
class HoldCreationResult:
    created: bool
    hold_id: int | None
    product_id: str
    requested_quantity: int
    available_quantity: int | None
    customer_availability: CustomerAvailability | None
    reason: ReservationReason


class HoldStatus(StrEnum):
    ACTIVE = "Active"
    RELEASED = "Released"
    CONVERTED = "Converted"


class HoldReleaseReason(StrEnum):
    HOLD_RELEASED = "HOLD_RELEASED"
    HOLD_NOT_FOUND = "HOLD_NOT_FOUND"
    HOLD_NOT_ACTIVE = "HOLD_NOT_ACTIVE"


@dataclass(frozen=True)
class HoldRecord:
    hold_id: int
    product_id: str
    customer_reference: str | None
    quantity: int
    status: HoldStatus
    notes: str | None
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class HoldReleaseResult:
    released: bool
    hold_id: int
    product_id: str | None
    reason: HoldReleaseReason
