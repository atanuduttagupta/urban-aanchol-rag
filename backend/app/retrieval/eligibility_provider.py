from psycopg import Connection

from backend.app.retrieval.filters import build_product_filter_sql
from backend.app.retrieval.models import RetrievalRequest


class MetadataEligibilityProvider:
    """PostgreSQL implementation of product eligibility."""

    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def get_eligible_product_ids(
        self,
        request: RetrievalRequest,
    ) -> set[str]:
        query = """
            SELECT p.product_id
            FROM products p
            WHERE 1 = 1
        """

        filter_sql, parameters = build_product_filter_sql(
            request.filters
        )

        query += filter_sql

        with self.connection.cursor() as cursor:
            cursor.execute(query, parameters)
            rows = cursor.fetchall()

        return {row[0] for row in rows}