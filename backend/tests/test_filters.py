from backend.app.retrieval.filters import build_product_filter_sql


def test_empty_filters():
    sql, parameters = build_product_filter_sql(None)

    assert sql == ""
    assert parameters == []


def test_exact_text_and_range_filters():
    sql, parameters = build_product_filter_sql(
        {
            "category": "Saree",
            "availability": "Available",
            "fabric": "Cotton",
            "colour": "Blue",
            "min_price": 1500,
            "max_price": 2500,
        }
    )

    assert "p.category = %s" in sql
    assert "p.availability = %s" in sql
    assert "p.fabric ILIKE %s" in sql
    assert "p.colour ILIKE %s" in sql
    assert "p.price >= %s" in sql
    assert "p.price <= %s" in sql

    assert parameters == [
        "Saree",
        "Available",
        "%Cotton%",
        "%Blue%",
        1500,
        2500,
    ]


def test_normalized_text_filter():
    sql, parameters = build_product_filter_sql(
        {
            "occasion": "Wedding",
        }
    )

    assert "FROM product_occasions attribute" in sql
    assert "attribute.product_id = p.product_id" in sql
    assert "attribute.occasion ILIKE %s" in sql
    assert parameters == ["%Wedding%"]


def test_multiple_normalized_text_filters():
    sql, parameters = build_product_filter_sql(
        {
            "occasion": "Wedding",
            "style": "Traditional",
            "mood": "Elegant",
            "tag": "Festive",
        }
    )

    assert "FROM product_occasions attribute" in sql
    assert "FROM product_styles attribute" in sql
    assert "FROM product_moods attribute" in sql
    assert "FROM product_tags attribute" in sql

    assert parameters == [
        "%Wedding%",
        "%Traditional%",
        "%Elegant%",
        "%Festive%",
    ]


def test_colour_filter_is_partial_and_case_insensitive():
    sql, parameters = build_product_filter_sql(
        {
            "colour": "blue",
        }
    )

    assert "p.colour ILIKE %s" in sql
    assert parameters == ["%blue%"]


def test_availability_is_exact_filter():
    sql, parameters = build_product_filter_sql(
        {
            "availability": "Available",
        }
    )

    assert "p.availability = %s" in sql
    assert parameters == ["Available"]


def test_price_range_filters():
    sql, parameters = build_product_filter_sql(
        {
            "min_price": 1500,
            "max_price": 3000,
        }
    )

    assert "p.price >= %s" in sql
    assert "p.price <= %s" in sql

    assert parameters == [1500, 3000]


def test_multiple_values_within_normalized_filter_use_or():
    sql, parameters = build_product_filter_sql(
        {
            "mood": ["Elegant", "Vibrant"],
        }
    )

    assert sql.count("FROM product_moods attribute") == 1
    assert sql.count("attribute.mood ILIKE %s") == 2

    assert parameters == [
        "%Elegant%",
        "%Vibrant%",
    ]


def test_multiple_values_across_filters_use_and():
    sql, parameters = build_product_filter_sql(
        {
            "occasion": "Wedding",
            "mood": ["Elegant", "Vibrant"],
        }
    )

    assert "FROM product_occasions attribute" in sql
    assert "FROM product_moods attribute" in sql

    assert sql.count("attribute.mood ILIKE %s") == 2

    assert parameters == [
        "%Wedding%",
        "%Elegant%",
        "%Vibrant%",
    ]
