import hashlib
import json
from datetime import date
from uuid import UUID

from backend.app.orders.models import CreateOrderRequest
from backend.app.orders.order_pricing import MONEY_PRECISION


class IdempotencyConflictError(Exception):
    """Raised when an idempotency key is reused with a different request."""


def calculate_order_request_hash(
    request: CreateOrderRequest,
) -> str:
    """Calculate a deterministic SHA-256 fingerprint of an order request."""

    payload = {
        "customer_id": request.customer_id,
        "items": [
            {
                "product_id": item.product_id,
                "quantity": item.quantity,
                "line_discount": format(
                    item.line_discount.quantize(MONEY_PRECISION),
                    "f",
                ),
                "notes": item.notes,
                "hold_id": item.hold_id,
            }
            for item in request.items
        ],
        "discount_amount": format(
            request.discount_amount.quantize(MONEY_PRECISION),
            "f",
        ),
        "expected_delivery_date": (
            request.expected_delivery_date.isoformat()
            if isinstance(request.expected_delivery_date, date)
            else None
        ),
        "ship_to_contact_name": request.ship_to_contact_name,
        "ship_to_phone": request.ship_to_phone,
        "ship_to_address": request.ship_to_address,
        "notes": request.notes,
    }

    canonical_json = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )

    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


def calculate_advisory_lock_id(
    customer_id: int,
    idempotency_key: UUID,
) -> int:
    """Generate a deterministic PostgreSQL advisory-lock identifier."""

    lock_identity = f"{customer_id}:{idempotency_key}"

    digest = hashlib.sha256(lock_identity.encode("utf-8")).digest()

    return int.from_bytes(
        digest[:8],
        byteorder="big",
        signed=True,
    )
