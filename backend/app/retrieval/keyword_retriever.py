from psycopg import Connection

from backend.app.retrieval.filters import build_product_filter_sql
from backend.app.retrieval.models import (
    ProductResult,
    RetrievalPolicy,
    RetrievalRequest,
)


class KeywordProductRetriever:
    """PostgreSQL full-text product retrieval."""

    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def retrieve(
        self,
        request: RetrievalRequest,
        policy: RetrievalPolicy,
    ) -> list[ProductResult]:

        query = """
            SELECT
                p.product_id,
                p.product_name,
                p.category,
                p.price,
                p.availability,
                ts_rank(
                    p.search_vector,
                    websearch_to_tsquery('simple', %s)
                ) AS rank
            FROM products p
            WHERE p.search_vector @@ websearch_to_tsquery('simple', %s)
        """

        parameters: list[object] = [
            request.query,
            request.query,
        ]

        filter_sql, filter_parameters = build_product_filter_sql(
            request.filters
        )

        query += filter_sql
        parameters.extend(filter_parameters)

        query += """
            ORDER BY rank DESC, p.product_id
            LIMIT %s
        """

        parameters.append(policy.fusion_window)

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
                score=float(row[5]),
                retrieval_method="keyword",
            )
            for row in rows
        ]