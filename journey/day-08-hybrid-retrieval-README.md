# Day 8 — Hybrid Retrieval Foundation

## Objective

Establish the retrieval architecture for Urban Aanchol's RAG system with a clear separation between product eligibility, retrieval candidate depth, ranking/fusion, and final user-facing result limit.

## Key Work

### 1. Retrieval Request vs Retrieval Policy

Separated the user-facing result count from internal retrieval configuration.

- `RetrievalRequest.limit` = maximum products returned to the user.
- `RetrievalPolicy.fusion_window` = candidate depth supplied by each ranking backend.
- `RetrievalPolicy.rrf_k` = Reciprocal Rank Fusion parameter.

This prevents the user-facing limit from prematurely restricting internal candidate retrieval.

### 2. Metadata Eligibility Layer

Introduced `EligibilityProvider` and `MetadataEligibilityProvider`.

Eligibility determines which products satisfy hard metadata constraints, including:

- category
- availability
- brand
- collection
- fabric
- colour
- secondary colour
- pattern
- border
- price range
- occasion
- style
- mood
- tag

The eligibility layer deliberately does not apply the final result limit.

### 3. Shared Product Filter Builder

Introduced:

```text
backend/app/retrieval/filters.py
```

with:

```python
build_product_filter_sql(filters)
```

It centralizes exact, partial text, price-range, and normalized attribute filters.

### 4. Keyword Retrieval

`KeywordProductRetriever` now accepts both `RetrievalRequest` and `RetrievalPolicy`.

PostgreSQL full-text search continues to use `websearch_to_tsquery` and `ts_rank`.

The internal `LIMIT` now uses `policy.fusion_window`, not `request.limit`.

### 5. Semantic Retrieval

`SemanticProductRetriever` now uses the same retrieval contract.

Semantic retrieval continues to use:

- `all-MiniLM-L6-v2`
- 384-dimensional embeddings
- PostgreSQL/pgvector similarity search

Its internal candidate depth also uses `policy.fusion_window`.

### 6. Centralized Eligibility

The hidden availability restriction was removed from vector search.

Availability and other hard metadata constraints are now handled centrally through `MetadataEligibilityProvider`.

The resulting architecture is:

```text
User Query
    ↓
Eligibility / Metadata Constraints
    ↓
Keyword Ranking ─┐
                 ├── Hybrid Fusion
Semantic Ranking ┘
    ↓
Final Limit
```

### 7. Hybrid Retrieval with RRF

Introduced `HybridProductRetriever`.

It accepts:

```text
EligibilityProvider
+
Sequence[ProductRetriever]
```

Current ranking retrievers:

- Keyword
- Semantic

The generic design leaves room for future:

- Graph retrieval
- Image retrieval

### 8. Reciprocal Rank Fusion

Hybrid retrieval uses:

```text
contribution = 1 / (rrf_k + rank)
```

with default:

```text
rrf_k = 60
```

The hybrid layer fuses ranked candidates and applies `request.limit` only to the final result set.

### 9. Integration Testing

Added real PostgreSQL/pgvector integration tests covering:

- Jaipuri cotton blue retrieval
- Mul cotton blue retrieval
- Mul cotton green retrieval
- price-range filtering
- metadata eligibility
- keyword + semantic hybrid ranking

The hybrid tests demonstrated genuine RRF fusion rather than simply returning one backend's ranking.

### 10. Catalogue Versioning

The original catalogue was renamed:

```text
products_dummy.xlsx
    ↓
products_dummy_v1.0.xlsx
```

A newer catalogue was added:

```text
products_dummy_v1.1.xlsx
```

The current v1.1 catalogue contains 30 populated products:

```text
UA-0001 → UA-0030
```

Reserved empty IDs are not imported.

A catalogue regression test validates this behavior.

The legacy product-mapper validation continues to use v1.0 because it intentionally validates the original 9-product dataset.

### 11. Test Coverage

Final backend test result:

```text
31 passed in 71.20s
```

Coverage includes:

- retrieval models
- filter construction
- eligibility provider
- keyword retrieval
- semantic retrieval
- metadata retrieval
- hybrid retrieval
- hybrid integration
- product filtering
- catalogue loading
- product mapping

### 12. Repository Cleanup

Removed the temporary diagnostic script:

```text
backend/tests/check_late_products.py
```

Trailing whitespace was also removed after `git diff --cached --check` identified two issues.

## Final Architecture Snapshot

```text
                    User Query
                        │
                        ▼
              RetrievalRequest
                        │
              ┌─────────┴─────────┐
              │                   │
              ▼                   ▼
       EligibilityProvider   RetrievalPolicy
              │                   │
              ▼                   │
      Eligible Product IDs        │
              │                   │
              └─────────┬─────────┘
                        │
              ┌─────────┴─────────┐
              │                   │
              ▼                   ▼
        Keyword Search      Semantic Search
              │                   │
              │   fusion_window   │
              └─────────┬─────────┘
                        ▼
                RRF Hybrid Fusion
                        │
                        ▼
                 request.limit
                        │
                        ▼
                  Final Results
```

## Key Design Principles Established

1. Eligibility is separate from ranking.
2. User-facing result limit is separate from internal candidate depth.
3. Hard metadata constraints are not semantic scores.
4. Hybrid retrieval owns final result limiting.
5. RRF combines ranked candidate lists.
6. Retrieval backends are replaceable through interfaces.
7. Future Graph and Image retrievers can plug into the hybrid layer.
8. Real integration tests validate retrieval against PostgreSQL/pgvector.
9. Catalogue versions are explicit rather than silently overwritten.
10. Correctness and grounded retrieval take priority over prematurely adding advanced agent features.

## Day 8 Completion

**Day 8: COMPLETE**

Commit:

```text
6fd350b feat: establish Day 8 hybrid retrieval
```

The Git working tree was clean after the commit.

Next planned milestone: **Day 9 — build on the committed retrieval foundation.**
