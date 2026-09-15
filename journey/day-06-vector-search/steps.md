# Urban Aanchol — Day 6 Steps

## Step 1 — Decide the persistent semantic-retrieval goal

Day 6 started from the Day 5 in-memory semantic-search experiment.

The objective was to persist embeddings in PostgreSQL so semantic retrieval could become part of the application's durable retrieval architecture.

Two retrieval targets were defined:

- Products
- Knowledge chunks

---

## Step 2 — Assess the local PostgreSQL environment

The local database was checked for pgvector support.

The `vector` extension was initially unavailable.

Two `pg_config.exe` installations were found:

```text
C:\ProgramData\anaconda3\Library\bin\pg_config.exe
C:\Program Files\PostgreSQL\18\bin\pg_config.exe
```

The correct database installation was identified as PostgreSQL 18:

```text
PostgreSQL 18.6
```

The project deliberately used the PostgreSQL 18 installation rather than the unrelated Anaconda PostgreSQL tooling.

---

## Step 3 — Prepare Windows build tooling

Because a ready-to-use pgvector package was not available through the existing PostgreSQL installation, pgvector was built locally.

Visual Studio Community 2026 was installed with the:

```text
Desktop development with C++
```

workload.

The x64 Native Tools Command Prompt was used.

The following were verified:

```text
cl
nmake
```

Both worked successfully.

---

## Step 4 — Build pgvector

The pgvector source was cloned at release:

```text
v0.8.6
```

The source was placed under:

```text
C:\pgvector
```

The build command was:

```powershell
nmake /F Makefile.win
```

The build completed successfully.

---

## Step 5 — Install and enable pgvector

The installation command was:

```powershell
nmake /F Makefile.win install
```

The PostgreSQL installation received:

- `vector.dll`
- `vector.control`
- pgvector SQL extension files
- headers/libraries

The extension was enabled with:

```sql
CREATE EXTENSION vector;
```

Verification returned:

```text
vector | 0.8.6
```

The local stack was therefore:

```text
PostgreSQL 18.6
+
pgvector 0.8.6
```

---

## Step 6 — Inspect existing database schema

The existing Day 5 tables were inspected.

Relevant source tables:

```text
products
knowledge_chunks
```

Product records already contained structured fields such as:

- category
- fabric
- colour
- brand
- collection
- price
- availability
- description

Knowledge chunks contained:

- chunk ID
- document ID
- chunk index
- section title
- chunk text
- content type
- language
- token count
- metadata

This confirmed the correct sources for semantic embedding.

---

## Step 7 — Design embedding storage

A separate-table approach was selected.

Created:

```text
product_embeddings
knowledge_chunk_embeddings
```

Both use:

```text
VECTOR(384)
```

Both store:

```text
model_name
model_version
dimensions
```

Both use unique constraints so the same source record cannot have duplicate embeddings for the same model/version.

This keeps embeddings separate from source-of-truth business data.

---

## Step 8 — Create the embedding schema

The Day 6 schema was created in:

```text
database/schema/015_create_embedding_tables.sql
```

The schema created both product and knowledge embedding tables.

Foreign keys use cascade deletion so an embedding does not survive deletion of its source record.

Dimension checks enforce the current 384-dimensional model configuration.

---

## Step 9 — Design product embedding text

A product embedding should represent semantic meaning, not every database field.

The V1 product text includes:

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

It intentionally excludes:

```text
product_id
price
availability
timestamps
```

Structured values such as price and availability remain retrieval/filtering concerns.

---

## Step 10 — Implement and test product embedding text

Created:

```text
backend/app/database/embedding_text.py
```

A test was run against:

```text
UA-0001
```

The generated text was verified to contain the expected semantic product information.

---

## Step 11 — Implement embedding generation

Created:

```text
backend/app/database/embedding_generator.py
```

The model was:

```text
sentence-transformers/all-MiniLM-L6-v2
```

The model produces:

```text
384 dimensions
```

Embeddings are normalized before storage.

The first test verified:

```text
Model dimensions: 384
Embedding length: 384
```

---

## Step 12 — Create product embedding persistence

Created:

```text
backend/app/database/embedding_repository.py
```

The repository uses:

```sql
ON CONFLICT (product_id, model_name, model_version)
DO UPDATE
```

This makes repeated imports idempotent.

---

## Step 13 — Persist the first product embedding

Created a test for:

```text
UA-0001
```

The first product embedding was generated and stored successfully.

The database returned an embedding UUID.

PostgreSQL verification then confirmed:

```text
dimensions = 384
stored_dimensions = 384
```

---

## Step 14 — Batch-import product embeddings

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

## Step 15 — Create product vector search

Created:

```text
backend/app/database/vector_search.py
```

The search uses pgvector cosine distance:

```sql
embedding <=> query_vector
```

The returned value is converted to a similarity-style score:

```text
1 - cosine_distance
```

The query joins embeddings to products and restricts results to:

```text
availability = Available
```

---

## Step 16 — Test persistent product semantic retrieval

The query:

```text
Something elegant for a family function
```

was embedded and searched against PostgreSQL.

The database returned ranked products.

The test demonstrated both success and a design lesson: semantic similarity can retrieve semantically related products from the wrong category.

This confirmed that semantic retrieval should later be combined with metadata/SQL constraints and reranking.

---

## Step 17 — Inspect knowledge chunks

The existing knowledge base was inspected.

There were 5 policy chunks:

```text
How to Order
Delivery
Payment
Shipping Charges
Returns
```

These came from the Urban Aanchol Order & Policies document.

---

## Step 18 — Design knowledge embedding text

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
Section: How to Order

Customers can place orders through WhatsApp...
```

The test confirmed the correct output.

---

## Step 19 — Create knowledge embedding repository

Created:

```text
backend/app/database/knowledge_embedding_repository.py
```

The repository uses:

```sql
ON CONFLICT (chunk_id, model_name, model_version)
DO UPDATE
```

This keeps knowledge embedding imports idempotent.

---

## Step 20 — Batch-import knowledge embeddings

Created:

```text
backend/app/database/import_knowledge_embeddings.py
```

All 5 policy chunks were embedded.

Result:

```text
Knowledge chunks loaded: 5
Knowledge embeddings saved: 5
```

---

## Step 21 — Create knowledge vector search

Created:

```text
backend/app/database/knowledge_vector_search.py
```

The search uses the same embedding model and pgvector cosine-distance mechanism as product retrieval.

The source is `knowledge_chunk_embeddings`, joined to `knowledge_chunks`.

---

## Step 22 — Test persistent knowledge semantic retrieval

The query:

```text
How long does delivery take?
```

was embedded and searched.

Results ranked:

```text
Delivery         0.8165
Payment          0.2330
Shipping Charges 0.1935
How to Order     0.1853
Returns          0.0961
```

Delivery was the clear top result.

This demonstrated persistent semantic retrieval for business knowledge.

---

## Step 23 — Perform final data-integrity check

The database was checked with counts.

Final state:

```text
products                  9
product_embeddings        9
knowledge_chunks          5
knowledge_embeddings      5
```

No source records were missing embeddings.

---

## Step 24 — Perform code review and cleanup

Three cleanup areas were agreed:

1. Centralize embedding configuration.
2. Separate knowledge embedding persistence into its own repository.
3. Remove the deprecated Sentence Transformers dimension method.

Created:

```text
backend/app/database/embedding_config.py
```

with:

```text
MODEL_NAME
MODEL_VERSION
EMBEDDING_DIMENSIONS
```

Updated the embedding generator to use the centralized configuration.

Created:

```text
backend/app/database/knowledge_embedding_repository.py
```

and removed the persistence function from the importer.

The deprecated method:

```text
get_sentence_embedding_dimension()
```

was removed in favor of the centralized configured dimension.

The product embedding test passed again.

The knowledge embedding importer passed again.

---

## Step 25 — Verify idempotency

A duplicate check was run against:

```text
knowledge_chunk_embeddings
```

The result was:

```text
(0 rows)
```

This confirmed no duplicate `(chunk_id, model_name, model_version)` records were created after rerunning the importer.

---

## Step 26 — Day 6 completion state

Day 6 completed with:

```text
pgvector                    working
Product embeddings          9/9
Knowledge embeddings        5/5
Product semantic search    working
Knowledge semantic search  working
Idempotency                 verified
Code cleanup                complete
```

Documentation and Git commit are intentionally separate from this technical trace.

---

## Next Day

Day 7 starts from the combined Day 5 + Day 6 retrieval foundation:

```text
SQL
+
Metadata
+
Full-text
+
Semantic/vector retrieval
```

The next objective is:

```text
Hybrid Retrieval
+
Reranking
```

The goal is to make retrieval obey hard business constraints while using semantic similarity to improve relevance.
