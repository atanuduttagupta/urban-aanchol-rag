from collections.abc import Mapping, Sequence

from backend.app.retrieval.models import RetrievalIntent

from .attribute_matcher import match_catalogue_attributes
from .limit_extractor import extract_requested_limit
from .price_extractor import extract_price_filters
from .retrieval_safety import detect_retrieval_safety


def understand_query(
    query: str,
    vocabulary: Mapping[str, Sequence[str]],
) -> RetrievalIntent:
    """
    Convert a customer query into a deterministic RetrievalIntent.

    The original customer message is preserved unchanged.
    Explicit catalogue attributes, price constraints, and requested
    result limits are extracted when they can be identified
    deterministically.

    The remaining natural-language query is preserved as the
    semantic query for keyword and semantic retrieval.
    """
    filters: dict[str, object] = {}

    attribute_matches = match_catalogue_attributes(
        query=query,
        vocabulary=vocabulary,
    )

    # Structured attributes take precedence over duplicate tag values.
    structured_attributes = {
        "category",
        "fabric",
        "brand",
        "collection",
        "colour",
        "secondary_colour",
        "pattern",
        "border",
    }

    structured_values = {
        value.strip().casefold()
        for attribute_name, values in attribute_matches.items()
        if attribute_name in structured_attributes
        for value in values
    }

    for attribute_name, values in attribute_matches.items():
        if attribute_name == "tag":
            values = [
                value
                for value in values
                if value.strip().casefold() not in structured_values
            ]

        if not values:
            continue

        if len(values) == 1:
            filters[attribute_name] = values[0]
        else:
            filters[attribute_name] = values

    price_filters = extract_price_filters(query)
    filters.update(price_filters)

    requested_limit = extract_requested_limit(
        query=query,
        vocabulary=vocabulary,
    )

    retrieval_safety = detect_retrieval_safety(
        query=query,
        vocabulary=vocabulary,
    )

    return RetrievalIntent(
        original_query=query,
        semantic_query=query,
        filters=filters or None,
        requested_limit=requested_limit,
        retrieval_safety=retrieval_safety,
    )
