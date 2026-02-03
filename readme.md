# SupportOps AI Backend

Production-style FastAPI backend for multi-tenant ticketing with AI triage and background jobs.

**Features**

- Multi-tenant orgs with RBAC (admin, agent, customer)
- Tickets + comments
- Redis Queue worker for AI triage
- AI triage with strict JSON validation
- Audit logs and admin metrics
- JWT access + refresh tokens with rotation
- Docker Compose for Postgres and Redis
- Tests and ruff linting

**Architecture**

- `app/api` for request handlers and dependencies
- `app/services` for business logic
- `app/models` for SQLAlchemy models
- `app/jobs` for RQ workers
- `app/core` for config, logging, and security

**Quickstart**

1. Copy `.env.example` to `.env` and adjust values.
2. Start dependencies: `docker compose up -d`
3. Create and activate venv: `python -m venv .venv`, then `.\.venv\Scripts\Activate.ps1`
4. Install dependencies: `python -m pip install -e .`
5. Run migrations: `alembic upgrade head`
6. Start API: `uvicorn app.main:app --reload`
7. Start worker in another shell: `.\.venv\Scripts\rq.exe worker -u redis://localhost:6379/0`

**Auth Header**

- Use `Authorization: Bearer <access_token>` on all protected endpoints.

**API Overview**

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `GET /api/v1/me`
- `POST /api/v1/orgs/{org_id}/tickets`
- `GET /api/v1/orgs/{org_id}/tickets?status=&priority=&cursor=&limit=`
- `PATCH /api/v1/orgs/{org_id}/tickets/{ticket_id}`
- `POST /api/v1/orgs/{org_id}/tickets/{ticket_id}/comments`
- `POST /api/v1/orgs/{org_id}/tickets/{ticket_id}/ai/triage`
- `GET /api/v1/orgs/{org_id}/tickets/{ticket_id}/ai/triage`
- `GET /api/v1/orgs/{org_id}/metrics`

**Environment Variables**

- `DATABASE_URL` PostgreSQL connection string
- `REDIS_URL` Redis connection string
- `JWT_SECRET` secret used to sign tokens
- `ACCESS_TOKEN_EXPIRE_MINUTES` access token TTL
- `REFRESH_TOKEN_EXPIRE_DAYS` refresh token TTL
- `OPENAI_API_KEY` optional; if unset, a deterministic stub is used
- `OPENAI_MODEL` model name for OpenAI calls
- `AI_TIMEOUT_SECONDS` model call timeout
- `RQ_JOB_TIMEOUT` job timeout in seconds
- `RQ_ASYNC` set false to run jobs inline (useful for tests)

**Background Jobs**

- Triage jobs are enqueued to RQ with 3 retries and exponential backoff.
- If an AI insight exists and is less than 24 hours old, the job skips to avoid duplicates.
- Outputs are validated with Pydantic before saving to the database.

**Security Notes**

- Passwords are stored as bcrypt hashes.
- Refresh tokens are rotated and only their hashes are stored.
- RBAC is enforced server-side for every org-scoped endpoint.

**Tests**

- `pytest`

**Key Tradeoffs**

- Register endpoint also creates the initial org and admin membership.
- Pagination uses a simple cursor based on ticket id ordering.
- Customer users can create tickets and comment but cannot update tickets or view metrics.

**Next Improvements**

- Add org management endpoints and user invitations.
- Add rate limiting and IP-based abuse protection.
- Replace stub AI with structured response formats when available.
- Add OpenTelemetry traces and richer metrics.
