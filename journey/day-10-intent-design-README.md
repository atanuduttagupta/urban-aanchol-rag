# Urban Aanchol — Day 10 Journey

**Focus:** Retrieval Safety, Conversation Context & LLM-Assisted Retrieval Orchestration

## 1. Objective

Day 10 extends the deterministic Query Understanding foundation from Day 9 into a retrieval-safe orchestration layer.

The objective is to distinguish:
- queries that can be retrieved deterministically,
- queries resolvable from conversation context,
- queries requiring controlled LLM assistance,
- queries requiring clarification or rejection.

The LLM does **not** directly control SQL or retrieval.

```text
Customer Query
      |
      v
Deterministic Query Understanding
      |
      v
Retrieval Safety Detection
      |
      v
Conversation Context Resolution
      |
      +----> Resolved ----------------------+
      |                                      |
      +----> Ambiguous                       |
      |          |                           |
      |          v                           |
      |    LLM Escalation Policy             |
      |          |                           |
      |          v                           |
      |    LLM Intent Proposal               |
      |          |                           |
      |          v                           |
      |    Validate Proposal                 |
      |          |                           |
      |          v                           |
      |    Merge with Deterministic Intent   |
      |          |                           |
      +----------+---------------------------+
                         |
                         v
                Retrieval Service
                         |
                         v
                  Hybrid Retrieval
```

## 2. Core Design Principles

### Deterministic first
The system first uses deterministic logic for catalogue attributes, price constraints, requested quantity, and retrieval safety.

### Retrieval safety instead of parser completeness
The important question is whether a query can be safely sent to retrieval, not whether every possible sentence is structurally parsed.

`retrieval_safe=True` is assigned only when no known retrieval-critical ambiguity remains.

### Conservative handling
When uncertain, ambiguity is safer than an unsafe retrieval decision.

### Controlled LLM fallback
The LLM is used only when deterministic analysis identifies an ambiguity eligible for LLM resolution.

The LLM proposes intent; it does not execute retrieval.

## 3. Retrieval Safety

Created:

```text
backend/app/query_understanding/retrieval_safety.py
```

The `RetrievalSafety` model contains:

```python
@dataclass(frozen=True)
class RetrievalSafety:
    retrieval_safe: bool
    signals: tuple[str, ...] = ()
```

Detected retrieval-critical signals include:

### Conversational references
- the one
- that one
- this one
- the previous
- earlier
- as before
- same as
- like that
- first/second/third one

### Comparisons
- cheaper than
- more expensive than
- more costly than
- similar to
- different from
- better than

### Catalogue-aware negation
- not red
- without zari
- except cotton
- avoid silk

Negation is considered retrieval-critical when it relates to a known catalogue value.

### Approximate constraints
- around ₹3000
- approximately ₹3000
- about ₹3000
- not too expensive
- affordable

## 4. Conversation Context

Created:

```text
backend/app/conversation/models.py
```

Current short-lived retrieval context:

```python
@dataclass(frozen=True)
class ConversationContext:
    previous_query: str | None = None
    last_result_ids: tuple[str, ...] = ()
    selected_product_id: str | None = None
```

This is deliberately separate from future customer/account history.

## 5. Deterministic Reference Resolution

Created:

```text
backend/app/conversation/resolver.py
```

Currently supported references include:

```text
first one
1st one
second one
2nd one
third one
3rd one
this saree
that saree
this one
that one
```

Trusted context comes from:

```text
last_result_ids
selected_product_id
```

For example:

```text
Customer: Show me 5 blue sarees.
Customer: I like the second one.
```

`second one` can resolve to `last_result_ids[1]`.

Phrases such as `previous one` intentionally remain potentially ambiguous.

## 6. Resolution Status

Created:

```text
backend/app/conversation/resolution.py
```

Statuses:

```text
RESOLVED
AMBIGUOUS
UNRESOLVED
```

- **RESOLVED:** safe to proceed.
- **AMBIGUOUS:** retrieval-critical ambiguity exists and may be eligible for controlled LLM resolution.
- **UNRESOLVED:** a required reference cannot be resolved from available context.

## 7. LLM Resolution Policy

Created:

```text
backend/app/query_understanding/llm_resolution_policy.py
```

Initial LLM-eligible signals:

```text
conversational_reference_detected
comparison_detected
approximate_constraint_detected
```

Negation is intentionally not automatically escalated because catalogue-aware deterministic exclusion handling can eventually support it.

The policy only decides whether LLM resolution is permitted.

## 8. Provider-Independent LLM Interface

Created:

```text
backend/app/query_understanding/llm_interface.py
```

```python
class LLMIntentResolver(Protocol):
    def resolve(
        self,
        intent: RetrievalIntent,
        context: ConversationContext,
    ) -> LLMIntentProposal:
        ...
```

This keeps the architecture independent of a specific LLM provider.

## 9. LLM Intent Proposal

Created:

```text
backend/app/query_understanding/llm_models.py
```

```python
@dataclass(frozen=True)
class LLMIntentProposal:
    semantic_query: str | None = None
    filters: dict[str, Any] | None = None
    requested_limit: int | None = None
    resolved_product_id: str | None = None
```

The LLM proposes a constrained intent rather than executing retrieval.

## 10. LLM Proposal Validation

Created:

```text
backend/app/query_understanding/llm_intent_validator.py
```

Validation covers:

- supported filter names,
- catalogue values against the current vocabulary,
- numeric/non-negative price values,
- positive requested limits,
- trusted resolved product IDs.

Invalid proposals are rejected before retrieval.

Supported structured filters include:

```text
category
availability
brand
collection
fabric
colour
secondary_colour
pattern
border
occasion
style
mood
tag
min_price
max_price
```

## 11. Deterministic + LLM Intent Merge

Created:

```text
backend/app/query_understanding/intent_merger.py
```

The merger combines deterministic intent with a validated LLM proposal.

Important rule:

> Deterministic structured constraints cannot be silently overwritten by conflicting LLM values.

Conflicting filters or requested limits cause the merge to fail.

## 12. Retrieval Orchestrator

Created:

```text
backend/app/query_understanding/retrieval_orchestrator.py
```

Flow:

```text
Query Understanding
        |
        v
Retrieval Safety
        |
        v
Conversation Resolution
        |
        v
LLM Policy
        |
        v
LLM Proposal
        |
        v
Validation
        |
        v
Intent Merge
```

Statuses:

```text
READY_FOR_RETRIEVAL
NEEDS_LLM
NEEDS_CLARIFICATION
REJECTED
```

## 13. Product Repository

Created:

```text
backend/app/catalogue/product_repository.py
backend/app/catalogue/postgres_product_repository.py
```

The repository abstraction supports direct product retrieval by product ID.

The PostgreSQL implementation retrieves:

```text
product_id
product_name
category
price
availability
```

This supports conversational product selection without another semantic search.

## 14. Retrieval Service Integration

Created:

```text
backend/app/retrieval/service.py
```

`RetrievalService` now coordinates orchestration and hybrid retrieval.

It accepts an injected:

```text
LLMIntentResolver
```

Execution states include:

- `COMPLETED`
- `NEEDS_LLM`
- `NEEDS_CLARIFICATION`
- `REJECTED`

A resolved product reference can use `ProductRepository.get_product()` directly.

## 15. Natural-Language Quantity Handling

Final regression testing exposed that:

```text
I need 5 blue sarees
```

was not being recognized as a requested quantity.

The extractor was extended to support:

```text
I need 5
I want 4
```

alongside existing forms such as:

```text
show me 5
give me 5
find 5
list 5
top 5
```

Regression tests were added and the full backend suite subsequently passed.

## 16. Testing

Day 10 added focused tests for:

- conversation context,
- reference resolution,
- resolution status,
- retrieval safety,
- LLM resolution policy,
- LLM proposal model,
- LLM proposal validation,
- intent merging,
- retrieval orchestration,
- product repository,
- retrieval service,
- natural-language quantity extraction.

Final full backend regression testing passed.

## 17. Quality Checks

Final checks:

```text
Full backend tests       PASS
git diff --check         PASS
Day 10 Ruff checks       PASS
```

Ruff fixes were deliberately limited to files touched during Day 10. Existing unrelated Ruff findings were not broadly reformatted.

## 18. Final Architecture

```text
                    CUSTOMER QUERY
                          |
                          v
              +-----------------------+
              | Query Understanding   |
              |-----------------------|
              | Attributes            |
              | Price                 |
              | Quantity              |
              | Safety Signals        |
              +-----------+-----------+
                          |
                          v
              +-----------------------+
              | Retrieval Safety      |
              +-----------+-----------+
                          |
                 +--------+--------+
                 |                 |
              SAFE/RESOLVED      AMBIGUOUS
                 |                 |
                 |                 v
                 |       +-------------------+
                 |       | LLM Policy        |
                 |       +---------+---------+
                 |                 |
                 |                 v
                 |       +-------------------+
                 |       | LLM Intent        |
                 |       | Proposal           |
                 |       +---------+---------+
                 |                 |
                 |                 v
                 |       +-------------------+
                 |       | Validation        |
                 |       +---------+---------+
                 |                 |
                 |                 v
                 |       +-------------------+
                 |       | Intent Merge      |
                 |       +---------+---------+
                 |                 |
                 +--------+--------+
                          |
                          v
                 +-------------------+
                 | Retrieval Service |
                 +---------+---------+
                           |
                           v
                 +-------------------+
                 | Hybrid Retrieval  |
                 +-------------------+
```

## 19. Key Lessons

1. Retrieval safety is more important than parser completeness.
2. The LLM should be constrained and validated.
3. Conversation context is different from customer history.
4. Deterministic logic remains authoritative for hard structured constraints.
5. Provider independence should be preserved.

## 20. Day 10 Completion

Day 10 establishes:

```text
Deterministic Query Understanding
        +
Retrieval Safety
        +
Conversation Context
        +
Controlled LLM Escalation
        +
Validated Intent
        +
Hybrid Retrieval
```

This provides the foundation for the customer-facing recommendation/agent layer.

## 21. Git Commit

```powershell
git commit -m "feat: establish Day 10 retrieval orchestration foundation"
```

Then verify:

```powershell
git status --short
```

After committing, push:

```powershell
git push
```
