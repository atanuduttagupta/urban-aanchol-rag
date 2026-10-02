from backend.app.conversation.models import ConversationContext
from backend.app.query_understanding.llm_models import (
    LLMIntentProposal,
)
from backend.app.query_understanding.retrieval_orchestrator import (
    OrchestrationStatus,
    prepare_retrieval,
)

TEST_VOCABULARY = {
    "colour": ["Red", "Blue", "Green"],
    "fabric": ["Silk", "Cotton"],
    "occasion": ["Wedding", "Durga Puja"],
}


class StubLLMResolver:
    def __init__(self, proposal: LLMIntentProposal) -> None:
        self.proposal = proposal
        self.called = False

    def resolve(self, intent, context):
        self.called = True
        return self.proposal


def test_safe_query_is_ready_without_llm() -> None:
    resolver = StubLLMResolver(
        LLMIntentProposal(
            filters={"colour": "Red"},
        )
    )

    result = prepare_retrieval(
        query="Show me red silk sarees",
        context=ConversationContext(),
        vocabulary=TEST_VOCABULARY,
        llm_resolver=resolver,
    )

    assert result.status == OrchestrationStatus.READY_FOR_RETRIEVAL
    assert result.intent is not None
    assert resolver.called is False


def test_ambiguous_llm_eligible_query_requires_llm() -> None:
    result = prepare_retrieval(
        query="Show me something around ₹3000",
        context=ConversationContext(),
        vocabulary=TEST_VOCABULARY,
    )

    assert result.status == OrchestrationStatus.NEEDS_LLM
    assert result.intent is None


def test_valid_llm_proposal_produces_retrieval_ready_intent() -> None:
    resolver = StubLLMResolver(
        LLMIntentProposal(
            filters={"max_price": 3000},
        )
    )

    result = prepare_retrieval(
        query="Show me something around ₹3000",
        context=ConversationContext(),
        vocabulary=TEST_VOCABULARY,
        llm_resolver=resolver,
    )

    assert result.status == OrchestrationStatus.READY_FOR_RETRIEVAL
    assert result.intent is not None
    assert result.intent.filters == {
        "max_price": 3000,
    }
    assert resolver.called is True


def test_invalid_llm_proposal_is_rejected() -> None:
    resolver = StubLLMResolver(
        LLMIntentProposal(
            filters={"colour": "Unicorn Pink"},
        )
    )

    result = prepare_retrieval(
        query="Show me something around ₹3000",
        context=ConversationContext(),
        vocabulary=TEST_VOCABULARY,
        llm_resolver=resolver,
    )

    assert result.status == OrchestrationStatus.REJECTED
    assert result.intent is None


def test_llm_conflict_is_rejected() -> None:
    resolver = StubLLMResolver(
        LLMIntentProposal(
            filters={"colour": "Red"},
        )
    )

    result = prepare_retrieval(
        query="Show me blue sarees around ₹3000",
        context=ConversationContext(),
        vocabulary=TEST_VOCABULARY,
        llm_resolver=resolver,
    )

    assert result.status == OrchestrationStatus.REJECTED
    assert result.intent is None


def test_resolvable_reference_does_not_call_llm() -> None:
    resolver = StubLLMResolver(LLMIntentProposal())

    result = prepare_retrieval(
        query="Show me something like the first one",
        context=ConversationContext(
            last_result_ids=("UA-0024", "UA-0018"),
        ),
        vocabulary=TEST_VOCABULARY,
        llm_resolver=resolver,
    )

    assert result.status == OrchestrationStatus.READY_FOR_RETRIEVAL
    assert result.resolved_product_id == "UA-0024"
    assert resolver.called is False


def test_first_one_reference_is_resolved() -> None:
    result = prepare_retrieval(
        query="show me the first one",
        context=ConversationContext(
            last_result_ids=("UA-0024", "UA-0018"),
        ),
        vocabulary=TEST_VOCABULARY,
    )

    assert result.status == OrchestrationStatus.READY_FOR_RETRIEVAL
    assert result.resolved_product_id == "UA-0024"
