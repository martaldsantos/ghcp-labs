# Codebase Tour — Start Here! 🗺️

> Welcome to PeopleFlow! This guide will help you navigate the codebase.
> Read this on your first day, then use it as a reference when you get lost.

## Folder Structure

```
src/
├── employees/                 # Employee CRUD — start reading here
│   ├── employees_router.py    # API endpoints (GET/POST/PATCH /employees)
│   ├── employees_service.py   # Business logic (validation, orchestration)
│   └── employees_schemas.py   # Pydantic models (request/response shapes)
│
├── onboarding/                # New hire onboarding workflow
│   ├── onboarding_router.py   # API endpoints for onboarding plans
│   ├── onboarding_service.py  # Plan creation, task management logic
│   └── onboarding_tasks.py    # Celery async tasks (emails, provisioning)
│
├── performance/               # Performance review cycles
│   ├── reviews_router.py      # API endpoints for review cycles
│   └── reviews_service.py     # Review cycle + individual review logic
│
├── auth/                      # Authentication & authorization
│   ├── auth_middleware.py      # JWT extraction, tenant identification
│   └── permissions.py         # Role-based access control decorator
│
└── shared/                    # Shared utilities used across all modules
    ├── database.py            # DB session management, TenantQuery helper
    ├── exceptions.py          # Centralized exception hierarchy
    └── logger.py              # Structured JSON logging
```

## Where to Start Reading

Follow this order to build a mental model of the codebase:

### Day 1: Understand the foundations
1. **`src/shared/exceptions.py`** — Read this first. Every error in the app
   flows through this file. Understanding the exception pattern unlocks
   understanding of every router and service.

2. **`src/auth/permissions.py`** — The `@require_role()` decorator appears
   on every route handler. Read the docstring to understand our three roles:
   `hr_admin`, `manager`, `employee`.

3. **`src/auth/auth_middleware.py`** — How authentication works. Pay
   attention to the `CurrentUser` dataclass — you'll see `request.state.user`
   everywhere.

### Day 2: Follow a request end-to-end
4. **`src/employees/employees_router.py`** — Pick one route (start with
   `POST /employees`) and follow the code from router → service → database.

5. **`src/employees/employees_service.py`** — Notice how every method
   takes `tenant_id` as the first parameter. This is the multi-tenancy
   pattern. Read the docstring on `create_employee()` for business rules.

6. **`src/employees/employees_schemas.py`** — Our API contract. The
   frontend generates TypeScript types from these, so changes here are
   breaking changes.

### Day 3: Understand async tasks
7. **`src/onboarding/onboarding_tasks.py`** — This is where Celery comes
   in. Read the module docstring for WHY we use Celery instead of FastAPI
   background tasks (the #1 new-joiner question).

## Key Patterns You'll See Everywhere

### Pattern 1: Router → Service → Database
```python
# Router: handles HTTP concerns
@router.post("/employees", status_code=201)
@require_role("hr_admin")
async def create_employee(request: Request, body: EmployeeCreate):
    tenant_id = request.state.user.tenant_id
    return await service.create_employee(tenant_id, body.model_dump())

# Service: handles business logic
async def create_employee(self, tenant_id: str, data: dict) -> dict:
    # validation, duplicate checks, orchestration
    ...

# Database: handles persistence
query = TenantQuery(session, tenant_id)
results = await query.filter(Employee, ...)
```

### Pattern 2: Exception handling
```python
# In service code — raise domain exceptions
raise NotFoundError(f"Employee '{id}' not found")
raise ValidationError("Email cannot be changed after creation")

# The global handler (main.py) catches these and returns:
# {"error": {"code": "NOT_FOUND", "message": "Employee 'abc' not found"}}
```

### Pattern 3: Permission checks
```python
@router.get("/employees")
@require_role("hr_admin", "manager")  # Only these roles can access
async def list_employees(request: Request):
    ...
```

## What NOT to Touch Without Senior Review

These areas are complex and easy to break. Always get a review from
@thomas-k or @sarah-m before modifying:

- **`src/auth/auth_middleware.py`** — Bugs here affect every request.
  A bad change can lock out all users or leak data between tenants.

- **`src/shared/database.py`** — The `TenantQuery` helper enforces
  data isolation. Removing or bypassing the tenant filter is a
  security incident.

- **Database migrations** — Always run migrations on a staging copy
  first. Never add `DROP` statements without explicit approval.

- **Celery task signatures** — Changing task parameters breaks
  in-flight tasks that are already queued. Use versioned task names
  if you need to change signatures.

## First Week Checklist

- [ ] Clone the repo and run `docker-compose up -d`
- [ ] Run the API locally (`uvicorn src.main:app --reload`)
- [ ] Read `architecture.md` for the system overview
- [ ] Read this file (you're doing it!)
- [ ] Read `how-we-work.md` for team conventions
- [ ] Read `data-model.md` for entity relationships
- [ ] Set up your IDE (VS Code recommended, see `.vscode/settings.json`)
- [ ] Meet your onboarding buddy (check Slack #new-joiners)
- [ ] Attend your first standup
- [ ] Pick one of the starter issues in `docs/issues/` and submit a PR
- [ ] Complete security awareness training (link in your onboarding plan)

## Getting Help

- **Codebase questions**: Ask in #engineering on Slack, or ask your Copilot Space
- **Architecture decisions**: @thomas-k (Tech Lead)
- **Product questions**: @lisa-p (Product Manager)
- **Infrastructure/deployment**: @ahmed-r (Platform Engineer)
- **HR platform domain questions**: @julia-s (Domain Expert)
