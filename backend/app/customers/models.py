from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Customer:
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
