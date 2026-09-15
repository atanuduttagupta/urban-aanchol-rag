from backend.app.database.connection import get_database_connection


def search_similar_products(
    connection,
    query_embedding: list[float],
    limit: int = 5,
) -> list[dict]:
    query = """
        SELECT
            p.product_id,
            p.product_name,
            p.category,
            p.price,
            p.availability,
            1 - (pe.embedding <=> %s::vector) AS similarity
        FROM product_embeddings pe
        JOIN products p
            ON p.product_id = pe.product_id
        WHERE
            pe.model_name = %s
            AND pe.model_version = %s
            AND p.availability = 'Available'
        ORDER BY pe.embedding <=> %s::vector
        LIMIT %s;
    """

    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    model_version = "v1"

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (
                query_embedding,
                model_name,
                model_version,
                query_embedding,
                limit,
            ),
        )

        rows = cursor.fetchall()

    return [
        {
            "product_id": row[0],
            "product_name": row[1],
            "category": row[2],
            "price": row[3],
            "availability": row[4],
            "similarity": float(row[5]),
        }
        for row in rows
    ]