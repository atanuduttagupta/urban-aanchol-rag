from backend.app.database.connection import get_database_connection
from backend.app.retrieval.keyword_retriever import KeywordProductRetriever
from backend.app.retrieval.models import (
    RetrievalPolicy,
    RetrievalRequest,
)

def test_keyword_retrieval_with_filters():
    connection = get_database_connection()

    try:
        retriever = KeywordProductRetriever(connection)

        request = RetrievalRequest(
            query="handloom saree",
            limit=5,
            filters={
                "category": "Saree",
                "availability": "Available",
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
            result.retrieval_method == "keyword"
            for result in results
        )
        assert all(
            result.score is not None
            for result in results
        )

    finally:
        connection.close()