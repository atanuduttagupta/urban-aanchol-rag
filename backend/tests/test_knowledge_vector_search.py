from backend.app.database.connection import get_database_connection
from backend.app.database.embedding_generator import EmbeddingGenerator
from backend.app.database.knowledge_vector_search import (
    search_similar_knowledge,
)


QUERY = "How long does delivery take?"


generator = EmbeddingGenerator()
query_embedding = generator.generate(QUERY)

connection = get_database_connection()

try:
    results = search_similar_knowledge(
        connection=connection,
        query_embedding=query_embedding,
        limit=5,
    )

    print("Query:", QUERY)
    print()
    print("Knowledge semantic search results:")

    for index, result in enumerate(results, start=1):
        print(
            f"{index}. "
            f"{result['section_title']} | "
            f"similarity={result['similarity']:.4f}"
        )
        print(f"   {result['chunk_text']}")

finally:
    connection.close()