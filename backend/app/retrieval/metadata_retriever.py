from psycopg import Connection

from backend.app.retrieval.filters import build_product_filter_sql
from backend.app.retrieval.models import ProductResult, RetrievalRequest


class MetadataProductRetriever:
    """PostgreSQL implementation of structured product metadata retrieval."""

    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def retrieve(self, request: RetrievalRequest) -> list[ProductResult]:
        query = """
            SELECT
                p.product_id,
                p.product_name,
                p.category,
                p.price,
                p.availability
            FROM products p
            WHERE 1 = 1
        """

        filter_sql, parameters = build_product_filter_sql(
            request.filters
        )

        query += filter_sql

        query += """
            ORDER BY p.product_id
        """

        with self.connection.cursor() as cursor:
            cursor.execute(query, parameters)
            rows = cursor.fetchall()

        return [
            ProductResult(
                product_id=row[0],
                product_name=row[1],
                category=row[2],
                price=row[3],
                availability=row[4],
                score=None,
                retrieval_method="metadata",
            )
            for row in rows
        ]