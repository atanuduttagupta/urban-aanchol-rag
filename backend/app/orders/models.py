from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum


class OrderStatus(StrEnum):
    DRAFT = "Draft"
    PLACED = "Placed"
    CONFIRMED = "Confirmed"
    PROCESSING = "Processing"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


@dataclass(frozen=True)
class Order:
    order_id: int
    order_number: str
    customer_id: int
    order_date: datetime
    payment_due_at: datetime
    order_status: OrderStatus

    subtotal: Decimal
    discount_amount: Decimal
    delivery_charge: Decimal
    grand_total: Decimal

    created_at: datetime
    updated_at: datetime

    expected_delivery_date: date | None = None

    invoice_number: str | None = None
    invoice_date: date | None = None
    invoice_issued_at: datetime | None = None

    currency: str = "INR"

    bill_to_contact_name: str | None = None
    bill_to_phone: str | None = None
    bill_to_address: str | None = None

    ship_to_contact_name: str | None = None
    ship_to_phone: str | None = None
    ship_to_address: str | None = None

    notes: str | None = None

    attribute1: str | None = None
    attribute2: str | None = None
    attribute3: str | None = None
    attribute4: str | None = None
    attribute5: str | None = None

    def __post_init__(self):
        for field_name in ("order_id", "customer_id"):
            value = getattr(self, field_name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{field_name} must be a positive integer")

        if not isinstance(self.order_number, str) or not self.order_number.strip():
            raise ValueError("order_number cannot be empty")

        if not isinstance(self.order_status, OrderStatus):
            raise ValueError("Invalid order_status")

        for field_name in (
            "order_date",
            "payment_due_at",
            "created_at",
            "updated_at",
        ):
            value = getattr(self, field_name)

            if not isinstance(value, datetime):
                raise ValueError(f"{field_name} must be a datetime")

            if value.tzinfo is None or value.utcoffset() is None:
                raise ValueError(f"{field_name} must be timezone-aware")

        if self.payment_due_at <= self.order_date:
            raise ValueError("payment_due_at must be later than order_date")

        if self.expected_delivery_date is not None:
            if type(self.expected_delivery_date) is not date:
                raise ValueError("expected_delivery_date must be a date")

        if self.invoice_date is not None:
            if type(self.invoice_date) is not date:
                raise ValueError("invoice_date must be a date")

        if self.invoice_issued_at is not None:
            if not isinstance(self.invoice_issued_at, datetime):
                raise ValueError("invoice_issued_at must be a datetime")

        for field_name in (
            "subtotal",
            "discount_amount",
            "delivery_charge",
            "grand_total",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, Decimal) or not value.is_finite():
                raise ValueError(f"{field_name} must be a finite Decimal")
            if value < 0:
                raise ValueError(f"{field_name} cannot be negative")

        if self.discount_amount > self.subtotal:
            raise ValueError("discount_amount cannot exceed subtotal")

        expected_total = self.subtotal - self.discount_amount + self.delivery_charge
        if self.grand_total != expected_total:
            raise ValueError("grand_total does not match order amounts")

        if not isinstance(self.currency, str) or len(self.currency) != 3:
            raise ValueError("currency must be a three-character code")

        if not self.currency.isalpha() or self.currency != self.currency.upper():
            raise ValueError("currency must be uppercase alphabetic characters")

        invoice_values = (
            self.invoice_number,
            self.invoice_date,
            self.invoice_issued_at,
        )
        if any(value is None for value in invoice_values) and not all(
            value is None for value in invoice_values
        ):
            raise ValueError("Invoice fields must be all set or all None")

        if self.invoice_number is not None:
            if (
                not isinstance(self.invoice_number, str)
                or not self.invoice_number.strip()
            ):
                raise ValueError("invoice_number cannot be empty")


@dataclass(frozen=True)
class OrderItem:
    order_item_id: int
    order_id: int
    product_id: str
    product_name: str
    category: str

    quantity: int
    unit_price: Decimal
    line_discount: Decimal
    line_total: Decimal

    created_at: datetime
    updated_at: datetime

    brand: str | None = None
    notes: str | None = None

    attribute1: str | None = None
    attribute2: str | None = None
    attribute3: str | None = None
    attribute4: str | None = None
    attribute5: str | None = None

    def __post_init__(self):
        for field_name in ("order_item_id", "order_id", "quantity"):
            value = getattr(self, field_name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{field_name} must be a positive integer")

        for field_name in ("created_at", "updated_at"):
            if not isinstance(getattr(self, field_name), datetime):
                raise ValueError(f"{field_name} must be a datetime")

        for field_name in ("product_id", "product_name", "category"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} cannot be empty")

        object.__setattr__(self, "product_id", self.product_id.strip())

        for field_name in ("unit_price", "line_discount", "line_total"):
            value = getattr(self, field_name)
            if not isinstance(value, Decimal) or not value.is_finite():
                raise ValueError(f"{field_name} must be a finite Decimal")
            if value < 0:
                raise ValueError(f"{field_name} cannot be negative")

        gross_total = self.quantity * self.unit_price

        if self.line_discount > gross_total:
            raise ValueError("line_discount cannot exceed gross line amount")

        expected_total = gross_total - self.line_discount

        if self.line_total != expected_total:
            raise ValueError("line_total does not match item amounts")


@dataclass(frozen=True)
class OrderItemRequest:
    product_id: str
    quantity: int
    line_discount: Decimal = Decimal("0.00")
    notes: str | None = None
    hold_id: int | None = None

    def __post_init__(self):
        if not isinstance(self.product_id, str) or not self.product_id.strip():
            raise ValueError("product_id cannot be empty")

        object.__setattr__(self, "product_id", self.product_id.strip())

        if (
            isinstance(self.quantity, bool)
            or not isinstance(self.quantity, int)
            or self.quantity <= 0
        ):
            raise ValueError("quantity must be a positive integer")

        if (
            not isinstance(self.line_discount, Decimal)
            or not self.line_discount.is_finite()
            or self.line_discount < 0
        ):
            raise ValueError("line_discount must be a non-negative Decimal")

        if self.notes is not None and not isinstance(self.notes, str):
            raise ValueError("notes must be a string or None")

        if self.hold_id is not None:
            if (
                isinstance(self.hold_id, bool)
                or not isinstance(self.hold_id, int)
                or self.hold_id <= 0
            ):
                raise ValueError("hold_id must be a positive integer or None")


@dataclass(frozen=True)
class CreateOrderRequest:
    customer_id: int
    items: tuple[OrderItemRequest, ...]

    discount_amount: Decimal = Decimal("0.00")
    expected_delivery_date: date | None = None

    ship_to_contact_name: str | None = None
    ship_to_phone: str | None = None
    ship_to_address: str | None = None

    notes: str | None = None

    def __post_init__(self):
        if (
            isinstance(self.customer_id, bool)
            or not isinstance(self.customer_id, int)
            or self.customer_id <= 0
        ):
            raise ValueError("customer_id must be a positive integer")

        if not isinstance(self.items, tuple) or not self.items:
            raise ValueError("items must be a non-empty tuple")

        if not all(isinstance(item, OrderItemRequest) for item in self.items):
            raise ValueError("All items must be OrderItemRequest instances")

        product_ids = [item.product_id.strip() for item in self.items]

        if len(product_ids) != len(set(product_ids)):
            raise ValueError("Duplicate product IDs are not allowed")

        hold_ids = [item.hold_id for item in self.items if item.hold_id is not None]

        if len(hold_ids) != len(set(hold_ids)):
            raise ValueError("Duplicate hold IDs are not allowed")

        if (
            not isinstance(self.discount_amount, Decimal)
            or not self.discount_amount.is_finite()
            or self.discount_amount < 0
        ):
            raise ValueError("discount_amount must be a non-negative Decimal")

        if self.expected_delivery_date is not None:
            if type(self.expected_delivery_date) is not date:
                raise ValueError("expected_delivery_date must be a date")

        for field_name in (
            "ship_to_contact_name",
            "ship_to_phone",
            "ship_to_address",
            "notes",
        ):
            value = getattr(self, field_name)

            if value is not None and not isinstance(value, str):
                raise ValueError(f"{field_name} must be a string or None")


@dataclass(frozen=True)
class ProductOrderSnapshot:
    product_id: str
    product_name: str
    category: str
    brand: str | None
    price: Decimal | None
    availability: str
    stock_quantity: int


@dataclass(frozen=True)
class OrderCreationResult:
    order: Order
    items: tuple[OrderItem, ...]
