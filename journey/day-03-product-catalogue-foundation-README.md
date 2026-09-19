# Day 3 — Product Catalogue Foundation

## Objective

Establish a clean, repeatable product catalogue foundation for Urban Aanchol that can later feed the website, database, search, recommendations, and RAG chatbot.

The catalogue is designed as a **product catalogue**, not a saree-only catalogue, while keeping Excel simple enough for business-side maintenance.

## 1. Catalogue Scope

The catalogue supports:

- Saree
- Blouse
- Dupatta
- Jewelry
- Accessories
- Other

`category` is therefore a core product attribute.

This avoids designing the data model around sarees only and leaves room for future boutique products.

## 2. V1 Catalogue Schema

The V1 Excel catalogue contains 24 fields:

1. `product_id`
2. `product_name`
3. `category`
4. `brand`
5. `collection`
6. `fabric`
7. `colour`
8. `secondary_colour`
9. `pattern`
10. `border`
11. `occasion`
12. `style`
13. `mood`
14. `tags`
15. `price`
16. `availability`
17. `launch_date`
18. `created_date`
19. `last_updated`
20. `description`
21. `image_url`
22. `video_url`
23. `product_url`
24. `remarks`

The schema is intentionally general enough to support current and future product categories.

## 3. Excel as Business Source of Truth

Excel remains the initial business-friendly source of truth.

The intended future flow is:

```text
Excel / Google Sheets
        ↓
Validated product records
        ↓
PostgreSQL
        ↓
Search / Indexing
        ↓
RAG / Recommendations
```

The application database will contain a derived/operational copy for:

- Website catalogue
- Search
- Recommendations
- RAG
- Availability checks

The business owner should not need to maintain the technical database directly.

## 4. Product Identification

Every product receives a stable unique `product_id`.

Example:

```text
UA-0001
```

Product IDs should remain stable even when other product information changes.

This gives future synchronization a reliable identifier for detecting additions and updates.

## 5. Multi-Value Fields

The following fields support comma-separated values in Excel:

- `colour`
- `secondary_colour`
- `occasion`
- `style`
- `mood`
- `tags`

Example:

```text
occasion = Durga Puja, Wedding, Party
```

This keeps the Excel catalogue human-readable while allowing a product to have multiple applicable attributes.

### Future normalization

During import/synchronization:

- commas are treated as separators
- leading/trailing whitespace is removed
- empty values are ignored
- accidental duplicate values are removed
- human-friendly capitalization is preserved
- blank fields remain valid
- search-specific normalization can be applied separately

The business-facing Excel format stays simple; structured normalization belongs in the application data pipeline.

## 6. Required, Optional, and Unknown Information

Core product information should normally be populated, including:

- Product ID
- Product name
- Category
- Price
- Availability
- Description

Optional fields may be blank when they do not apply.

The system must **not invent missing product information**. Unknown information should remain blank or be represented appropriately.

This is especially important because catalogue data will later become a source for the RAG chatbot.

## 7. Price

`price` represents the selling price in Indian Rupees.

Excel should contain a numeric value such as:

```text
4999
```

rather than:

```text
₹4,999
```

The application can format the value for customer-facing display.

Price must be greater than or equal to zero.

## 8. Availability

Availability is an explicit catalogue attribute.

Initial logical values:

- Available
- Sold
- Reserved
- Inactive

The recommendation system should normally recommend only products that are currently available.

Availability therefore needs to remain structured rather than being inferred from free-form descriptions.

## 9. Dates

The catalogue includes:

- `launch_date`
- `created_date`
- `last_updated`

These support product lifecycle information and future Excel-to-database synchronization.

Where possible, Excel should store actual date values rather than free-form date text.

The future import pipeline will convert them into standard database date/timestamp representations.

## 10. Description and Remarks

`description` is intended for useful customer-facing product information without unsupported claims.

`remarks` is for general/internal notes.

Important searchable or filterable product information should have a proper structured field rather than being hidden only inside `remarks`.

## 11. Media

V1 stores:

- `image_url`
- `video_url`

Media files themselves are not stored inside the database.

The architecture is intended to support multiple media assets later without creating columns such as:

```text
image_url_1
image_url_2
image_url_3
```

A separate product-media structure can support multiple images/videos when the catalogue grows.

## 12. Category-Specific Flexibility

The Excel schema deliberately avoids a large number of category-specific columns.

For example, blouse-specific or jewelry-specific attributes should not create irrelevant columns for every product.

A future PostgreSQL implementation may use:

```text
additional_attributes JSONB
```

for flexible category-specific information.

Frequently filtered attributes can later be promoted to proper structured fields if needed.

## 13. Data Quality Rules

The catalogue must be validated before records enter the application database.

The future validation/import layer should detect:

- Missing required fields
- Duplicate product IDs
- Invalid prices
- Negative prices
- Invalid dates
- Invalid availability values

Invalid records should be **reported rather than silently corrected**.

The goal is to prevent bad catalogue data from reaching website search and RAG responses.

## 14. Excel Processing

Python `openpyxl` was selected for `.xlsx` catalogue processing.

It is recorded as:

- Direct dependency in `backend/requirements.txt`
- Exact environment dependency in `backend/requirements-lock.txt`

Excel processing should remain behind a small internal import/validation layer so the rest of the application does not depend directly on the Excel library.

## 15. Vendor Independence

The catalogue uses standard data concepts and canonical URLs.

It should remain independent of any particular:

- Hosting provider
- Database provider
- Vector database
- LLM provider
- Media provider

This supports the project's broader vendor-independence principle.

## 16. Future Synchronization

The planned synchronization architecture is:

```text
Excel / Google Sheets
        ↓
Validated product records
        ↓
PostgreSQL
        ↓
Search / Indexing
        ↓
RAG
```

Future synchronization should detect:

- New products
- Product updates
- Availability changes

This lets the business continue using a familiar catalogue-management workflow while the application uses structured operational data.

## 17. Dummy Development Catalogue

A dummy Excel workbook was created for development.

It contains:

- 24 expected fields
- 9 product records
- 7 Sarees
- 2 Blouses
- Unique product IDs
- Numeric prices
- Explicit availability values

The supplied product images are real development assets, but the commercial catalogue information is illustrative.

Therefore:

> The dummy workbook must not be treated as the live Urban Aanchol catalogue.

Dummy names, prices, URLs, and other illustrative commercial values must be replaced/validated before production use.

## 18. Day 3 Work Completed

- Product catalogue scope finalized
- V1 24-field schema finalized
- Product ID strategy defined
- Multi-value field convention defined
- Multi-value normalization rules defined
- Price rules defined
- Availability states defined
- Date rules defined
- Description/remarks responsibilities defined
- Media URL approach defined
- Category-specific flexibility defined
- Data-quality rules defined
- Excel processing library selected
- Excel/Google Sheets → PostgreSQL → Search/RAG flow documented
- Dummy Excel catalogue created
- Supplied product images included for development
- Catalogue design documented
- Day 3 changes committed and pushed
- Final working tree verified clean

## 19. Day 3 Completion Checklist

- [x] Catalogue scope defined
- [x] 24-field V1 schema defined
- [x] Stable product ID defined
- [x] Multi-value fields defined
- [x] Normalization rules defined
- [x] Price rules defined
- [x] Availability rules defined
- [x] Date fields defined
- [x] Media fields defined
- [x] Category-specific flexibility defined
- [x] Data-quality rules defined
- [x] `openpyxl` selected
- [x] Dummy catalogue created
- [x] Dummy catalogue manually checked
- [x] Future synchronization flow documented
- [x] Day 3 checkpoint committed/pushed

## Day 3 Outcome

Urban Aanchol now has a defined product data contract that can support:

```text
Business Catalogue
       ↓
Website
       ↓
Database
       ↓
Keyword / Metadata Search
       ↓
Semantic Search
       ↓
Hybrid Retrieval
       ↓
RAG / Recommendations
```

The next step is to make this catalogue operationally reliable by implementing the first validation/import pipeline.

**Next: Day 4 — Catalogue Validation & Import Foundation**

Target flow:

```text
Excel
  ↓
Excel Reader
  ↓
Validation
  ↓
Validation Report
```
