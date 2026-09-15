from uuid import UUID




def save_product_embedding(
    connection,
    product_id: str,
    model_name: str,
    model_version: str,
    embedding: list[float],
    dimensions: int,
) -> UUID:
    query = """
        INSERT INTO product_embeddings (
            product_id,
            model_name,
            model_version,
            dimensions,
            embedding
        )
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (product_id, model_name, model_version)
        DO UPDATE SET
            dimensions = EXCLUDED.dimensions,
            embedding = EXCLUDED.embedding,
            updated_at = CURRENT_TIMESTAMP
        RETURNING embedding_id;
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (
                product_id,
                model_name,
                model_version,
                dimensions,
                embedding,
            ),
        )
        result = cursor.fetchone()

    return result[0]