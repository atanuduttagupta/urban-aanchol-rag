from psycopg import Connection

from backend.app.retrieval.models import ProductResult


class PostgresProductRepository:
    """PostgreSQL implementation of product lookup by product ID."""

    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def get_product(
        self,
        product_id: str,
    ) -> ProductResult | None:
        query = """
            SELECT
                p.product_id,
                p.product_name,
                p.category,
                p.price,
                p.availability
            FROM products p
            WHERE p.product_id = %s
        """

        with self.connection.cursor() as cursor:
            cursor.execute(query, (product_id,))
            row = cursor.fetchone()

        if row is None:
            return None

        return ProductResult(
            product_id=row[0],
            product_name=row[1],
            category=row[2],
            price=row[3],
            availability=row[4],
            retrieval_method="direct",
        )
