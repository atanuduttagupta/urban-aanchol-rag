from backend.app.database.connection import get_database_connection
from backend.app.database.embedding_generator import EmbeddingGenerator
from backend.app.database.vector_search import search_similar_products


QUERY = "Something elegant for a family function"


generator = EmbeddingGenerator()
query_embedding = generator.generate(QUERY)

connection = get_database_connection()

try:
    results = search_similar_products(
        connection=connection,
        query_embedding=query_embedding,
        limit=5,
    )

    print("Query:", QUERY)
    print()
    print("Semantic search results:")

    for index, result in enumerate(results, start=1):
        print(
            f"{index}. "
            f"{result['product_id']} | "
            f"{result['product_name']} | "
            f"{result['category']} | "
            f"₹{result['price']} | "
            f"similarity={result['similarity']:.4f}"
        )

finally:
    connection.close()