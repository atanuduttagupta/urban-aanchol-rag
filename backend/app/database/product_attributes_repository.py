from typing import Iterable

from psycopg import Connection


def insert_product_attributes(
    connection: Connection,
    products: Iterable[dict],
) -> dict[str, int]:
    counts = {
        "occasions": 0,
        "styles": 0,
        "moods": 0,
        "tags": 0,
    }

    with connection.cursor() as cursor:
        for product in products:
            product_id = product["product_id"]

            for occasion in product.get("occasion", []):
                cursor.execute(
                    """
                    INSERT INTO product_occasions (product_id, occasion)
                    VALUES (%s, %s)
                    ON CONFLICT (product_id, occasion) DO NOTHING
                    """,
                    (product_id, occasion),
                )
                counts["occasions"] += cursor.rowcount

            for style in product.get("style", []):
                cursor.execute(
                    """
                    INSERT INTO product_styles (product_id, style)
                    VALUES (%s, %s)
                    ON CONFLICT (product_id, style) DO NOTHING
                    """,
                    (product_id, style),
                )
                counts["styles"] += cursor.rowcount

            for mood in product.get("mood", []):
                cursor.execute(
                    """
                    INSERT INTO product_moods (product_id, mood)
                    VALUES (%s, %s)
                    ON CONFLICT (product_id, mood) DO NOTHING
                    """,
                    (product_id, mood),
                )
                counts["moods"] += cursor.rowcount

            for tag in product.get("tags", []):
                cursor.execute(
                    """
                    INSERT INTO product_tags (product_id, tag)
                    VALUES (%s, %s)
                    ON CONFLICT (product_id, tag) DO NOTHING
                    """,
                    (product_id, tag),
                )
                counts["tags"] += cursor.rowcount

    return counts