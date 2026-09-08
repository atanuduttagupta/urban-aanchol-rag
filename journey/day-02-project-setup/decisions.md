# Day 2 — Technical Decisions

## 1. Python Version

### Decision

Use:

```text
Python 3.11.9
```

### Reason

Python 3.11 provides a mature and broadly compatible foundation for the AI, RAG, web, and machine-learning ecosystem we expect to use later.

Python 3.13 is installed on the system, but it is not required for this project.

### Project rule

Use Python 3.11 for the Urban Aanchol project unless a future dependency requires a deliberate change.

---

## 2. Backend Framework

### Decision

Use:

```text
FastAPI
```

with:

```text
Uvicorn
```

as the development ASGI server.

### Reason

FastAPI is suitable because it is:

- Python-based
- Open-source
- Lightweight
- Easy to learn and maintain
- Well suited for REST APIs
- Automatically documented through OpenAPI/Swagger
- Easy to integrate with RAG and AI components
- Portable across hosting providers

### Vendor-independence consideration

The backend will expose standard HTTP/JSON APIs rather than relying on proprietary hosting-specific APIs.

This should make the backend easier to move between providers later.

---

## 3. Frontend Technology

### Decision

Start with:

```text
HTML5
CSS3
JavaScript
```

without introducing a frontend framework at this stage.

### Reason

This gives us:

- Zero software cost
- Minimal dependencies
- Fast development
- Easy debugging
- Excellent portability
- No framework lock-in
- Easy deployment to static hosting
- Easy replacement or migration later

A framework such as React can be introduced later if the website becomes complex enough to justify it.

### Project rule

Do not introduce a frontend framework merely because it is popular. Introduce one only when it provides a clear benefit to the project.

---

## 4. API Design

### Decision

Use standard HTTP/JSON API principles.

Current endpoints:

```text
GET /
GET /health
```

### Reason

A standard API contract allows the frontend, chatbot, mobile browser, future PWA, or another client to communicate with the backend without depending on a particular vendor.

### Future direction

As the project grows, APIs should remain clearly separated from:

- Database implementation
- LLM provider
- Vector database
- Media storage provider
- Hosting provider

---

## 5. Database Direction

### Decision

No production database was introduced on Day 2.

The planned database direction is:

```text
PostgreSQL + pgvector
```

when catalogue and RAG development begins.

### Reason

PostgreSQL can potentially handle both:

- Structured product/catalogue data
- Vector embeddings for semantic retrieval

This can reduce unnecessary infrastructure and keep the initial architecture relatively simple.

### Vendor-independence consideration

The application should communicate with the database through a standard database layer rather than embedding provider-specific logic throughout the application.

SQLAlchemy may be introduced later to improve database abstraction and portability.

---

## 6. Catalogue Source of Truth

### Decision

The boutique's product catalogue will initially remain maintained in:

```text
Excel / Google Sheets
```

### Reason

The catalogue is already familiar and practical for boutique operations.

The website/RAG system should not force the business owner to maintain products directly inside a technical database.

### Future direction

A controlled synchronization process will eventually transform:

```text
Excel / Google Sheets
        ↓
Structured catalogue data
        ↓
PostgreSQL
        ↓
Search / RAG indexes
```

This keeps the business-facing data-entry process simple while allowing the technical system to scale.

---

## 7. Media Storage

### Decision

No media-storage provider was selected permanently on Day 2.

Candidate options will be evaluated when catalogue/media implementation begins.

Possible options include:

- Cloudinary
- Cloudflare R2
- Supabase Storage
- Google Drive

### Reason

Free limits, storage requirements, bandwidth limits, and terms can change.

We will select the option that best satisfies the project's primary requirements at the time:

1. Zero/free cost where practical
2. Reliable image/video delivery
3. Easy integration
4. Standard HTTPS URLs
5. Easy migration

### Vendor-independence rule

Product data should store canonical media URLs rather than embedding provider-specific media logic throughout the application.

---

## 8. LLM Provider

### Decision

No permanent LLM provider will be selected during Day 2.

### Reason

The project has a strict:

```text
Zero-cost / free-first
```

requirement.

LLM providers and free quotas can change over time.

### Architecture rule

The application should use an internal abstraction/interface for LLM calls so that providers can be changed later.

Possible future providers/models may include:

- Gemini
- Groq
- Open-source Hugging Face models
- Other compatible providers

The application should not make the entire RAG system dependent on one provider.

---

## 9. Vector Database

### Decision

No dedicated vector database will be introduced during Day 2.

### Planned direction

Initially evaluate:

```text
PostgreSQL + pgvector
```

before introducing a separate vector database.

Possible future alternatives include:

- Chroma
- Qdrant
- Weaviate

### Reason

A separate vector database adds infrastructure and operational complexity.

For the initial boutique catalogue, PostgreSQL + pgvector may be sufficient.

---

## 10. RAG Architecture Principle

### Decision

RAG will be added after the website and catalogue foundations are stable.

The architecture should separate:

```text
User query
    ↓
Scope / safety checks
    ↓
Query understanding
    ↓
Retrieval
    ↓
Reranking
    ↓
Grounded response
```

### Reason

The chatbot must not simply generate answers from an LLM.

It should use the boutique's actual:

- Product catalogue
- Product availability
- Prices
- Fabric information
- Saree Guide content
- Business policies
- Other approved knowledge

as its source of truth.

---

## 11. Product Availability

### Decision

Product availability will be treated as an important catalogue attribute.

Possible future values:

```text
available
sold
reserved
inactive
```

### Reason

The chatbot must not recommend a saree as available when it has already been sold or reserved.

Availability should therefore be part of retrieval/filtering logic rather than relying only on the LLM.

---

## 12. Website Ordering Model

### Decision

The initial website will prioritize:

```text
WhatsApp enquiry/order
```

rather than implementing a shopping cart and automated checkout.

### Reason

The current boutique business process involves:

1. Customer selects a saree
2. Availability is confirmed
3. Customer contacts the boutique
4. Payment is made in advance
5. Saree is delivered

A full e-commerce checkout would add unnecessary complexity and cost to the MVP.

### Future possibility

A cart/payment system can be introduced later if the business process changes.

---

## 13. Saree Guide

### Decision

The website will contain a dedicated:

```text
Saree Guide
```

section.

### Purpose

It will contain useful educational content such as:

- How sarees are made
- Fabric guides
- Washing and care instructions
- Storage guidance
- Draping tips
- Occasion/style guides
- Other useful saree-related topics

### Architectural consideration

Guide content should be structured so that new topics can be added without changing the main website architecture.

The content can later become part of the RAG knowledge base.

---

## 14. Responsive Web Application

### Decision

Build one responsive web application rather than separate native applications.

### Target devices

- Android
- iPhone
- iPad
- Windows
- macOS

### Reason

The target customers primarily need a convenient website experience.

Separate Android/iOS applications would add development and maintenance cost without providing enough MVP value.

A PWA can be considered later if it provides meaningful benefits.

---

## 15. Hosting Strategy

### Decision

No hosting provider is permanently selected during Day 2.

### Principle

The application should be deployable using standard technologies such as:

```text
Static frontend
+
Python HTTP backend
+
PostgreSQL
```

### Reason

Potential hosting providers may change their free tiers or policies.

Keeping the application portable reduces vendor lock-in.

Possible future hosting candidates include:

- GitHub Pages
- Cloudflare Pages
- Netlify
- Vercel
- Hugging Face Spaces
- Render
- Railway
- Fly.io

These are candidates, not permanent architectural dependencies.

---

## 16. Cost Principle

### Highest-priority project constraint

The project follows:

```text
Zero cost / Free-first
```

### Rule

Before introducing any paid service, evaluate whether a free or open-source alternative can provide the required functionality.

Paid services should only be considered when:

1. The free option is genuinely insufficient, and
2. The business value justifies the cost.

If a feature cannot reasonably be implemented for free, the feature can be postponed or removed from the MVP.

---

## 17. Vendor Lock-in Principle

### Decision

Avoid unnecessary dependency on any single vendor.

This applies to:

- Hosting
- Database
- LLM
- Embedding model
- Vector database
- Media storage
- Authentication
- Payment
- Search

### Preferred approach

Use portable interfaces and standards:

```text
HTTP
JSON
SQL
PostgreSQL
HTTPS URLs
Files
Environment variables
Docker (when useful)
```

Provider-specific functionality should be isolated behind replaceable components.

---

## 18. Development Approach

### Decision

Build the project incrementally.

The development cycle will generally be:

```text
Build
  ↓
Test
  ↓
Document
  ↓
Commit
  ↓
Continue
```

### Reason

The project is being developed with approximately:

```text
1 hour per day
```

Small, verifiable steps reduce the risk of large debugging sessions and make progress easier to track.

---

## 19. Git and Documentation

### Decision

GitHub will be used as the long-term source repository.

The project will maintain:

```text
docs/
journey/
issues/
```

### Purpose

- `docs/` → current architecture and project documentation
- `journey/` → historical day-by-day learning/build record
- `issues/` → troubleshooting and lessons learned

### Important principle

Documentation should describe not only what was built, but also important decisions and reasons behind them.

This will make the project easier to continue after a long break.

---

## 20. Day 2 Status

### Completed

- Python 3.11 project foundation
- FastAPI backend
- Uvicorn server
- API root endpoint
- API health endpoint
- Swagger documentation
- Dependency requirements
- Dependency lock file
- Initial responsive frontend
- Urban Aanchol visual foundation
- Website navigation
- Saree Guide section
- Frontend browser testing

### Not finalized yet

The following remain intentionally open decisions:

- Production hosting provider
- Media storage provider
- LLM provider
- Embedding model
- Vector database
- Production database deployment
- Authentication
- Payment provider

These will be evaluated when their respective phases are reached.

## Overall Day 2 Architectural Principle

Build a **simple, portable, zero-cost-first foundation** today so that more advanced AI/RAG capabilities can be added later without rebuilding the website from scratch.
