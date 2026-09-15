# Urban Aanchol — Day 6: Persistent Semantic Retrieval

## Objective

Day 6 converted the semantic-search proof of concept from an in-memory experiment into a persistent PostgreSQL + pgvector retrieval foundation.

The goal was to support two semantic retrieval paths:

1. Product semantic retrieval for natural-language product discovery.
2. Knowledge semantic retrieval for boutique policies and other RAG knowledge.

The implementation was deliberately built incrementally: infrastructure first, one-product verification, batch persistence, then retrieval tests and code cleanup.

---

## Starting Point

At the end of Day 5, Urban Aanchol already had:

- A validated and normalized Excel product catalogue.
- PostgreSQL product and knowledge tables.
- Product metadata tables for occasion, style, mood, and tags.
- Media and product-media relationships.
- Knowledge documents and chunks.
- SQL and full-text retrieval experiments.
- An in-memory Sentence Transformers semantic-search experiment.

Day 6 made semantic retrieval persistent.

---

## Day 6 Architecture

```text
                         Urban Aanchol
                              |
             +----------------+----------------+
             |                                 |
          Products                       Knowledge Chunks
             |                                 |
     embedding text builder          section + chunk builder
             |                                 |
             +---------------+-----------------+
                             |
                    Sentence Transformers
                    all-MiniLM-L6-v2
                             |
                       384 dimensions
                             |
                         pgvector
                    PostgreSQL 18.6
                             |
              +--------------+--------------+
              |                             |
    product_embeddings          knowledge_chunk_embeddings
              |                             |
      Product vector search        Knowledge vector search
```

The product and knowledge source data remain separate from their embedding records.

---

## Infrastructure Completed

### PostgreSQL

The local database was verified as:

- PostgreSQL 18.6
- Database: `urban_aanchol`

### pgvector

The standard package was not available through the existing Windows PostgreSQL installation, so pgvector was built locally from source.

Completed steps:

1. Confirmed the PostgreSQL 18 `pg_config.exe` location.
2. Installed Visual Studio Community 2026 with the required Desktop development with C++ workload.
3. Verified `cl` and `nmake` using the x64 Native Tools Command Prompt.
4. Cloned pgvector release `v0.8.6`.
5. Built it with `nmake /F Makefile.win`.
6. Installed it with `nmake /F Makefile.win install`.
7. Enabled the PostgreSQL extension with `CREATE EXTENSION vector;`.
8. Verified pgvector version `0.8.6`.

This established PostgreSQL 18.6 + pgvector 0.8.6 locally.

---

## Embedding Storage Design

A separate embedding-table approach was selected instead of adding embedding columns directly to product or knowledge tables.

### Product embeddings

`product_embeddings` stores:

- `embedding_id`
- `product_id`
- `model_name`
- `model_version`
- `dimensions`
- `embedding VECTOR(384)`
- timestamps

It has a foreign key to `products` and a unique constraint on:

```text
(product_id, model_name, model_version)
```

### Knowledge embeddings

`knowledge_chunk_embeddings` stores:

- `embedding_id`
- `chunk_id`
- `model_name`
- `model_version`
- `dimensions`
- `embedding VECTOR(384)`
- timestamps

It has a foreign key to `knowledge_chunks` and a unique constraint on:

```text
(chunk_id, model_name, model_version)
```

The separation allows future model/version experiments without changing the core product and knowledge source records.

The current schema is intentionally dimension-specific (`VECTOR(384)`) because the Day 6 implementation uses `all-MiniLM-L6-v2`.

---

## Embedding Configuration

Embedding configuration was centralized in:

```text
backend/app/database/embedding_config.py
```

Current configuration:

```text
MODEL_NAME = sentence-transformers/all-MiniLM-L6-v2
MODEL_VERSION = v1
EMBEDDING_DIMENSIONS = 384
```

`v1` is an application-level version label for this embedding configuration; it is not a claim about an upstream model version.

This avoids repeating model and dimension settings across multiple files.

---

## Product Embedding Text

Product embedding text is generated from semantic product characteristics.

Included in the current V1 builder:

- Product name
- Category
- Brand
- Collection
- Fabric
- Colour
- Secondary colour
- Pattern
- Border
- Description
- Remarks

The following are deliberately not embedded:

- Internal product ID
- Price
- Availability
- Timestamps

Price and availability are structured business facts and should be handled by SQL/metadata filters rather than semantic similarity.

The current builder does not yet include the normalized occasion, style, mood, and tag tables. That is a planned production-pipeline enhancement.

---

## Knowledge Embedding Text

Knowledge embedding text combines:

```text
Section title
+
Chunk text
```

Example:

```text
Section: Delivery

Delivery normally takes 5 to 7 working days after order confirmation.
```

Database IDs and timestamps are excluded because they do not provide semantic meaning.

---

## Embedding Generation

The project uses:

```text
sentence-transformers/all-MiniLM-L6-v2
```

The model was loaded successfully and produced 384-dimensional embeddings.

Embeddings are generated with normalized output:

```python
normalize_embeddings=True
```

This supports the cosine-distance based pgvector retrieval used in Day 6.

---

## Product Embedding Pipeline

The product pipeline became:

```text
Excel catalogue
      |
validation
      |
normalization
      |
product records
      |
embedding text
      |
Sentence Transformer
      |
384-dimensional vector
      |
product_embeddings
```

A one-product test was performed first using `UA-0001`.

The generated embedding was verified as:

```text
Dimensions: 384
Embedding length: 384
```

It was then persisted to PostgreSQL and verified with `vector_dims()`.

After that, all 9 products were batch processed.

Final product embedding count:

```text
Products:             9
Product embeddings:   9
```

---

## Knowledge Embedding Pipeline

The knowledge pipeline became:

```text
knowledge_chunks
      |
section + chunk text
      |
Sentence Transformer
      |
384-dimensional vector
      |
knowledge_chunk_embeddings
```

The existing Order & Policies document contained 5 chunks:

- How to Order
- Delivery
- Payment
- Shipping Charges
- Returns

All 5 were embedded and persisted.

Final knowledge embedding count:

```text
Knowledge chunks:        5
Knowledge embeddings:    5
```

---

## Idempotent Persistence

Both product and knowledge embedding persistence uses:

```sql
ON CONFLICT (...)
DO UPDATE
```

This prevents duplicate records when an embedding importer is rerun for the same model/version.

The uniqueness boundaries are:

```text
product_id + model_name + model_version
```

and

```text
chunk_id + model_name + model_version
```

A duplicate-check query was run for knowledge embeddings and returned:

```text
(0 rows)
```

This confirms that rerunning the importer did not create duplicate knowledge embedding records.

---

## Product Semantic Retrieval Test

A natural-language query was tested:

> Something elegant for a family function

PostgreSQL + pgvector ranked the persisted product embeddings.

Top results included:

```text
1. UA-0005 | Beige & Red Handloom Saree | similarity=0.1189
2. UA-0008 | Sky Blue Cotton Blouse     | similarity=0.0927
3. UA-0004 | Purple Striped Saree       | similarity=0.0750
4. UA-0006 | Red & White Saree           | similarity=0.0731
5. UA-0003 | Navy Blue Handloom Saree    | similarity=0.0718
```

The result also demonstrated an important architectural lesson: semantic similarity alone can return a semantically related but category-inappropriate product, such as a blouse for a query that implicitly seeks a saree.

Therefore semantic retrieval must not be the sole decision mechanism.

The planned production approach is:

```text
query understanding
+
SQL/metadata filters
+
keyword/full-text
+
semantic retrieval
+
reranking
```

---

## Knowledge Semantic Retrieval Test

A natural-language business question was tested:

> How long does delivery take?

The persisted knowledge embeddings returned:

```text
1. Delivery         similarity=0.8165
2. Payment          similarity=0.2330
3. Shipping Charges similarity=0.1935
4. How to Order     similarity=0.1853
5. Returns          similarity=0.0961
```

The Delivery chunk was the clear top result and contained the relevant business fact:

```text
Delivery normally takes 5 to 7 working days after order confirmation.
```

This verified persistent semantic retrieval against the knowledge base.

---

## Availability Guardrail

Product vector search already filters for:

```sql
p.availability = 'Available'
```

This is intentional.

Semantic similarity should rank eligible candidates, but it must not cause Sold, Reserved, or Inactive products to be presented as available recommendations.

---

## Code Organization

Day 6 introduced or refined these areas:

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

The repositories keep database persistence separate from embedding generation and import orchestration.

---

## Testing and Verification

Manual verification scripts were used during Day 6 to validate each logical step.

Verified:

- Embedding model loads.
- Product embedding has 384 dimensions.
- Product vector is persisted.
- PostgreSQL reports stored vector dimension as 384.
- All 9 products receive embeddings.
- Knowledge text builder works.
- All 5 knowledge chunks receive embeddings.
- Product semantic search returns ranked products.
- Knowledge semantic search returns ranked chunks.
- Rerunning knowledge embedding import does not create duplicates.
- Final data-integrity counts are:

```text
products                  9
product_embeddings        9
knowledge_chunks          5
knowledge_embeddings      5
```

---

## Known Limitations / Future Work

These are deliberately not treated as Day 6 blockers.

### 1. Product embedding attributes

The production embedding text should eventually incorporate:

- occasion
- style
- mood
- tags

from the normalized PostgreSQL tables.

### 2. Batch inference optimization

The current importer generates embeddings product-by-product. For a larger catalogue, Sentence Transformers should be used with batched input.

### 3. Automated pytest assertions

The current scripts are useful verification scripts. They should gradually become proper automated tests with assertions and fixtures.

### 4. Multiple embedding dimensions

The current schema uses `VECTOR(384)`. Future support for different embedding dimensions/models should be designed without changing core product or knowledge source tables.

### 5. Vector indexes

The dataset is currently tiny. Approximate nearest-neighbor pgvector indexing should be introduced when the catalogue/knowledge volume justifies it.

### 6. Hybrid retrieval

Day 6 deliberately stops at persistent semantic retrieval. Day 7 will combine semantic search with existing SQL/full-text/metadata retrieval and introduce reranking.

---

## Day 6 Outcome

Day 6 successfully established a persistent semantic retrieval foundation.

Urban Aanchol now has:

```text
Structured product data
        +
Structured knowledge data
        +
Persistent 384-dim embeddings
        +
PostgreSQL + pgvector
        +
Product semantic retrieval
        +
Knowledge semantic retrieval
```

This is the foundation for the next retrieval layer.

### Next phase

**Day 7 — Hybrid Retrieval + Reranking**

Planned direction:

```text
User query
    ↓
Query understanding
    ↓
SQL / metadata / full-text
    +
Semantic/vector retrieval
    ↓
Candidate set
    ↓
Reranking
    ↓
Better grounded retrieval
```

Day 7 should build on the working Day 5 SQL/full-text foundation and Day 6 persistent vector foundation rather than replacing either.
