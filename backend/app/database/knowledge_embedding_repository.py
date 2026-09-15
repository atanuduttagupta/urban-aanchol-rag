def save_knowledge_chunk_embedding(
    connection,
    chunk_id,
    embedding,
    dimensions: int,
) -> None:
    query = """
        INSERT INTO knowledge_chunk_embeddings (
            chunk_id,
            model_name,
            model_version,
            dimensions,
            embedding
        )
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (chunk_id, model_name, model_version)
        DO UPDATE SET
            dimensions = EXCLUDED.dimensions,
            embedding = EXCLUDED.embedding,
            updated_at = CURRENT_TIMESTAMP;
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (
                chunk_id,
                "sentence-transformers/all-MiniLM-L6-v2",
                "v1",
                dimensions,
                embedding,
            ),
        )