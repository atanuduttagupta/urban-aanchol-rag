from backend.app.database.connection import get_database_connection
from backend.app.database.embedding_generator import EmbeddingGenerator
from backend.app.retrieval.hybrid_retriever import HybridProductRetriever
from backend.app.retrieval.keyword_retriever import KeywordProductRetriever
from backend.app.retrieval.metadata_retriever import MetadataProductRetriever
from backend.app.retrieval.models import RetrievalRequest
from backend.app.retrieval.semantic_retriever import SemanticProductRetriever
from backend.app.retrieval.models import RetrievalPolicy
from backend.app.retrieval.eligibility_provider import (
    MetadataEligibilityProvider,
)


def test_hybrid_retrieval_jaipuri_cotton_blue():
    connection = get_database_connection()

    try:
        hybrid_retriever = HybridProductRetriever(
            eligibility_provider=MetadataEligibilityProvider(connection),
            ranking_retrievers=[
                KeywordProductRetriever(connection),
                SemanticProductRetriever(
                    connection=connection,
                    embedding_generator=EmbeddingGenerator(),
                ),
            ],
        )

        request = RetrievalRequest(
            query="Jaipuri Cotton blue",
            limit=5,
            filters={
                "fabric": "Jaipuri Cotton",
                "colour": "Blue",
                "availability": "Available",
            },
        )

        policy = RetrievalPolicy(
            fusion_window=5,
            rrf_k=60,
        )

        results = hybrid_retriever.retrieve(
            request,
            policy,
        )

        print("\nJaipuri Cotton + Blue results:")

        for rank, result in enumerate(results, start=1):
            print(
                f"{rank}. {result.product_id} | "
                f"{result.product_name} | "
                f"₹{result.price} | "
                f"{result.availability} | "
                f"score={result.score:.6f}"
            )

        assert results
        assert len(results) <= 5

        assert all(
            result.availability == "Available"
            for result in results
        )

        assert all(
            result.retrieval_method == "hybrid"
            for result in results
        )

        assert all(
            result.score is not None
            for result in results
        )

    finally:
        connection.close()

def test_hybrid_retrieval_mul_cotton_blue():
    connection = get_database_connection()

    try:
        hybrid_retriever = HybridProductRetriever(
            eligibility_provider=MetadataEligibilityProvider(connection),
            ranking_retrievers=[
                KeywordProductRetriever(connection),
                SemanticProductRetriever(
                    connection=connection,
                    embedding_generator=EmbeddingGenerator(),
                ),
            ],
        )

        request = RetrievalRequest(
            query="Mul Cotton blue",
            limit=5,
            filters={
                "fabric": "Mul Cotton",
                "colour": "Blue",
                "availability": "Available",
            },
        )

        policy = RetrievalPolicy(
            fusion_window=5,
            rrf_k=60,
        )

        results = hybrid_retriever.retrieve(
            request,
            policy,
        )

        print("\nMul Cotton + Blue results:")

        for rank, result in enumerate(results, start=1):
            print(
                f"{rank}. {result.product_id} | "
                f"{result.product_name} | "
                f"₹{result.price} | "
                f"{result.availability} | "
                f"score={result.score:.6f}"
            )

        assert results
        assert len(results) <= 5
        assert all(
            result.availability == "Available"
            for result in results
        )
        assert all(
            result.retrieval_method == "hybrid"
            for result in results
        )
        assert all(
            result.score is not None
            for result in results
        )

    finally:
        connection.close()



def test_eligibility_mul_cotton_blue():
    connection = get_database_connection()

    try:
        provider = MetadataEligibilityProvider(connection)

        request = RetrievalRequest(
            query="Mul Cotton blue",
            limit=5,
            filters={
                "fabric": "Mul Cotton",
                "colour": "Blue",
                "availability": "Available",
            },
        )

        eligible_ids = provider.get_eligible_product_ids(request)

        print("\nEligible Mul Cotton + Blue products:")
        for product_id in sorted(eligible_ids):
            print(product_id)

        assert eligible_ids

    finally:
        connection.close()


def test_hybrid_retrieval_mul_cotton_green():
    connection = get_database_connection()

    try:
        hybrid_retriever = HybridProductRetriever(
            eligibility_provider=MetadataEligibilityProvider(connection),
            ranking_retrievers=[
                KeywordProductRetriever(connection),
                SemanticProductRetriever(
                    connection=connection,
                    embedding_generator=EmbeddingGenerator(),
                ),
            ],
        )

        request = RetrievalRequest(
            query="Mul Cotton green",
            limit=5,
            filters={
                "fabric": "Mul Cotton",
                "colour": "Green",
                "availability": "Available",
            },
        )

        policy = RetrievalPolicy(
            fusion_window=20,
            rrf_k=60,
        )

        results = hybrid_retriever.retrieve(
            request,
            policy,
        )

        print("\nMul Cotton + Green results:")

        for rank, result in enumerate(results, start=1):
            print(
                f"{rank}. {result.product_id} | "
                f"{result.product_name} | "
                f"₹{result.price} | "
                f"{result.availability} | "
                f"score={result.score:.6f}"
            )

        assert results
        assert len(results) <= 5

        assert all(
            result.availability == "Available"
            for result in results
        )

        assert all(
            result.retrieval_method == "hybrid"
            for result in results
        )

        assert all(
            result.score is not None
            for result in results
        )

    finally:
        connection.close()

def test_hybrid_retrieval_mul_cotton_price_range():
    connection = get_database_connection()

    hybrid_retriever = HybridProductRetriever(
        eligibility_provider=MetadataEligibilityProvider(connection),
        ranking_retrievers=[
            KeywordProductRetriever(connection),
            SemanticProductRetriever(
                connection=connection,
                embedding_generator=EmbeddingGenerator(),
            ),
        ],
    )

    request = RetrievalRequest(
        query="Mul Cotton saree between 1200 and 2200",
        limit=5,
        filters={
            "fabric": "Mul Cotton",
            "min_price": 1200,
            "max_price": 2200,
            "availability": "Available",
        },
    )

    policy = RetrievalPolicy(
        fusion_window=20,
        rrf_k=60,
    )

    # ---------------------------------------------------------
    # 1. Get all eligible products
    # ---------------------------------------------------------
    eligibility_provider = MetadataEligibilityProvider(connection)

    eligible_ids = eligibility_provider.get_eligible_product_ids(request)

    print("\n=== ELIGIBLE PRODUCTS ===")
    print(f"Eligible count: {len(eligible_ids)}")
    print(sorted(eligible_ids))

    # ---------------------------------------------------------
    # 2. Get Keyword ranking
    # ---------------------------------------------------------
    keyword_retriever = KeywordProductRetriever(connection)

    keyword_results = keyword_retriever.retrieve(
        request,
        policy,
    )

    keyword_rank = {
        result.product_id: rank
        for rank, result in enumerate(keyword_results, start=1)
    }

    # ---------------------------------------------------------
    # 3. Get Semantic ranking
    # ---------------------------------------------------------
    semantic_retriever = SemanticProductRetriever(
        connection=connection,
        embedding_generator=EmbeddingGenerator(),
    )

    semantic_results = semantic_retriever.retrieve(
        request,
        policy,
    )

    semantic_rank = {
        result.product_id: rank
        for rank, result in enumerate(semantic_results, start=1)
    }

    # Actual semantic similarity score returned by vector search.
    semantic_similarity = {
        result.product_id: result.score
        for result in semantic_results
    }

    # ---------------------------------------------------------
    # 4. Calculate RRF score for ALL eligible products
    # ---------------------------------------------------------
    rrf_k = policy.rrf_k

    diagnostic_rows = []

    for product_id in sorted(eligible_ids):

        k_rank = keyword_rank.get(product_id)
        s_rank = semantic_rank.get(product_id)

        # Actual semantic similarity from pgvector.
        similarity = semantic_similarity.get(product_id)

        # Keyword contribution to RRF.
        keyword_rrf_score = (
            1 / (rrf_k + k_rank)
            if k_rank is not None
            else 0.0
        )

        # Semantic contribution to RRF.
        semantic_rrf_score = (
            1 / (rrf_k + s_rank)
            if s_rank is not None
            else 0.0
        )

        # Final fused RRF score.
        rrf_score = (
            keyword_rrf_score
            + semantic_rrf_score
        )

        diagnostic_rows.append(
            (
                product_id,
                k_rank,
                s_rank,
                similarity,
                keyword_rrf_score,
                semantic_rrf_score,
                rrf_score,
            )
        )

    # ---------------------------------------------------------
    # 5. Sort exactly like HybridProductRetriever
    # ---------------------------------------------------------
    diagnostic_rows.sort(
        key=lambda row: (
            row[6],       # RRF score
            row[0],       # product_id
        ),
        reverse=True,
    )

    # ---------------------------------------------------------
    # 6. Display complete ranking
    # ---------------------------------------------------------
    print("\n=== RRF DIAGNOSTIC: ALL ELIGIBLE PRODUCTS ===")

    print(
        f"{'Rank':<6}"
        f"{'Product':<10}"
        f"{'Keyword':<10}"
        f"{'Semantic':<10}"
        f"{'Similarity':<14}"
        f"{'K RRF':<12}"
        f"{'S RRF':<12}"
        f"{'RRF Score':<14}"
        f"{'Selected':<10}"
    )

    print("-" * 108)

    for final_rank, row in enumerate(
        diagnostic_rows,
        start=1,
    ):

        (
            product_id,
            k_rank,
            s_rank,
            similarity,
            keyword_rrf_score,
            semantic_rrf_score,
            rrf_score,
        ) = row

        selected = (
            "YES"
            if final_rank <= request.limit
            else ""
        )

        similarity_text = (
            f"{similarity:.6f}"
            if similarity is not None
            else "-"
        )

        print(
            f"{final_rank:<6}"
            f"{product_id:<10}"
            f"{str(k_rank):<10}"
            f"{str(s_rank):<10}"
            f"{similarity_text:<14}"
            f"{keyword_rrf_score:<12.6f}"
            f"{semantic_rrf_score:<12.6f}"
            f"{rrf_score:<14.6f}"
            f"{selected:<10}"
        )

    # ---------------------------------------------------------
    # 7. Run actual Hybrid retrieval
    # ---------------------------------------------------------
    results = hybrid_retriever.retrieve(
        request,
        policy,
    )

    print("\n=== ACTUAL HYBRID TOP 5 ===")

    for rank, result in enumerate(
        results,
        start=1,
    ):
        print(
            f"{rank}. "
            f"{result.product_id} | "
            f"{result.product_name} | "
            f"score={result.score:.6f}"
        )

    # ---------------------------------------------------------
    # 8. Basic assertions
    # ---------------------------------------------------------

    # We confirmed that only 8 products satisfy:
    # Mul Cotton + ₹1200–₹2200 + Available.
    assert len(eligible_ids) == 8

    # User requested only the top 5 final results.
    assert len(results) == 5

    actual_ids = [
        result.product_id
        for result in results
    ]

    expected_ids = [
        row[0]
        for row in diagnostic_rows[:request.limit]
    ]

    assert actual_ids == expected_ids

def test_hybrid_retrieval_keyword_and_semantic():
    connection = get_database_connection()

    hybrid_retriever = HybridProductRetriever(
        eligibility_provider=MetadataEligibilityProvider(connection),
        ranking_retrievers=[
            KeywordProductRetriever(connection),
            SemanticProductRetriever(
                connection=connection,
                embedding_generator=EmbeddingGenerator(),
            ),
        ],
    )

    request = RetrievalRequest(
        query="Mul Cotton",
        limit=5,
        filters={
            "fabric": "Mul Cotton",
            "availability": "Available",
        },
    )

    policy = RetrievalPolicy(
        fusion_window=20,
        rrf_k=60,
    )

    # ---------------------------------------------------------
    # 1. Eligibility
    # ---------------------------------------------------------
    eligibility_provider = MetadataEligibilityProvider(connection)

    eligible_ids = eligibility_provider.get_eligible_product_ids(request)

    print("\n=== ELIGIBLE PRODUCTS ===")
    print(f"Eligible count: {len(eligible_ids)}")
    print(sorted(eligible_ids))

    # ---------------------------------------------------------
    # 2. Keyword ranking
    # ---------------------------------------------------------
    keyword_retriever = KeywordProductRetriever(connection)

    keyword_results = keyword_retriever.retrieve(
        request,
        policy,
    )

    print("\n=== KEYWORD RANKING ===")

    keyword_rank = {}

    for rank, result in enumerate(keyword_results, start=1):
        keyword_rank[result.product_id] = rank

        print(
            f"{rank}. "
            f"{result.product_id} | "
            f"{result.product_name} | "
            f"score={result.score:.6f}"
        )

    # ---------------------------------------------------------
    # 3. Semantic ranking
    # ---------------------------------------------------------
    semantic_retriever = SemanticProductRetriever(
        connection=connection,
        embedding_generator=EmbeddingGenerator(),
    )

    semantic_results = semantic_retriever.retrieve(
        request,
        policy,
    )

    print("\n=== SEMANTIC RANKING ===")

    semantic_rank = {}
    semantic_similarity = {}

    for rank, result in enumerate(semantic_results, start=1):
        semantic_rank[result.product_id] = rank
        semantic_similarity[result.product_id] = result.score

        print(
            f"{rank}. "
            f"{result.product_id} | "
            f"{result.product_name} | "
            f"similarity={result.score:.6f}"
        )

    # ---------------------------------------------------------
    # 4. Calculate RRF for every product appearing
    #    in either ranking
    # ---------------------------------------------------------
    rrf_k = policy.rrf_k

    candidate_ids = (
        set(keyword_rank)
        | set(semantic_rank)
    )

    diagnostic_rows = []

    for product_id in candidate_ids:

        k_rank = keyword_rank.get(product_id)
        s_rank = semantic_rank.get(product_id)

        keyword_rrf = (
            1 / (rrf_k + k_rank)
            if k_rank is not None
            else 0.0
        )

        semantic_rrf = (
            1 / (rrf_k + s_rank)
            if s_rank is not None
            else 0.0
        )

        rrf_score = keyword_rrf + semantic_rrf

        diagnostic_rows.append(
            (
                product_id,
                k_rank,
                s_rank,
                semantic_similarity.get(product_id),
                keyword_rrf,
                semantic_rrf,
                rrf_score,
            )
        )

    # ---------------------------------------------------------
    # 5. Sort exactly like HybridProductRetriever
    # ---------------------------------------------------------
    diagnostic_rows.sort(
        key=lambda row: (
            row[6],       # RRF score
            row[0],       # product_id
        ),
        reverse=True,
    )

    # ---------------------------------------------------------
    # 6. Display combined RRF ranking
    # ---------------------------------------------------------
    print("\n=== TRUE HYBRID RRF DIAGNOSTIC ===")

    print(
        f"{'Rank':<6}"
        f"{'Product':<10}"
        f"{'Keyword':<10}"
        f"{'Semantic':<10}"
        f"{'Similarity':<14}"
        f"{'K RRF':<12}"
        f"{'S RRF':<12}"
        f"{'RRF Score':<14}"
        f"{'Selected':<10}"
    )

    print("-" * 108)

    for final_rank, row in enumerate(
        diagnostic_rows,
        start=1,
    ):

        (
            product_id,
            k_rank,
            s_rank,
            similarity,
            keyword_rrf,
            semantic_rrf,
            rrf_score,
        ) = row

        selected = (
            "YES"
            if final_rank <= request.limit
            else ""
        )

        similarity_text = (
            f"{similarity:.6f}"
            if similarity is not None
            else "-"
        )

        print(
            f"{final_rank:<6}"
            f"{product_id:<10}"
            f"{str(k_rank):<10}"
            f"{str(s_rank):<10}"
            f"{similarity_text:<14}"
            f"{keyword_rrf:<12.6f}"
            f"{semantic_rrf:<12.6f}"
            f"{rrf_score:<14.6f}"
            f"{selected:<10}"
        )

    # ---------------------------------------------------------
    # 7. Run actual Hybrid retrieval
    # ---------------------------------------------------------
    results = hybrid_retriever.retrieve(
        request,
        policy,
    )

    print("\n=== ACTUAL HYBRID TOP 5 ===")

    for rank, result in enumerate(
        results,
        start=1,
    ):
        print(
            f"{rank}. "
            f"{result.product_id} | "
            f"{result.product_name} | "
            f"score={result.score:.6f}"
        )

    # ---------------------------------------------------------
    # 8. Verify Hybrid matches our diagnostic calculation
    # ---------------------------------------------------------
    assert len(results) == min(
        request.limit,
        len(diagnostic_rows),
    )

    actual_ids = [
        result.product_id
        for result in results
    ]

    expected_ids = [
        row[0]
        for row in diagnostic_rows[:request.limit]
    ]

    assert actual_ids == expected_ids