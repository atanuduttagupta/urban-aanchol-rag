# Day 4 — Catalogue Validation & Import Foundation

## Objective

Build the foundation for safely reading, validating, and normalizing
the Urban Aanchol product catalogue before it is stored in a database
or used by the RAG system.

## Pipeline

Excel Catalogue
↓
Excel Reader
↓
Raw Product Records
↓
Validator
↓
Normalized Product Records

Invalid catalogue data must stop the pipeline before database import
or RAG processing.

## Work Completed

### 1. Excel Reader

Created:

`backend/app/catalogue/excel_reader.py`

The reader:

- Opens the `Products` worksheet.
- Dynamically locates the catalogue header row.
- Does not assume that headers are on a fixed Excel row.
- Reads all product records.
- Preserves Excel dates and numeric values.

Verified with the dummy catalogue:

- 24 headers detected.
- 9 products loaded.

### 2. Catalogue Schema

Created:

`backend/app/catalogue/schema.py`

Defines:

- Expected 24 catalogue columns.
- Allowed product categories.
- Allowed availability values.

### 3. Catalogue Validator

Created:

`backend/app/catalogue/validator.py`

Validation currently checks:

- Required product ID.
- Required product name.
- Valid product category.
- Valid availability.
- Numeric price.
- Non-negative price.
- Valid date fields.
- Missing columns.
- Unexpected columns.
- Duplicate column names.
- Duplicate product IDs.

### 4. Validation Tests

Created:

`backend/app/catalogue/test_validator.py`

The validator was tested with:

- Valid catalogue → passed.
- Negative price → correctly detected.
- Duplicate product ID → correctly detected.

The clean catalogue currently validates successfully:

```text
Products validated: 9
Validation errors: 0
Catalogue validation passed.
```

### 5. Reusable Validation Command

Created:

`backend/app/catalogue/validate.py`

The catalogue can be validated using:

```powershell
python -m backend.app.catalogue.validate
```

### 6. Catalogue Normalization

Created:

`backend/app/catalogue/normalizer.py`

Normalization converts business-friendly Excel values into
application-friendly structures.

Examples:

```text
"Everyday, Office Wear"
```

becomes:

```python
["Everyday", "Office Wear"]
```

The following fields are normalized as lists:

- occasion
- style
- mood
- tags

Prices are normalized to `Decimal`.

Excel datetime values are normalized to Python `date`.

### 7. Combined Catalogue Pipeline

Created:

`backend/app/catalogue/pipeline.py`

The combined pipeline performs:

```text
Read
↓
Validate
↓
Normalize
```

Invalid data causes the pipeline to stop.

The pipeline was successfully tested with all 9 dummy products.

## Current Catalogue Flow

```text
products_dummy.xlsx
        ↓
   Excel Reader
        ↓
   Raw Records
        ↓
    Validator
        ↓
   Normalizer
        ↓
Normalized Products
```

## Architectural Principles

- Excel remains the business-friendly catalogue source.
- Validation happens before database import.
- Normalized records are independent of Excel formatting.
- The application should not depend on a fixed Excel header row.
- Product IDs must remain stable.
- The database and RAG system should consume normalized records.
- The design remains independent of a specific database or hosting provider.

## Files Added

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
```

## Day 4 Outcome

The Urban Aanchol catalogue now has a tested foundation for:

- Reading Excel data.
- Validating catalogue quality.
- Detecting invalid records.
- Normalizing product attributes.
- Preparing clean product records for database import.

## Next Day

Day 5 will focus on database design and the first local PostgreSQL
integration.

We will design the database before introducing database infrastructure.
