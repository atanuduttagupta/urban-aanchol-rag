from typing import Iterable

from psycopg import Connection
from psycopg.types.json import Jsonb


def insert_product_media(
    connection: Connection,
    products: Iterable[dict],
) -> dict[str, int]:
    counts = {
        "images": 0,
        "videos": 0,
        "links": 0,
    }

    with connection.cursor() as cursor:
        for product in products:
            product_id = product["product_id"]

            media_items = [
                ("image", product.get("image_url")),
                ("video", product.get("video_url")),
            ]

            for media_type, media_url in media_items:
                if not media_url:
                    continue

                cursor.execute(
                    """
                    INSERT INTO media_assets (
                        media_type,
                        media_url,
                        source,
                        status,
                        metadata
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING media_id
                    """,
                    (
                        media_type,
                        media_url,
                        "Excel Catalogue",
                        "Active",
                        Jsonb({}),
                    ),
                )

                media_id = cursor.fetchone()[0]

                cursor.execute(
                    """
                    INSERT INTO product_media (
                        product_id,
                        media_id,
                        relationship_type,
                        sort_order
                    )
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (
                        product_id,
                        media_id,
                        relationship_type
                    ) DO NOTHING
                    """,
                    (
                        product_id,
                        media_id,
                        "primary",
                        1,
                    ),
                )

                counts[f"{media_type}s"] += 1
                counts["links"] += cursor.rowcount

    return counts