
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from backend.app.orders.models import OrderStatus


class OrderItemCreateRequest(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    product_id: str = Field(min_length=1, max_length=50)
    quantity: int = Field(strict=True, gt=0)
    notes: str | None = None
    hold_id: int | None = Field(default=None, strict=True, gt=0)


class OrderCreateRequest(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    customer_id: int = Field(strict=True, gt=0)
    items: list[OrderItemCreateRequest] = Field(min_length=1)

    expected_delivery_date: date | None = None

    ship_to_contact_name: str | None = Field(
        default=None,
        max_length=150,
    )
    ship_to_phone: str | None = Field(
        default=None,
        max_length=20,
    )
    ship_to_address: str | None = None

    notes: str | None = None


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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

    brand: str | None
    notes: str | None

    attribute1: str | None
    attribute2: str | None
    attribute3: str | None
    attribute4: str | None
    attribute5: str | None


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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

    expected_delivery_date: date | None

    invoice_number: str | None
    invoice_date: date | None
    invoice_issued_at: datetime | None

    currency: str

    bill_to_contact_name: str | None
    bill_to_phone: str | None
    bill_to_address: str | None

    ship_to_contact_name: str | None
    ship_to_phone: str | None
    ship_to_address: str | None

    notes: str | None

    attribute1: str | None
    attribute2: str | None
    attribute3: str | None
    attribute4: str | None
    attribute5: str | None


class OrderCreationResponse(BaseModel):
    order: OrderResponse
    items: list[OrderItemResponse]
