import os
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
ENV_FILE = PROJECT_ROOT / ".env"
MONEY_PRECISION = Decimal("0.01")


class DeliveryChargeConfigurationError(RuntimeError):
    """Raised when delivery charge configuration is missing or invalid."""


def get_flat_delivery_charge() -> Decimal:
    """
    Read and validate the configured flat delivery charge in INR.

    The value is loaded from the project root .env file.
    """
    load_dotenv(ENV_FILE)

    raw_value = os.getenv("DELIVERY_FLAT_CHARGE")

    if raw_value is None or not raw_value.strip():
        raise DeliveryChargeConfigurationError(
            "DELIVERY_FLAT_CHARGE is not configured in the project root .env file."
        )

    try:
        charge = Decimal(raw_value.strip())
    except InvalidOperation as exc:
        raise DeliveryChargeConfigurationError(
            "DELIVERY_FLAT_CHARGE must be a valid decimal amount."
        ) from exc

    if not charge.is_finite():
        raise DeliveryChargeConfigurationError("DELIVERY_FLAT_CHARGE must be finite.")

    if charge < 0:
        raise DeliveryChargeConfigurationError(
            "DELIVERY_FLAT_CHARGE cannot be negative."
        )

    return charge.quantize(MONEY_PRECISION, rounding=ROUND_HALF_UP)
