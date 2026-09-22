from backend.app.database.connection import get_database_connection
from backend.app.retrieval.metadata_retriever import MetadataProductRetriever
from backend.app.retrieval.models import RetrievalRequest


def test_metadata_retrieval_with_filters():
    connection = get_database_connection()

    try:
        retriever = MetadataProductRetriever(connection)

        request = RetrievalRequest(
            query="",
            limit=5,
            filters={
                "category": "Saree",
                "availability": "Available",
                "max_price": 3000,
            },
        )

        results = retriever.retrieve(request)

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
            result.retrieval_method == "metadata"
            for result in results
        )

    finally:
        connection.close()