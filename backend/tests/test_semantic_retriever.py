from backend.app.database.connection import get_database_connection
from backend.app.database.embedding_generator import EmbeddingGenerator
from backend.app.retrieval.models import (
    RetrievalPolicy,
    RetrievalRequest,
)
from backend.app.retrieval.semantic_retriever import SemanticProductRetriever


def test_semantic_retrieval_with_filters():
    connection = get_database_connection()

    try:
        retriever = SemanticProductRetriever(
            connection=connection,
            embedding_generator=EmbeddingGenerator(),
        )

        request = RetrievalRequest(
            query="Something elegant for a family function",
            limit=5,
            filters={
                "category": "Saree",
                "availability": "Available",
                "max_price": 3000,
            },
        )

        policy = RetrievalPolicy(
            fusion_window=5,
            rrf_k=60,
        )

        results = retriever.retrieve(
            request,
            policy,
        )

        assert results

        assert all(
            result.category == "Saree"
            for result in results
        )

        assert all(
            result.availability == "Available"
            for result in results
        )

        assert all(
            result.price <= 3000
            for result in results
        )

        assert all(
            result.retrieval_method == "semantic"
            for result in results
        )

        assert all(
            result.score is not None
            for result in results
        )

    finally:
        connection.close()