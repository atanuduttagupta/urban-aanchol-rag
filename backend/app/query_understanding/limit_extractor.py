import re
from collections.abc import Mapping, Sequence


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().casefold())


def _matches_catalogue_value(
    value: str,
    vocabulary: Mapping[str, Sequence[str]],
) -> bool:
    normalized_value = _normalize(value)

    for values in vocabulary.values():
        for catalogue_value in values:
            normalized_catalogue_value = _normalize(catalogue_value)

            if normalized_value == normalized_catalogue_value:
                return True

            # Support simple plural requests such as "sarees"
            # when the catalogue contains "Saree".
            if normalized_value == f"{normalized_catalogue_value}s":
                return True

    return False


def extract_requested_limit(
    query: str,
    vocabulary: Mapping[str, Sequence[str]] | None = None,
) -> int | None:
    """
    Extract an explicitly requested number of results.

    Result-display language is handled independently from the catalogue.

    When a number is followed directly by a catalogue item, the catalogue
    vocabulary is used to determine whether that number represents a
    requested result count.
    """
    patterns = (
        r"\bshow\s+me\s+(\d+)",
        r"\bshow\s+(\d+)",
        r"\bgive\s+me\s+(\d+)",
        r"\bfind\s+(\d+)",
        r"\blist\s+(\d+)",
        r"\btop\s+(\d+)",
    )

    for pattern in patterns:
        match = re.search(pattern, query, flags=re.IGNORECASE)

        if match:
            value = int(match.group(1))

            if value > 0:
                return value

    if vocabulary:
        catalogue_item_pattern = re.compile(
            r"\b(\d+)\s+([A-Za-z][A-Za-z\s-]*)\b",
            flags=re.IGNORECASE,
        )

        for match in catalogue_item_pattern.finditer(query):
            value = int(match.group(1))
            following_text = match.group(2).strip()

            words = following_text.split()

            # Try the shortest catalogue phrase first.
            for length in range(1, len(words) + 1):
                candidate = " ".join(words[:length])

                if _matches_catalogue_value(
                    candidate,
                    vocabulary,
                ):
                    if value > 0:
                        return value

    return None