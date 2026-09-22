from psycopg import Connection

from backend.app.database.embedding_generator import EmbeddingGenerator
from backend.app.database.vector_search import search_similar_products
from backend.app.retrieval.models import (
    ProductResult,
    RetrievalPolicy,
    RetrievalRequest,
)


class SemanticProductRetriever:
    def __init__(
        self,
        connection: Connection,
        embedding_generator: EmbeddingGenerator,
    ) -> None:
        self.connection = connection
        self.embedding_generator = embedding_generator

    def retrieve(
        self,
        request: RetrievalRequest,
        policy: RetrievalPolicy,
    ) -> list[ProductResult]:
        query_embedding = self.embedding_generator.generate(request.query)

        rows = search_similar_products(
            self.connection,
            query_embedding,
            limit=policy.fusion_window,
            filters=request.filters,
        )

        return [
            ProductResult(
                product_id=row["product_id"],
                product_name=row["product_name"],
                category=row["category"],
                price=row["price"],
                availability=row["availability"],
                score=float(row["similarity"]),
                retrieval_method="semantic",
            )
            for row in rows
        ]