# Day 6 — Persistent Semantic Retrieval

## Objective

Convert the Day 5 in-memory semantic-search experiment into a persistent PostgreSQL + pgvector retrieval foundation.

Day 6 establishes two durable semantic retrieval paths:

1. **Product semantic retrieval** for natural-language product discovery.
2. **Knowledge semantic retrieval** for boutique policies and future RAG knowledge.

The implementation was built incrementally: infrastructure → schema → one-record verification → batch persistence → vector search → integrity checks → code cleanup.

---

## Starting Point

At the end of Day 5, Urban Aanchol already had:

- A validated and normalized Excel catalogue.
- PostgreSQL product and knowledge tables.
- Structured occasion, style, mood, and tag data.
- Media and product-media relationships.
- Knowledge documents and chunks.
- SQL retrieval.
- Metadata retrieval.
- PostgreSQL Full-Text Search.
- An in-memory Sentence Transformers semantic-search experiment.

Day 6 made semantic retrieval persistent.

---

## 1. Local PostgreSQL and pgvector

The local database environment was assessed for pgvector support.

Initially, the PostgreSQL `vector` extension was unavailable.

Two `pg_config.exe` installations were identified:

```text
C:\ProgramData\anaconda3\Library\bin\pg_config.exe
C:\Program Files\PostgreSQL\18\bin\pg_config.exe
```

The actual application database installation was identified as:

```text
PostgreSQL 18.6
```

The project deliberately used the PostgreSQL 18 installation rather than the unrelated Anaconda PostgreSQL tooling.

### Windows build tooling

Because a ready-to-use pgvector package was not available through the existing installation, pgvector was built locally.

Visual Studio Community 2026 was installed with:

```text
Desktop development with C++
```

The x64 Native Tools Command Prompt was used and both were verified:

```text
cl
nmake
```

### pgvector build

pgvector release:

```text
v0.8.6
```

Source location:

```text
C:\pgvector
```

Build:

```powershell
nmake /F Makefile.win
```

Install:

```powershell
nmake /F Makefile.win install
```

The PostgreSQL `vector` extension was then enabled:

```sql
CREATE EXTENSION vector;
```

Verified:

```text
vector | 0.8.6
```

### Result

The local vector stack became:

```text
PostgreSQL 18.6
+
pgvector 0.8.6
```

---

## 2. Embedding Storage Design

Embeddings are stored separately from source-of-truth product and knowledge data.

Created:

```text
product_embeddings
knowledge_chunk_embeddings
```

Both use:

```text
VECTOR(384)
```

and store:

```text
model_name
model_version
dimensions
```

### Product embeddings

The table is linked to `products`.

Uniqueness is enforced by:

```text
(product_id, model_name, model_version)
```

### Knowledge embeddings

The table is linked to `knowledge_chunks`.

Uniqueness is enforced by:

```text
(chunk_id, model_name, model_version)
```

Foreign keys use cascade deletion so an embedding cannot remain after its source record is deleted.

### Why separate tables?

This:

- Keeps business/source data independent from embedding artifacts.
- Allows multiple embedding model/version records.
- Makes re-embedding easier.
- Avoids coupling the core schema to one AI model.
- Supports future model experimentation.

The schema was created in:

```text
database/schema/015_create_embedding_tables.sql
```

Dimension checks enforce the current 384-dimensional model configuration.

---

## 3. Embedding Configuration

Created:

```text
backend/app/database/embedding_config.py
```

Current configuration:

```text
MODEL_NAME = sentence-transformers/all-MiniLM-L6-v2
MODEL_VERSION = v1
EMBEDDING_DIMENSIONS = 384
```

`v1` is an application-level configuration version label.

Centralizing the configuration prevents model name, version, and dimension settings from drifting across modules.

The current schema is intentionally `VECTOR(384)` because the selected model produces 384-dimensional embeddings. Supporting models with different dimensions will require a deliberate future schema/index strategy.

---

## 4. Product Embedding Text

Created:

```text
backend/app/database/embedding_text.py
```

The current V1 product embedding text contains semantic product characteristics:

```text
Product
Category
Brand
Collection
Fabric
Colour
Secondary colour
Pattern
Border
Description
Remarks
```

It deliberately excludes:

```text
product_id
price
availability
timestamps
```

### Reason

Price and availability are authoritative structured business facts.

For example:

```text
under ₹3000
```

should be handled through SQL/metadata filtering rather than relying on semantic similarity.

Likewise, current availability must come from structured data.

Internal identifiers and timestamps do not provide useful semantic meaning.

### Planned enhancement

The current builder does not yet include normalized:

- occasion
- style
- mood
- tags

These remain available through structured PostgreSQL tables and can be incorporated into the production embedding pipeline after the persistent vector path is stable.

---

## 5. Embedding Generation

Created:

```text
backend/app/database/embedding_generator.py
```

Selected model:

```text
sentence-transformers/all-MiniLM-L6-v2
```

Output dimension:

```text
384
```

Embeddings are generated with normalized output:

```python
normalize_embeddings=True
```

This matches the cosine-distance retrieval strategy used with pgvector.

Initial verification confirmed:

```text
Model dimensions: 384
Embedding length: 384
```

---

## 6. Product Embedding Persistence

Created:

```text
backend/app/database/embedding_repository.py
```

Persistence uses:

```sql
ON CONFLICT (product_id, model_name, model_version)
DO UPDATE
```

This makes repeated imports idempotent.

### First product verification

Product:

```text
UA-0001
```

The embedding was generated and persisted successfully.

PostgreSQL verification confirmed the stored vector dimension:

```text
stored_dimensions = 384
```

### Batch import

Created:

```text
backend/app/database/import_product_embeddings.py
```

All 9 catalogue products were processed.

Result:

```text
Products loaded: 9
Embeddings saved: 9
```

---

## 7. Product Vector Search

Created:

```text
backend/app/database/vector_search.py
```

The search uses pgvector cosine distance:

```sql
embedding <=> query_vector
```

The distance is converted into a similarity-style ranking signal:

```text
1 - cosine_distance
```

The search joins embeddings with product records and enforces:

```text
availability = Available
```

This ensures vector similarity cannot cause Sold, Reserved, or Inactive products to be presented as currently available.

---

## 8. Persistent Product Semantic Search Test

Query:

```text
Something elegant for a family function
```

The query was embedded and searched against persisted PostgreSQL vectors.

The search returned ranked products, including:

```text
UA-0005 — Beige & Red Handloom Saree
```

among the top results.

The experiment also demonstrated an important limitation: semantic similarity can return a semantically related but inappropriate category, such as a blouse when the intended product type is a saree.

Therefore:

> Semantic retrieval is a ranking signal, not the final eligibility mechanism.

The intended production flow remains:

```text
Query Understanding
        ↓
SQL / Metadata Constraints
        ↓
Semantic Retrieval
        ↓
Reranking
```

---

## 9. Knowledge Embedding Text

The existing knowledge base contained five policy chunks:

```text
How to Order
Delivery
Payment
Shipping Charges
Returns
```

Created:

```text
backend/app/database/knowledge_embedding_text.py
```

Knowledge embedding text is:

```text
Section title
+
Chunk text
```

For example:

```text
Section: Delivery

[chunk content]
```

Including the section title gives short policy chunks additional semantic context.

---

## 10. Knowledge Embedding Persistence

Created:

```text
backend/app/database/knowledge_embedding_repository.py
```

Persistence uses:

```sql
ON CONFLICT (chunk_id, model_name, model_version)
DO UPDATE
```

This keeps knowledge embedding imports idempotent.

Created:

```text
backend/app/database/import_knowledge_embeddings.py
```

All five policy chunks were embedded.

Result:

```text
Knowledge chunks loaded: 5
Knowledge embeddings saved: 5
```

---

## 11. Knowledge Vector Search

Created:

```text
backend/app/database/knowledge_vector_search.py
```

The search uses:

- The same embedding model.
- The same 384-dimensional vector configuration.
- pgvector cosine-distance retrieval.
- `knowledge_chunk_embeddings` joined to `knowledge_chunks`.

This keeps product and knowledge semantic retrieval technically consistent while maintaining separate retrieval paths.

---

## 12. Persistent Knowledge Semantic Search Test

Query:

```text
How long does delivery take?
```

Returned rankings:

```text
Delivery          0.8165
Payment           0.2330
Shipping Charges  0.1935
How to Order      0.1853
Returns           0.0961
```

The Delivery chunk was the clear top result.

This demonstrated that semantic retrieval is working persistently against the business knowledge base.

---

## 13. Idempotency Verification

Embedding imports are designed to be safely rerunnable.

A duplicate check was performed for:

```text
knowledge_chunk_embeddings
```

Result:

```text
(0 rows)
```

This confirmed that rerunning the importer did not create duplicate records for the same source/model/version combination.

---

## 14. Code Organization and Cleanup

Three important cleanup areas were completed.

### Centralized embedding configuration

Created:

```text
backend/app/database/embedding_config.py
```

Model name, application version, and dimensions now have a single configuration source.

### Separate knowledge repository

Created:

```text
backend/app/database/knowledge_embedding_repository.py
```

Knowledge persistence is separated from importer orchestration, matching the product repository pattern.

### Deprecated dimension method removed

The deprecated Sentence Transformers dimension method:

```text
get_sentence_embedding_dimension()
```

was removed from the implementation.

The configured embedding dimension is now obtained from the centralized application configuration.

Product and knowledge embedding workflows were rerun successfully after cleanup.

---

## 15. Final Data Integrity Check

Final database counts:

```text
products                  9
product_embeddings        9
knowledge_chunks          5
knowledge_embeddings      5
```

Therefore:

```text
9 / 9 products have embeddings
5 / 5 knowledge chunks have embeddings
```

No source records were missing their corresponding embeddings.

---

## 16. Manual Verification Approach

Day 6 used small executable verification scripts to inspect each logical stage.

Verified:

- pgvector extension works.
- Embedding model loads.
- Product embeddings have 384 dimensions.
- Product vectors persist correctly.
- All 9 products receive embeddings.
- Knowledge embedding text is generated correctly.
- All 5 knowledge chunks receive embeddings.
- Product semantic search returns ranked results.
- Knowledge semantic search returns ranked results.
- Repeated imports do not create duplicates.
- Final source/embedding counts match.

These scripts are appropriate for the foundation stage.

As the application becomes more production-oriented, they should gradually evolve into proper pytest tests with assertions and fixtures.

---

## 17. Deliberately Deferred

The following were intentionally not implemented on Day 6:

- Approximate vector indexes
- Production-scale batch optimization
- Persistent hybrid ranking
- Reranking model
- Query understanding
- Query routing
- LLM response generation
- Complete end-to-end RAG
- Multimodal retrieval

### Why no vector index yet?

The current dataset is only:

```text
9 products
5 knowledge chunks
```

Exact pgvector retrieval is sufficient at this scale. Approximate nearest-neighbor indexes can be introduced when catalogue/knowledge volume justifies the additional complexity.

### Why no full hybrid retrieval yet?

Day 6's purpose is to establish reliable persistent semantic retrieval.

Hybrid retrieval belongs to the next stage and should build on, rather than replace, the working SQL, metadata, Full-Text, and vector layers.

---

## 18. Known Technical Debt / Planned Enhancements

### Product embedding attributes

Production embedding text should eventually incorporate:

- Occasion
- Style
- Mood
- Tags

from normalized PostgreSQL tables.

### Multiple embedding dimensions

The current schema is intentionally:

```text
VECTOR(384)
```

Future support for different models/dimensions requires a deliberate schema and indexing strategy.

### Larger-scale embedding generation

For a much larger catalogue, embedding generation should use batched Sentence Transformer inference rather than processing records individually.

### Automated tests

Manual scripts should gradually be replaced or supplemented with pytest-based automated tests.

---

## 19. Files Added or Refined

The Day 6 database layer includes:

```text
backend/app/database/
├── connection.py
├── embedding_config.py
├── embedding_generator.py
├── embedding_repository.py
├── embedding_text.py
├── import_product_embeddings.py
├── knowledge_embedding_repository.py
├── knowledge_embedding_text.py
├── import_knowledge_embeddings.py
├── vector_search.py
└── knowledge_vector_search.py
```

Database schema:

```text
database/schema/015_create_embedding_tables.sql
```

---

## 20. Day 6 Completion Checklist

- [x] PostgreSQL 18.6 verified
- [x] Correct PostgreSQL installation selected
- [x] Windows C++ build tooling prepared
- [x] pgvector 0.8.6 built
- [x] pgvector installed
- [x] `vector` extension enabled
- [x] Product embedding table created
- [x] Knowledge embedding table created
- [x] Model/version/dimension tracking added
- [x] Product embedding text builder created
- [x] Knowledge embedding text builder created
- [x] Local embedding generation verified
- [x] Product embedding persistence verified
- [x] 9/9 product embeddings imported
- [x] Product vector search verified
- [x] Knowledge embedding persistence verified
- [x] 5/5 knowledge embeddings imported
- [x] Knowledge vector search verified
- [x] Availability hard filter enforced in product vector search
- [x] Idempotency verified
- [x] Embedding configuration centralized
- [x] Knowledge persistence separated into a repository
- [x] Deprecated dimension method removed
- [x] Final data-integrity counts verified

---

## Day 6 Outcome

Day 6 converted semantic search from an in-memory experiment into a persistent retrieval capability:

```text
Structured Products
        +
Structured Knowledge
        ↓
Embedding Text
        ↓
Sentence Transformers
all-MiniLM-L6-v2
        ↓
384-dimensional normalized vectors
        ↓
PostgreSQL + pgvector
        ↓
+----------------------------+
| Product Vector Search      |
| Knowledge Vector Search    |
+----------------------------+
```

Urban Aanchol now has:

```text
SQL retrieval
+
Metadata retrieval
+
Full-Text Search
+
Persistent semantic/vector retrieval
```

The architecture remains vendor-independent and preserves the separation between authoritative structured facts and semantic ranking.

### Next: Day 7 — Hybrid Retrieval + Reranking

Day 7 builds on the combined Day 5 + Day 6 foundation:

```text
User Query
    ↓
Query Understanding
    ↓
SQL / Metadata / Full-Text
        +
Semantic / Vector Retrieval
    ↓
Candidate Set
    ↓
Hybrid Ranking / Reranking
    ↓
Grounded Retrieval
```

The key goal is to combine the strengths of lexical, structured, and semantic retrieval while enforcing hard business constraints.
