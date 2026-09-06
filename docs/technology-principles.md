# Urban Aanchol — Technology Principles

## 1. Zero Cost First

The project should use free or open-source options wherever practical.

Paid services should only be considered when genuinely necessary.

## 2. No Vendor Lock-In

Avoid designing the application around provider-specific features.

Prefer:

- Standard HTTP APIs
- PostgreSQL
- SQL
- Files
- Standard REST APIs
- Portable Python code
- Canonical HTTPS media URLs

## 3. Replaceable Components

The following should use abstraction layers where practical:

- LLM provider
- Embedding model
- Vector database
- Media storage
- Hosting
- Retrieval engine

## 4. Simple Before Complex

Start with the simplest architecture that solves the problem.

Do not introduce agentic RAG, multimodal RAG, or other advanced components before they provide real value.

## 5. Excel as Initial Catalogue Source

Product information will initially be maintained in Excel.

The system should eventually support automated synchronization from Excel / Google Sheets into the application database and retrieval index.

## 6. Product Availability Matters

Availability must be part of product data and retrieval logic.

Sold or reserved products should not be presented as available.

## 7. Grounded Answers

The chatbot should answer using retrieved boutique/product information.

If reliable information cannot be found, it should say so rather than hallucinating.

## 8. Security and Privacy

Collect only information required for the business workflow.

Do not expose internal system instructions, private data, or administrative information through the chatbot.

## 9. Production Quality

The MVP should look like a real boutique website.

Simplify functionality if necessary, but do not compromise unnecessarily on presentation quality.

## 10. Development Constraint

Development will proceed incrementally with approximately one hour of work per day.