from backend.app.query_understanding.llm_models import (
    LLMIntentProposal,
)


def test_empty_llm_proposal_is_allowed() -> None:
    proposal = LLMIntentProposal()

    assert proposal.semantic_query is None
    assert proposal.filters is None
    assert proposal.requested_limit is None
    assert proposal.resolved_product_id is None


def test_llm_proposal_stores_retrieval_fields() -> None:
    proposal = LLMIntentProposal(
        semantic_query="cheaper festive saree",
        filters={
            "colour": "blue",
            "occasion": "wedding",
        },
        requested_limit=5,
        resolved_product_id="UA-0024",
    )

    assert proposal.semantic_query == "cheaper festive saree"
    assert proposal.filters == {
        "colour": "blue",
        "occasion": "wedding",
    }
    assert proposal.requested_limit == 5
    assert proposal.resolved_product_id == "UA-0024"
