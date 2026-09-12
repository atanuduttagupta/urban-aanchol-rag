# Urban Aanchol RAG — Day 5 Steps
## Database Design & Retrieval Foundation

## Database and schema

1. Defined boundaries between Excel, PostgreSQL, vector retrieval, knowledge storage, graph retrieval and media storage.
2. Defined generalized `products` schema.
3. Created normalized tables for occasions, styles, moods and tags.
4. Created `media_assets` and `product_media`.
5. Created knowledge document/chunk tables.
6. Created graph entity/relation and document/chunk entity-link tables.
7. Created retrieval indexes for common structured fields.
8. Added PostgreSQL connectivity using `psycopg`.
9. Created product mapping and repository logic.
10. Imported the validated dummy Excel catalogue.

## Import validation

11. Imported 9 products.
12. Imported 18 occasions, 18 styles, 18 moods and 44 tags.
13. Imported 9 images, 9 videos and 18 product-media links.
14. Created the Order & Policies knowledge document with five chunks.
15. Created and linked five policy-topic graph entities.
16. Verified representative graph traversal.

## Retrieval tests

17. Tested SQL: available sarees under ₹3,000 → 6 products.
18. Tested metadata: Traditional + Office Wear → UA-0001.
19. Tested PostgreSQL Full-Text Search: `handloom saree` → UA-0001, UA-0003, UA-0005.
20. Tested SQL + Full-Text: available handloom sarees under ₹3,000 → UA-0001, UA-0005, UA-0003.

## Semantic retrieval

21. Verified Python 3.11.9 and approximately 19.8 GB RAM.
22. Installed `sentence-transformers` 5.7.0.
23. Loaded `all-MiniLM-L6-v2`.
24. Generated a 384-dimensional embedding successfully.
25. Ran semantic similarity for `Something elegant for a family function`.
26. Compared Full-Text and semantic retrieval for `Something graceful to wear to Puja`.
27. Observed that unrestricted semantic retrieval can return an inappropriate category.
28. Applied `availability = Available` and `category = Saree` before semantic ranking.
29. Re-ran the experiment and confirmed only eligible sarees were ranked.

## Important observations

- SQL is strong for exact business constraints.
- Metadata joins support structured customer preferences.
- Full-Text Search is strong when catalogue wording contains the requested terms.
- Semantic search helps when customer wording differs from catalogue wording.
- Semantic search alone can return unsuitable categories.
- Therefore hard eligibility constraints must be applied before semantic ranking.
- Hybrid retrieval and reranking are required for the eventual recommendation system.

## Final Day 5 state

```text
PostgreSQL connection             ✅
Product schema                    ✅
Product import                    ✅
Multi-value attributes            ✅
Media relationships               ✅
Knowledge documents               ✅
Knowledge chunks                  ✅
Knowledge graph foundation        ✅
Policy knowledge                  ✅
SQL retrieval                     ✅
Metadata retrieval                ✅
Full-Text Search                  ✅
SQL + Full-Text retrieval         ✅
Local embeddings                  ✅
Semantic similarity               ✅
Hard-filter + semantic ranking    ✅
```

## Deliberately deferred

- pgvector storage
- vector indexes
- persistent product embeddings
- persistent knowledge embeddings
- production hybrid ranking
- reranking model
- query understanding
- query routing
- LLM response generation
- complete end-to-end RAG

**Day 5 complete.**
