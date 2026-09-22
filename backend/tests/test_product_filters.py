from backend.app.retrieval.filters import build_product_filter_sql


def test_empty_filters():
    sql, parameters = build_product_filter_sql({})

    assert sql == ""
    assert parameters == []


def test_exact_and_text_and_price_filters():
    sql, parameters = build_product_filter_sql(
        {
            "category": "Saree",
            "fabric": "Cotton",
            "max_price": 3000,
        }
    )

    assert "p.category = %s" in sql
    assert "p.fabric ILIKE %s" in sql
    assert "p.price <= %s" in sql

    assert parameters == [
        "Saree",
        "%Cotton%",
        3000,
    ]


def test_normalized_text_filter():
    sql, parameters = build_product_filter_sql(
        {
            "occasion": "Puja",
        }
    )

    assert "attribute.occasion ILIKE %s" in sql

    assert parameters == [
        "%Puja%",
    ]


def test_multiple_normalized_text_filters():
    sql, parameters = build_product_filter_sql(
        {
            "occasion": "Puja",
            "style": "Traditional",
            "tag": "Handloom",
        }
    )

    assert "attribute.occasion ILIKE %s" in sql
    assert "attribute.style ILIKE %s" in sql
    assert "attribute.tag ILIKE %s" in sql

    assert parameters == [
        "%Puja%",
        "%Traditional%",
        "%Handloom%",
    ]


def test_colour_uses_partial_case_insensitive_matching():
    sql, parameters = build_product_filter_sql(
        {
            "colour": "Blue",
        }
    )

    assert "p.colour ILIKE %s" in sql
    assert parameters == [
        "%Blue%",
    ]


def test_availability_uses_exact_matching():
    sql, parameters = build_product_filter_sql(
        {
            "availability": "Available",
        }
    )

    assert "p.availability = %s" in sql
    assert parameters == [
        "Available",
    ]


def test_price_range_filters():
    sql, parameters = build_product_filter_sql(
        {
            "min_price": 1500,
            "max_price": 3000,
        }
    )

    assert "p.price >= %s" in sql
    assert "p.price <= %s" in sql

    assert parameters == [
        1500,
        3000,
    ]