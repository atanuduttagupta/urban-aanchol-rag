# Day 5 — Database Design & Retrieval Foundation

## Objective

Establish the PostgreSQL data model and initial retrieval foundation for the Urban Aanchol website and future RAG chatbot.

Day 5 connects the validated catalogue to a structured application store and experimentally validates multiple retrieval mechanisms before persistent vector storage is introduced.

---

## 1. Data Architecture

The project maintains clear boundaries between:

```text
Excel
  = human-friendly catalogue source

PostgreSQL
  = structured application/runtime store

Vector layer
  = semantic retrieval

Knowledge store
  = RAG documents and chunks

Graph layer
  = relationship-aware retrieval

Media store
  = images/videos and their relationships
```

The overall retrieval direction is:

```text
User Query
    ↓
Query Understanding
    ↓
Query Router
    ├── SQL / Metadata
    ├── Full-Text
    ├── Semantic
    ├── Knowledge RAG
    └── Graph when useful
              ↓
       Hybrid Retrieval
              ↓
          Reranking
              ↓
       Grounded LLM Answer
```

---

## 2. PostgreSQL Product Model

PostgreSQL is the structured application/runtime store.

The core `products` model contains:

```text
product_id
product_name
category
brand
collection
fabric
colour
secondary_colour
pattern
border
price
availability
description
product_url
remarks
additional_attributes
launch_date
created_at
updated_at
```

One product row represents one sellable product.

The model remains generalized across:

```text
Saree
Blouse
Dupatta
Jewelry
Accessories
Other
```

Frequently queried/business-critical facts remain structured PostgreSQL fields.

Examples include:

- Category
- Fabric
- Colour
- Brand
- Collection
- Price
- Availability

For evolving or rare category-specific attributes, the flexible escape hatch is:

```text
additional_attributes JSONB
```

An attribute can later be promoted to a structured field/table when it becomes a frequent filter or recommendation signal.

---

## 3. Normalized Product Attributes

Created relational tables for:

```text
product_occasions
product_styles
product_moods
product_tags
```

Excel can remain business-friendly with comma-separated values, while PostgreSQL stores the values relationally for reliable filtering, joins, and retrieval.

Tags are treated as discovery labels and do not replace authoritative product facts such as:

- Price
- Availability
- Fabric

---

## 4. Media Architecture

Created:

```text
media_assets
product_media
```

This separates media from the product record and supports:

- Multiple images
- Multiple videos
- Standalone media
- Future thumbnails/metadata
- Media relationships

V1 Excel remains simple with:

```text
image_url
video_url
```

During import, these can be transformed into the scalable media model.

Standalone videos are supported because future content may include:

- Product showcases
- Styling/draping tutorials
- Care tutorials
- Collection announcements
- Behind-the-scenes content

---

## 5. Knowledge and Graph Foundation

Created the knowledge model:

```text
knowledge_documents
knowledge_chunks
knowledge_entities
knowledge_entity_relations
knowledge_document_entities
knowledge_chunk_entities
```

Knowledge documents are deliberately not forced to contain a direct `product_id`.

A document may apply to:

- The boutique generally
- A fabric
- An occasion
- A category
- Many products
- One product

This allows the knowledge base to support both general educational content and product-related knowledge.

### Order & Policies knowledge

The **Urban Aanchol Order & Policies** document was loaded with five chunks:

1. How to Order
2. Delivery
3. Payment
4. Shipping Charges
5. Returns

Five policy-topic entities were created and linked:

```text
ordering
delivery
payment
shipping
returns
```

Representative graph relationships and traversal were verified successfully.

GraphRAG is treated as a first-class future capability. At the current scale, PostgreSQL relationships and recursive SQL are sufficient; a dedicated graph database can be introduced later behind an abstraction if justified.

---

## 6. Product Facts vs Knowledge

The architecture separates authoritative product facts from explanatory knowledge.

Examples:

```text
Price / Availability
        ↓
Structured product data

Care / Fabric education / Policies
        ↓
Knowledge documents and chunks
```

Transactional or live product facts should not be reconstructed from embeddings or generated prose.

Future transactional state should come from live structured/transactional data.

---

## 7. Database Connectivity and Import

PostgreSQL connectivity was added using `psycopg`.

The validated dummy Excel catalogue was imported into PostgreSQL.

Import results:

```text
Products:       9
Occasions:     18
Styles:        18
Moods:         18
Tags:          44
Images:         9
Videos:         9
Media links:   18
```

The import establishes the first operational database representation of the validated catalogue.

---

## 8. Structured SQL Retrieval

SQL was tested for explicit business constraints.

Example query:

> Available sarees under ₹3,000

Result:

```text
6 products
```

This demonstrated deterministic filtering by:

- Category
- Availability
- Price

SQL is therefore the appropriate mechanism for authoritative structured constraints.

---

## 9. Metadata Retrieval

Structured metadata was tested across related product attributes.

Example:

> Traditional sarees suitable for Office Wear

Result:

```text
UA-0001 — White & Grey Handloom Saree — ₹2,450
```

This demonstrated filtering/joining across product, style, and occasion data.

Metadata retrieval is a retrieval strategy; SQL is the database mechanism used to execute the structured filtering.

---

## 10. PostgreSQL Full-Text Search

PostgreSQL native Full-Text Search was validated rather than introducing a separate search engine at boutique scale.

Query:

```text
handloom saree
```

Returned:

```text
UA-0001
UA-0003
UA-0005
```

Full-Text Search is useful when customer wording overlaps with catalogue terminology.

The project will optimize stored/generated search vectors and additional indexes later when scale or performance requires them.

---

## 11. SQL + Full-Text Retrieval

A combined deterministic retrieval experiment was performed.

Query:

> Available handloom sarees under ₹3,000

Result:

```text
UA-0001
UA-0005
UA-0003
```

This demonstrated an early hybrid pattern where structured business constraints and textual matching work together.

---

## 12. Local Semantic Embeddings

The initial embedding approach uses local Sentence Transformers.

Selected model:

```text
sentence-transformers/all-MiniLM-L6-v2
```

Dimensions:

```text
384
```

The model was successfully loaded and a 384-dimensional embedding was generated locally.

This avoids per-query embedding API cost and keeps the initial implementation open-source and portable.

A replaceable embedding interface is planned so the model can be changed later without rewriting retrieval logic.

---

## 13. Semantic Retrieval Experiment

Query:

```text
Something elegant for a family function
```

Semantic retrieval ranked:

```text
UA-0005 — Beige & Red Handloom Saree
```

first.

This demonstrated that semantic similarity can recover relevance from natural-language intent even when exact catalogue wording may differ.

---

## 14. Keyword vs Semantic Comparison

Query:

```text
Something graceful to wear to Puja
```

Full-Text Search returned no keyword matches, while semantic retrieval returned meaningful candidates.

This demonstrated that keyword and semantic retrieval are complementary:

```text
Keyword / Full-Text
    ↓
Strong when wording overlaps

Semantic
    ↓
Useful when wording differs
```

Neither mechanism should be treated as sufficient by itself.

---

## 15. Hard Constraints Before Semantic Ranking

An important Day 5 finding was that semantic similarity is **not** the eligibility mechanism.

Unrestricted semantic retrieval can return a semantically related but inappropriate product category.

Therefore the intended retrieval contract is:

```text
Customer Query
      ↓
Hard Business Constraints
      ↓
Eligible Candidates
      ↓
Semantic Ranking
      ↓
Reranking
```

Hard constraints may include:

- Availability
- Category
- Explicit budget
- Other explicit eligibility requirements

Semantic similarity should rank eligible candidates; it must not override explicit business constraints.

---

## 16. Retrieval Strategy

The project will eventually combine the retrieval mechanisms according to the signal being requested:

```text
SQL / Metadata
    → authoritative structured constraints

Full-Text
    → exact/lexical catalogue wording

Semantic
    → meaning-based similarity

Knowledge RAG
    → educational/policy information

Graph
    → relationship-aware retrieval
```

A future query router can select one or more paths and combine their results.

Product search/similarity and knowledge RAG are related but distinct retrieval paths.

---

## 17. Product Similarity Direction

Future product similarity can combine multiple signals:

```text
Structured attributes
        +
Semantic text similarity
        +
Graph relationships
        +
Image similarity
        ↓
Reranking
```

This provides a foundation for later multimodal product discovery.

---

## 18. Practical Retrieval Principles

Day 5 tested the schema and retrieval design against practical customer needs such as:

- Product discovery
- Budget filtering
- Occasion
- Comparison
- Care
- Delivery
- Payment
- Returns
- Future post-purchase questions

No additional mandatory product columns were required as a result of these checks.

Complaint handling is conceptually separated into:

```text
Information retrieval
        +
Policy retrieval
        +
Authorized transaction workflow
```

The future system should not diagnose causes or promise refunds/replacements without supporting policy and authorized transaction workflows.

---

## 19. Deliberately Deferred

The following were intentionally left for the next stage:

- pgvector storage
- Vector indexes
- Persistent product embeddings
- Persistent knowledge embeddings
- Production hybrid ranking
- Reranking model
- Query understanding
- Query routing
- LLM response generation
- Complete end-to-end RAG

Day 5 ends after validating SQL, metadata, Full-Text Search, local semantic embeddings, and hard-filtered semantic ranking.

---

## 20. Day 5 Completion Checklist

- [x] PostgreSQL logical data model defined
- [x] Excel → PostgreSQL product import completed
- [x] Normalized product attributes created
- [x] Media relationships created
- [x] Knowledge document/chunk model created
- [x] Graph entity/relation foundation created
- [x] Order & Policies knowledge loaded
- [x] Representative graph traversal verified
- [x] SQL retrieval tested
- [x] Metadata retrieval tested
- [x] PostgreSQL Full-Text Search tested
- [x] SQL + Full-Text retrieval tested
- [x] Local Sentence Transformer embeddings verified
- [x] Semantic similarity tested
- [x] Keyword vs semantic behavior compared
- [x] Hard-filter + semantic ranking validated
- [x] Vendor-independent retrieval direction established

---

## Day 5 Outcome

Day 5 established the structured database and retrieval foundation:

```text
Excel
  ↓
Validation
  ↓
PostgreSQL
  ├── SQL
  ├── Metadata
  ├── Full Text
  ├── Knowledge
  └── Graph
        ↓
Local Semantic Embeddings
        ↓
Future Vector Search
        ↓
Hybrid Retrieval + Reranking
        ↓
Grounded RAG / Recommendation
```

The central architectural principle established on Day 5 is:

> **Use the right retrieval mechanism for the right signal, then combine them under explicit business constraints.**

**Next: Day 6 — Persistent Vector Storage & Retrieval**

The next stage introduces pgvector, persistent product/knowledge embeddings, and the vector retrieval layer.
