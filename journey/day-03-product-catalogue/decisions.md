# Day 3 — Product Catalogue Decisions

## 1. Catalogue scope

The catalogue is an **Urban Aanchol Product Catalogue**, not a saree-only
catalogue.

The system must support products such as:

- Saree
- Blouse
- Dupatta
- Jewelry
- Accessories
- Other

`category` is therefore a core product attribute.

---

## 2. Excel as source of truth

Excel remains the business-friendly source of truth for catalogue management.

The application database will contain a derived/operational copy for:

- Website catalogue
- Search
- Recommendations
- RAG
- Availability checks

---

## 3. Product identification

Every product receives a stable unique `product_id`.

Example:

`UA-0001`

Product IDs should remain stable even when other product information changes.

---

## 4. Flexible multi-value fields

The following fields support comma-separated values in Excel:

- colour
- secondary_colour
- occasion
- style
- mood
- tags

This keeps catalogue maintenance simple for the boutique while allowing
multiple values per product.

---

## 5. Remarks

A `remarks` field is included for general/internal notes.

It is not intended to replace structured catalogue attributes.

Important searchable/filterable information should have a proper field.

---

## 6. Category-specific attributes

We will not create many category-specific Excel columns.

For example, blouse-specific or jewelry-specific attributes should not force
irrelevant columns onto every product.

A future PostgreSQL implementation may use:

`additional_attributes JSONB`

for flexible category-specific information.

---

## 7. Dates

The catalogue includes:

- `launch_date`
- `created_date`
- `last_updated`

These support product lifecycle information and future Excel-to-database
synchronization.

---

## 8. Availability

Availability is an explicit product attribute.

Initial logical states include:

- Available
- Sold
- Reserved
- Inactive

The recommendation system should normally recommend only products that are
currently available.

---

## 9. Media

The V1 catalogue keeps:

- `image_url`
- `video_url`

Media files themselves are not stored inside the database.

The architecture should later support multiple media assets without requiring
columns such as `image_url_1`, `image_url_2`, etc.

---

## 10. Data quality

The system must not invent missing product information.

Unknown information should remain blank or be represented appropriately.

This is particularly important because catalogue data will become a source
for the RAG chatbot.

---

## 11. Vendor independence

The catalogue schema uses standard data concepts and URLs.

It should remain independent of any particular:

- Hosting provider
- Database provider
- Vector database
- LLM provider
- Media provider

---

## 12. Future synchronization

A future automated pipeline will synchronize:

Excel / Google Sheets
→ validated product records
→ PostgreSQL
→ search/indexing
→ RAG

The synchronization process should detect additions, updates, and availability
changes.

---

## 13. Dummy catalogue

The current workbook contains dummy commercial information for development.

The supplied product images are real images provided for development, but
dummy names, prices, URLs, and other catalogue values must not be treated as
real production information.

The dummy workbook must not be published as the live catalogue without
validation and replacement of the illustrative data.

## 14. Multi-value field normalization

Excel multi-value fields use comma-separated values for business-friendly
catalogue maintenance.

Applicable fields include:

- `colour`
- `secondary_colour`
- `occasion`
- `style`
- `mood`
- `tags`

During future import/synchronization:

- commas are treated as separators
- leading and trailing whitespace is removed
- empty values are ignored
- accidental duplicate values are removed
- original human-friendly capitalization is preserved
- blank fields remain valid
- search-specific normalization can be applied separately

Excel remains simple and human-readable; structured normalization is handled
by the import/data pipeline.

## 15. Numeric and date field normalization

### Price

`price` is stored as a numeric value representing Indian Rupees.

Excel should contain:

`4999`

rather than:

`₹4,999`

The application can format the value for display.

Price must be greater than or equal to zero.

### Dates

The following fields are date fields:

- `launch_date`
- `created_date`
- `last_updated`

They should be stored as actual Excel dates where possible rather than
free-form text.

The future import pipeline will convert them into a standard database date or
timestamp representation.

### Data validation

The future import process should detect:

- invalid prices
- negative prices
- invalid dates
- missing required fields
- duplicate product IDs
- invalid availability values

Invalid records should be reported rather than silently corrected.

## 16. Excel processing library

Python `openpyxl` will be used for reading and processing `.xlsx` catalogue
files.

The dependency is recorded in:

- `backend/requirements.txt` — direct project dependency
- `backend/requirements-lock.txt` — exact installed environment versions

The application should keep Excel processing behind a small internal data
import/validation layer so that the rest of the system remains independent
of the Excel library.