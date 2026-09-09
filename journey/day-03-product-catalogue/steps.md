# Day 3 — Product Catalogue Foundation

## Objective

Define the rules for converting the Urban Aanchol Excel catalogue into clean,
consistent product records that can later be loaded into PostgreSQL and used
by search and RAG.

## Step 1 — Confirm the source of truth

The Urban Aanchol product catalogue is maintained primarily in Excel.

Excel is the business-friendly source of truth.

The application database will be a derived/operational copy used by the
website, search, chatbot, and RAG system.

---

## Step 2 — Product ID

`product_id` must uniquely identify a product.

Example:

- UA-0001
- UA-0002
- UA-0003

Once assigned, a product ID should not be casually reused for another product.

---

## Step 3 — Required vs optional fields

Core fields such as product ID, product name, category, price, availability,
and description should normally be populated.

Optional fields such as brand, collection, pattern, border, video URL,
and remarks may be blank when they are not applicable.

A blank value is preferable to invented information.

---

## Step 4 — Category

`category` determines the type of product.

Examples:

- Saree
- Blouse
- Dupatta
- Jewelry
- Accessories
- Other

Category-specific information should not be forced into unrelated fields.

---

## Step 5 — Multiple values

The following fields may contain multiple comma-separated values:

- colour
- secondary_colour
- occasion
- style
- mood
- tags

Example:

`occasion = Durga Puja, Wedding, Party`

Example:

`tags = red, festive, traditional, gold border`

These values will later be normalized during database/indexing if necessary.

---

## Step 6 — Price

`price` represents the selling price in Indian Rupees.

Use numeric values rather than storing the currency symbol inside the value.

Example:

`4999`

not:

`₹4,999`

The website can format the numeric value as Indian currency.

---

## Step 7 — Availability

Availability must be explicit.

Possible initial values:

- Available
- Sold
- Reserved
- Inactive

Only products marked `Available` should normally be recommended as
currently purchasable.

---

## Step 8 — Dates

Use dates consistently:

- `launch_date` — when the product/collection was launched
- `created_date` — when the catalogue record was created
- `last_updated` — when the catalogue record was last changed

---

## Step 9 — Description

The description should contain useful customer-facing information.

It should describe the product rather than repeat structured fields unnecessarily.

Avoid unsupported claims.

---

## Step 10 — Remarks

`remarks` is intended for general or internal notes.

It should not become the primary source for structured filtering.

Important customer-facing attributes should have proper catalogue fields.

---

## Step 11 — Media

The catalogue stores URLs rather than binary image/video data.

Current fields:

- `image_url`
- `video_url`

Multiple media assets can be supported later through a separate product-media
structure without changing the core product model.

---

## Step 12 — Unknown information

Never invent catalogue information.

If information is unknown:

- leave the field blank, or
- mark it as unavailable where appropriate.

The RAG chatbot must not infer unsupported product facts as if they were
catalogue facts.

---

## Step 13 — Future flexibility

Future category-specific attributes will be handled using a flexible structure,
such as PostgreSQL `JSONB`, rather than continually adding large numbers of
columns to the Excel catalogue.

---

## Completion Criteria

The Excel catalogue has a documented and repeatable interpretation model
suitable for future database import and RAG indexing.