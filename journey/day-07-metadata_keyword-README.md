# Day 7 — Retrieval Foundation

## 1. Objective

Establish a clean, vendor-independent product retrieval foundation for the Urban Aanchol RAG system.

Day 7 introduced three independent retrieval strategies behind a common application contract:

1. Metadata / structured retrieval
2. Keyword / PostgreSQL Full-Text Search (FTS)
3. Semantic / vector retrieval

The goal was to make each strategy independently testable and ready to be combined into Hybrid Retrieval in the next phase.

## 2. Retrieval Contract

Created under `backend/app/retrieval/`.

### RetrievalRequest
Represents a retrieval request with:
- `query`
- `limit`
- optional structured `filters`

### ProductResult
Common product result representation:
- `product_id`
- `product_name`
- `category`
- `price`
- `availability`
- `score`
- `retrieval_method`

### Retriever Interfaces
Protocol-based product and knowledge retriever interfaces keep consuming application logic independent of the retrieval implementation.

## 3. Metadata / Structured Retrieval

Implemented: `backend/app/retrieval/metadata_retriever.py`

Metadata retrieval uses structured catalogue information and direct SQL queries.

Supported direct filters:
- Category
- Brand
- Collection
- Fabric
- Colour
- Secondary colour
- Pattern
- Border
- Availability
- Minimum price
- Maximum price

Normalized attributes are stored in:
- `product_occasions`
- `product_styles`
- `product_moods`
- `product_tags`

These are retrieved using SQL `EXISTS` conditions.

**Key distinction:** Metadata retrieval is the retrieval strategy; SQL is the mechanism used to implement it.

## 4. Keyword / Full-Text Retrieval

Implemented: `backend/app/retrieval/keyword_retriever.py`

PostgreSQL native Full-Text Search was added to the product catalogue.

Migration:
`database/schema/017_product_full_text_search.sql`

The migration adds:
- `products.search_vector` (`tsvector`)
- trigger-based automatic maintenance of `search_vector`
- GIN index `idx_products_search_vector`

Searchable product content:
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

Price, availability, dates and URLs remain structured/application data rather than FTS content.

The implementation uses PostgreSQL:
- `to_tsvector`
- `websearch_to_tsquery`
- `ts_rank`
- GIN indexing

The `simple` text-search configuration is used for catalogue terminology.

**Key distinction:** Full-Text Search is a native database text-retrieval technique. It is separate from semantic/vector search and does not require an embedding model.

## 5. Semantic / Vector Retrieval

Implemented: `backend/app/retrieval/semantic_retriever.py`

Pipeline:

`User query → Sentence Transformer embedding → pgvector similarity search → ProductResult`

Reuses the Day 6 embedding foundation:
- Model: `sentence-transformers/all-MiniLM-L6-v2`
- Dimensions: 384
- PostgreSQL extension: pgvector
- Normalized embeddings
- Centralized model configuration

Existing `EmbeddingGenerator` and `search_similar_products()` are reused rather than duplicated.

## 6. Validation Results

### Metadata
Structured test:
- Category = Saree
- Fabric = Cotton
- Maximum price = ₹3,000
- Availability = Available

Returned five matching products from the nine-product catalogue.

A second test:
- Category = Saree
- Occasion = Office Wear
- Maximum price = ₹3,000
- Availability = Available

returned `UA-0001 — White & Grey Handloom Saree`.

### Keyword / FTS
Query: `handloom saree`

Returned:
1. `UA-0003 — Navy Blue Handloom Saree`
2. `UA-0001 — White & Grey Handloom Saree`
3. `UA-0005 — Beige & Red Handloom Saree`

With Category = Saree, Maximum price = ₹2,800 and Availability = Available, the query returned:
1. `UA-0001 — White & Grey Handloom Saree`
2. `UA-0005 — Beige & Red Handloom Saree`

A broader test adding Fabric = Cotton and Occasion = Office Wear returned only:
`UA-0001 — White & Grey Handloom Saree`.

### Semantic
Query: `Something elegant for a family function`

Returned:
1. `UA-0005 — Beige & Red Handloom Saree`
2. `UA-0008 — Sky Blue Cotton Blouse`
3. `UA-0004 — Purple Striped Saree`

This successfully validated vector retrieval and also demonstrated that semantic similarity alone does not enforce business/catalogue constraints.

### Common contract
All three retrievers returned `ProductResult` objects with retrieval methods:
- `metadata`
- `keyword`
- `semantic`

## 7. Key Architectural Findings

### Metadata ≠ SQL
Metadata represents structured business/catalogue information. SQL is the database query mechanism used to retrieve it.

### FTS ≠ Semantic Search
FTS matches indexed textual terms and phrases. Semantic retrieval searches vector representations of meaning.

### Semantic similarity is a relevance signal, not a hard constraint
A semantically similar result can still violate requirements such as category, availability or price. Hard catalogue/business constraints must be handled explicitly.

### Retrieval scores are not directly interchangeable
FTS `ts_rank` and vector similarity measure different things. Their raw scores should not be compared directly. Hybrid retrieval will require an explicit combination strategy.

## 8. Retrieval Architecture

```text
                         USER QUERY
                             |
                    Query Understanding
                             |
          +------------------+------------------+
          |                  |                  |
          v                  v                  v
      METADATA            KEYWORD            SEMANTIC
       / SQL                FTS               VECTOR
          |                  |                  |
          +------------------+------------------+
                             |
                       HYBRID RETRIEVAL
                             |
                         RERANKING
                             |
                         RAG / AGENT
```

Day 7 establishes the three retrieval foundations. Hybrid retrieval and reranking are intentionally deferred.

## 9. Environment Issue — ISSUE-005

A Windows Application Control policy blocked the native scikit-learn 1.9.1 extension:

`_radius_neighbors.cp311-win_amd64.pyd`

Reinstalling the same version did not resolve the problem.

The project was tested successfully with:
`scikit-learn==1.7.2`

Validation confirmed:
- scikit-learn import works
- `sklearn.metrics` import works
- sentence-transformers import works
- embedding generation works
- PostgreSQL + pgvector semantic search works

The project therefore pins `scikit-learn==1.7.2`.

No further Windows investigation is required for this project.

## 10. Day 7 Outcome

Urban Aanchol now has three independently implemented and validated product retrieval strategies:

```text
Metadata / SQL              ✅
Keyword / PostgreSQL FTS    ✅
Semantic / pgvector         ✅
```

All three use a common retrieval contract and are ready for the next architectural layer.

**Next milestone: Hybrid Retrieval**

The next stage will determine how metadata constraints, keyword relevance and semantic similarity are combined to produce reliable product candidates before reranking and RAG generation.
