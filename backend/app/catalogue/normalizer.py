from datetime import date, datetime
from decimal import Decimal


MULTI_VALUE_FIELDS = {
    "occasion",
    "style",
    "mood",
    "tags",
}


def normalize_text(value):
    """Normalize a text value."""
    if value is None:
        return None

    value = str(value).strip()

    return value if value else None


def normalize_multi_value(value):
    """Convert a comma-separated value into a clean list."""
    if value is None:
        return []

    values = str(value).split(",")

    return [
        item.strip()
        for item in values
        if item.strip()
    ]


def normalize_price(value):
    """Normalize price into a numeric Decimal value."""
    if value is None:
        return None

    if isinstance(value, Decimal):
        return value

    if isinstance(value, (int, float)):
        return Decimal(str(value))

    return Decimal(str(value).strip())


def normalize_date(value):
    """Normalize date/datetime values to a date."""
    if value is None:
        return None

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    return value


def normalize_product(product: dict) -> dict:
    """Convert one raw Excel product record into a normalized record."""

    normalized = {}

    for field, value in product.items():

        if field in MULTI_VALUE_FIELDS:
            normalized[field] = normalize_multi_value(value)

        elif field == "price":
            normalized[field] = normalize_price(value)

        elif field in {
            "launch_date",
            "created_date",
            "last_updated",
        }:
            normalized[field] = normalize_date(value)

        else:
            normalized[field] = normalize_text(value)

    return normalized


def normalize_products(products: list[dict]) -> list[dict]:
    """Normalize all product records."""

    return [
        normalize_product(product)
        for product in products
    ]