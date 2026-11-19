from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from backend.app.orders.models import OrderItemRequest

MONEY_PRECISION = Decimal("0.01")


def _to_money(value: Decimal, field_name: str) -> Decimal:
    """Validate and normalize a monetary value to two decimal places."""
    if not isinstance(value, Decimal) or not value.is_finite():
        raise ValueError(f"{field_name} must be a finite Decimal")

    if value < 0:
        raise ValueError(f"{field_name} cannot be negative")

    return value.quantize(MONEY_PRECISION, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class OrderLinePricing:
    product_id: str
    quantity: int
    unit_price: Decimal
    line_discount: Decimal
    gross_total: Decimal
    line_total: Decimal


@dataclass(frozen=True)
class OrderPricing:
    lines: tuple[OrderLinePricing, ...]
    subtotal: Decimal
    discount_amount: Decimal
    delivery_charge: Decimal
    grand_total: Decimal


def calculate_order_pricing(
    items: tuple[OrderItemRequest, ...],
    unit_prices: dict[str, Decimal],
    discount_amount: Decimal,
    delivery_charge: Decimal,
) -> OrderPricing:
    """
    Calculate order pricing using database-derived product prices.

    All monetary values are normalized to two decimal places.
    """

    if not isinstance(items, tuple) or not items:
        raise ValueError("items must be a non-empty tuple")

    if not all(isinstance(item, OrderItemRequest) for item in items):
        raise ValueError("All items must be OrderItemRequest instances")

    if not isinstance(unit_prices, dict):
        raise ValueError("unit_prices must be a dictionary")

    product_ids = [item.product_id for item in items]

    if len(product_ids) != len(set(product_ids)):
        raise ValueError("Duplicate product IDs are not allowed")

    if set(unit_prices) != set(product_ids):
        raise ValueError("Product prices do not match requested products")

    normalized_discount = _to_money(
        discount_amount,
        "discount_amount",
    )

    normalized_delivery = _to_money(
        delivery_charge,
        "delivery_charge",
    )

    line_results = []

    for item in items:
        unit_price = _to_money(
            unit_prices[item.product_id],
            "unit_price",
        )

        line_discount = _to_money(
            item.line_discount,
            "line_discount",
        )

        gross_total = _to_money(
            unit_price * item.quantity,
            "gross_total",
        )

        if line_discount > gross_total:
            raise ValueError(
                f"Line discount exceeds gross amount for {item.product_id}"
            )

        line_total = _to_money(
            gross_total - line_discount,
            "line_total",
        )

        line_results.append(
            OrderLinePricing(
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=unit_price,
                line_discount=line_discount,
                gross_total=gross_total,
                line_total=line_total,
            )
        )

    subtotal = _to_money(
        sum(
            (line.line_total for line in line_results),
            Decimal("0.00"),
        ),
        "subtotal",
    )

    if normalized_discount > subtotal:
        raise ValueError("Order discount cannot exceed subtotal")

    grand_total = _to_money(
        subtotal - normalized_discount + normalized_delivery,
        "grand_total",
    )

    return OrderPricing(
        lines=tuple(line_results),
        subtotal=subtotal,
        discount_amount=normalized_discount,
        delivery_charge=normalized_delivery,
        grand_total=grand_total,
    )
