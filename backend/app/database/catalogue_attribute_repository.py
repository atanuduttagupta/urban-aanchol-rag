from psycopg import Connection


def get_occasions(connection: Connection) -> list[str]:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT DISTINCT occasion
            FROM product_occasions
            ORDER BY occasion
            """
        )
        return [row[0] for row in cursor.fetchall()]


def get_styles(connection: Connection) -> list[str]:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT DISTINCT style
            FROM product_styles
            ORDER BY style
            """
        )
        return [row[0] for row in cursor.fetchall()]


def get_moods(connection: Connection) -> list[str]:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT DISTINCT mood
            FROM product_moods
            ORDER BY mood
            """
        )
        return [row[0] for row in cursor.fetchall()]


def get_tags(connection: Connection) -> list[str]:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT DISTINCT tag
            FROM product_tags
            ORDER BY tag
            """
        )
        return [row[0] for row in cursor.fetchall()]


def get_categories(connection: Connection) -> list[str]:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT DISTINCT category
            FROM products
            ORDER BY category
            """
        )
        return [row[0] for row in cursor.fetchall()]


def get_brands(connection: Connection) -> list[str]:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT DISTINCT brand
            FROM products
            WHERE brand IS NOT NULL
              AND TRIM(brand) <> ''
            ORDER BY brand
            """
        )
        return [row[0] for row in cursor.fetchall()]


def get_collections(connection: Connection) -> list[str]:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT DISTINCT collection
            FROM products
            WHERE collection IS NOT NULL
              AND TRIM(collection) <> ''
            ORDER BY collection
            """
        )
        return [row[0] for row in cursor.fetchall()]


def get_fabrics(connection: Connection) -> list[str]:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT DISTINCT fabric
            FROM products
            WHERE fabric IS NOT NULL
              AND TRIM(fabric) <> ''
            ORDER BY fabric
            """
        )
        return [row[0] for row in cursor.fetchall()]


def get_colours(connection: Connection) -> list[str]:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT DISTINCT colour
            FROM products
            WHERE colour IS NOT NULL
              AND TRIM(colour) <> ''
            ORDER BY colour
            """
        )
        return [row[0] for row in cursor.fetchall()]


def get_secondary_colours(connection: Connection) -> list[str]:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT DISTINCT secondary_colour
            FROM products
            WHERE secondary_colour IS NOT NULL
              AND TRIM(secondary_colour) <> ''
            ORDER BY secondary_colour
            """
        )
        return [row[0] for row in cursor.fetchall()]


def get_patterns(connection: Connection) -> list[str]:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT DISTINCT pattern
            FROM products
            WHERE pattern IS NOT NULL
              AND TRIM(pattern) <> ''
            ORDER BY pattern
            """
        )
        return [row[0] for row in cursor.fetchall()]


def get_borders(connection: Connection) -> list[str]:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT DISTINCT border
            FROM products
            WHERE border IS NOT NULL
              AND TRIM(border) <> ''
            ORDER BY border
            """
        )
        return [row[0] for row in cursor.fetchall()]


def get_catalogue_vocabulary(
    connection: Connection,
) -> dict[str, list[str]]:
    """
    Return the current catalogue vocabulary used by query understanding.
    """
    return {
        "category": get_categories(connection),
        "brand": get_brands(connection),
        "collection": get_collections(connection),
        "fabric": get_fabrics(connection),
        "colour": get_colours(connection),
        "secondary_colour": get_secondary_colours(connection),
        "pattern": get_patterns(connection),
        "border": get_borders(connection),
        "occasion": get_occasions(connection),
        "style": get_styles(connection),
        "mood": get_moods(connection),
        "tag": get_tags(connection),
    }