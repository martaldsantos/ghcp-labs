# PeopleFlow Architecture Overview

> Last updated: 2025-11-15 | Author: @thomas-k (Tech Lead)

## System Overview

PeopleFlow is a multi-tenant B2B SaaS platform for HR lifecycle management.
It handles employee onboarding, performance reviews, and offboarding for
companies ranging from 50 to 5,000 employees.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENTS                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ React SPA    │  │ Mobile App   │  │ External Integrations│  │
│  │ (Vite + TS)  │  │ (React Nat.) │  │ (Slack, GitHub, etc) │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
└─────────┼─────────────────┼─────────────────────┼──────────────┘
          │                 │                     │
          ▼                 ▼                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                     NGINX (Reverse Proxy)                       │
│              TLS termination, rate limiting                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Application                           │
│  ┌──────────┐  ┌──────────┐  ┌────────────┐  ┌─────────────┐  │
│  │Employees │  │Onboarding│  │Performance │  │   Auth       │  │
│  │  Router  │  │  Router  │  │  Router    │  │ Middleware   │  │
│  └────┬─────┘  └────┬─────┘  └─────┬──────┘  └──────┬──────┘  │
│       │              │              │                │          │
│  ┌────▼─────┐  ┌────▼─────┐  ┌────▼──────┐         │          │
│  │ Service  │  │ Service  │  │ Service   │         │          │
│  │  Layer   │  │  Layer   │  │  Layer    │         │          │
│  └────┬─────┘  └────┬─────┘  └─────┬─────┘         │          │
└───────┼──────────────┼──────────────┼───────────────┼──────────┘
        │              │              │               │
        ▼              ▼              ▼               │
┌─────────────────────────────────┐                   │
│         PostgreSQL              │                   │
│  (Multi-tenant, row-level      │                   │
│   isolation via tenant_id)     │                   │
└─────────────────────────────────┘                   │
                                                      │
        ┌─────────────────────────────────────────────┘
        │  (Async tasks)
        ▼
┌─────────────────────────────────┐    ┌──────────────────────┐
│       Redis (Broker)            │───▶│   Celery Workers     │
│                                 │    │  - Welcome emails    │
└─────────────────────────────────┘    │  - Tool provisioning │
                                       │  - Notifications     │
                                       └──────────────────────┘
```

## Multi-Tenancy Model

**Approach:** Row-level isolation with a `tenant_id` column on every table.

### Why row-level instead of schema-per-tenant?

We evaluated three options when starting the project:

| Approach | Pros | Cons | Decision |
|----------|------|------|----------|
| Separate databases | Strongest isolation | Expensive, complex migrations | ❌ |
| Schema-per-tenant | Good isolation | Complex connection pooling, migration per schema | ❌ |
| Row-level (tenant_id) | Simple ops, one migration path | Must enforce filtering everywhere | ✅ |

We chose row-level isolation because:
1. **Operational simplicity**: One database, one migration pipeline, one backup strategy.
2. **Cost**: A single connection pool serves all tenants.
3. **Speed**: Adding a new tenant is an INSERT, not a DDL operation.

The trade-off is that **every query must filter by `tenant_id`**. To enforce this,
we use the `TenantQuery` helper in `src/shared/database.py`. If you're writing raw
SQL (please don't), you must include a `WHERE tenant_id = :tenant_id` clause.

### Data isolation guarantees

- The `TenantAuthMiddleware` extracts `tenant_id` from the JWT on every request.
- All service methods take `tenant_id` as their first parameter.
- The `TenantQuery` helper automatically adds the tenant filter.
- Database indexes include `tenant_id` as the first column for query performance.

## Request Lifecycle

Here's what happens when a request hits the API:

```
1. NGINX terminates TLS, applies rate limiting
2. Request reaches FastAPI
3. TenantAuthMiddleware:
   a. Extracts JWT from Authorization header
   b. Validates token signature against JWKS
   c. Extracts tenant_id and user info
   d. Sets context variables (for logging)
   e. Attaches CurrentUser to request.state
4. Router handler executes:
   a. @require_role decorator checks permissions
   b. Pydantic validates request body
   c. Service method is called with tenant_id
   d. TenantQuery ensures all DB queries are scoped
5. Response is returned with standard error envelope on failure
```

## Technology Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| API framework | FastAPI | Async, auto-generated OpenAPI docs, Pydantic validation |
| Database | PostgreSQL 15 | Mature, excellent JSON support, row-level security |
| ORM | SQLAlchemy 2.0 (async) | Industry standard, good migration support |
| Migrations | Alembic | Pairs with SQLAlchemy, version-controlled |
| Task queue | Celery + Redis | Reliable async tasks, retries, monitoring (see FAQ) |
| Auth | JWT (python-jose) | Stateless, works with our SSO provider (Auth0) |
| Frontend | React + TypeScript + Vite | Fast builds, type safety |
| Monitoring | Datadog | Structured logs, APM, alerting |

## Environment Setup

See [common-tasks.md](common-tasks.md) for setup instructions. Key services needed locally:

```bash
# Start dependencies
docker-compose up -d postgres redis

# Run API
uvicorn src.main:app --reload --port 8000

# Run Celery workers
celery -A src.onboarding.onboarding_tasks worker --loglevel=info
```

## Key Design Decisions

1. **Service layer pattern**: Routers handle HTTP, services handle business logic.
   Never put business rules in routers.

2. **Structured exceptions**: All errors go through `PeopleFlowError` subclasses
   (see `src/shared/exceptions.py`). Never raise raw `HTTPException` from services.

3. **Permission decorator**: `@require_role()` instead of FastAPI `Depends()` for
   cleaner function signatures.

4. **Structured logging**: JSON logs with automatic tenant context for Datadog.
   Never use `print()` in production code.
