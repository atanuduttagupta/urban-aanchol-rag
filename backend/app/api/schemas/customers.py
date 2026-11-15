from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CustomerCreateRequest(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    full_name: str = Field(min_length=1, max_length=150)
    mobile_number: str = Field(min_length=1, max_length=20)
    whatsapp_number: str | None = Field(default=None, max_length=20)
    email: str | None = Field(default=None, max_length=254)

    bill_to_contact_name: str | None = Field(default=None, max_length=150)
    bill_to_phone: str | None = Field(default=None, max_length=20)
    bill_to_address: str | None = None

    ship_to_contact_name: str | None = Field(default=None, max_length=150)
    ship_to_phone: str | None = Field(default=None, max_length=20)
    ship_to_address: str | None = None

    notes: str | None = None

    attribute1: str | None = Field(default=None, max_length=255)
    attribute2: str | None = Field(default=None, max_length=255)
    attribute3: str | None = Field(default=None, max_length=255)
    attribute4: str | None = Field(default=None, max_length=255)
    attribute5: str | None = Field(default=None, max_length=255)


class CustomerUpdateRequest(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    full_name: str | None = Field(default=None, max_length=150)
    mobile_number: str | None = Field(default=None, max_length=20)
    whatsapp_number: str | None = Field(default=None, max_length=20)
    email: str | None = Field(default=None, max_length=254)

    bill_to_contact_name: str | None = Field(default=None, max_length=150)
    bill_to_phone: str | None = Field(default=None, max_length=20)
    bill_to_address: str | None = None

    ship_to_contact_name: str | None = Field(default=None, max_length=150)
    ship_to_phone: str | None = Field(default=None, max_length=20)
    ship_to_address: str | None = None

    notes: str | None = None

    attribute1: str | None = Field(default=None, max_length=255)
    attribute2: str | None = Field(default=None, max_length=255)
    attribute3: str | None = Field(default=None, max_length=255)
    attribute4: str | None = Field(default=None, max_length=255)
    attribute5: str | None = Field(default=None, max_length=255)


class CustomerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    customer_id: int
    full_name: str
    mobile_number: str
    whatsapp_number: str | None
    email: str | None

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

    created_at: datetime
    updated_at: datetime
