from pydantic import BaseModel, ConfigDict, Field

from backend.app.inventory.models import (
    AdminAvailability,
    CustomerAvailability,
    ReservationReason,
)


class InventoryResponse(BaseModel):
    product_id: str
    stock_quantity: int
    reserved_quantity: int
    available_quantity: int
    admin_availability: AdminAvailability
    customer_availability: CustomerAvailability
    can_reserve: bool


class ReservationCheckRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    product_id: str = Field(min_length=1, max_length=50)
    quantity: int = Field(gt=0)


class ReservationDecisionResponse(BaseModel):
    allowed: bool
    product_id: str
    requested_quantity: int
    available_quantity: int | None
    customer_availability: CustomerAvailability | None
    reason: ReservationReason
