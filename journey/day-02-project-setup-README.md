# Day 2 — Project Setup

## Objective

Set up the initial Urban Aanchol backend API and frontend foundation while keeping the project simple, portable, zero-cost-first, and ready for later RAG development.

## Day 2 Principles

The following principles from the project architecture were carried into implementation:

- **Python 3.11.9** is the project runtime.
- **FastAPI + Uvicorn** provide the initial backend/API layer.
- **HTML5 + CSS3 + JavaScript** provide the initial frontend without introducing a framework prematurely.
- APIs use standard HTTP/JSON principles to reduce vendor lock-in.
- PostgreSQL + pgvector remains the planned database direction, but database implementation is deferred.
- LLM, embedding, vector-database, media-storage, hosting, and payment providers remain replaceable decisions.
- The existing boutique ordering model remains based on WhatsApp/phone enquiry, availability confirmation, prepayment, and delivery.
- Development follows an incremental Build → Test → Document → Commit workflow.

## 1. Development Environment

The project uses:

```text
Python 3.11.9
VS Code
Git
```

Python 3.13 may remain installed on the computer, but Python 3.11.9 is the selected project runtime for ecosystem compatibility.

Verify:

```powershell
py -3.11 --version
python --version
```

The project virtual environment is:

```text
.venv/
```

Activate it with:

```powershell
.\.venv\Scripts\Activate.ps1
```

## 2. Backend Setup

Created:

```text
backend/
├── requirements.txt
└── app/
    ├── __init__.py
    └── main.py
```

### Technology

- Python 3.11.9
- FastAPI 0.141.1
- Uvicorn 0.52.4

Install the initial backend dependencies with:

```powershell
python -m pip install fastapi==0.141.1 uvicorn==0.52.4
```

Direct project dependencies are recorded in:

```text
backend/requirements.txt
```

The complete environment is recorded in:

```text
backend/requirements-lock.txt
```

Generate/update the lock file with:

```powershell
python -m pip freeze > backend\requirements-lock.txt
```

## 3. FastAPI Application

Created:

```text
backend/app/main.py
```

The initial API exposes:

```text
GET /
GET /health
```

Application:

```python
from fastapi import FastAPI

app = FastAPI(title="Urban Aanchol API")


@app.get("/")
def root():
    return {"message": "Urban Aanchol API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}
```

Start the development server:

```powershell
uvicorn backend.app.main:app --reload
```

The development server runs at:

```text
http://127.0.0.1:8000
```

### API verification

Root:

```text
http://127.0.0.1:8000/
```

Expected:

```json
{
  "message": "Urban Aanchol API is running"
}
```

Health:

```text
http://127.0.0.1:8000/health
```

Expected:

```json
{
  "status": "healthy"
}
```

Swagger/OpenAPI:

```text
http://127.0.0.1:8000/docs
```

Verified endpoints:

- `GET /`
- `GET /health`

## 4. Backend Architectural Decision

FastAPI was selected because it is open-source, lightweight, Python-based, suitable for REST APIs, automatically documented through OpenAPI/Swagger, and well suited to future RAG/AI integration.

Uvicorn is used as the development ASGI server.

The backend will expose standard HTTP/JSON APIs rather than depending on hosting-provider-specific APIs.

This keeps future migration between hosting providers practical.

## 5. Frontend Setup

Created:

```text
frontend/
├── index.html
├── style.css
├── script.js
└── assets/
```

The initial frontend uses:

```text
HTML5
CSS3
JavaScript
```

No frontend framework was introduced.

### Reason

This provides:

- Zero software cost
- Minimal dependencies
- Fast development
- Easy debugging
- Easy static hosting
- Strong portability
- No unnecessary framework lock-in

A framework can be introduced later only if website complexity creates a clear need.

## 6. Initial Website

The initial `frontend/index.html` includes:

- Header
- Urban Aanchol branding
- Hero section
- Collection section
- Saree Guide section
- About section
- Contact section
- Footer
- Navigation between sections

The initial visual direction uses:

- Cream background
- Maroon primary colour
- Gold accent
- Serif typography
- Responsive layout/navigation

## 7. Saree Guide

A dedicated `Saree Guide` navigation item and section were added.

The section is intentionally simple at this stage but is designed to grow into a flexible knowledge area.

Planned topics include:

- How sarees are made
- Saree fabric guides
- Washing and care
- Storage
- Draping
- Occasion/style guidance
- Other saree-related educational content

Guide content can later become part of the RAG knowledge base.

## 8. Frontend Validation

The website was opened directly in a browser and verified.

Validated:

- Page loads correctly
- CSS is applied
- Urban Aanchol branding is visible
- Cream/maroon/gold visual direction is applied
- Hero section displays
- Collection section is reachable
- Saree Guide section is reachable
- About section is reachable
- Contact section is reachable
- Navigation links work

## 9. API and Frontend Separation

The Day 2 foundation deliberately separates:

```text
Frontend
   ↓
HTTP/JSON
   ↓
FastAPI backend
```

The backend is not coupled to a specific frontend technology.

This allows the same API to support future website improvements, a PWA, or other clients without changing the core backend contract.

## 10. Database and RAG Decisions Deferred

No production database or RAG implementation was introduced on Day 2.

Planned database direction:

```text
PostgreSQL + pgvector
```

The database is expected to eventually support:

- Structured catalogue data
- Vector embeddings
- Semantic retrieval

Other future alternatives remain possible, including separate vector databases, because vendor independence is a project principle.

RAG will be introduced after catalogue and application foundations are sufficiently stable.

The intended future flow is:

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

The chatbot should use approved catalogue/business knowledge rather than relying only on LLM generation.

## 11. Other Future Provider Decisions

No provider was permanently selected on Day 2 for:

- Hosting
- Media storage
- LLM
- Embedding model
- Vector database
- Authentication
- Payments

The guiding requirements are:

1. Zero/free cost where practical
2. Open-source/portable options where possible
3. Standard interfaces
4. Easy migration

Product media should ultimately use standard HTTPS URLs.

## 12. Business and Product Architecture Decisions

### Catalogue

The business-facing catalogue remains intended for:

```text
Excel / Google Sheets
```

Future synchronization:

```text
Excel / Google Sheets
        ↓
Structured catalogue
        ↓
PostgreSQL
        ↓
Search / RAG
```

### Availability

Availability is intended to be a first-class catalogue attribute so the chatbot does not present sold/reserved products as currently available.

### Ordering

The MVP prioritizes:

```text
WhatsApp enquiry/order
```

rather than a full shopping cart and automated checkout.

This follows the existing workflow:

```text
Customer enquiry
      ↓
Availability confirmation
      ↓
Prepayment
      ↓
Delivery
```

### Responsive Web

One responsive web application is planned for:

- Android
- iPhone
- iPad
- Windows
- macOS

A PWA can be considered later if useful.

## 13. Day 2 Scope

### Completed

- FastAPI backend created
- Uvicorn development server configured
- Root API endpoint created
- Health-check endpoint created
- Swagger/OpenAPI verified
- Backend requirements created
- Dependency lock file created
- Initial frontend created
- Responsive CSS foundation added
- Urban Aanchol cream/maroon/gold visual foundation added
- Home/hero foundation added
- Collection section added
- Saree Guide section added
- About section added
- Contact section added
- Navigation tested in browser

### Intentionally Deferred

- Database implementation
- PostgreSQL setup
- pgvector setup
- Catalogue import
- RAG implementation
- LLM integration
- Vector search
- Production hosting selection
- Permanent media provider selection
- Authentication
- Payment integration
- Frontend framework

## 14. Day 2 Completion Checklist

- [x] Python 3.11.9 project runtime verified
- [x] FastAPI installed
- [x] Uvicorn installed
- [x] Backend structure created
- [x] Root API endpoint tested
- [x] Health endpoint tested
- [x] Swagger UI tested
- [x] Requirements file created
- [x] Dependency lock file created
- [x] Frontend structure created
- [x] Initial website created
- [x] Responsive styling added
- [x] Urban Aanchol visual direction established
- [x] Saree Guide added
- [x] Browser testing completed
- [x] Navigation verified

## Day 2 Outcome

The project now has a working application foundation:

```text
Responsive Website
        ↓
   HTTP / JSON
        ↓
FastAPI Backend
        ↓
Future Database / RAG / AI
```

The foundation is intentionally simple, portable, and ready for the catalogue and database work that follows.

**Next:** Day 3 — Product Catalogue Foundation
