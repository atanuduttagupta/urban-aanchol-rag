from decimal import Decimal

import pytest

from backend.app.orders.delivery_charge import (
    DeliveryChargeConfigurationError,
    get_flat_delivery_charge,
)


def test_reads_and_rounds_delivery_charge(monkeypatch):
    monkeypatch.setenv("DELIVERY_FLAT_CHARGE", "50.555")

    result = get_flat_delivery_charge()

    assert result == Decimal("50.56")


def test_accepts_explicit_zero_delivery_charge(monkeypatch):
    monkeypatch.setenv("DELIVERY_FLAT_CHARGE", "0")

    assert get_flat_delivery_charge() == Decimal("0.00")


@pytest.mark.parametrize(
    "value",
    ["-10", "NaN", "Infinity", "-Infinity", "invalid"],
)
def test_rejects_invalid_delivery_charge(monkeypatch, value):
    monkeypatch.setenv("DELIVERY_FLAT_CHARGE", value)

    with pytest.raises(DeliveryChargeConfigurationError):
        get_flat_delivery_charge()


def test_rejects_missing_delivery_charge(monkeypatch):
    monkeypatch.delenv("DELIVERY_FLAT_CHARGE", raising=False)

    with pytest.raises(DeliveryChargeConfigurationError):
        get_flat_delivery_charge()


def test_rejects_empty_delivery_charge(monkeypatch):
    monkeypatch.setenv("DELIVERY_FLAT_CHARGE", "  ")

    with pytest.raises(DeliveryChargeConfigurationError):
        get_flat_delivery_charge()
