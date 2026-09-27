from psycopg import Connection

from backend.app.database.catalogue_attribute_repository import (
    get_catalogue_vocabulary,
)
from backend.app.query_understanding.query_understanding import (
    understand_query,
)
from backend.app.retrieval.hybrid_retriever import HybridProductRetriever
from backend.app.retrieval.models import (
    ProductResult,
    RetrievalPolicy,
    RetrievalRequest,
)


class QueryPipeline:
    """Orchestrate query understanding and hybrid product retrieval."""

    def __init__(
        self,
        connection: Connection,
        hybrid_retriever: HybridProductRetriever,
        policy: RetrievalPolicy,
        default_limit: int = 5,
    ) -> None:
        self.connection = connection
        self.hybrid_retriever = hybrid_retriever
        self.policy = policy
        self.default_limit = default_limit

    def retrieve(
        self,
        query: str,
        limit: int | None = None,
    ) -> list[ProductResult]:
        vocabulary = get_catalogue_vocabulary(
            self.connection,
        )

        intent = understand_query(
            query=query,
            vocabulary=vocabulary,
        )

        resolved_limit = intent.requested_limit or limit or self.default_limit

        request = RetrievalRequest(
            query=intent.semantic_query,
            limit=resolved_limit,
            filters=intent.filters,
        )

        return self.hybrid_retriever.retrieve(
            request=request,
            policy=self.policy,
        )
