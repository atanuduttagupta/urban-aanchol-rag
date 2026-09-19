# Day 4 — Catalogue Validation & Import Foundation

## Objective

Build a reliable boundary between the business-friendly Urban Aanchol Excel catalogue and the application's internal product representation.

The Day 4 pipeline is:

```text
Excel Catalogue
      ↓
Excel Reader
      ↓
Raw Product Records
      ↓
Validation
      ↓
Normalization
      ↓
Clean Product Records
```

Invalid catalogue data must stop before database import or RAG processing.

---

## 1. Excel Reader

Created:

```text
backend/app/catalogue/excel_reader.py
```

The reader:

- Opens the `Products` worksheet.
- Dynamically locates the catalogue header row.
- Does not assume headers are on a fixed Excel row.
- Reads product records into dictionaries.
- Preserves numeric and date values.

Dynamic header detection is important because the dummy workbook contains introductory information before the actual table headers.

This makes the importer more resilient to small future changes in workbook layout.

### Verification

Created:

```text
backend/app/catalogue/test_excel_reader.py
```

Run:

```powershell
python -m backend.app.catalogue.test_excel_reader
```

Verified:

```text
Headers found: 24
Products read: 9
```

The first product was also inspected to confirm correct field mapping.

---

## 2. Canonical Catalogue Schema

Created:

```text
backend/app/catalogue/schema.py
```

The V1 catalogue contains 24 fields:

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
occasion
style
mood
tags
price
availability
launch_date
created_date
last_updated
description
image_url
video_url
product_url
remarks
```

The schema also defines allowed product categories:

- Saree
- Blouse
- Dupatta
- Jewelry
- Accessories
- Other

And allowed availability values:

- Available
- Sold
- Reserved
- Inactive

Syntax was verified with:

```powershell
python -m py_compile backend\app\catalogue\schema.py
```

---

## 3. Product IDs

`product_id` is the stable business identifier for a product.

Examples:

```text
UA-0001
UA-0002
UA-0003
```

Product IDs must be:

- Present
- Unique
- Stable

The application should not depend on provider-generated IDs as the business identity of a product.

---

## 4. Multi-Value Fields

The following catalogue fields intentionally support multiple values:

- `occasion`
- `style`
- `mood`
- `tags`

In Excel they remain business-friendly comma-separated text.

Example:

```text
Everyday, Office Wear
```

The application normalizes this into:

```python
["Everyday", "Office Wear"]
```

The same business-friendly approach can apply to other multi-value catalogue fields defined in the V1 schema, such as colour-related values, when they are represented as comma-separated data.

### Normalization rules

During import/synchronization:

- Commas are treated as separators.
- Leading/trailing whitespace is removed.
- Empty values are ignored.
- Accidental duplicate values are removed.
- Human-friendly capitalization is preserved.
- Blank fields remain valid.
- Search-specific normalization can be applied separately.

Excel remains simple for business maintenance; structured normalization is handled by the application pipeline.

---

## 5. Required, Optional, and Unknown Information

Core information should normally be populated, including:

- Product ID
- Product name
- Category
- Price
- Availability
- Description

Optional fields may be blank when they do not apply.

The system must **not invent missing product information**.

Unknown information should remain blank or be represented appropriately.

This is especially important because normalized catalogue data will later become a trusted source for the RAG chatbot.

---

## 6. Price Handling

Prices must:

- Be present where required.
- Be numeric.
- Not be negative.

The normalization layer converts valid prices to Python `Decimal`.

Example:

```text
2450
```

becomes:

```python
Decimal("2450")
```

Using `Decimal` provides a predictable representation for later database storage and avoids unnecessary floating-point ambiguity.

---

## 7. Date Handling

The catalogue contains:

- `launch_date`
- `created_date`
- `last_updated`

Excel datetime values are normalized to Python `date` values.

The application should not depend on Excel's internal datetime representation after normalization.

---

## 8. Availability

Availability is a structured product attribute.

Initial logical states:

- Available
- Sold
- Reserved
- Inactive

The website and future RAG system should treat availability as structured data.

The RAG system must not recommend Sold, Reserved, or Inactive products as currently available.

---

## 9. Description and Remarks

`description` is intended for useful customer-facing product information without unsupported claims.

`remarks` is retained for general/internal or supplementary notes.

Structured catalogue fields should be preferred whenever information has a defined meaning. `remarks` should not become the primary source for filtering or recommendation logic.

---

## 10. Category-Specific Flexibility

The Excel schema intentionally avoids a large number of category-specific columns.

For example, blouse-specific or jewelry-specific information should not force irrelevant columns onto every product.

A future PostgreSQL representation may use:

```text
additional_attributes JSONB
```

for flexible category-specific information.

Frequently filtered attributes can later be promoted to proper structured fields if required.

---

## 11. Media

V1 catalogue media is represented through:

- `image_url`
- `video_url`

Media files themselves are not stored inside the database.

The architecture is intended to support multiple media assets later without creating columns such as:

```text
image_url_1
image_url_2
image_url_3
```

A separate product-media structure can support multiple images and videos when needed.

---

## 12. Catalogue Validator

Created:

```text
backend/app/catalogue/validator.py
```

Validation checks include:

- Required product ID
- Required product name
- Required price
- Valid product category
- Valid availability
- Numeric price
- Non-negative price
- Valid date fields
- Missing columns
- Unexpected columns
- Duplicate column names
- Duplicate product IDs

Invalid catalogue records are reported rather than silently corrected.

---

## 13. Validation Testing

Created:

```text
backend/app/catalogue/test_validator.py
```

### Clean catalogue

Run:

```powershell
python -m backend.app.catalogue.test_validator
```

Verified:

```text
Products validated: 9
Validation errors: 0
Catalogue validation passed.
```

### Negative price test

A temporary negative price was introduced:

```python
products[0]["price"] = -100
```

The validator correctly detected:

```text
price cannot be negative
```

The temporary change was removed afterward.

### Duplicate product ID test

A temporary duplicate ID was introduced:

```python
products[1]["product_id"] = products[0]["product_id"]
```

The validator correctly detected:

```text
duplicate product_id 'UA-0001'
```

The temporary change was removed afterward.

---

## 14. Normalization Boundary

Normalization is deliberately separated from validation.

Validation answers:

> Is this catalogue data acceptable?

Normalization answers:

> How should acceptable catalogue data be represented inside the application?

This separation makes both components easier to test and replace.

Created:

```text
backend/app/catalogue/normalizer.py
```

The normalizer currently:

- Strips surrounding whitespace from text.
- Converts empty text values to `None`.
- Converts multi-value fields into lists.
- Converts prices to `Decimal`.
- Converts Excel datetime values to `date`.

Created:

```text
backend/app/catalogue/test_normalizer.py
```

Run:

```powershell
python -m backend.app.catalogue.test_normalizer
```

Verified:

```text
Products normalized: 9
```

The first normalized product was inspected and confirmed to contain list-based attributes, a `Decimal` price, and normalized date values.

---

## 15. Reusable Validation Command

Created:

```text
backend/app/catalogue/validate.py
```

The catalogue can be validated independently with:

```powershell
python -m backend.app.catalogue.validate
```

Verified:

```text
Urban Aanchol Catalogue Validation
----------------------------------
Products checked: 9
Validation errors: 0

Catalogue validation passed.
```

This provides a reusable quality check whenever the Excel catalogue changes.

---

## 16. Combined Catalogue Pipeline

Created:

```text
backend/app/catalogue/pipeline.py
```

The reusable pipeline performs:

```text
read_products()
      ↓
validate_products()
      ↓
normalize_products()
```

The main entry point is:

```python
load_catalogue(file_path)
```

A convenience function is also available:

```python
load_default_catalogue()
```

If validation errors exist, the pipeline stops and does not return normalized catalogue records.

### Complete pipeline test

Created:

```text
backend/app/catalogue/test_pipeline.py
```

Run:

```powershell
python -m backend.app.catalogue.test_pipeline
```

Verified:

```text
Products loaded through pipeline: 9
```

All 9 dummy products currently pass the clean read → validate → normalize pipeline.

---

## 17. Database and RAG Boundary

The catalogue processing layer is deliberately independent of the eventual database implementation.

The flow is:

```text
Excel
  ↓
Read
  ↓
Validate
  ↓
Normalize
  ↓
Clean Product Records
  ↓
Future PostgreSQL
  ↓
Search / Indexing
  ↓
RAG
```

The RAG layer should consume trusted, normalized catalogue data rather than reading Excel directly.

This prepares the same catalogue records for future:

- Keyword search
- Structured/metadata filtering
- Vector embeddings
- Product retrieval
- Recommendations
- RAG responses

---

## 18. Vendor Independence

The catalogue-processing components should remain independent of:

- Cloud providers
- Hosting providers
- Vector databases
- LLM providers
- Media providers
- Database hosting providers

Excel reading, validation, and normalization are kept separate from database and AI layers.

Standard Python data structures and portable interfaces are preferred.

---

## 19. Dummy Catalogue

Current development workbook:

```text
data/catalogue/products_dummy.xlsx
```

It contains:

- 24 expected fields
- 9 illustrative products
- 7 Sarees
- 2 Blouses
- Unique product IDs
- Numeric prices
- Explicit availability values

The supplied product images are real development assets, but the product IDs, names, descriptions, prices, dates, availability, URLs, and other commercial values are dummy assumptions.

Therefore:

> The dummy catalogue must not be treated as production business data.

It must be replaced or fully validated before being used as the live catalogue.

---

## 20. Files Created or Updated

```text
backend/app/catalogue/
├── __init__.py
├── excel_reader.py
├── schema.py
├── validator.py
├── normalizer.py
├── pipeline.py
├── test_excel_reader.py
├── test_validator.py
├── test_normalizer.py
├── test_pipeline.py
└── validate.py

journey/day-04-catalogue-validation/
├── README.md
├── steps.md
└── decisions.md
```

---

## 21. Day 4 Completion Checklist

- [x] Excel reader works
- [x] Dynamic header detection works
- [x] 24 catalogue fields are recognized
- [x] Product categories are defined
- [x] Availability values are defined
- [x] Product ID rules are defined
- [x] Catalogue validation works
- [x] Negative price is detected
- [x] Duplicate product ID is detected
- [x] Normalization works
- [x] Multi-value fields are normalized
- [x] Price is normalized to `Decimal`
- [x] Dates are normalized
- [x] Reusable validation command works
- [x] Combined read → validate → normalize pipeline works
- [x] All 9 dummy products pass the clean pipeline
- [x] Catalogue processing remains database/provider independent

---

## Day 4 Outcome

Day 4 established a tested and reusable catalogue ingestion boundary:

```text
                Urban Aanchol Excel
                        ↓
                  Excel Reader
                        ↓
                   Raw Records
                        ↓
                    Validator
                        ↓
                   Normalizer
                        ↓
              Clean Product Records
                        ↓
              Future Database / RAG
```

This prevents invalid catalogue data from flowing directly into the database or AI/RAG layers.

**Next: Day 5 — Database Design**

The next milestone designs the PostgreSQL data model before introducing database infrastructure, while preserving stable product IDs, structured multi-value attributes, flexible category-specific attributes, availability, future search/RAG requirements, and vendor independence.
