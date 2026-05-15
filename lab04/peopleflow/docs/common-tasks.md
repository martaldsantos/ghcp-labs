# Common Tasks — Step-by-Step Recipes

> These are the tasks you'll do most often as a PeopleFlow developer.
> Follow these recipes until the patterns feel natural.

---

## 1. Adding a New API Endpoint

**Example**: Adding `GET /employees/{id}/reviews` to fetch an employee's review history.

### Step 1: Define the schema (if needed)
```python
# src/employees/employees_schemas.py (or create a new schemas file)

class EmployeeReviewHistoryResponse(BaseModel):
    employee_id: str
    reviews: list[ReviewSummary]
    total: int
```

### Step 2: Add the service method
```python
# src/employees/employees_service.py

async def get_employee_reviews(
    self, tenant_id: str, employee_id: str
) -> dict:
    """Fetch all reviews for an employee across all cycles."""
    async with get_db_session() as session:
        query = TenantQuery(session, tenant_id)
        # Always use TenantQuery — never raw queries without tenant_id
        reviews = await query.filter(
            ReviewModel,
            ReviewModel.reviewee_id == employee_id,
        )
        return {"employee_id": employee_id, "reviews": reviews, "total": len(reviews)}
```

### Step 3: Add the route handler
```python
# src/employees/employees_router.py

@router.get("/{employee_id}/reviews")
@require_role("hr_admin", "manager", "employee")
async def get_employee_reviews(request: Request, employee_id: str):
    """Get all performance reviews for a specific employee."""
    tenant_id = request.state.user.tenant_id
    return await service.get_employee_reviews(tenant_id, employee_id)
```

### Step 4: Write tests
```python
# tests/test_employees.py

async def test_get_employee_reviews_returns_reviews():
    # Arrange: create employee + review cycle + review
    # Act: GET /employees/{id}/reviews
    # Assert: response contains the review
    ...

async def test_get_employee_reviews_tenant_isolation():
    # Verify that tenant A cannot see tenant B's reviews
    ...
```

### Step 5: Run tests and open a PR
```bash
pytest tests/ -v
ruff check src/
mypy src/
git checkout -b feature/employee-review-history
git commit -m "feat(employees): add review history endpoint"
```

---

## 2. Adding a New Celery Task

**Example**: Adding a task to send a reminder email when an onboarding task is overdue.

### Step 1: Define the task
```python
# src/onboarding/onboarding_tasks.py

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_overdue_task_reminder(
    self, tenant_id: str, employee_id: str, task_title: str
):
    """Send a reminder when an onboarding task is past its due date.

    Idempotent: checks if a reminder was already sent today before sending.
    """
    try:
        # Check if reminder was already sent today (idempotency)
        # Send email via SendGrid
        # Log the action
        ...
    except Exception as exc:
        raise self.retry(exc=exc)
```

### Step 2: Key rules for Celery tasks
- Always use `bind=True` to access `self` for retries.
- Set `max_retries` and `default_retry_delay`.
- Use JSON-serializable arguments only (no ORM objects!).
- Make tasks **idempotent** — retrying should not cause duplicate actions.
- Never import Django/FastAPI request context inside tasks.

### Step 3: Schedule periodic tasks (if needed)
```python
# In celery_app configuration:
celery_app.conf.beat_schedule = {
    "check-overdue-onboarding-tasks": {
        "task": "src.onboarding.onboarding_tasks.check_overdue_tasks",
        "schedule": crontab(hour=9, minute=0),  # Daily at 09:00 UTC
    },
}
```

---

## 3. Adding a New Permission Role

**Example**: Adding a "department_lead" role with permissions between manager and hr_admin.

### Step 1: Update the role hierarchy
```python
# src/auth/permissions.py

ROLE_HIERARCHY = {
    "hr_admin": 4,        # Was 3
    "department_lead": 3,  # NEW
    "manager": 2,
    "employee": 1,
}
```

### Step 2: Update JWT handling
Work with the auth team to add the new role to the JWT claims. This
typically involves:
1. Updating the Auth0 rules/actions
2. Updating the `CurrentUser` dataclass in `auth_middleware.py`
3. Adding the role to the validation logic

### Step 3: Apply to routes
```python
@router.delete("/{employee_id}")
@require_role("hr_admin", "department_lead")  # Add new role where needed
async def delete_employee(request: Request, employee_id: str):
    ...
```

### Step 4: Update tests
Add test cases that verify the new role's access patterns.

---

## 4. Running the Test Suite Locally

### Quick run (most common)
```bash
# Run all tests
pytest tests/ -v

# Run tests for a specific module
pytest tests/test_employees.py -v

# Run a single test
pytest tests/test_employees.py::test_create_employee_success -v
```

### With coverage
```bash
pytest --cov=src --cov-report=html tests/
# Open htmlcov/index.html in your browser
```

### Required services
Tests use a separate PostgreSQL database. Make sure it's running:
```bash
docker-compose up -d postgres-test
```

The test database is automatically created and torn down by the
`conftest.py` fixtures.

### Common issues
- **"Connection refused"**: Make sure Docker is running and
  `docker-compose up -d` has been executed.
- **"Table not found"**: Run migrations on the test DB:
  `alembic -x db_url=postgresql://... upgrade head`
- **Flaky tests**: If a test fails intermittently, check for missing
  test isolation (shared state between tests).

---

## 5. Deploying to the Staging Environment

### Prerequisites
- You have access to the `peopleflow-staging` GCP project.
- You have `gcloud` CLI installed and authenticated.
- You are on the `main` branch (or a branch you want to test).

### Step 1: Build and push the Docker image
```bash
# The CI pipeline does this automatically on merge to main.
# For manual staging deploys from a branch:
docker build -t europe-west3-docker.pkg.dev/peopleflow-staging/api/peopleflow:$(git rev-parse --short HEAD) .
docker push europe-west3-docker.pkg.dev/peopleflow-staging/api/peopleflow:$(git rev-parse --short HEAD)
```

### Step 2: Deploy to Cloud Run
```bash
gcloud run deploy peopleflow-api \
  --image europe-west3-docker.pkg.dev/peopleflow-staging/api/peopleflow:$(git rev-parse --short HEAD) \
  --region europe-west3 \
  --project peopleflow-staging
```

### Step 3: Run smoke tests
```bash
# Hit the health endpoint
curl https://api-staging.peopleflow.io/health

# Run the staging smoke test suite
pytest tests/smoke/ --base-url=https://api-staging.peopleflow.io
```

### Step 4: Verify in Datadog
Check the [Staging Dashboard](https://app.datadoghq.eu/dashboard/peopleflow-staging)
for errors, latency spikes, or unexpected behavior.

### Important notes
- Staging shares a database with a snapshot of production data (anonymized).
- Never create test data with real email addresses in staging.
- Staging Celery workers run on a reduced pool (2 workers vs 8 in prod).
