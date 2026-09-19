# Day 1 — Foundation & Architecture

## Objective

Establish the initial development foundation for the Urban Aanchol website and RAG chatbot: create the GitHub repository, configure the development environment, establish the project structure, define the architecture and MVP principles, and create a reproducible project journey and issue-management structure.

## Business Context

Urban Aanchol is a home-based saree boutique. The current business workflow is:

- Products are advertised primarily through Facebook and Instagram.
- Customers enquire through phone or WhatsApp.
- Availability is confirmed manually.
- Customers prepay.
- Sarees are delivered.

The planned website will provide a digital catalogue and an AI-powered RAG chatbot to help customers discover sarees and obtain accurate boutique/business information without unnecessarily changing the existing ordering model.

## Core Project Principles

### Zero Cost / Free First

This is the highest-priority constraint.

Technology choices should prefer:

1. Free and open-source options
2. Self-hosted options where practical
3. Portable alternatives
4. Paid services only when genuinely necessary

If a feature cannot reasonably meet the zero-cost requirement, it can be postponed or removed from the MVP.

### Vendor Independence

Avoid vendor lock-in from the beginning. Major components should be replaceable without rebuilding the entire application.

Prefer portable standards and technologies such as:

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

### MVP First

Build a focused but professional MVP before advanced AI features.

Initial priorities:

- Responsive website
- Product catalogue
- Product information
- Text-based RAG chatbot
- Natural-language saree discovery
- Basic conversational follow-up
- Business/FAQ information
- Availability-aware recommendations
- WhatsApp enquiry/order flow

Advanced capabilities such as voice, image similarity, multimodal RAG, agentic retrieval and virtual try-on are intentionally deferred.

The website should look like a real boutique website rather than a developer prototype, even when functionality is deliberately kept simple.

### Incremental Development

The project follows:

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

This keeps development manageable and creates a reproducible technical history.

## Day 1 Work Completed

### Development Environment

- Verified Windows development environment
- Verified VS Code
- Verified Git
- Installed Python 3.11.9
- Selected Python 3.11 for the project
- Created and activated the project virtual environment
- Configured VS Code to use the project's Python 3.11 environment

Python 3.13 can remain installed on the computer; the project runtime is Python 3.11 for broader AI/ML ecosystem compatibility.

### GitHub

Created the public repository:

```text
urban-aanchol-rag
```

Initial repository setup included:

- README
- Python `.gitignore`
- Local Git repository
- Remote GitHub connection
- Initial commit
- Push to GitHub

### Initial Project Structure

```text
urban-aanchol-rag/
├── backend/
├── frontend/
├── data/
├── docs/
├── journey/
└── issues/
```

Purpose:

| Folder | Purpose |
|---|---|
| `backend/` | Backend/API application |
| `frontend/` | Website |
| `data/` | Catalogue and data-related files |
| `docs/` | Architecture and project documentation |
| `journey/` | Day-by-day development record |
| `issues/` | Troubleshooting and lessons learned |

### Permanent Documentation

Created:

```text
docs/
├── architecture.md
├── mvp.md
└── technology-principles.md
```

These capture the planned architecture, MVP scope and technology principles.

### Journey Documentation

Established the development journey structure:

```text
journey/
├── README.md
└── day-01-foundation/
    ├── README.md
    ├── steps.md
    └── decisions.md
```

This consolidated Day 1 README is the cleaned replacement for the three original Day 1 files.

### Issue Management

Established a common issue structure outside individual day folders:

```text
issues/
├── README.md
├── python/
├── vscode/
├── git-github/
├── frontend/
├── backend/
├── database/
├── rag/
└── deployment/
```

Issues are kept separately so they can be referenced across multiple development days.

### Git Ignore

Configured Git to exclude the local Python virtual environment:

```text
.venv/
```

Secrets and other environment-specific files will also be excluded as the project evolves.

## Architecture Decisions Established

### Frontend

Initial frontend foundation:

```text
HTML5
CSS3
JavaScript
```

Reason: zero software cost, low complexity, easy debugging, portability and minimal framework lock-in.

### Backend

Initial backend direction:

```text
Python
FastAPI
```

Reason: Python aligns well with future RAG/AI requirements, while FastAPI provides a lightweight standard HTTP API layer.

### Database

Planned database direction:

```text
PostgreSQL + pgvector
```

Reason: PostgreSQL can provide structured catalogue storage together with vector similarity search through pgvector, potentially reducing infrastructure complexity and cost.

No database implementation was part of Day 1.

### Catalogue Source of Truth

Initial catalogue maintenance:

```text
Excel / Google Sheets
```

Planned evolution:

```text
Excel / Google Sheets
        ↓
Structured catalogue
        ↓
Database
        ↓
Search / RAG
```

### Media

Product images and videos should ultimately be referenced through standard HTTPS URLs. The exact media-storage provider is deferred until the catalogue/media phase.

### LLM and Embeddings

The project will not be permanently tied to one LLM or embedding provider.

The design should allow models/providers to be replaced, with open-source and free-first options preferred.

### RAG Evolution

The intended retrieval evolution is:

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

The advanced stages are architectural direction, not Day 1 implementation.

### Saree Guide

A dedicated `Saree Guide` section is planned for useful content such as:

- Saree making
- Fabric guides
- Washing and care
- Storage
- Draping
- Occasion/style guidance

New topics should be addable without changing the main website structure. Guide content can later become part of the RAG knowledge base.

### Ordering

The MVP will prioritize:

```text
WhatsApp enquiry/order
```

rather than a full cart and checkout.

This fits the existing workflow of manual availability confirmation, prepayment and delivery while avoiding unnecessary MVP complexity and cost.

### Availability

Availability is intended to be a first-class product attribute because the RAG system must not present unavailable products as currently available.

### Responsive Web

One responsive web application is planned for:

- Android
- iPhone
- iPad
- Windows
- macOS

A PWA may be considered later if it provides clear value.

## Day 1 Issue

### Python / VS Code Interpreter

Python 3.11.9 was installed, but VS Code initially used Python 3.13.9.

Resolution:

- Select `Python: Select Interpreter` in VS Code.
- Select the project's Python 3.11 / `.venv` environment.
- Verify with:

```powershell
python --version
```

Expected:

```text
Python 3.11.9
```

The issue was documented in the common issue structure.

## Reproducible Day 1 Setup

The essential setup sequence was:

1. Create the `urban-aanchol-rag` GitHub repository.
2. Clone it locally.
3. Verify Git and Python.
4. Verify/install Python 3.11.9.
5. Create `.venv` with Python 3.11.
6. Activate the environment.
7. Configure VS Code to use `.venv`.
8. Create `backend`, `frontend`, `data`, `docs`, `journey` and `issues`.
9. Create architecture, MVP and technology-principles documentation.
10. Establish the journey and issue-management structures.
11. Configure `.gitignore`.
12. Review Git status and ensure `.venv` is not tracked.
13. Commit the foundation:

```powershell
git commit -m "docs: establish project architecture and Day 1 foundation"
```

14. Push to GitHub:

```powershell
git push origin main
```

15. Verify:

```powershell
git status
```

Expected:

```text
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

## Day 1 Completion Checklist

- [x] GitHub repository created
- [x] Git verified
- [x] Python 3.11.9 installed
- [x] Python 3.11 virtual environment created
- [x] VS Code configured for Python 3.11
- [x] Initial project folders created
- [x] Architecture documentation created
- [x] MVP documentation created
- [x] Technology principles documented
- [x] Development journey structure created
- [x] Common issue structure created
- [x] `.venv` excluded from Git
- [x] Python / VS Code issue documented
- [x] Initial commit created
- [x] Changes pushed to GitHub
- [x] Repository synchronization verified

## Day 1 Outcome

The Urban Aanchol project now has a documented, version-controlled and vendor-independent foundation.

The implementation phase can begin from Day 2.

**Next:** Day 2 — Project Setup
