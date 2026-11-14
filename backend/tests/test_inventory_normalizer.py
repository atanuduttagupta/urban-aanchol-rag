
import pytest

from backend.app.catalogue.normalizer import normalize_stock_quantity


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (0, 0),
        (10, 10),
        (5.0, 5),
        ("12", 12),
    ],
)
def test_stock_quantity_normalizes_to_integer(value, expected):
    result = normalize_stock_quantity(value)

    assert result == expected
    assert isinstance(result, int)


def test_none_stock_quantity_returns_none():
    assert normalize_stock_quantity(None) is None
