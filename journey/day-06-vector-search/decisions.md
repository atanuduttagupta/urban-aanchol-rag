# Urban Aanchol — Day 6 Decisions

## D6-01 — Use PostgreSQL + pgvector for persistent semantic retrieval

**Decision:** Use PostgreSQL with pgvector as the local persistent vector store.

**Reasoning:**

- PostgreSQL is already the structured application database.
- pgvector keeps structured and vector retrieval close together.
- SQL filters can be combined directly with vector retrieval.
- This supports the planned hybrid retrieval architecture.
- It avoids introducing a second database unnecessarily at the current scale.

**Result:** PostgreSQL 18.6 + pgvector 0.8.6 is the Day 6 local vector foundation.

---

## D6-02 — Build pgvector locally on Windows

**Decision:** Build pgvector from source rather than switching the database installation or using an unrelated package manager environment.

**Reasoning:**

The machine had multiple PostgreSQL-related tools, including Anaconda's `pg_config`, while the actual application database was PostgreSQL 18 installed under:

```text
C:\Program Files\PostgreSQL\18
```

Using the correct PostgreSQL installation avoided mixing environments.

**Result:** pgvector was successfully compiled and installed against PostgreSQL 18.

---

## D6-03 — Use Sentence Transformers for the initial embedding model

**Decision:** Use:

```text
sentence-transformers/all-MiniLM-L6-v2
```

**Reasoning:**

- It was already successfully tested during Day 5.
- It runs locally on the available machine.
- It produces 384-dimensional embeddings.
- It is practical for the current small catalogue and knowledge base.
- It avoids requiring a paid embedding API during development.

**Result:** Model loading and embedding generation were verified.

---

## D6-04 — Normalize embeddings

**Decision:** Generate normalized embeddings.

Implementation:

```python
normalize_embeddings=True
```

**Reasoning:**

The retrieval implementation uses cosine-distance semantics in pgvector.

**Result:** Product and knowledge embeddings are generated using the same normalization behavior.

---

## D6-05 — Store embeddings in separate tables

**Decision:** Do not add vector columns directly to `products` or `knowledge_chunks`.

Use:

```text
product_embeddings
knowledge_chunk_embeddings
```

**Reasoning:**

- Keeps source-of-truth business data independent from embedding artifacts.
- Allows multiple model/version records.
- Makes re-embedding workflows easier.
- Avoids coupling the product schema to one AI model.
- Supports future model experimentation.

**Result:** Separate embedding tables became part of the Day 6 architecture.

---

## D6-06 — Track model name, model version, and dimensions

**Decision:** Store:

```text
model_name
model_version
dimensions
```

with every embedding.

**Reasoning:**

Embeddings are model-dependent artifacts. Retrieval must not accidentally compare vectors generated under incompatible configurations.

`v1` is an application-level configuration version.

**Result:** Model/version-aware uniqueness is enforced at the database level.

---

## D6-07 — Use 384-dimensional pgvector columns for the current model

**Decision:** Use:

```sql
VECTOR(384)
```

for Day 6.

**Reasoning:**

`all-MiniLM-L6-v2` produces 384 dimensions.

The dimension constraint protects the current schema from accidentally storing an incompatible vector.

**Known limitation:**

The current schema is not yet a general multi-dimension embedding store. Supporting future models with other dimensions requires a deliberate schema/index strategy.

This is technical debt, not a Day 6 blocker.

---

## D6-08 — Keep semantic text separate from structured business facts

**Decision:** Do not embed every product field.

Semantic product text contains descriptive characteristics.

Price and availability remain structured.

**Reasoning:**

A customer request such as:

```text
under ₹3000
```

should be handled by SQL rather than hoping semantic similarity understands a numerical constraint.

Likewise, availability must be authoritative and current.

**Result:** Semantic retrieval and structured filtering have distinct responsibilities.

---

## D6-09 — Do not embed internal identifiers

**Decision:** Exclude IDs and database timestamps from embedding text.

**Reasoning:**

Identifiers are useful for database joins but do not represent semantic product or policy meaning.

**Result:** Product and knowledge embedding text contains human-meaningful content rather than database metadata.

---

## D6-10 — Include section title in knowledge embeddings

**Decision:** Embed:

```text
Section title + chunk text
```

rather than chunk text alone.

**Reasoning:**

Short policy chunks gain useful context from their section name.

Example:

```text
Section: Delivery
```

makes the following sentence more semantically anchored.

**Result:** The knowledge text builder follows this rule.

---

## D6-11 — Keep product and knowledge retrieval separate

**Decision:** Maintain separate retrieval functions for products and knowledge chunks.

**Reasoning:**

A question asking:

```text
Show me a saree for Puja
```

has a product-retrieval objective.

A question asking:

```text
How long does delivery take?
```

has a knowledge-retrieval objective.

Combining both indiscriminately would make routing and grounding harder.

**Result:** Separate vector search modules were created.

---

## D6-12 — Use availability as a hard product filter

**Decision:** Product vector search filters for:

```text
availability = Available
```

**Reasoning:**

Sold, Reserved, and Inactive products should not be presented as currently available recommendations.

Semantic relevance cannot override this business rule.

**Result:** Availability is enforced in product vector SQL.

---

## D6-13 — Use idempotent embedding persistence

**Decision:** Use unique source/model/version keys with:

```sql
ON CONFLICT DO UPDATE
```

**Reasoning:**

Embedding imports will be rerun when:

- catalogue data changes,
- knowledge content changes,
- embedding generation is repeated,
- indexing is rebuilt.

Repeated runs must not create duplicate embeddings.

**Result:** Duplicate verification returned zero duplicate knowledge records.

---

## D6-14 — Centralize embedding configuration

**Decision:** Store the current model configuration in:

```text
backend/app/database/embedding_config.py
```

**Reasoning:**

Hardcoding the same model name/version/dimension in several modules creates drift risk.

**Result:** Model name, application version, and dimensions now have one configuration source.

---

## D6-15 — Separate knowledge persistence from knowledge import orchestration

**Decision:** Put knowledge embedding database persistence in:

```text
knowledge_embedding_repository.py
```

rather than keeping the SQL insert function inside the importer.

**Reasoning:**

This keeps responsibilities separated:

```text
Importer
  → text construction
  → embedding generation
  → repository
  → database
```

The product pipeline already followed this pattern.

**Result:** Product and knowledge persistence now follow a consistent repository architecture.

---

## D6-16 — Do not over-optimize the small dataset

**Decision:** Keep the Day 6 embedding import simple and process the 9 products / 5 chunks successfully before optimizing.

**Reasoning:**

The current dataset is tiny.

Batched Sentence Transformer inference and approximate vector indexes are more important when data volume grows.

**Result:** Performance optimization is deferred until justified by catalogue/knowledge scale.

---

## D6-17 — Treat semantic scores as ranking signals, not customer-facing confidence

**Decision:** Do not expose cosine-similarity values as percentages or confidence claims to customers.

**Reasoning:**

A value such as:

```text
0.1189
```

is a model/vector-space ranking signal, not an 11.89% probability of relevance.

**Result:** Similarity scores remain internal retrieval signals.

---

## D6-18 — Semantic retrieval is not the final recommendation mechanism

**Decision:** Do not let vector similarity alone decide the final product recommendation.

**Evidence:**

The query:

```text
Something elegant for a family function
```

returned a blouse among the top product results.

**Reasoning:**

Semantic similarity can identify related meaning but may not enforce category or other business constraints.

**Result:** Day 7 will combine:

```text
SQL
+
metadata
+
full-text
+
semantic retrieval
+
reranking
```

---

## D6-19 — Do not replace the existing SQL/full-text retrieval

**Decision:** Keep the Day 5 retrieval mechanisms.

**Reasoning:**

Semantic retrieval complements rather than replaces:

- exact filters
- SQL
- full-text search
- metadata

This is the foundation of the planned hybrid retrieval architecture.

**Result:** Day 6 adds persistent semantic retrieval alongside the existing retrieval capabilities.

---

## D6-20 — Keep normalized occasion/style/mood/tag data out of the V1 product text builder for now

**Decision:** Do not immediately duplicate the normalized attribute tables into the first product embedding experiment.

**Reasoning:**

The current objective was to prove persistent vector storage and retrieval.

Occasion/style/mood/tags remain available structurally and should be incorporated into the production embedding pipeline after the basic persistence path is stable.

**Result:** This is a planned enhancement, not a discarded feature.

---

## D6-21 — Use manual verification scripts during the foundation stage

**Decision:** Use small executable test scripts during Day 6 to validate each logical step.

**Reasoning:**

The project is being built incrementally and educationally. Printing concrete database/model results made it easy to inspect each stage.

**Known limitation:**

These scripts should evolve into proper pytest tests with assertions as the application becomes more production-oriented.

---

## D6-22 — Do not add vector indexes yet

**Decision:** No approximate nearest-neighbor index was added during Day 6.

**Reasoning:**

The current dataset contains only:

```text
9 products
5 knowledge chunks
```

A vector index would add complexity without meaningful benefit at this scale.

**Result:** Exact pgvector retrieval is sufficient for the current foundation.

---

## D6-23 — Preserve vendor independence

**Decision:** Keep the embedding layer behind application-level interfaces rather than exposing provider-specific assumptions to the rest of the application.

**Reasoning:**

The project has a strong zero-cost and no-vendor-lock-in requirement.

The embedding model/provider may change later.

**Result:** The embedding generator, configuration, repositories, and search modules form replaceable boundaries.

---

## D6-24 — Day 6 ends at persistent semantic retrieval

**Decision:** Do not implement hybrid retrieval, reranking, conversational RAG, or agentic behavior in Day 6.

**Reasoning:**

Day 6's purpose is to establish a reliable persistent semantic foundation.

The next layer should build on this rather than mixing several retrieval concerns together.

**Result:** Day 7 begins with hybrid retrieval and reranking.
