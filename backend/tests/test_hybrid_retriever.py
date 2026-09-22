from backend.app.retrieval.hybrid_retriever import HybridProductRetriever
from backend.app.retrieval.models import (
    ProductResult,
    RetrievalPolicy,
    RetrievalRequest,
)


class StubRetriever:
    def __init__(self, results):
        self.results = results

    def retrieve(self, request, policy):
        return self.results

class StubEligibilityProvider:
    def __init__(self, product_ids):
        self.product_ids = set(product_ids)

    def get_eligible_product_ids(self, request):
        return self.product_ids


def product(product_id, name, method):
    return ProductResult(
        product_id=product_id,
        product_name=name,
        category="Saree",
        price=2500,
        availability="Available",
        score=0.5,
        retrieval_method=method,
    )


def test_hybrid_retrieval_fuses_keyword_and_semantic_results():
    eligibility = StubEligibilityProvider([
        "UA-0001",
        "UA-0002",
        "UA-0003",
    ])

    keyword = StubRetriever([
        product("UA-0001", "Product A", "keyword"),
        product("UA-0002", "Product B", "keyword"),
    ])

    semantic = StubRetriever([
        product("UA-0002", "Product B", "semantic"),
        product("UA-0003", "Product C", "semantic"),
    ])

    retriever = HybridProductRetriever(
        eligibility_provider=eligibility,
        ranking_retrievers=[
            keyword,
            semantic,
        ],
)

    request = RetrievalRequest(
        query="elegant saree",
        limit=3,
    )

    policy = RetrievalPolicy(
        fusion_window=10,
        rrf_k=60,
    )

    results = retriever.retrieve(
        request,
        policy,
    )

    assert len(results) == 3

    assert [result.product_id for result in results] == [
        "UA-0002",
        "UA-0001",
        "UA-0003",
    ]

    assert all(
        result.retrieval_method == "hybrid"
        for result in results
    )

    assert results[0].score > results[1].score
    assert results[1].score > results[2].score


def test_hybrid_retrieval_respects_metadata_eligibility():
    eligibility = StubEligibilityProvider([
        "UA-0001",
        "UA-0002",
    ])

    keyword = StubRetriever([
        product("UA-0001", "Product A", "keyword"),
        product("UA-0003", "Product C", "keyword"),
    ])

    semantic = StubRetriever([
        product("UA-0003", "Product C", "semantic"),
        product("UA-0002", "Product B", "semantic"),
    ])

    retriever = HybridProductRetriever(
        eligibility_provider=eligibility,
        ranking_retrievers=[
            keyword,
            semantic,
        ],
    )

    request = RetrievalRequest(
        query="red saree",
        limit=5,
    )

    policy = RetrievalPolicy(
        fusion_window=10,
        rrf_k=60,
    )

    results = retriever.retrieve(
        request,
        policy,
    )

    result_ids = [result.product_id for result in results]

    assert "UA-0001" in result_ids
    assert "UA-0002" in result_ids
    assert "UA-0003" not in result_ids


def test_hybrid_retrieval_does_not_use_metadata_limit_as_candidate_limit():
    eligibility = StubEligibilityProvider([
        "UA-0001",
        "UA-0002",
        "UA-0003",
        "UA-0004",
        "UA-0005",
        "UA-0006",
        "UA-0007",
    ])

    keyword = StubRetriever([
        product("UA-0006", "Product F", "keyword"),
        product("UA-0001", "Product A", "keyword"),
    ])

    semantic = StubRetriever([
        product("UA-0006", "Product F", "semantic"),
        product("UA-0002", "Product B", "semantic"),
    ])

    retriever = HybridProductRetriever(
        eligibility_provider=eligibility,
        ranking_retrievers=[
            keyword,
            semantic,
        ],
    )

    request = RetrievalRequest(
        query="test",
        limit=2,
    )

    policy = RetrievalPolicy(
        fusion_window=10,
        rrf_k=60,
    )

    results = retriever.retrieve(
        request,
        policy,
    )

    assert len(results) == 2

    result_ids = [
        result.product_id
        for result in results
    ]

    # UA-0006 is beyond the first 2 eligibility candidates.
    # It must still be eligible for hybrid ranking.
    assert "UA-0006" in result_ids

    assert results[0].product_id == "UA-0006"