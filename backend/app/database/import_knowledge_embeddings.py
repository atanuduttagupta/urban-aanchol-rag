from backend.app.database.connection import get_database_connection
from backend.app.database.embedding_generator import EmbeddingGenerator
from backend.app.database.knowledge_embedding_text import (
    build_knowledge_embedding_text,
)

from backend.app.database.knowledge_embedding_repository import (
    save_knowledge_chunk_embedding,
)


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
MODEL_VERSION = "v1"


def import_knowledge_embeddings() -> None:
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
                ORDER BY chunk_index;
                """
            )

            chunks = cursor.fetchall()

        print(f"Knowledge chunks loaded: {len(chunks)}")

        if not chunks:
            raise ValueError("No knowledge chunks found.")

        generator = EmbeddingGenerator()

        saved_count = 0

        for chunk_id, section_title, chunk_text in chunks:
            embedding_text = build_knowledge_embedding_text(
                section_title=section_title,
                chunk_text=chunk_text,
            )

            embedding = generator.generate(embedding_text)

            save_knowledge_chunk_embedding(
                connection=connection,
                chunk_id=chunk_id,
                embedding=embedding,
                dimensions=generator.dimensions,
            )

            saved_count += 1

            print(
                f"Embedded chunk: {chunk_id} | "
                f"{section_title}"
            )

        connection.commit()

        print()
        print(f"Knowledge embeddings saved: {saved_count}")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    import_knowledge_embeddings()