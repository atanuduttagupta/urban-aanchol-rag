from typing import Any


EXACT_FILTER_COLUMNS = {
    "category": "p.category",
    "availability": "p.availability",
}

TEXT_FILTER_COLUMNS = {
    "brand": "p.brand",
    "collection": "p.collection",
    "fabric": "p.fabric",
    "colour": "p.colour",
    "secondary_colour": "p.secondary_colour",
    "pattern": "p.pattern",
    "border": "p.border",
}

NORMALIZED_FILTER_TABLES = {
    "occasion": "product_occasions",
    "style": "product_styles",
    "mood": "product_moods",
    "tag": "product_tags",
}


def build_product_filter_sql(
    filters: dict[str, Any] | None,
) -> tuple[str, list[object]]:
    filters = filters or {}

    conditions: list[str] = []
    parameters: list[object] = []

    # Exact structured filters.
    for filter_name, column in EXACT_FILTER_COLUMNS.items():
        value = filters.get(filter_name)

        if value is not None:
            conditions.append(f"{column} = %s")
            parameters.append(value)

    # Descriptive text filters.
    for filter_name, column in TEXT_FILTER_COLUMNS.items():
        value = filters.get(filter_name)

        if value is not None:
            conditions.append(f"{column} ILIKE %s")
            parameters.append(f"%{value}%")

    # Numeric range filters.
    if filters.get("min_price") is not None:
        conditions.append("p.price >= %s")
        parameters.append(filters["min_price"])

    if filters.get("max_price") is not None:
        conditions.append("p.price <= %s")
        parameters.append(filters["max_price"])

    # Normalized descriptive attributes.
    for filter_name, table_name in NORMALIZED_FILTER_TABLES.items():
        value = filters.get(filter_name)

        if value is None:
            continue

        values = value if isinstance(value, list) else [value]

        value_conditions = []
        for item in values:
            value_conditions.append(
                f"attribute.{filter_name} ILIKE %s"
            )
            parameters.append(f"%{item}%")

        conditions.append(
            f"""
            EXISTS (
                SELECT 1
                FROM {table_name} attribute
                WHERE attribute.product_id = p.product_id
                AND (
                    {" OR ".join(value_conditions)}
                )
            )
            """
        )

    if not conditions:
        return "", parameters

    sql = "".join(
        f"\n            AND {condition}"
        for condition in conditions
    )

    return sql, parameters