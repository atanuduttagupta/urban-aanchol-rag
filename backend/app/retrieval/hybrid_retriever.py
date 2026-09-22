from collections.abc import Sequence

from backend.app.retrieval.interfaces import (
    EligibilityProvider,
    ProductRetriever,
)
from backend.app.retrieval.models import (
    ProductResult,
    RetrievalPolicy,
    RetrievalRequest,
)


class HybridProductRetriever:
    """Combine multiple ranked product retrievers using Reciprocal Rank Fusion."""

    def __init__(
        self,
        eligibility_provider: EligibilityProvider,
        ranking_retrievers: Sequence[ProductRetriever],
    ) -> None:
        self.eligibility_provider = eligibility_provider
        self.ranking_retrievers = ranking_retrievers

    def retrieve(
        self,
        request: RetrievalRequest,
        policy: RetrievalPolicy,
    ) -> list[ProductResult]:
        # ---------------------------------------------------------
        # 1. Eligibility determines which products may participate.
        # ---------------------------------------------------------
        eligible_ids = self.eligibility_provider.get_eligible_product_ids(
            request
        )

        # ---------------------------------------------------------
        # 2. Run every ranking retriever.
        #
        # Each retriever uses policy.fusion_window rather than
        # request.limit.
        # ---------------------------------------------------------
        fused_scores: dict[str, float] = {}
        result_by_product: dict[str, ProductResult] = {}

        for retriever in self.ranking_retrievers:
            results = retriever.retrieve(
                request,
                policy,
            )

            for rank, result in enumerate(results, start=1):

                # Ignore products that fail eligibility.
                if result.product_id not in eligible_ids:
                    continue

                # Reciprocal Rank Fusion contribution.
                contribution = 1.0 / (
                    policy.rrf_k + rank
                )

                fused_scores[result.product_id] = (
                    fused_scores.get(result.product_id, 0.0)
                    + contribution
                )

                # Preserve the first available product representation.
                result_by_product.setdefault(
                    result.product_id,
                    result,
                )

        # ---------------------------------------------------------
        # 3. Sort by fused RRF score.
        #
        # Product ID is the deterministic tie-breaker.
        # ---------------------------------------------------------
        ranked_product_ids = sorted(
            fused_scores,
            key=lambda product_id: (
                fused_scores[product_id],
                product_id,
            ),
            reverse=True,
        )

        # ---------------------------------------------------------
        # 4. Apply the user-facing limit ONLY after fusion.
        # ---------------------------------------------------------
        return [
            ProductResult(
                product_id=product_id,
                product_name=result_by_product[
                    product_id
                ].product_name,
                category=result_by_product[
                    product_id
                ].category,
                price=result_by_product[
                    product_id
                ].price,
                availability=result_by_product[
                    product_id
                ].availability,
                score=fused_scores[product_id],
                retrieval_method="hybrid",
            )
            for product_id in ranked_product_ids[
                :request.limit
            ]
        ]