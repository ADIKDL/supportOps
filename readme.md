# SupportOps AI Backend

Production-style **Python backend** that demonstrates real-world backend engineering patterns + AI integration:

- Multi-tenant organizations
- RBAC (Admin / Agent / Customer)
- Tickets + comments workflow
- Background jobs with Redis Queue (RQ)
- AI ticket triage (category, urgency score, suggested reply) with **strict JSON validation**
- Audit logs + basic admin metrics
- Clean project structure, tests, and local dev with Docker

> Built as an interview-ready project to showcase backend + AI compatibility (not “toy demo” code).

---

## Demo Goals

This project is designed to prove:

- I can build **secure, scalable APIs** (validation, auth, RBAC, pagination)
- I understand **reliability** (queues, retries, idempotency, timeouts)
- I can integrate **LLM-based features safely** (structured output, validation, audit logging)
- I can structure Python projects cleanly and test them

---

## Features

### Core

- **Multi-tenant** organizations (org-scoped endpoints)
- **RBAC**: Admin / Agent / Customer
- Ticket lifecycle: `new → open → pending → resolved`
- Ticket priority: `low / med / high / urgent`
- Ticket comments

### AI

- AI ticket triage runs asynchronously:
  - `category`: billing | bug | feature | other
  - `urgency_score`: 1–10
  - `suggested_reply`: short customer-facing response
- Output is **validated** with Pydantic before saving
- Supports:
  - **Real provider** (if `OPENAI_API_KEY` is set)
  - **Deterministic stub** provider (if no API key — works offline)

### Reliability & Ops

- Background jobs via **Redis + RQ**
- Retries with exponential backoff (3 attempts)
- Idempotent triage: if triage exists and is **< 24h old**, it won’t duplicate
- Audit log for sensitive changes and AI actions
- Admin metrics endpoint (ticket counts by status/category)

---

## Tech Stack

- **API:** FastAPI (Python 3.11+)
- **DB:** PostgreSQL + SQLAlchemy 2.x + Alembic migrations
- **Queue:** Redis + RQ workers
- **Validation:** Pydantic v2
- **Testing:** pytest
- **Quality:** ruff (lint/format)
- **HTTP Client:** httpx
- **Config:** python-dotenv
- **Local Dev:** Docker Compose

---

## Architecture Overview

**Request flow (high level):**

Client → FastAPI → Postgres  
 ↘ enqueue triage job → Redis (RQ) → Worker → AI Provider → Postgres

**Key design ideas:**

- Keep request handlers fast; push long work to the worker.
- Validate at boundaries (Pydantic request/response + AI JSON schema validation).
- Enforce RBAC _server-side_ on every org-scoped endpoint.
- Make background jobs safe and retryable (idempotency + timeouts + backoff).

---
