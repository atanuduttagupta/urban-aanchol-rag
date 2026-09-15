from backend.app.database.connection import get_database_connection
from backend.app.database.knowledge_embedding_text import (
    build_knowledge_embedding_text,
)


connection = get_database_connection()

try:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                chunk_id,
                section_title,
                chunk_text
            FROM knowledge_chunks
            ORDER BY chunk_index
            LIMIT 1;
            """
        )

        chunk = cursor.fetchone()

    if chunk is None:
        raise ValueError("No knowledge chunks found.")

    chunk_id, section_title, chunk_text = chunk

    embedding_text = build_knowledge_embedding_text(
        section_title=section_title,
        chunk_text=chunk_text,
    )

    print("Chunk ID:", chunk_id)
    print()
    print(embedding_text)

finally:
    connection.close()