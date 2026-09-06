# Urban Aanchol — Development Journey

This folder documents the complete step-by-step development journey of the **Urban Aanchol website and RAG-based chatbot**.

The purpose of this documentation is to make the project **reproducible**. Someone with a similar development environment should be able to follow the journey from Day 1 onward and understand not only **what was done**, but also **why decisions were made** and **how problems were solved**.

---

## 🎯 Project Goal

Build a polished, responsive website for **Urban Aanchol**, a home-based saree boutique based in Kolkata, West Bengal, India, with an AI-powered RAG chatbot that helps customers:

- Discover sarees
- Search using natural language
- Find sarees based on colour, fabric, occasion, festival, mood, style, brand and budget
- Check product information and availability
- Get answers about boutique policies and ordering
- Connect with the boutique through WhatsApp

The system will evolve incrementally from a simple catalogue into an advanced RAG and conversational recommendation system.

---

# 🏗️ Development Philosophy

The project follows these principles throughout the development journey.

### 1. Zero Cost First

The boutique is a home-based business, so the primary objective is to build the system using **free or open-source solutions wherever practical**.

Paid services should only be considered when they provide significant value and there is no practical free alternative.

### 2. No Vendor Lock-In

The architecture should not depend unnecessarily on a single cloud provider, database, LLM provider, vector database, storage provider or hosting platform.

Where practical, components should be replaceable.

### 3. Open Source First

Prefer:

- Open-source software
- Standard APIs
- Standard SQL
- Portable Python
- Open-source AI/ML models
- Standard web technologies

### 4. Simple Before Complex

Start with the simplest solution that solves the current problem.

Advanced capabilities such as:

- Agentic RAG
- Multi-hop retrieval
- Multimodal RAG
- Image similarity
- Voice
- Virtual try-on

should be introduced only when they provide meaningful business value.

### 5. Production Quality

The MVP should look and behave like a **real boutique website**, not a developer prototype.

If necessary, functionality will be reduced before visual and user experience quality is compromised.

### 6. One Hour Per Day

Development is intentionally limited to approximately **one hour per day**.

Each development day should have:

- A clear objective
- A small set of tasks
- A verifiable outcome
- Documentation of important decisions
- Documentation of issues encountered

---

# 📚 Journey Structure

Each development day is stored in its own folder.

```text
journey/
│
├── README.md
│
├── day-01-foundation/
│   ├── README.md
│   ├── steps.md
│   └── decisions.md
│
├── day-02-project-setup/
│   ├── README.md
│   ├── steps.md
│   └── decisions.md
│
├── day-03-product-catalogue/
│   ├── README.md
│   ├── steps.md
│   └── decisions.md
│
└── ...
```

The common project-level `issues/` folder contains problems and their resolutions.

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

This keeps **daily activities** separate from the **long-term issue/solution knowledge base**.

---

# 🗺️ Development Roadmap

| Day / Phase | Topic | Status |
|---|---|---|
| Day 1 | Foundation & Architecture | 🟢 Complete |
| Day 2 | Project Setup | ⬜ Planned |
| Day 3 | Product Catalogue | ⬜ Planned |
| Day 4 | Media Management | ⬜ Planned |
| Day 5 | Website Foundation | ⬜ Planned |
| Day 6+ | Website Development | ⬜ Planned |
| Phase 3 | RAG MVP | ⬜ Planned |
| Phase 4 | Hybrid Search & Recommendation Agent | ⬜ Planned |
| Phase 5 | Conversational Recommendation | ⬜ Planned |
| Phase 6 | Voice Input | ⬜ Planned |
| Phase 7 | Image Similarity Search | ⬜ Planned |
| Phase 8 | Multimodal / Agentic RAG | ⬜ Planned |
| Phase 9 | Virtual Try-On | ⬜ Optional |
| Phase 10 | Production Polish & Evaluation | ⬜ Planned |

The roadmap may change as the project evolves.

---

# 📅 How to Follow the Journey

Start with **Day 1** and proceed sequentially.

For each day:

1. Read `README.md`
2. Follow `steps.md`
3. Review `decisions.md`
4. Check the relevant `issues/` documentation if problems occur
5. Verify the expected result
6. Commit the completed work to Git

Each day should ideally end with a clean Git working tree.

Expected result:

```text
nothing to commit, working tree clean
```

---

# 📝 Documentation Rules

During development, important information should be documented rather than kept only in chat or personal notes.

### Record:

- Commands used
- Configuration changes
- Important technical decisions
- Problems encountered
- Error messages
- Root causes
- Resolutions
- Verification steps
- Lessons learned

### Avoid:

- Recording passwords
- API keys
- Access tokens
- Personal/private customer information
- Other secrets

Secrets must never be committed to GitHub.

---

# 🐛 Issue Documentation

Issues are documented separately from the daily journey.

A typical issue should contain:

```text
Problem
↓
Expected behaviour
↓
Actual behaviour
↓
Investigation
↓
Root cause
↓
Resolution
↓
Verification
↓
Lesson learned
```

This allows the repository to become a reusable troubleshooting knowledge base.

---

# 🔄 Git Workflow

Development follows a simple workflow:

```text
Make changes
     ↓
Test / Verify
     ↓
Review git status
     ↓
git add .
     ↓
git commit
     ↓
git push
     ↓
Verify clean working tree
```

Git commits should describe the purpose of the change.

Example:

```text
docs: document Day 1 development journey
```

or:

```text
feat: add product catalogue search
```

---

# 🤖 Planned RAG Evolution

The chatbot is intentionally designed to evolve over time.

```text
Structured Product Data
        ↓
Keyword / Exact Search
        ↓
Vector Semantic Search
        ↓
Hybrid Retrieval
        ↓
Reranking
        ↓
Conversational Retrieval
        ↓
Agentic Retrieval
        ↓
Image Similarity Retrieval
        ↓
Multimodal RAG
```

The project should not implement all of these capabilities at once.

Each stage should be introduced only after the previous stage is stable.

---

# 🛍️ Business-First Approach

The technology should serve the boutique rather than becoming the objective itself.

The chatbot should ultimately help customers answer questions such as:

> "Show me a vibrant red saree for Durga Puja under ₹5,000."

> "I need something elegant and lightweight for a birthday party."

> "Do you have any pastel Tussar sarees?"

> "Show me blue silk sarees."

> "Is this saree available?"

> "How can I order?"

The chatbot should provide **grounded answers based on the boutique's actual product and business information**.

It should never invent:

- Products
- Prices
- Availability
- Fabrics
- Policies
- Delivery information

---

# 🔐 Safety & Guardrails

The chatbot will remain focused on the Urban Aanchol business domain.

It should:

- Answer relevant saree and boutique questions
- Politely reject unrelated requests
- Refuse unsafe requests
- Avoid hallucinated information
- Respect product availability
- Protect internal system information
- Treat retrieved information as data rather than executable instructions

---

# 📈 Long-Term Objective

The final system should provide a foundation that can support:

- A professional boutique website
- Product catalogue
- Natural-language saree discovery
- RAG chatbot
- Hybrid search
- Conversational recommendations
- Voice input
- Image-based saree search
- Multimodal RAG
- Advanced agentic retrieval
- Optional virtual try-on

The implementation will remain **free-first, portable and vendor-independent** wherever practical.

---

## 🚀 Start Here

Begin with:

**[Day 1 — Foundation & Architecture](./day-01-foundation/README.md)**

Then continue sequentially through the development journey.

---

**Urban Aanchol — Building a smarter way to discover sarees.**
