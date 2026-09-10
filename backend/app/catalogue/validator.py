from datetime import date, datetime
from decimal import Decimal

from .schema import (
    ALLOWED_AVAILABILITY,
    ALLOWED_CATEGORIES,
    EXPECTED_HEADERS,
)


def validate_headers(headers: list[str]) -> list[str]:
    """Validate the catalogue column structure."""
    errors = []

    actual_headers = set(headers)
    expected_headers = set(EXPECTED_HEADERS)

    missing_headers = expected_headers - actual_headers
    unexpected_headers = actual_headers - expected_headers

    if missing_headers:
        errors.append(
            f"Missing columns: {', '.join(sorted(missing_headers))}"
        )

    if unexpected_headers:
        errors.append(
            f"Unexpected columns: {', '.join(sorted(unexpected_headers))}"
        )

    if len(headers) != len(set(headers)):
        errors.append("Duplicate column names found.")

    return errors


def validate_product(product: dict, row_number: int) -> list[str]:
    """Validate one product record."""
    errors = []

    product_id = product.get("product_id")
    product_name = product.get("product_name")
    category = product.get("category")
    price = product.get("price")
    availability = product.get("availability")

    if not product_id:
        errors.append(f"Row {row_number}: product_id is required.")

    if not product_name:
        errors.append(f"Row {row_number}: product_name is required.")

    if category not in ALLOWED_CATEGORIES:
        errors.append(
            f"Row {row_number}: invalid category '{category}'."
        )

    if availability not in ALLOWED_AVAILABILITY:
        errors.append(
            f"Row {row_number}: invalid availability '{availability}'."
        )

    if price is None:
        errors.append(f"Row {row_number}: price is required.")
    elif not isinstance(price, (int, float, Decimal)):
        errors.append(
            f"Row {row_number}: price must be numeric."
        )
    elif price < 0:
        errors.append(
            f"Row {row_number}: price cannot be negative."
        )

    for field in ("launch_date", "created_date", "last_updated"):
        value = product.get(field)

        if value is not None and not isinstance(value, (date, datetime)):
            errors.append(
                f"Row {row_number}: {field} must be a valid date."
            )

    return errors


def validate_products(
    products: list[dict],
    headers: list[str],
) -> list[str]:
    """Validate the complete catalogue."""
    errors = validate_headers(headers)

    seen_product_ids = set()

    for index, product in enumerate(products, start=1):
        errors.extend(validate_product(product, index))

        product_id = product.get("product_id")

        if product_id:
            if product_id in seen_product_ids:
                errors.append(
                    f"Product {index}: duplicate product_id '{product_id}'."
                )

            seen_product_ids.add(product_id)

    return errors