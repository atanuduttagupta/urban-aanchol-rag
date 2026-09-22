from backend.app.retrieval.models import (
    ProductCandidate,
    RetrievalPolicy,
    RetrievalRequest,
)


def test_retrieval_request_limit_is_user_facing():
    request = RetrievalRequest(
        query="blue cotton saree",
        limit=5,
    )

    assert request.limit == 5


def test_retrieval_policy_is_separate_from_request_limit():
    request = RetrievalRequest(
        query="blue cotton saree",
        limit=5,
    )

    policy = RetrievalPolicy(
        fusion_window=25,
        rrf_k=60,
    )

    assert request.limit == 5
    assert policy.fusion_window == 25
    assert policy.rrf_k == 60


def test_product_candidate_contains_rank_and_source():
    candidate = ProductCandidate(
        product_id="TEST-001",
        product_name="Test Saree",
        score=0.95,
        rank=1,
        retrieval_method="semantic",
    )

    assert candidate.rank == 1
    assert candidate.retrieval_method == "semantic"