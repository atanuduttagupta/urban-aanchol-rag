# Day 4 — Decisions: Catalogue Validation & Import Foundation

## 1. Purpose of Day 4

Day 4 establishes a reliable boundary between the business-friendly
Excel catalogue and the application's internal product representation.

The pipeline is:

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
```

Invalid catalogue data must stop before database import or RAG processing.

## 2. Excel Remains the Business-Friendly Source

The Urban Aanchol catalogue is maintained in Excel because it is practical
for the boutique owner to create and update product information.

The application should not depend on Excel formatting details.

Therefore:

- Excel is the input/source for catalogue data.
- The application reads Excel through a dedicated reader.
- Excel-specific handling stays isolated from the rest of the application.

## 3. Dynamic Header Detection

The Excel reader must not assume that the catalogue headers are always
on a particular row.

The reader searches for required catalogue headers and identifies the
actual header row dynamically.

This was necessary because the dummy workbook contains introductory
information before the actual table headers.

This approach also makes the importer more resilient if the workbook
layout changes slightly in the future.

## 4. Canonical Catalogue Schema

The V1 catalogue contains 24 common fields:

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

The schema is defined in:

```text
backend/app/catalogue/schema.py
```

## 5. Product Categories

Urban Aanchol sells more than sarees.

The initial allowed categories are:

- Saree
- Blouse
- Dupatta
- Jewelry
- Accessories
- Other

The `category` field is therefore a central part of the product model.

Saree-specific attributes should not be forced into every product record.

## 6. Flexible Category-Specific Attributes

Future category-specific information will be supported through a
database-level `additional_attributes` JSONB field.

Examples may include:

```json
{
  "weave": "Handloom",
  "blouse_piece": true
}
```

or:

```json
{
  "sleeve_type": "Elbow Length",
  "neck_type": "Round"
}
```

This avoids creating many category-specific columns in the Excel
catalogue and keeps the database extensible.

## 7. Multi-Value Fields

The following fields are intentionally allowed to contain multiple
values:

- occasion
- style
- mood
- tags

In Excel they remain easy to enter as comma-separated text.

Example:

```text
Everyday, Office Wear
```

The application normalizes this into:

```python
["Everyday", "Office Wear"]
```

This provides a convenient business data-entry format while giving
the application structured values for filtering, search, and RAG.

## 8. Remarks

`remarks` is retained as a general-purpose notes field.

It may contain internal or supplementary comments.

It should not be treated as the primary structured source for product
filtering or recommendation logic.

Structured catalogue fields should be preferred whenever information
has a defined meaning.

## 9. Price Handling

Prices must:

- Be present for products requiring a price.
- Be numeric.
- Not be negative.

The normalization layer converts valid numeric prices to Python
`Decimal` values.

This provides a predictable representation for later database storage
and avoids unnecessary floating-point ambiguity.

## 10. Date Handling

The catalogue contains:

- launch_date
- created_date
- last_updated

Excel datetime values are normalized to Python `date` values.

The application should not depend on Excel's internal datetime
representation after normalization.

## 11. Availability

The initial allowed availability values are:

- Available
- Sold
- Reserved
- Inactive

Availability is important for both the website and the future RAG
system.

The RAG system must not recommend Sold, Reserved, or Inactive products
as currently available.

## 12. Product IDs

`product_id` is the business identifier for a product.

Examples:

```text
UA-0001
UA-0002
UA-0003
```

Product IDs must be:

- Present.
- Unique.
- Stable.

The system should not depend on provider-generated identifiers as the
business identity of a product.

## 13. Validation Before Import

Validation occurs before normalization is accepted into downstream
systems.

The validator checks:

- Required product ID.
- Required product name.
- Valid category.
- Valid availability.
- Required price.
- Numeric price.
- Non-negative price.
- Valid date fields.
- Missing columns.
- Unexpected columns.
- Duplicate column names.
- Duplicate product IDs.

If validation fails, the combined pipeline raises an error and does not
return normalized catalogue records.

## 14. Validation Testing

Validation was tested with both valid and deliberately invalid data.

### Valid catalogue

Result:

```text
Products validated: 9
Validation errors: 0
Catalogue validation passed.
```

### Negative price

A temporary negative price was introduced.

The validator correctly detected:

```text
price cannot be negative
```

The test modification was removed afterward.

### Duplicate product ID

A temporary duplicate product ID was introduced.

The validator correctly detected:

```text
duplicate product_id 'UA-0001'
```

The test modification was removed afterward.

## 15. Normalization Boundary

Normalization is intentionally separated from validation.

Validation answers:

> Is this catalogue data acceptable?

Normalization answers:

> How should acceptable catalogue data be represented inside the application?

This separation makes both components easier to test and replace.

## 16. Normalized Product Representation

The normalizer currently:

- Strips surrounding whitespace from text.
- Converts empty text values to `None`.
- Converts multi-value fields into lists.
- Converts price values to `Decimal`.
- Converts datetime values to `date`.

The normalized representation is the preferred input for the future
database and RAG layers.

## 17. Combined Catalogue Pipeline

The reusable pipeline is implemented in:

```text
backend/app/catalogue/pipeline.py
```

The pipeline performs:

```text
read_products()
      ↓
validate_products()
      ↓
normalize_products()
```

Invalid data stops the process.

This creates a single controlled entry point for future imports.

## 18. Reusable Validation Command

Catalogue validation can be executed independently with:

```powershell
python -m backend.app.catalogue.validate
```

This allows catalogue quality to be checked whenever the Excel file
changes.

## 19. Database Independence

PostgreSQL is the planned initial database technology, but the catalogue
processing layer must not depend on a specific PostgreSQL hosting provider.

The current architecture keeps:

- Excel reading.
- Validation.
- Normalization.

separate from the database layer.

This preserves the project's vendor-independent design principle.

## 20. RAG Readiness

The normalized catalogue is designed to become the source for future:

- Keyword search.
- Structured filtering.
- Vector embeddings.
- Product retrieval.
- RAG responses.
- Recommendation logic.

The RAG layer should consume trusted, normalized catalogue data rather
than reading Excel directly.

## 21. Dummy Catalogue

The current workbook is:

```text
data/catalogue/products_dummy.xlsx
```

It contains 9 illustrative products.

The product images supplied for the exercise are real uploaded images,
but the product IDs, descriptions, prices, dates, availability and URLs
are dummy assumptions.

The dummy catalogue must not be treated as production business data.

## 22. Vendor Independence Principle

No catalogue processing component should depend on a particular:

- Cloud provider.
- Hosting provider.
- Vector database.
- LLM provider.
- Media provider.

Standard Python data structures, file formats, HTTP interfaces, SQL and
portable database concepts are preferred.

## 23. Day 4 Outcome

Day 4 successfully established:

```text
Excel Catalogue
      ↓
Excel Reader
      ↓
Validation
      ↓
Normalization
      ↓
Clean Product Records
```

All 9 dummy products currently pass the complete pipeline.

## 24. Next Decision Area

Day 5 will focus on database design.

The database schema will be designed before selecting or deploying a
hosted database service.

The design will preserve:

- Stable product IDs.
- Structured multi-value attributes.
- Flexible category-specific attributes.
- Product availability.
- Future search/RAG requirements.
- Vendor independence.
