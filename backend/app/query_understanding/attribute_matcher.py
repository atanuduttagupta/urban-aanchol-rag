import re
from collections.abc import Mapping, Sequence
from .plural_variants import generate_plural_variants


def _normalize_for_matching(value: str) -> str:
    """Normalize text for deterministic attribute matching."""
    normalized = value.strip().casefold()
    return re.sub(r"\s+", " ", normalized)


def match_catalogue_attributes(
    query: str,
    vocabulary: Mapping[str, Sequence[str]],
) -> dict[str, list[str]]:
    """
    Match customer query text against the current catalogue vocabulary.

    Matching is case-insensitive and whitespace-normalized.
    Only complete catalogue attribute phrases are considered.

    The matcher is vocabulary-driven: it does not maintain a hard-coded
    list of attribute names. New catalogue attributes can therefore be
    matched without changing this module.
    """
    normalized_query = _normalize_for_matching(query)
    matches: dict[str, list[str]] = {}

    for attribute_name, values in vocabulary.items():
        attribute_matches = []

        for value in values:
            normalized_value = _normalize_for_matching(value)

            if not normalized_value:
                continue

            candidate_values = {normalized_value}

            candidate_values.update(
                generate_plural_variants(normalized_value)
            )

            for candidate in candidate_values:
                pattern = rf"(?<!\w){re.escape(candidate)}(?!\w)"

                if re.search(pattern, normalized_query):
                    attribute_matches.append(value)
                    break

        if attribute_matches:
            matches[attribute_name] = attribute_matches

    return matches