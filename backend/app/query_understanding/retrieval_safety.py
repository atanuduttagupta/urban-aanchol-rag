import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class RetrievalSafety:
    """
    Describes whether deterministic parsing is safe to use
    without requiring additional interpretation.

    `retrieval_safe=True` means there is positive evidence that
    no known retrieval-critical ambiguity remains.

    `signals` records why the query was considered unsafe.
    """

    retrieval_safe: bool
    signals: tuple[str, ...] = ()


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().casefold())


def _catalogue_values(
    vocabulary: Mapping[str, Sequence[str]],
) -> tuple[str, ...]:
    values: list[str] = []

    for attribute_values in vocabulary.values():
        for value in attribute_values:
            normalized = _normalize(value)
            if normalized and normalized not in values:
                values.append(normalized)

    return tuple(values)


def _contains_catalogue_value(
    text: str,
    catalogue_values: Sequence[str],
) -> bool:
    for value in catalogue_values:
        pattern = rf"(?<!\w){re.escape(value)}(?!\w)"
        if re.search(pattern, text):
            return True

    return False


def _has_retrieval_critical_negation(
    query: str,
    catalogue_values: Sequence[str],
) -> bool:
    negative_patterns = (
        r"\bnot\s+",
        r"\bdon't\s+want\s+",
        r"\bdo\s+not\s+want\s+",
        r"\bdont\s+want\s+",
        r"\bwithout\s+",
        r"\bexcept\s+",
        r"\bavoid\s+",
    )

    for pattern in negative_patterns:
        matches = re.finditer(pattern, query)

        for match in matches:
            following_text = query[match.end() :]

            if _contains_catalogue_value(
                following_text,
                catalogue_values,
            ):
                return True

    return False


def detect_retrieval_safety(
    query: str,
    vocabulary: Mapping[str, Sequence[str]],
) -> RetrievalSafety:
    """
    Detect known retrieval-critical ambiguity signals.

    This detector is intentionally conservative:
    if a known retrieval-critical pattern is detected,
    deterministic retrieval is considered unsafe.

    Unknown descriptive language is NOT considered unsafe;
    it can remain in the semantic query.

    Catalogue values are obtained dynamically from the supplied
    vocabulary rather than being hard-coded here.
    """
    normalized = _normalize(query)
    signals: list[str] = []

    catalogue_values = _catalogue_values(vocabulary)

    # Conversational / relative references.
    reference_patterns = (
        r"\bthe one\b",
        r"\bthat one\b",
        r"\bthis one\b",
        r"\bthe previous\b",
        r"\bearlier\b",
        r"\bas before\b",
        r"\bsame as\b",
        r"\blike that\b",
        r"\b(?:first|second|third|1st|2nd|3rd)\s+one\b",
        r"\b(?:this|that)\s+(?:saree|one)\b",
    )

    if any(re.search(pattern, normalized) for pattern in reference_patterns):
        signals.append("conversational_reference_detected")

    # Explicit comparison.
    comparison_patterns = (
        r"\bcheaper than\b",
        r"\bmore expensive than\b",
        r"\bmore costly than\b",
        r"\bsimilar to\b",
        r"\bdifferent from\b",
        r"\bbetter than\b",
    )

    if any(re.search(pattern, normalized) for pattern in comparison_patterns):
        signals.append("comparison_detected")

    # Negation targeting a known catalogue value.
    if _has_retrieval_critical_negation(
        query=normalized,
        catalogue_values=catalogue_values,
    ):
        signals.append("negation_detected")

    # Approximate / soft constraints.
    approximation_patterns = (
        r"\baround\s+(?:₹|rs\.?|inr)?\s*\d",
        r"\bapproximately\s+(?:₹|rs\.?|inr)?\s*\d",
        r"\babout\s+(?:₹|rs\.?|inr)?\s*\d",
        r"\bnot too expensive\b",
        r"\baffordable\b",
    )

    if any(re.search(pattern, normalized) for pattern in approximation_patterns):
        signals.append("approximate_constraint_detected")

    return RetrievalSafety(
        retrieval_safe=not signals,
        signals=tuple(signals),
    )
