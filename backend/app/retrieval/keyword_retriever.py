from psycopg import Connection

from backend.app.retrieval.models import ProductResult, RetrievalRequest


class KeywordProductRetriever:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def retrieve(self, request: RetrievalRequest) -> list[ProductResult]:
        filters = request.filters or {}

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

        # Direct product metadata filters
        direct_filters = {
            "category": "p.category",
            "brand": "p.brand",
            "collection": "p.collection",
            "fabric": "p.fabric",
            "colour": "p.colour",
            "secondary_colour": "p.secondary_colour",
            "pattern": "p.pattern",
            "border": "p.border",
            "availability": "p.availability",
        }

        for filter_name, column in direct_filters.items():
            value = filters.get(filter_name)

            if value is not None:
                query += f" AND {column} = %s"
                parameters.append(value)

        # Price range filters
        if filters.get("min_price") is not None:
            query += " AND p.price >= %s"
            parameters.append(filters["min_price"])

        if filters.get("max_price") is not None:
            query += " AND p.price <= %s"
            parameters.append(filters["max_price"])

        # Normalized product attributes
        normalized_filters = {
            "occasion": "product_occasions",
            "style": "product_styles",
            "mood": "product_moods",
            "tag": "product_tags",
        }

        for filter_name, table_name in normalized_filters.items():
            value = filters.get(filter_name)

            if value is not None:
                query += f"""
                    AND EXISTS (
                        SELECT 1
                        FROM {table_name} attribute
                        WHERE attribute.product_id = p.product_id
                        AND attribute.{filter_name} = %s
                    )
                """
                parameters.append(value)

        query += """
            ORDER BY rank DESC, p.product_id
            LIMIT %s
        """

        parameters.append(request.limit)

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