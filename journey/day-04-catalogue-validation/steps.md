# Day 4 — Steps: Catalogue Validation & Import Foundation

## Objective

Build and verify the foundation that reads the Urban Aanchol Excel
catalogue, validates its structure and data, normalizes the records,
and produces clean product records ready for database import.

## Step 1 — Confirm the Day 4 Structure

Created:

```text
journey/day-04-catalogue-validation/
├── README.md
├── steps.md
└── decisions.md

backend/app/catalogue/
└── __init__.py
```

## Step 2 — Build the Excel Reader

Created:

```text
backend/app/catalogue/excel_reader.py
```

The reader:

- Opens the `Products` worksheet.
- Locates the header row dynamically.
- Does not assume the headers are on a fixed Excel row.
- Reads product records into dictionaries.
- Preserves numeric and date values.

Test file:

```text
backend/app/catalogue/test_excel_reader.py
```

Test command:

```powershell
python -m backend.app.catalogue.test_excel_reader
```

Verified:

```text
Headers found: 24
Products read: 9
```

The first product was also inspected to confirm that the fields were
mapped correctly.

## Step 3 — Define the Catalogue Schema

Created:

```text
backend/app/catalogue/schema.py
```

Defined:

- The expected 24 catalogue fields.
- Allowed product categories:
  - Saree
  - Blouse
  - Dupatta
  - Jewelry
  - Accessories
  - Other
- Allowed availability values:
  - Available
  - Sold
  - Reserved
  - Inactive

Syntax was verified using:

```powershell
python -m py_compile backend\app\catalogue\schema.py
```

## Step 4 — Build the Catalogue Validator

Created:

```text
backend/app/catalogue/validator.py
```

The validator checks:

- Required product ID.
- Required product name.
- Valid category.
- Valid availability.
- Required price.
- Numeric price.
- Non-negative price.
- Valid date values.
- Missing columns.
- Unexpected columns.
- Duplicate column names.
- Duplicate product IDs.

## Step 5 — Test Valid Catalogue Data

Created:

```text
backend/app/catalogue/test_validator.py
```

The test loads the Excel catalogue and runs validation.

Test command:

```powershell
python -m backend.app.catalogue.test_validator
```

Verified:

```text
Products validated: 9
Validation errors: 0
Catalogue validation passed.
```

## Step 6 — Test Negative Price Detection

A temporary test change set the first product price to:

```python
products[0]["price"] = -100
```

The validator correctly detected:

```text
price cannot be negative
```

The temporary test change was then removed.

## Step 7 — Test Duplicate Product ID Detection

A temporary test change assigned the first product's ID to the
second product:

```python
products[1]["product_id"] = products[0]["product_id"]
```

The validator correctly detected:

```text
duplicate product_id 'UA-0001'
```

The temporary test change was then removed.

## Step 8 — Create a Reusable Validation Command

Created:

```text
backend/app/catalogue/validate.py
```

This provides a reusable catalogue validation entry point.

Command:

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

## Step 9 — Build Catalogue Normalization

Created:

```text
backend/app/catalogue/normalizer.py
```

Normalization rules:

### Multi-value fields

The following comma-separated Excel values are converted into lists:

- occasion
- style
- mood
- tags

Example:

```text
Everyday, Office Wear
```

becomes:

```python
["Everyday", "Office Wear"]
```

### Price

Prices are normalized to `Decimal`.

Example:

```text
2450
```

becomes:

```python
Decimal("2450")
```

### Dates

Excel datetime values are normalized to Python `date` values.

## Step 10 — Test Normalization

Created:

```text
backend/app/catalogue/test_normalizer.py
```

Test command:

```powershell
python -m backend.app.catalogue.test_normalizer
```

Verified:

```text
Products normalized: 9
```

The first product was inspected and confirmed to contain:

- List-based `occasion`.
- List-based `style`.
- List-based `mood`.
- List-based `tags`.
- `Decimal` price.
- `date` values for catalogue dates.

## Step 11 — Build the Combined Catalogue Pipeline

Created:

```text
backend/app/catalogue/pipeline.py
```

The pipeline combines:

```text
Read
↓
Validate
↓
Normalize
```

If validation errors exist, the pipeline stops and does not return
normalized catalogue data.

The main function is:

```python
load_catalogue(file_path)
```

A convenience function was also created:

```python
load_default_catalogue()
```

## Step 12 — Test the Complete Pipeline

Created:

```text
backend/app/catalogue/test_pipeline.py
```

Test command:

```powershell
python -m backend.app.catalogue.test_pipeline
```

Verified:

```text
Products loaded through pipeline: 9
```

The first normalized product was inspected successfully.

## Final Day 4 Architecture

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

## Day 4 Validation Principles

- Invalid catalogue data must not proceed to database import.
- Excel formatting should not dictate application structure.
- Multi-value business fields are normalized before application use.
- Product IDs must remain stable and unique.
- Catalogue validation should be reusable.
- The normalized product representation should remain independent
  of the eventual database provider.

## Files Created or Updated

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

## Day 4 Completion Criteria

- [x] Excel reader works.
- [x] Dynamic header detection works.
- [x] 24 catalogue fields are recognized.
- [x] Catalogue validation works.
- [x] Invalid negative price is detected.
- [x] Duplicate product ID is detected.
- [x] Catalogue normalization works.
- [x] Combined read → validate → normalize pipeline works.
- [x] All 9 dummy products pass the clean pipeline.

## Next Day

Day 5 will begin with database design.

We will design the PostgreSQL data model before installing or selecting
any hosted database service. The design will remain vendor-independent
and compatible with the existing normalized catalogue pipeline.
