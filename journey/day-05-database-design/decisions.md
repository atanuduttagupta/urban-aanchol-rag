# Urban Aanchol RAG — Day 5 Decisions
## Database Design & Retrieval Foundation

### D01 — Excel remains the human-friendly catalogue source
Excel remains the source maintained by the boutique; PostgreSQL is the application-facing runtime store.

### D02 — PostgreSQL is the structured application store
PostgreSQL provides SQL, joins, filtering, knowledge storage, graph relationships and future pgvector support.

### D03 — One product row represents one sellable product
This provides stable product identity for search, media, recommendations and future orders.

### D04 — Keep the product model generalized
Categories remain `Saree, Blouse, Dupatta, Jewelry, Accessories, Other`.

### D05 — Frequently queried facts remain structured
Category, fabric, colour, brand, collection, price and availability remain normal PostgreSQL fields.

### D06 — JSONB is the flexible escape hatch
`additional_attributes` supports evolving/rare attributes. Promote an attribute to a structured field/table when it becomes a frequent filter or recommendation signal.

### D07 — Normalize multi-value attributes
Occasions, styles, moods and tags use separate PostgreSQL relation tables while Excel can remain comma-separated.

### D08 — Tags are discovery labels
Tags must not replace authoritative facts such as price, availability or fabric.

### D09 — Media is separate from products
Use `media_assets` and `product_media` instead of permanently adding multiple media columns.

### D10 — Support standalone videos
Media need not belong to a product because future videos can be tutorials, collection announcements, styling content or behind-the-scenes content.

### D11 — Keep V1 Excel media simple
Retain `image_url` and `video_url` in Excel; transform them into the scalable media model during import.

### D12 — Knowledge documents are not directly product-bound
A document may apply to the boutique, a fabric, an occasion, a category, many products or one product.

### D13 — GraphRAG is a first-class capability
Use knowledge entities and relationships from the beginning. PostgreSQL is sufficient for the initial graph implementation; a dedicated graph database can be added later behind an abstraction.

### D14 — Separate product facts from explanatory knowledge
Price and availability come from structured product data. Care, fabric education and policies come from knowledge documents.

### D15 — PostgreSQL Full-Text Search first
Use native PostgreSQL Full-Text Search rather than adding Elasticsearch/OpenSearch at boutique scale.

### D16 — Local Sentence Transformers for initial embeddings
Use `sentence-transformers` with `all-MiniLM-L6-v2` because it is local, open-source and has no per-query embedding API cost.

### D17 — Validate embeddings before vector storage
The model was experimentally verified before introducing persistent vector storage.

### D18 — Semantic search is not eligibility
Semantic similarity ranks candidates; it must not override explicit business constraints.

### D19 — Hard constraints precede semantic ranking
Apply explicit requirements such as availability, category and budget before semantic ranking.

### D20 — Hybrid retrieval is central
The future retrieval layer combines SQL, metadata, Full-Text, semantic search and graph retrieval where appropriate.

### D21 — SQL is authoritative for transactional/product facts
Price, availability and future transactional state must come from live structured/transactional data rather than embeddings or generated prose.

### D22 — Product recommendation and knowledge RAG are different paths
Product search/similarity primarily retrieves products; educational/policy questions primarily retrieve knowledge. A common router can select the appropriate path.

### D23 — Product similarity will eventually be multi-signal
Future similarity can combine structured attributes, semantic text, graph relationships and image similarity, followed by reranking.

### D24 — Retrieval quality must be experimentally evaluated
Day 5 compared SQL, Full-Text and semantic behavior rather than assuming embeddings alone are sufficient.

### D25 — Use a replaceable embedding interface
The application should depend on an embedding abstraction so the local model can be replaced later without rewriting retrieval logic.

### D26 — PostgreSQL can support initial graph traversal
Recursive SQL is sufficient for the initial graph scale. A dedicated graph database remains a future option.

### D27 — Optimize Full-Text later
Native `to_tsvector`/`plainto_tsquery` behavior was validated first. Stored/generated search vectors and additional indexes can be introduced later.

### D28 — Practical customer questions drove the schema
The model was checked against product discovery, budget, occasion, comparison, care, delivery/payment/return and future post-purchase questions. No additional mandatory product columns were required.

### D29 — Complaint handling separates information from action
Future complaint handling may retrieve product facts, care knowledge and policy, but must not diagnose causes or promise refunds/replacements without supporting policy and authorized transaction workflows.

### D30 — Day 5 ends before pgvector
Day 5 concludes after validating SQL, metadata, Full-Text, semantic embeddings and hard-filtered semantic ranking. Persistent vector retrieval belongs to the next stage.

## Final architectural principle

> **Use the right retrieval mechanism for the right signal, then combine them under explicit business constraints.**

```text
Natural Language
      ↓
Query Understanding
      ↓
SQL + Metadata + Full Text + Semantic + Graph
      ↓
Hard Eligibility Filters
      ↓
Hybrid Ranking / Reranking
      ↓
Grounded Product or Knowledge Response
```
