# Day 9 --- Query Understanding & Retrieval Intent

## Objective

Build a deterministic Query Understanding layer that converts a
customer's natural-language product-search request into a structured
`RetrievalIntent`, while preserving the original customer language for
keyword and semantic retrieval.

The design goal:

``` text
Customer Message
       ↓
Query Understanding
       ↓
RetrievalIntent
       ↓
RetrievalRequest
       ↓
Day 8 Hybrid Retrieval
```

Day 9 deliberately did **not** introduce an LLM. The deterministic
foundation was established first so that a future LLM can be added as a
controlled fallback rather than becoming tightly coupled to retrieval.

------------------------------------------------------------------------

## Day 9 Architectural Principles

### 1. RetrievalIntent is separate from RetrievalRequest

`RetrievalIntent` represents what the customer asked for:

-   `original_query`
-   `semantic_query`
-   `filters`
-   `requested_limit`

`RetrievalRequest` represents what the retrieval system should execute:

-   `query`
-   `limit`
-   `filters`

### 2. Customer-requested result count is different from retrieval depth

A customer's requested number of products must not be confused with:

-   hybrid fusion window
-   keyword retrieval depth
-   semantic retrieval depth
-   RRF configuration

`RetrievalPolicy` owns internal retrieval configuration.

`RetrievalRequest.limit` is the user-facing result limit.

Hybrid retrieval applies the user-facing limit only after ranking and
fusion.

### 3. Deterministic extraction is conservative

The parser should extract only information that can be identified with
sufficient confidence.

Unknown language should remain available to semantic retrieval rather
than being converted into an invented structured filter.

> Unknown ≠ false.

### 4. Catalogue vocabulary must remain dynamic

The query-understanding layer should not hard-code the current catalogue
as a permanent vocabulary.

Catalogue attributes are obtained from the database through the
catalogue vocabulary repository.

------------------------------------------------------------------------

# Day 9A --- Retrieval Intent Foundation

## Work completed

Introduced `RetrievalIntent` in:

`backend/app/retrieval/models.py`

The model preserves:

``` python
original_query
semantic_query
filters
requested_limit
```

`requested_limit` is populated only when the customer explicitly asks
for a number.

If no number is requested:

``` python
requested_limit = None
```

This keeps the agent-level decision about how many results to display
separate from the default retrieval limit.

## Tests

Added tests covering:

-   original query preservation
-   semantic query preservation
-   structured filters
-   explicit requested result count

------------------------------------------------------------------------

# Day 9B --- Dynamic Catalogue Attribute Matching

## Work completed

Created:

`backend/app/query_understanding/attribute_matcher.py`

The matcher:

-   uses the current catalogue vocabulary
-   is case-insensitive
-   normalizes whitespace
-   supports multiple matching values
-   avoids partial-word matches
-   supports plural variants
-   handles overlapping catalogue phrases
-   prefers the longest/specific match
-   does not maintain a hard-coded catalogue-value list

Example:

``` text
light blue
```

can resolve to:

``` text
Light Blue
```

when that value exists in the current catalogue vocabulary.

Created:

`backend/app/database/catalogue_attribute_repository.py`

It provides catalogue vocabulary from the database for:

-   category
-   brand
-   collection
-   fabric
-   colour
-   secondary colour
-   pattern
-   border
-   occasion
-   style
-   mood
-   tag

------------------------------------------------------------------------

# Day 9C --- Natural-Language Price Extraction

## Work completed

Created:

`backend/app/query_understanding/price_extractor.py`

Supported deterministic price patterns include:

-   under
-   below
-   less than
-   up to
-   not exceeding
-   above
-   over
-   more than
-   between X and Y

Examples:

``` text
silk sarees not exceeding ₹3000
```

produces:

``` python
{"max_price": 3000.0}
```

and:

``` text
silk sarees between 2000 and 4000
```

produces:

``` python
{"min_price": 2000.0, "max_price": 4000.0}
```

The price extractor is intentionally conservative and does not invent
meanings for unsupported phrases.

------------------------------------------------------------------------

# Day 9D --- Requested Result Limit Extraction

## Work completed

Extended:

`backend/app/query_understanding/limit_extractor.py`

Supported explicit result-count patterns include requests such as:

``` text
Show me 6 sarees
Show 6 sarees
Give me 6 sarees
Find 6 sarees
List 6 sarees
Top 6 sarees
Please show me 6 sarees
I would like 4 sarees
I need 5 blue sarees
Can you show me 4 blue sarees?
```

The extractor also avoids treating price values as result limits.

Example:

``` text
Show me sarees below 3000
```

does not produce a requested result limit.

Zero is also rejected as a requested limit.

------------------------------------------------------------------------

# Day 9E --- Query Understanding Reliability

## Objective

Verify that independent extraction mechanisms work correctly together
without inventing unsupported filters.

### Reliability cases tested

**Limit + maximum price**

``` text
Show me 5 silk sarees under 3000
```

Expected:

``` python
filters = {
    "category": "Saree",
    "fabric": "Silk",
    "max_price": 3000.0,
}
requested_limit = 5
```

**Limit + price range**

``` text
Show me 4 blue sarees between 2000 and 4000
```

Expected:

``` python
filters = {
    "category": "Saree",
    "colour": "Blue",
    "min_price": 2000.0,
    "max_price": 4000.0,
}
requested_limit = 4
```

**Unknown descriptive language**

``` text
I want a graceful saree for my sister's wedding
```

If `graceful` is not a known catalogue value, it must not be invented as
a structured filter.

The known `Wedding` attribute can still be extracted, while the complete
customer message remains the semantic query.

## Day 9E validation

-   Query Understanding tests: **17 passed**
-   Full backend test suite: **110 passed**
-   Targeted Ruff: **All checks passed**
-   `git diff --check`: clean

------------------------------------------------------------------------

# Day 9F --- Query Pipeline Contract Verification

## Architectural finding

During Day 9F inspection, the project already had the required Query
Pipeline boundary.

Existing component:

`backend/app/retrieval/query_pipeline.py`

It already orchestrates:

``` text
Customer Query
      ↓
Catalogue Vocabulary
      ↓
understand_query()
      ↓
RetrievalIntent
      ↓
resolved result limit
      ↓
RetrievalRequest
      ↓
HybridProductRetriever
```

Therefore, no duplicate Request Builder abstraction was introduced.

> Do not create another abstraction when the existing architecture
> already provides the required responsibility.

## Limit precedence

The intended precedence is:

``` text
customer requested limit
        ↓
caller limit
        ↓
configured default
```

A Day 9F contract test verifies:

``` text
Customer asks for: 8
Caller provides:   3
Resulting limit:   8
```

This confirms that an explicit customer request takes precedence over a
generic caller limit.

## Validation

-   Pipeline tests: **4 passed**
-   Full backend test suite: **111 passed**
-   Targeted Ruff: **All checks passed**
-   `git diff --check`: clean

A duplicate test definition was accidentally introduced during
development. Ruff detected the `F811` redefinition, the duplicate was
removed, and the test suite was rerun successfully. This genuine issue
is recorded because it demonstrates why both pytest and static analysis
are part of the project validation workflow.

------------------------------------------------------------------------

# Final Day 9 Architecture

``` text
                    Customer Message
                           │
                           ▼
                 Query Understanding
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
   Attributes           Price             Result Limit
        │                  │                  │
        └──────────────────┼──────────────────┘
                           ▼
                    RetrievalIntent
                           │
                           ▼
                     QueryPipeline
                           │
                           ▼
                    RetrievalRequest
                           │
                           ▼
                 HybridProductRetriever
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
     Eligibility        Keyword          Semantic
          │                │                │
          └────────────────┼────────────────┘
                           ▼
                      RRF Fusion
                           │
                           ▼
                  User-facing limit
                           │
                           ▼
                     Product Results
```

------------------------------------------------------------------------

# Day 9 Test Checkpoint

At Day 9F completion:

``` text
111 backend tests passed
```

Git working tree was clean and synchronized with `origin/main`.

------------------------------------------------------------------------

# Day 9 Key Lessons

1.  Separate **customer intent** from **retrieval execution**.
2.  Keep the original customer query intact.
3.  Use structured metadata only when the parser can identify it
    confidently.
4.  Do not hard-code the current catalogue vocabulary into the parser.
5.  Keep price extraction separate from result-count extraction.
6.  Keep customer result limits separate from internal retrieval depth.
7.  Let the existing Query Pipeline construct `RetrievalRequest`.
8.  Do not add abstractions unless the architecture actually needs them.
9.  Use tests and Ruff together; each can catch different classes of
    problems.
10. Preserve unsupported natural language for semantic retrieval rather
    than inventing structured meaning.

------------------------------------------------------------------------

# Day 9 Completion Status

**Day 9 --- Query Understanding & Retrieval Intent: COMPLETE**

-   [x] 9A --- Retrieval Intent foundation
-   [x] 9B --- Dynamic catalogue attribute matching
-   [x] 9C --- Natural-language price extraction
-   [x] 9D --- Result-limit extraction and regression coverage
-   [x] 9E --- Query Understanding reliability
-   [x] 9F --- Query Pipeline contract verification

------------------------------------------------------------------------

# Next --- Day 10

Planned next architectural area:

**Query Understanding → LLM Fallback Design**

The first step should be architectural design, not provider/API
integration.

Target direction:

``` text
Customer Message
       ↓
Deterministic Query Understanding
       │
       ├── confidently understood
       │
       └── uncertain / unsupported language
                    ↓
               LLM fallback
                    ↓
             validated intent
                    ↓
             RetrievalIntent
                    ↓
             QueryPipeline
                    ↓
            Hybrid Retrieval
```

The future LLM should produce a constrained intent structure, not SQL or
direct database operations.

The concrete LLM/provider should remain behind an interface so that the
project stays free-first and vendor-independent.
