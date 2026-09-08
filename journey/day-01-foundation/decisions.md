# Day 1 — Technical Decisions

## 1. Project Goal

### Decision

Build a responsive website for the Urban Aanchol home-based saree boutique with an AI-powered RAG chatbot.

The website will eventually support:

- Saree catalogue browsing
- Saree discovery and recommendations
- Natural-language product questions
- Saree-related educational content
- Boutique/business information
- WhatsApp-based customer enquiries and ordering

### Business Context

The current business workflow is:

1. Products are advertised mainly through Facebook and Instagram.
2. Customers enquire through phone or WhatsApp.
3. Availability is confirmed manually.
4. Customers prepay.
5. The saree is delivered.

The website and chatbot should improve discovery and customer assistance without unnecessarily changing this business model.

---

## 2. Primary Project Constraint — Zero Cost / Free First

### Decision

The project must follow:

```text
Zero cost / Free-first
```

This is the highest-priority project constraint.

### Rule

Whenever we choose a technology or service, we should first look for:

1. Free/open-source options
2. Self-hosted options where practical
3. Portable alternatives
4. Paid options only when genuinely necessary

If a feature cannot reasonably be implemented within the zero-cost constraint, it can be postponed or removed from the MVP.

---

## 3. Vendor Independence

### Decision

Avoid vendor lock-in from the beginning.

The architecture should allow major components to be replaced without rebuilding the entire application.

This applies to:

- Hosting
- Database
- LLM
- Embedding model
- Vector database
- Media storage
- Search
- Payment services

### Preferred principles

Use portable technologies and standards such as:

```text
HTTP
JSON
SQL
PostgreSQL
HTTPS URLs
Files
Environment variables
Git
Docker when useful
```

Provider-specific functionality should be isolated rather than spread throughout the application.

---

## 4. Development Time

### Decision

Development will be limited to approximately:

```text
Maximum 1 hour per day
```

### Approach

The project will be built incrementally:

```text
Small task
   ↓
Test
   ↓
Document
   ↓
Commit
   ↓
Next task
```

### Reason

Small daily steps make the project manageable and reduce the risk of large debugging sessions.

---

## 5. MVP First

### Decision

Build an impressive but focused MVP before advanced AI features.

The MVP should prioritize:

- Professional responsive website
- Saree catalogue
- Product information
- Text-based RAG chatbot
- Natural-language saree discovery
- Basic conversational follow-up
- Business/FAQ information
- Availability-aware recommendations
- WhatsApp contact/order flow

Advanced features such as voice, image similarity, multimodal RAG, agentic retrieval, and virtual try-on will come later.

### Principle

Simplify functionality where necessary, but do not make the website look like a developer prototype.

---

## 6. Frontend Direction

### Decision

Use:

```text
HTML5
CSS3
JavaScript
```

as the initial frontend foundation.

### Reason

This provides:

- Zero software cost
- Minimal dependencies
- Easy debugging
- Portability
- Low complexity
- No framework lock-in

A frontend framework can be considered later if the application complexity justifies it.

---

## 7. Backend Direction

### Decision

Use:

```text
Python
FastAPI
```

for the backend API.

### Reason

Python is well suited to the future RAG/AI requirements.

FastAPI provides a lightweight standard HTTP API layer and can integrate with:

- Databases
- Embedding models
- Retrieval systems
- LLMs
- Future AI services

The detailed backend implementation was intentionally deferred from Day 1.

---

## 8. Database Direction

### Decision

Plan for:

```text
PostgreSQL + pgvector
```

as the initial database direction.

### Reason

PostgreSQL can potentially provide both:

- Structured catalogue storage
- Vector similarity search through pgvector

This may reduce infrastructure complexity and cost.

### Day 1 scope

No database was installed or configured on Day 1.

The database decision remains an architectural direction to be implemented in a later phase.

---

## 9. Catalogue Source of Truth

### Decision

The boutique's product catalogue will initially be maintained in:

```text
Excel / Google Sheets
```

### Reason

This is practical for a small boutique and avoids forcing catalogue maintenance into a technical database.

The future architecture should support synchronization:

```text
Excel / Google Sheets
        ↓
Structured catalogue
        ↓
Database
        ↓
Search / RAG
```

---

## 10. Media Strategy

### Decision

Product images and videos should ultimately be referenced through standard HTTPS URLs.

The catalogue can contain the corresponding image/video URLs.

### Reason

This keeps product data portable and allows the underlying media provider to be changed later.

Potential media-storage providers will be evaluated during the catalogue/media phase rather than being permanently selected on Day 1.

---

## 11. LLM Strategy

### Decision

Do not permanently commit the project to one LLM provider.

### Reason

The project has a strict zero-cost/free-first requirement and provider pricing/free quotas can change.

The future RAG system should use a replaceable LLM interface so that the provider/model can be changed without redesigning the whole application.

Possible future options include free or open-source models/providers.

---

## 12. Embedding Strategy

### Decision

Prefer open-source embedding models where practical.

### Reason

This supports:

- Zero/free-first development
- Local experimentation
- Vendor independence
- Easier migration between infrastructure providers

The exact embedding model will be selected when RAG implementation begins.

---

## 13. RAG Evolution

### Decision

The RAG architecture will evolve incrementally.

Planned progression:

```text
Structured product data
        ↓
Keyword / exact search
        ↓
Vector search
        ↓
Hybrid search
        ↓
Reranking
        ↓
Conversational retrieval
        ↓
Agentic retrieval
        ↓
Image similarity
        ↓
Multimodal RAG
```

### Reason

This avoids introducing advanced complexity before the simpler retrieval foundations are working.

---

## 14. Future AI Capabilities

### Decision

Advanced capabilities are planned but are not part of Day 1 implementation.

Potential future stages include:

- Conversational recommendation agent
- Voice input
- Image similarity search
- Multimodal RAG
- Advanced agentic retrieval
- Optional virtual try-on

These will only be added when they provide meaningful business value and can be implemented within the project's cost and time constraints.

---

## 15. Saree Guide

### Decision

The website should have a dedicated:

```text
Saree Guide
```

section.

### Purpose

It will allow the boutique to publish useful saree-related content, including topics such as:

- How sarees are made
- Saree fabric guides
- Washing and care
- Storage
- Draping
- Occasion/style guides
- Other future educational topics

### Architectural principle

New guide topics should be addable without changing the main website structure.

Guide content can later become part of the RAG knowledge base.

---

## 16. Ordering Strategy

### Decision

The MVP should prioritize:

```text
WhatsApp enquiry/order
```

rather than building a complete e-commerce checkout.

### Reason

The current business process already relies on:

- Phone
- WhatsApp
- Manual availability confirmation
- Prepayment
- Delivery

A full shopping cart and payment system would add unnecessary complexity and cost during the MVP stage.

---

## 17. Availability as a First-Class Data Attribute

### Decision

Product availability must eventually be represented explicitly in the catalogue.

Possible states:

```text
available
reserved
sold
inactive
```

### Reason

The RAG chatbot must not recommend a sold or reserved saree as currently available.

Availability should be handled by retrieval/filtering logic rather than relying solely on the LLM.

---

## 18. Responsive Web Application

### Decision

Build one responsive web application.

### Target devices

- Android
- iPhone
- iPad
- Windows
- macOS

### Reason

A responsive website provides broad device coverage without the cost and maintenance burden of separate native applications.

A PWA may be considered later if it provides clear value.

---

## 19. Git and GitHub

### Decision

Use Git and GitHub as the project's source-control foundation.

Repository:

```text
urban-aanchol-rag
```

### Purpose

Git provides:

- Version history
- Safe incremental development
- Recovery from mistakes
- Collaboration capability
- A permanent technical record

GitHub provides the remote repository and long-term project source of truth.

---

## 20. Project Structure

### Decision

Use a clear separation between application code, documentation, data, troubleshooting, and the learning/build journey.

Initial structure:

```text
urban-aanchol-rag/
├── backend/
├── frontend/
├── data/
├── docs/
├── journey/
└── issues/
```

### Purpose

- `backend/` → API and backend code
- `frontend/` → website code
- `data/` → catalogue/data-related files
- `docs/` → current architecture and project documentation
- `journey/` → day-by-day development record
- `issues/` → troubleshooting and lessons learned

---

## 21. Documentation Strategy

### Decision

Documentation is part of the project, not an afterthought.

Each development day should record:

```text
What was done
How it was done
Why decisions were made
Problems encountered
How problems were resolved
```

### Reason

This allows the project to remain understandable even after a long break and provides a reproducible history of the build.

---

## 22. Day 1 Scope

### Decision

Keep Day 1 deliberately small.

Day 1 was limited to:

- Establishing the project direction
- Defining the architecture
- Defining MVP scope
- Defining technology principles
- Creating the repository
- Creating the initial project structure
- Establishing documentation and issue-tracking structure
- Creating the first Git commit

### Explicitly deferred

The following were intentionally NOT implemented on Day 1:

- Database
- RAG
- Vector database
- LLM integration
- AI packages
- API implementation
- Frontend implementation
- Deployment

This separation keeps the foundation clean before implementation begins.

---

## 23. Day 1 Outcome

At the end of Day 1, the project had:

- GitHub repository
- Initial project structure
- Architecture documentation
- MVP documentation
- Technology principles
- Journey documentation
- Issue-management structure
- Initial Git commit
- Clean Git working tree

The implementation phase begins from Day 2.

---

## Overall Day 1 Principle

Build the project foundation first.

The architecture should remain:

```text
Simple
Portable
Zero-cost-first
Vendor-independent
Incremental
AI-ready
```

The goal is to avoid premature technical complexity while keeping the design capable of evolving into a production-quality RAG-powered saree boutique platform.
