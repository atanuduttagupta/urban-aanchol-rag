import re

from backend.app.customers.customer_repository import (
    PostgresCustomerRepository,
)
from backend.app.customers.models import Customer

CUSTOMER_FIELD_LIMITS = {
    "full_name": 150,
    "mobile_number": 20,
    "whatsapp_number": 20,
    "email": 254,
    "bill_to_contact_name": 150,
    "bill_to_phone": 20,
    "ship_to_contact_name": 150,
    "ship_to_phone": 20,
    "attribute1": 255,
    "attribute2": 255,
    "attribute3": 255,
    "attribute4": 255,
    "attribute5": 255,
}

OPTIONAL_FIELDS = (
    "whatsapp_number",
    "email",
    "bill_to_contact_name",
    "bill_to_phone",
    "bill_to_address",
    "ship_to_contact_name",
    "ship_to_phone",
    "ship_to_address",
    "notes",
    "attribute1",
    "attribute2",
    "attribute3",
    "attribute4",
    "attribute5",
)

REQUIRED_FIELDS = ("full_name", "mobile_number")

ALLOWED_FIELDS = set(REQUIRED_FIELDS + OPTIONAL_FIELDS)


class CustomerService:
    def __init__(
        self,
        repository: PostgresCustomerRepository,
    ) -> None:
        self.repository = repository

    @staticmethod
    def _validate_text(
        field_name: str,
        value: str | None,
        required: bool = False,
    ) -> str | None:
        if value is None:
            if required:
                raise ValueError(f"{field_name} is required.")
            return None

        if not isinstance(value, str):
            raise ValueError(f"{field_name} must be a string.")

        value = value.strip()

        if not value:
            if required:
                raise ValueError(f"{field_name} is required.")
            return None

        max_length = CUSTOMER_FIELD_LIMITS.get(field_name)

        if max_length is not None and len(value) > max_length:
            raise ValueError(
                f"{field_name} cannot exceed {max_length} characters."
            )

        return value

    @staticmethod
    def _validate_email(email: str | None) -> None:
        if email is not None and not re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+",
            email,
        ):
            raise ValueError("Invalid email address.")

    @staticmethod
    def _validate_phone(
        field_name: str,
        phone: str | None,
    ) -> None:
        if phone is None:
            return

        if not re.fullmatch(r"\+?[0-9().\-\s]+", phone):
            raise ValueError(
                f"{field_name} contains invalid characters."
            )

        if not any("0" <= char <= "9" for char in phone):
            raise ValueError(
                f"{field_name} must contain at least one digit."
            )

    def _normalize_customer_data(
        self,
        customer_data: dict[str, str | None],
        validate_required: bool = True,
    ) -> dict[str, str | None]:
        if not isinstance(customer_data, dict):
            raise ValueError("Customer data must be a dictionary.")

        unknown_fields = set(customer_data) - ALLOWED_FIELDS

        if unknown_fields:
            raise ValueError("Unknown customer fields supplied.")

        normalized = {}

        for field_name in ALLOWED_FIELDS:
            value = customer_data.get(field_name)

            normalized[field_name] = self._validate_text(
                field_name,
                value,
                required=(
                    field_name in REQUIRED_FIELDS
                    and (validate_required or field_name in customer_data)
                ),
            )

        self._validate_email(normalized["email"])

        for field_name in (
            "mobile_number",
            "whatsapp_number",
            "bill_to_phone",
            "ship_to_phone",
        ):
            self._validate_phone(
                field_name,
                normalized[field_name],
            )

        return normalized

    def create_customer(
        self,
        customer_data: dict[str, str | None],
    ) -> Customer:
        normalized = self._normalize_customer_data(customer_data)

        return self.repository.create_customer(normalized)

    def get_customer(self, customer_id: int) -> Customer | None:
        if isinstance(customer_id, bool) or not isinstance(customer_id, int):
            raise ValueError("Customer ID must be an integer.")

        if customer_id <= 0:
            raise ValueError("Customer ID must be greater than zero.")

        return self.repository.get_customer(customer_id)

    def list_customers(
        self,
        search: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Customer]:
        if search is not None:
            if not isinstance(search, str):
                raise ValueError("Search must be a string.")

            search = search.strip() or None

        if isinstance(limit, bool) or not isinstance(limit, int):
            raise ValueError("Limit must be an integer.")

        if limit <= 0 or limit > 100:
            raise ValueError("Limit must be between 1 and 100.")

        if isinstance(offset, bool) or not isinstance(offset, int):
            raise ValueError("Offset must be an integer.")

        if offset < 0:
            raise ValueError("Offset cannot be negative.")

        return self.repository.list_customers(
            search=search,
            limit=limit,
            offset=offset,
        )

    def update_customer(
        self,
        customer_id: int,
        updates: dict[str, str | None],
    ) -> Customer | None:
        if isinstance(customer_id, bool) or not isinstance(customer_id, int):
            raise ValueError("Customer ID must be an integer.")

        if customer_id <= 0:
            raise ValueError("Customer ID must be greater than zero.")

        if not isinstance(updates, dict):
            raise ValueError("Customer updates must be a dictionary.")

        if not updates:
            raise ValueError("At least one update field is required.")

        normalized = self._normalize_customer_data(
            updates,
            validate_required=False,
        )

        # Only update fields explicitly supplied by the caller.
        normalized = {
            field_name: normalized[field_name]
            for field_name in updates
        }

        return self.repository.update_customer(
            customer_id,
            normalized,
        )
