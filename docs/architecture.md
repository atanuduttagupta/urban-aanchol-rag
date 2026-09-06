# Urban Aanchol — System Architecture

## Goal

Build a responsive website for Urban Aanchol with an AI-powered RAG chatbot that helps customers discover sarees and answer boutique-related questions.

## Business Model

- Home-based saree boutique
- Location: Kolkata, West Bengal, India
- Primary marketing: Facebook and Instagram
- Orders: Phone and WhatsApp
- Payment: Customer prepays
- Delivery: Boutique delivers the saree
- Product availability is manually confirmed

## High-Level Architecture

Customer
   ↓
Website
   ↓
Saree Catalogue + Chatbot
   ↓
Backend API
   ↓
Retrieval Layer
   ├── Product data
   ├── Business information
   └── Policies / FAQs
   ↓
LLM
   ↓
Grounded Response
   ↓
Customer

## Planned Retrieval Evolution

1. Structured product search
2. Keyword / full-text search
3. Vector semantic search
4. Hybrid retrieval
5. Reranking
6. Conversational retrieval
7. Agentic / multi-step retrieval
8. Image similarity retrieval
9. Multimodal RAG

## Core Technologies

Frontend:
- HTML
- CSS
- JavaScript

Backend:
- Python
- FastAPI

Database:
- PostgreSQL
- pgvector

Embeddings:
- Open-source embedding models

LLM:
- Provider-independent abstraction

Source Catalogue:
- Excel / Google Sheets

Version Control:
- Git / GitHub

## Design Principle

Every major component should be replaceable without redesigning the entire application.