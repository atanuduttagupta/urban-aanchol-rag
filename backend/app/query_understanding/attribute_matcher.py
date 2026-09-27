import re
from collections.abc import Mapping, Sequence

from .plural_variants import generate_plural_variants


def _normalize_for_matching(value: str) -> str:
    """Normalize text for deterministic attribute matching."""
    normalized = value.strip().casefold()
    return re.sub(r"\s+", " ", normalized)


def _find_catalogue_matches(
    query: str,
    values: Sequence[str],
) -> list[tuple[int, int, str]]:
    """
    Find catalogue values occurring in the query.

    Returns:
        A list of (start, end, catalogue_value) matches.
    """
    matches: set[tuple[int, int, str]] = set()

    for value in values:
        normalized_value = _normalize_for_matching(value)

        if not normalized_value:
            continue

        candidate_values = {normalized_value}
        candidate_values.update(generate_plural_variants(normalized_value))

        for candidate in candidate_values:
            pattern = rf"(?<!\w){re.escape(candidate)}(?!\w)"

            for match in re.finditer(pattern, query):
                matches.add(
                    (
                        match.start(),
                        match.end(),
                        value,
                    )
                )

    return list(matches)


def _resolve_overlapping_matches(
    matches: Sequence[tuple[int, int, str]],
) -> list[tuple[int, int, str]]:
    """
    Resolve overlapping catalogue matches.

    When matches overlap, prefer the longest match.
    Non-overlapping matches are preserved.
    """
    ordered_matches = sorted(
        matches,
        key=lambda item: (
            -(item[1] - item[0]),
            item[0],
            item[2].casefold(),
        ),
    )

    accepted: list[tuple[int, int, str]] = []

    for candidate in ordered_matches:
        candidate_start, candidate_end, _ = candidate

        overlaps = any(
            candidate_start < accepted_end and candidate_end > accepted_start
            for accepted_start, accepted_end, _ in accepted
        )

        if not overlaps:
            accepted.append(candidate)

    return accepted


def match_catalogue_attributes(
    query: str,
    vocabulary: Mapping[str, Sequence[str]],
) -> dict[str, list[str]]:
    """
    Match customer query text against the current catalogue vocabulary.

    Matching is case-insensitive and whitespace-normalized.
    Only complete catalogue attribute phrases are considered.

    When catalogue values overlap, the most specific/longest match
    is preferred.

    The matcher is vocabulary-driven: it does not maintain a hard-coded
    list of attribute names or values.
    """
    normalized_query = _normalize_for_matching(query)
    matches: dict[str, list[str]] = {}

    for attribute_name, values in vocabulary.items():
        catalogue_matches = _find_catalogue_matches(
            query=normalized_query,
            values=values,
        )

        resolved_matches = _resolve_overlapping_matches(catalogue_matches)

        if not resolved_matches:
            continue

        matched_values = {value for _, _, value in resolved_matches}

        ordered_values = [value for value in values if value in matched_values]

        if ordered_values:
            matches[attribute_name] = ordered_values

    return matches
