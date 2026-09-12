# Urban Aanchol RAG — Day 5
## Database Design & Retrieval Foundation

Day 5 established the database and retrieval foundation for the Urban Aanchol website and future RAG chatbot.

## Objectives completed

- PostgreSQL logical data model
- Excel → PostgreSQL product import
- normalized product attributes
- scalable image/video media relationships
- knowledge documents and chunks
- GraphRAG relationship foundation
- SQL and metadata retrieval
- PostgreSQL Full-Text Search
- SQL + Full-Text retrieval
- local semantic embeddings
- semantic similarity experiments
- keyword vs semantic comparison
- hard business constraints before semantic ranking

## Architecture

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

### Data boundaries

```text
Excel           = human-friendly catalogue source
PostgreSQL      = structured application/runtime store
Vector layer    = semantic retrieval
Knowledge store = RAG documents/chunks
Graph layer     = relationship-aware retrieval
Media store     = images/videos + relationships
```

## Product model

Core `products` fields:

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

Categories remain generalized:

`Saree, Blouse, Dupatta, Jewelry, Accessories, Other`

One row represents one sellable product.

Frequently filtered/business-critical values remain structured. `additional_attributes` JSONB is the flexible escape hatch for evolving or rare attributes.

## Normalized attributes

Created:

```text
product_occasions
product_styles
product_moods
product_tags
```

Excel may remain comma-separated; PostgreSQL stores these relationally for reliable filtering and joins.

Tags are discovery labels, not replacements for authoritative facts.

## Media architecture

Created:

```text
media_assets
product_media
```

This supports multiple images/videos, standalone videos, future thumbnails/metadata, and relationships between media and products.

V1 Excel keeps `image_url` and `video_url` for simplicity.

Future videos can include product showcases, styling/draping, care tutorials, collection announcements, and behind-the-scenes content.

## Knowledge and GraphRAG foundation

Created:

```text
knowledge_documents
knowledge_chunks
knowledge_entities
knowledge_entity_relations
knowledge_document_entities
knowledge_chunk_entities
```

Knowledge documents are intentionally not forced to contain `product_id`; a document may be global, fabric-related, occasion-related, category-related, or product-specific.

The **Urban Aanchol Order & Policies** document was loaded with five chunks:

1. How to Order
2. Delivery
3. Payment
4. Shipping Charges
5. Returns

Five policy-topic entities were linked:

`ordering, delivery, payment, shipping, returns`

Representative graph relationships and traversal were tested successfully.

## Import results

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

## Retrieval experiments

### SQL retrieval

Tested:

> Available sarees under ₹3,000

Result: **6 products**

Validated exact filtering by category, availability, and price.

### Metadata retrieval

Tested:

> Traditional sarees suitable for Office Wear

Result:

`UA-0001 — White & Grey Handloom Saree — ₹2,450`

Validated joins across products, styles and occasions.

### PostgreSQL Full-Text Search

Tested:

`handloom saree`

Result:

`UA-0001, UA-0003, UA-0005`

### SQL + Full-Text

Tested:

> Available handloom sarees under ₹3,000

Result:

`UA-0001, UA-0005, UA-0003`

This demonstrated deterministic hybrid retrieval.

## Semantic retrieval

Selected and verified:

```text
Framework: sentence-transformers
Model: all-MiniLM-L6-v2
Dimensions: 384
```

The model successfully generated embeddings locally.

### Semantic experiment

Query:

`Something elegant for a family function`

`UA-0005 — Beige & Red Handloom Saree` ranked first.

### Keyword vs semantic experiment

Query:

`Something graceful to wear to Puja`

Full-Text Search returned no keyword matches, while semantic search returned meaningful candidates.

This demonstrated that keyword and semantic retrieval are complementary.

## Retrieval contract

Semantic similarity is **not** the eligibility mechanism.

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

Examples of hard constraints include availability, category, explicit budget, and other explicit eligibility requirements.

This prevents a semantically similar but unsuitable product from being presented as eligible.

## Day 5 outcome

Day 5 established:

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
```

**Day 5 is complete.**

The next major stage is persistent vector storage/retrieval with pgvector, embedding persistence, and the product/knowledge vector strategy.
