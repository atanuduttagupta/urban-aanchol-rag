from typing import Protocol

from backend.app.conversation.models import ConversationContext
from backend.app.query_understanding.llm_models import LLMIntentProposal
from backend.app.retrieval.models import RetrievalIntent


class LLMIntentResolver(Protocol):
    """
    Provider-independent interface for resolving retrieval ambiguity.

    Implementations may use Gemini, another hosted model, or a local
    model in the future.
    """

    def resolve(
        self,
        intent: RetrievalIntent,
        context: ConversationContext,
    ) -> LLMIntentProposal: ...
