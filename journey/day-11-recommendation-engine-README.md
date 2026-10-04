# Day 11 — Recommendation Engine

## Objective

Build a deterministic recommendation layer on top of the Day 8–10 hybrid retrieval and query-understanding foundation.

The recommendation layer must remain separate from retrieval, conversation orchestration, and LLM response generation.

---

## Day 11 Architecture

```text
Customer Query
      ↓
Query Understanding
      ↓
Retrieval Safety / Resolution
      ↓
Hybrid Retrieval
      ↓
ProductResult[]
      ↓
RecommendationService
      ├── Scoring
      ├── Ranking
      └── Grounded Explanation Signals
      ↓
Recommendation[]
```

---

## 11A — Recommendation Contract

Created:

```text
backend/app/recommendation/models.py
```

Introduced the `Recommendation` model:

- `product`
- `recommendation_score`
- `explanation_signals`

The existing `ProductResult.score` continues to represent the hybrid retrieval/RRF score.

The recommendation score is kept as a separate field so retrieval and recommendation semantics are not conflated.

### Tests

Created:

```text
backend/tests/test_recommendation_models.py
```

Focused test passed.

---

## 11B — Recommendation Signals

Reviewed the existing retrieval architecture.

The current hybrid retrieval pipeline already provides:

- metadata eligibility
- keyword retrieval
- semantic retrieval
- Reciprocal Rank Fusion
- price
- availability
- category

The product embedding text already contains:

- product name
- category
- brand
- collection
- fabric
- colour
- secondary colour
- pattern
- border
- description
- remarks

Therefore, arbitrary additional recommendation weights were not introduced.

### Design decision

The first recommendation baseline uses the existing hybrid RRF score as the recommendation score.

Hard constraints remain enforced by the eligibility layer.

---

## 11C — Deterministic Recommendation Scorer

Created:

```text
backend/app/recommendation/scorer.py
```

The scorer:

- preserves the existing hybrid retrieval score;
- handles missing scores safely;
- attaches grounded explanation signals;
- does not perform retrieval or filtering.

### Tests

Created:

```text
backend/tests/test_recommendation_scorer.py
```

All focused tests passed.

---

## 11D — Recommendation Ranker

Created:

```text
backend/app/recommendation/ranker.py
```

The ranker:

1. sorts recommendations by recommendation score;
2. uses product ID as a deterministic tie-breaker;
3. applies the user-facing limit.

It does not perform:

- SQL filtering;
- semantic retrieval;
- keyword retrieval;
- eligibility;
- score modification;
- LLM processing.

### Tests

Created:

```text
backend/tests/test_recommendation_ranker.py
```

All focused tests passed.

---

## 11E — Grounded Recommendation Explanations

Created:

```text
backend/app/recommendation/explanation.py
```

The explanation layer converts known recommendation signals into customer-facing explanation text.

The implementation intentionally avoids inventing product attributes that are not available to the recommendation layer.

For example, the system must not claim that a saree is suitable for a wedding unless that information is actually supported by retrieval/catalogue evidence.

### Tests

Created:

```text
backend/tests/test_recommendation_explanation.py
```

Tests verify both grounded explanations and the absence of unsupported claims.

---

## 11F — Recommendation Service

Created:

```text
backend/app/recommendation/service.py
```

`RecommendationService` coordinates:

```text
ProductResult[]
      ↓
score_product()
      ↓
rank_recommendations()
      ↓
Recommendation[]
```

The service does not perform retrieval.

This preserves the separation between retrieval and recommendation.

### Tests

Created:

```text
backend/tests/test_recommendation_service.py
```

All focused tests passed.

---

## 11G — Integration and Regression Testing

Created:

```text
backend/tests/test_recommendation_integration.py
```

Verified that hybrid retrieval results can flow into `RecommendationService` and produce correctly ranked recommendations.

### Regression result

Full backend test suite:

```text
207 passed
```

Execution time:

```text
234.28 seconds
```

Additional quality check:

```text
git diff --check
```

passed with no whitespace errors.

---

## Architecture Decisions

### 1. Retrieval and recommendation remain separate

`RetrievalService` remains responsible for retrieval orchestration.

`RecommendationService` is responsible for ranking retrieved products into recommendations.

This prevents recommendation-specific business logic from polluting the retrieval layer.

### 2. RRF score retains its meaning

`ProductResult.score` continues to represent hybrid retrieval relevance.

Recommendation scoring is represented separately.

### 3. No arbitrary scoring weights

No manually chosen semantic/keyword/metadata percentages were introduced.

The current implementation establishes a deterministic baseline that can later be evaluated and improved.

### 4. Hard constraints remain hard constraints

Eligibility and structured filters determine which products may participate.

Recommendation ranking operates only on eligible retrieval results.

### 5. Explanations are grounded

The recommendation layer only exposes explanation signals supported by the available retrieval/product information.

---

## Day 11 Outcome

Urban Aanchol now has a separate deterministic recommendation layer on top of hybrid retrieval.

Current flow:

```text
Query
 ↓
Query Understanding
 ↓
Retrieval Safety
 ↓
Hybrid Retrieval
 ↓
Recommendation Scoring
 ↓
Recommendation Ranking
 ↓
Grounded Recommendation
```

The LLM is intentionally not part of the recommendation engine.

Groq/open-source LLM integration remains planned for Day 13, where the LLM will generate natural-language responses from grounded retrieval/recommendation evidence.

---

## Files Added

```text
backend/app/recommendation/__init__.py
backend/app/recommendation/models.py
backend/app/recommendation/scorer.py
backend/app/recommendation/ranker.py
backend/app/recommendation/explanation.py
backend/app/recommendation/service.py

backend/tests/test_recommendation_models.py
backend/tests/test_recommendation_scorer.py
backend/tests/test_recommendation_ranker.py
backend/tests/test_recommendation_explanation.py
backend/tests/test_recommendation_service.py
backend/tests/test_recommendation_integration.py
```

---

## Completion Criteria

- [x] Recommendation model created
- [x] Recommendation signals reviewed
- [x] Deterministic scorer implemented
- [x] Recommendation ranker implemented
- [x] Grounded explanation layer implemented
- [x] Recommendation service implemented
- [x] Integration test implemented
- [x] Full backend regression passed
- [x] `git diff --check` passed

Day 11 implementation is complete and ready for final staging and commit.
