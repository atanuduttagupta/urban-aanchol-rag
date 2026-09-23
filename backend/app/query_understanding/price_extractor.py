import re


_PRICE = r"(?:₹|rs\.?|inr)?\s*(\d[\d,]*(?:\.\d{1,2})?)"


def _parse_price(value: str) -> float:
    return float(value.replace(",", ""))


def extract_price_filters(query: str) -> dict[str, float]:
    """
    Extract explicit price bounds from a customer query.

    Only phrases that clearly express a price constraint are matched.
    """
    filters: dict[str, float] = {}

    range_match = re.search(
        rf"\bbetween\s+{_PRICE}\s+(?:and|-)\s+{_PRICE}\b",
        query,
        flags=re.IGNORECASE,
    )

    if range_match:
        filters["min_price"] = _parse_price(range_match.group(1))
        filters["max_price"] = _parse_price(range_match.group(2))
        return filters

    max_match = re.search(
        rf"\b(?:under|below|less\s+than|up\s+to)\s+{_PRICE}\b",
        query,
        flags=re.IGNORECASE,
    )

    if max_match:
        filters["max_price"] = _parse_price(max_match.group(1))

    min_match = re.search(
        rf"\b(?:above|over|more\s+than)\s+{_PRICE}\b",
        query,
        flags=re.IGNORECASE,
    )

    if min_match:
        filters["min_price"] = _parse_price(min_match.group(1))

    return filters