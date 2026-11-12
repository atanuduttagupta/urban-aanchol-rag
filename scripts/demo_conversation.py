
from backend.app.catalogue.postgres_product_repository import (
    PostgresProductRepository,
)
from backend.app.conversation.models import ConversationContext
from backend.app.conversation.service import ConversationService
from backend.app.database.catalogue_attribute_repository import (
    get_catalogue_vocabulary,
)
from backend.app.database.connection import get_database_connection
from backend.app.database.embedding_generator import EmbeddingGenerator
from backend.app.recommendation.service import RecommendationService
from backend.app.retrieval.eligibility_provider import (
    MetadataEligibilityProvider,
)
from backend.app.retrieval.hybrid_retriever import HybridProductRetriever
from backend.app.retrieval.keyword_retriever import KeywordProductRetriever
from backend.app.retrieval.models import RetrievalPolicy
from backend.app.retrieval.semantic_retriever import SemanticProductRetriever
from backend.app.retrieval.service import (
    RetrievalExecutionStatus,
    RetrievalService,
)


def display_turn(number, message, result):
    print(f"\n{'=' * 65}")
    print(f"TURN {number}: {message}")
    print(f"Status: {result.status}")

    if result.reason:
        print(f"Reason: {result.reason}")

    for index, item in enumerate(result.recommendations, start=1):
        product = item.product
        print(
            f"{index}. {product.product_id} | "
            f"{product.product_name} | "
            f"Category: {product.category} | "
            f"Rs. {product.price} | "
            f"{product.availability}"
        )


def assert_available_sarees(recommendations, turn_number):
    assert recommendations, (
        f"Turn {turn_number} returned no products."
    )

    for item in recommendations:
        product = item.product

        assert product.category == "Saree", (
            f"Turn {turn_number}: {product.product_id} "
            f"has unexpected category: {product.category}"
        )

        assert product.availability == "Available", (
            f"Turn {turn_number}: {product.product_id} "
            f"is not available: {product.availability}"
        )


def main():
    connection = get_database_connection()

    try:
        vocabulary = get_catalogue_vocabulary(connection)

        embedding_generator = EmbeddingGenerator()

        hybrid_retriever = HybridProductRetriever(
            eligibility_provider=MetadataEligibilityProvider(connection),
            ranking_retrievers=[
                KeywordProductRetriever(connection),
                SemanticProductRetriever(
                    connection=connection,
                    embedding_generator=embedding_generator,
                ),
            ],
        )

        product_repository = PostgresProductRepository(connection)

        retrieval_service = RetrievalService(
            hybrid_retriever=hybrid_retriever,
            product_repository=product_repository,
            policy=RetrievalPolicy(
                fusion_window=30,
                rrf_k=60,
            ),
            default_limit=5,
        )

        conversation_service = ConversationService(
            retrieval_service=retrieval_service,
            recommendation_service=RecommendationService(),
        )

        context = ConversationContext()

        messages = [
            "Show me cotton sarees",
            "Show me some more",
            "Show me the first one",
        ]

        results = []

        for number, message in enumerate(messages, start=1):
            result = conversation_service.handle_message(
                message=message,
                context=context,
                vocabulary=vocabulary,
            )

            display_turn(number, message, result)
            results.append(result)

            if result.status != RetrievalExecutionStatus.COMPLETED:
                raise RuntimeError(
                    f"Turn {number} did not complete: {result.reason}"
                )

            context = result.context

        first_recommendations = results[0].recommendations
        second_recommendations = results[1].recommendations

        # Validate the first two recommendation turns.
        assert_available_sarees(first_recommendations, 1)
        assert_available_sarees(second_recommendations, 2)

        # Ensure the second turn contains no previously displayed products.
        first_ids = {
            item.product.product_id
            for item in first_recommendations
        }

        second_ids = {
            item.product.product_id
            for item in second_recommendations
        }

        assert first_ids.isdisjoint(second_ids), (
            "Duplicate products appeared in the second turn."
        )

        # Validate reference resolution in the third turn.
        selected = results[2].recommendations

        assert len(selected) == 1, (
            "The product reference should resolve to exactly one product."
        )

        expected_id = second_recommendations[0].product.product_id
        actual_id = selected[0].product.product_id

        assert actual_id == expected_id, (
            f"Expected {expected_id}, but selected {actual_id}."
        )

        print(f"\n{'=' * 65}")
        print("DAY 14 ACCEPTANCE CHECKS")
        print("PASS: Turn 1 returned available Sarees.")
        print("PASS: Turn 2 returned additional available Sarees.")
        print("PASS: No products were repeated between turns 1 and 2.")
        print("PASS: Turn 3 resolved the first product from turn 2.")
        print("\nDAY 14 CONVERSATION DEMO SUCCESSFUL.")

    finally:
        connection.close()


if __name__ == "__main__":
    main()
