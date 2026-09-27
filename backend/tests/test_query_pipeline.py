from backend.app.retrieval.models import (
    ProductResult,
    RetrievalPolicy,
)
from backend.app.retrieval.query_pipeline import QueryPipeline


class StubHybridRetriever:
    def __init__(self, results):
        self.results = results
        self.received_request = None
        self.received_policy = None

    def retrieve(self, request, policy):
        self.received_request = request
        self.received_policy = policy
        return self.results


class StubConnection:
    pass


def test_query_pipeline_uses_explicit_customer_limit(monkeypatch):
    expected_results = [
        ProductResult(
            product_id="UA-0001",
            product_name="Product A",
            category="Saree",
            price=2500,
            availability="Available",
            score=0.5,
            retrieval_method="hybrid",
        )
    ]

    hybrid = StubHybridRetriever(expected_results)
    policy = RetrievalPolicy(
        fusion_window=10,
        rrf_k=60,
    )

    vocabulary = {
        "category": ["Saree"],
        "colour": ["Blue"],
        "fabric": ["Cotton"],
    }

    def fake_get_catalogue_vocabulary(connection):
        return vocabulary

    def fake_understand_query(query, vocabulary):
        from backend.app.retrieval.models import RetrievalIntent

        return RetrievalIntent(
            original_query=query,
            semantic_query=query,
            filters={
                "category": "Saree",
                "colour": "Blue",
            },
            requested_limit=8,
        )

    monkeypatch.setattr(
        "backend.app.retrieval.query_pipeline.get_catalogue_vocabulary",
        fake_get_catalogue_vocabulary,
    )

    monkeypatch.setattr(
        "backend.app.retrieval.query_pipeline.understand_query",
        fake_understand_query,
    )

    pipeline = QueryPipeline(
        connection=StubConnection(),
        hybrid_retriever=hybrid,
        policy=policy,
        default_limit=5,
    )

    results = pipeline.retrieve(
        "Show me 8 blue sarees",
    )

    assert results == expected_results

    assert hybrid.received_request.query == "Show me 8 blue sarees"

    assert hybrid.received_request.filters == {
        "category": "Saree",
        "colour": "Blue",
    }

    assert hybrid.received_request.limit == 8
    assert hybrid.received_policy == policy


def test_query_pipeline_uses_configured_default_when_no_limit_requested(
    monkeypatch,
):
    hybrid = StubHybridRetriever([])
    policy = RetrievalPolicy(
        fusion_window=10,
        rrf_k=60,
    )

    def fake_get_catalogue_vocabulary(connection):
        return {
            "category": ["Saree"],
        }

    def fake_understand_query(query, vocabulary):
        from backend.app.retrieval.models import RetrievalIntent

        return RetrievalIntent(
            original_query=query,
            semantic_query=query,
            filters={"category": "Saree"},
            requested_limit=None,
        )

    monkeypatch.setattr(
        "backend.app.retrieval.query_pipeline.get_catalogue_vocabulary",
        fake_get_catalogue_vocabulary,
    )

    monkeypatch.setattr(
        "backend.app.retrieval.query_pipeline.understand_query",
        fake_understand_query,
    )

    pipeline = QueryPipeline(
        connection=StubConnection(),
        hybrid_retriever=hybrid,
        policy=policy,
        default_limit=6,
    )

    pipeline.retrieve(
        "Show me elegant sarees",
    )

    assert hybrid.received_request.limit == 6
    assert hybrid.received_request.filters == {
        "category": "Saree",
    }


def test_query_pipeline_caller_limit_is_used_when_customer_did_not_request_one(
    monkeypatch,
):
    hybrid = StubHybridRetriever([])
    policy = RetrievalPolicy(
        fusion_window=10,
        rrf_k=60,
    )

    def fake_get_catalogue_vocabulary(connection):
        return {
            "category": ["Saree"],
        }

    def fake_understand_query(query, vocabulary):
        from backend.app.retrieval.models import RetrievalIntent

        return RetrievalIntent(
            original_query=query,
            semantic_query=query,
            filters={"category": "Saree"},
            requested_limit=None,
        )

    monkeypatch.setattr(
        "backend.app.retrieval.query_pipeline.get_catalogue_vocabulary",
        fake_get_catalogue_vocabulary,
    )

    monkeypatch.setattr(
        "backend.app.retrieval.query_pipeline.understand_query",
        fake_understand_query,
    )

    pipeline = QueryPipeline(
        connection=StubConnection(),
        hybrid_retriever=hybrid,
        policy=policy,
        default_limit=5,
    )

    pipeline.retrieve(
        "Show me elegant sarees",
        limit=9,
    )

    assert hybrid.received_request.limit == 9

def test_query_pipeline_customer_limit_takes_precedence_over_caller_limit(
    monkeypatch,
):
    hybrid = StubHybridRetriever([])
    policy = RetrievalPolicy(
        fusion_window=10,
        rrf_k=60,
    )

    def fake_get_catalogue_vocabulary(connection):
        return {
            "category": ["Saree"],
        }

    def fake_understand_query(query, vocabulary):
        from backend.app.retrieval.models import RetrievalIntent

        return RetrievalIntent(
            original_query=query,
            semantic_query=query,
            filters={"category": "Saree"},
            requested_limit=8,
        )

    monkeypatch.setattr(
        "backend.app.retrieval.query_pipeline.get_catalogue_vocabulary",
        fake_get_catalogue_vocabulary,
    )

    monkeypatch.setattr(
        "backend.app.retrieval.query_pipeline.understand_query",
        fake_understand_query,
    )

    pipeline = QueryPipeline(
        connection=StubConnection(),
        hybrid_retriever=hybrid,
        policy=policy,
        default_limit=5,
    )

    pipeline.retrieve(
        "Show me 8 sarees",
        limit=3,
    )

    assert hybrid.received_request.limit == 8