import re


def _normalize_word(value: str) -> str:
    """Normalize a catalogue value for plural-variant generation."""
    return value.strip().casefold()


def generate_plural_variants(value: str) -> set[str]:
    """
    Generate conservative English plural variants for a catalogue value.

    The input value comes from the live catalogue vocabulary, so no
    Urban Aanchol-specific values are hard-coded here.

    Only simple word-level variants are generated.
    """
    normalized = _normalize_word(value)

    if not normalized or " " in normalized:
        return set()

    variants: set[str] = set()

    if normalized.endswith(("s", "x", "z", "ch", "sh")):
        variants.add(f"{normalized}es")
    elif normalized.endswith("y") and len(normalized) > 1:
        if normalized[-2] not in "aeiou":
            variants.add(f"{normalized[:-1]}ies")
        else:
            variants.add(f"{normalized}s")
    else:
        variants.add(f"{normalized}s")

    return variants