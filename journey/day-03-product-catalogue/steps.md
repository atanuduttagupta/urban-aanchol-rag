# Day 3 — Product Catalogue Foundation

## Objective

Establish the foundation for the Urban Aanchol product catalogue and define a clean, repeatable data contract that can later feed the website, database, search, and RAG chatbot.

## Completed Steps

### 1. Finalize catalogue scope

The catalogue is an **Urban Aanchol Product Catalogue**, not a saree-only catalogue.

Supported/current and future categories include:

- Saree
- Blouse
- Dupatta
- Jewelry
- Accessories
- Other

`category` is a core product attribute.

### 2. Finalize the V1 schema

The V1 Excel catalogue contains these 24 fields:

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

### 3. Confirm Excel as source of truth

Excel is the business-friendly source of truth for catalogue management.

The application database will later contain a derived/operational copy for:

- Website catalogue
- Search
- Recommendations
- RAG
- Availability checks

### 4. Product IDs

Every product receives a stable unique `product_id`, such as `UA-0001`.

Product IDs should remain stable even when other product information changes.

### 5. Required and optional fields

Core fields such as product ID, product name, category, price, availability, and description should normally be populated.

Optional fields may be blank when they are not applicable. A blank value is preferable to invented information.

### 6. Multi-value fields

The following Excel fields support comma-separated values:

- `colour`
- `secondary_colour`
- `occasion`
- `style`
- `mood`
- `tags`

Example:

`occasion = Durga Puja, Wedding, Party`

### 7. Multi-value normalization

During future import/synchronization:

- commas are treated as separators
- leading/trailing whitespace is removed
- empty values are ignored
- accidental duplicate values are removed
- original human-friendly capitalization is preserved
- blank fields remain valid
- search-specific normalization can be applied separately

Excel remains simple and human-readable; structured normalization is handled by the import/data pipeline.

### 8. Price

`price` represents the selling price in Indian Rupees.

Excel should contain a numeric value such as `4999`, rather than `₹4,999`.

The website can format the value as Indian currency.

Price must be greater than or equal to zero.

### 9. Availability

Initial logical values are:

- Available
- Sold
- Reserved
- Inactive

Only products marked `Available` should normally be recommended as currently purchasable.

### 10. Dates

The catalogue includes:

- `launch_date`
- `created_date`
- `last_updated`

Dates should be actual Excel dates where possible. The future import pipeline will convert them into standard database date/timestamp representations.

### 11. Description and remarks

Descriptions should contain useful customer-facing information without unsupported claims.

`remarks` is for general/internal notes and is not the primary source for structured filtering.

### 12. Media

V1 stores:

- `image_url`
- `video_url`

Media files are not stored inside the database. Multiple media assets can later use a separate product-media structure.

### 13. Data quality and unknown information

The system must not invent missing product information.

Future validation must detect:

- invalid prices
- negative prices
- invalid dates
- missing required fields
- duplicate product IDs
- invalid availability values

Invalid records should be reported rather than silently corrected.

### 14. Category-specific flexibility

We will not create many category-specific Excel columns.

Future category-specific attributes can use a flexible PostgreSQL `JSONB` structure rather than continually adding columns to Excel.

### 15. Excel processing library

Python `openpyxl` will be used for `.xlsx` catalogue processing.

It is recorded in:

- `backend/requirements.txt` — direct dependency
- `backend/requirements-lock.txt` — exact installed environment versions

Excel processing should remain behind an internal import/validation layer so the rest of the system remains independent of the Excel library.

### 16. Vendor independence

The catalogue schema uses standard data concepts and URLs and should remain independent of any particular hosting provider, database provider, vector database, LLM provider, or media provider.

### 17. Future synchronization

The planned flow is:

Excel / Google Sheets
→ validated product records
→ PostgreSQL
→ search/indexing
→ RAG

The synchronization process should detect additions, updates, and availability changes.

### 18. Dummy catalogue

The current workbook contains dummy commercial information for development.

The supplied product images are real images provided for development, but dummy names, prices, URLs, and other catalogue values must not be treated as production information.

### 19. Manual schema validation

The dummy workbook was manually validated and confirmed to contain:

- 24 expected columns
- 9 product records
- 7 Sarees
- 2 Blouses
- unique product IDs
- numeric prices
- explicit availability values

### 20. Git checkpoint

Day 3 documentation and dependency changes were committed and pushed to GitHub.

The final working tree was verified clean.

## Completion Criteria

Day 3 is complete when the catalogue schema, data rules, dependency decision, and catalogue design decisions are documented; the dummy catalogue exists in the repository; and the changes are committed, pushed, and verified clean.

## Next Day

Day 4 will build the first actual catalogue data-processing layer:

Excel → Excel Reader → Validation → Validation Report

The first goal is reliable data quality before introducing PostgreSQL, vector search, or RAG.
