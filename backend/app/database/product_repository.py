from typing import Iterable

from psycopg import Connection
from psycopg.types.json import Jsonb


def insert_products(
    connection: Connection,
    products: Iterable[dict],
) -> int:
    sql = """
        INSERT INTO products (
            product_id,
            product_name,
            category,
            brand,
            collection,
            fabric,
            colour,
            secondary_colour,
            pattern,
            border,
            price,
            availability,
            description,
            product_url,
            remarks,
            additional_attributes,
            launch_date,
            created_at,
            updated_at
        )
        VALUES (
            %(product_id)s,
            %(product_name)s,
            %(category)s,
            %(brand)s,
            %(collection)s,
            %(fabric)s,
            %(colour)s,
            %(secondary_colour)s,
            %(pattern)s,
            %(border)s,
            %(price)s,
            %(availability)s,
            %(description)s,
            %(product_url)s,
            %(remarks)s,
            %(additional_attributes)s,
            %(launch_date)s,
            %(created_at)s,
            %(updated_at)s
        )
        ON CONFLICT (product_id) DO UPDATE SET
            product_name = EXCLUDED.product_name,
            category = EXCLUDED.category,
            brand = EXCLUDED.brand,
            collection = EXCLUDED.collection,
            fabric = EXCLUDED.fabric,
            colour = EXCLUDED.colour,
            secondary_colour = EXCLUDED.secondary_colour,
            pattern = EXCLUDED.pattern,
            border = EXCLUDED.border,
            price = EXCLUDED.price,
            availability = EXCLUDED.availability,
            description = EXCLUDED.description,
            product_url = EXCLUDED.product_url,
            remarks = EXCLUDED.remarks,
            additional_attributes = EXCLUDED.additional_attributes,
            launch_date = EXCLUDED.launch_date,
            updated_at = EXCLUDED.updated_at
    """

    count = 0

    with connection.cursor() as cursor:
        for product in products:
            product_data = product.copy()
            product_data["additional_attributes"] = Jsonb(
                product_data["additional_attributes"]
            )

            cursor.execute(sql, product_data)
            count += 1

    return count