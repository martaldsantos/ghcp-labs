# FAQ for New Joiners

> These are the questions every new developer asks during their first weeks.
> Read through them — it'll save you a lot of Slack messages.

---

### 1. "Why do we use Celery instead of FastAPI background tasks?"

**Short answer**: Reliability.

FastAPI's `BackgroundTasks` run in the same process as the API server.
If the server restarts (deploy, crash, scaling event), all background tasks
are lost — no retry, no persistence. For a "fire and forget" log entry, that's
fine. For "send a welcome email to a new employee", losing the task means a
bad first impression.

Celery gives us:
- **Persistence**: Tasks are stored in Redis. If a worker dies, the task is
  re-queued and picked up by another worker.
- **Retries**: Failed tasks automatically retry with exponential backoff.
- **Monitoring**: The Flower dashboard shows what's queued, running, and failed.
- **Isolation**: Celery workers are separate processes — heavy tasks don't
  block the API server's event loop.

The trade-off is operational complexity (Redis + Celery workers to deploy and
monitor), but for an HR platform where reliability matters, it's worth it.

See `src/onboarding/onboarding_tasks.py` for our Celery task patterns.

---

### 2. "What's the `tenant_id` and why is it everywhere?"

PeopleFlow is a **multi-tenant** platform — each customer company is a "tenant"
that shares the same database but must never see another tenant's data.

We use **row-level isolation**: every table has a `tenant_id` column, and every
query must filter by it. This is simpler to operate than separate databases or
schemas per tenant, but it means you must ALWAYS include `tenant_id` in your
queries.

The `TenantQuery` helper in `src/shared/database.py` enforces this automatically.
Use it instead of writing raw queries.

If you forget `tenant_id`, you'll create a **data leak** between tenants. This
is our most critical class of bug.

---

### 3. "How do I get access to the staging database?"

1. Ask @ahmed-r in #infrastructure to add your GCP account to the
   `peopleflow-staging` project.
2. Install Cloud SQL Proxy: `gcloud components install cloud-sql-proxy`
3. Connect:
   ```bash
   cloud-sql-proxy peopleflow-staging:europe-west3:peopleflow-db &
   psql -h 127.0.0.1 -U readonly -d peopleflow_staging
   ```

**Important**: You get **read-only access**. Write access to staging requires
approval from @thomas-k. Production database access is restricted to the
on-call engineer during incidents only.

---

### 4. "Why are there two auth middlewares?"

They're not really two middlewares — it's one middleware and one decorator:

1. **`TenantAuthMiddleware`** (actual ASGI middleware): Runs on EVERY request.
   Extracts the JWT, validates it, and sets `tenant_id` + `user_id` in the
   request context. This ensures that all downstream code knows which tenant
   the request belongs to.

2. **`@require_role()` decorator** (not middleware): Applied per-route to check
   if the user's role is sufficient. Not every endpoint needs the same role
   check, so this is configured per-handler.

We separated them because:
- Tenant identification is universal (every request needs it).
- Permission checks vary per endpoint.
- Combining them into one middleware would require a centralized route-to-role
  mapping config, which we tried in v1 and it was error-prone.

---

### 5. "How do I run just my module's tests?"

```bash
# Run tests for employees module
pytest tests/test_employees.py -v

# Run a single test function
pytest tests/test_employees.py::test_create_employee_success -v

# Run with coverage for your module
pytest --cov=src/employees tests/test_employees.py

# Watch mode (re-runs on file changes)
ptw tests/test_employees.py
```

---

### 6. "What's the difference between `ValidationError` and Pydantic's `ValidationError`?"

Two different things:

- **Pydantic's `ValidationError`**: Raised automatically when a request body
  doesn't match the schema (wrong types, missing fields). FastAPI catches this
  and returns a 422 with Pydantic's error format.

- **Our `ValidationError`** (from `src/shared/exceptions.py`): Raised manually
  in service code for **business rule** violations (e.g. "review end date must
  be after start date"). Returns our standard error envelope:
  `{"error": {"code": "VALIDATION_ERROR", "message": "..."}}`.

Rule of thumb: If Pydantic can catch it with type annotations, let it. If it's
a business rule, raise our `ValidationError`.

---

### 7. "Why doesn't the test database reset between tests?"

It does — but only if you're using the test fixtures correctly. Every test
should use the `db_session` fixture from `conftest.py`, which wraps each
test in a transaction and rolls back after the test completes.

If your test is leaking data, check that you're:
1. Using `db_session` (not creating your own sessions)
2. Not committing explicitly inside the test
3. Not using `session.execute()` with DDL (DDL auto-commits in PostgreSQL)

---

### 8. "Can I use `print()` for debugging?"

For local debugging, sure. But **never** commit `print()` statements.

In production we use structured JSON logging (see `src/shared/logger.py`).
Use the logger instead:

```python
from src.shared.logger import get_logger
logger = get_logger(__name__)

logger.info("Employee created", extra={"employee_id": emp.id})
logger.warning("Duplicate email attempt", extra={"email": email})
```

The structured logger automatically includes `tenant_id` and `user_id` from
the request context, so you don't need to add them manually.

---

### 9. "How do I add a database migration?"

```bash
# 1. Make your model changes in the relevant module

# 2. Generate a migration
alembic revision --autogenerate -m "add phone_number to employees"

# 3. Review the generated migration file in alembic/versions/
#    ALWAYS review — autogenerate sometimes gets it wrong

# 4. Run the migration locally
alembic upgrade head

# 5. Run on test DB too
alembic -x db_url=postgresql://test:test@localhost:5433/peopleflow_test upgrade head

# 6. Test that downgrade works
alembic downgrade -1
alembic upgrade head
```

**Critical**: Never add `DROP TABLE` or `DROP COLUMN` in a single migration.
Use a two-step process:
1. First migration: Stop writing to the column/table
2. Second migration (after deploy): Drop it

---

### 10. "Where do I find the API documentation?"

The API docs are auto-generated from our FastAPI route definitions and
Pydantic schemas:

- **Local**: http://localhost:8000/docs (Swagger UI)
- **Staging**: https://api-staging.peopleflow.io/docs
- **Production**: Not publicly accessible (internal only)

The docs are only as good as our docstrings and schema definitions. If you
add a new endpoint, write a clear docstring — it becomes the API documentation.
