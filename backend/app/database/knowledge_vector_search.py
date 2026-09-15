def search_similar_knowledge(
    connection,
    query_embedding: list[float],
    limit: int = 5,
) -> list[dict]:
    query = """
        SELECT
            kc.chunk_id,
            kc.document_id,
            kc.section_title,
            kc.chunk_text,
            1 - (kce.embedding <=> %s::vector) AS similarity
        FROM knowledge_chunk_embeddings kce
        JOIN knowledge_chunks kc
            ON kc.chunk_id = kce.chunk_id
        WHERE
            kce.model_name = %s
            AND kce.model_version = %s
        ORDER BY kce.embedding <=> %s::vector
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
            "chunk_id": row[0],
            "document_id": row[1],
            "section_title": row[2],
            "chunk_text": row[3],
            "similarity": float(row[4]),
        }
        for row in rows
    ]