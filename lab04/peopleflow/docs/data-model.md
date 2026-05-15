# PeopleFlow Data Model

> This document describes the core entities, their relationships, and
> important business rules. Refer to this when writing queries, creating
> migrations, or understanding why the code behaves a certain way.

## Entity Relationship Diagram

```
┌─────────────────┐       ┌─────────────────┐
│    Tenant        │       │   Department     │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │──┐    │ id (PK)         │
│ name            │  │    │ tenant_id (FK)  │──┐
│ slug            │  │    │ name            │  │
│ plan (free/pro) │  │    │ head_id (FK)    │  │
│ created_at      │  │    │ created_at      │  │
└─────────────────┘  │    └─────────────────┘  │
                     │                          │
        ┌────────────┘                          │
        │    ┌──────────────────────────────────┘
        │    │
        ▼    ▼
┌─────────────────────┐     ┌──────────────────────┐
│     Employee         │     │   OnboardingPlan      │
├─────────────────────┤     ├──────────────────────┤
│ id (PK)             │──┐  │ id (PK)              │
│ tenant_id (FK)      │  │  │ tenant_id (FK)       │
│ email               │  │  │ employee_id (FK)     │◄──┐
│ first_name          │  │  │ status               │   │
│ last_name           │  │  │ created_at           │   │
│ department_id (FK)  │  │  │ updated_at           │   │
│ manager_id (FK) ────│──┘  └──────────┬───────────┘   │
│ job_title           │                │               │
│ status              │                │ has many       │
│ start_date          │                ▼               │
│ employment_type     │     ┌──────────────────────┐   │
│ created_at          │     │   OnboardingTask      │   │
│ updated_at          │     ├──────────────────────┤   │
└────────┬────────────┘     │ id (PK)              │   │
         │                  │ plan_id (FK)         │   │
         │                  │ title                │   │
         │ has many         │ category             │   │
         │                  │ due_day              │   │
         ▼                  │ status               │   │
┌─────────────────────┐     │ completed_at         │   │
│    ReviewCycle       │     └──────────────────────┘   │
├─────────────────────┤                                │
│ id (PK)             │                                │
│ tenant_id (FK)      │     employee has one ───────────┘
│ title               │     (active plan at a time)
│ start_date          │
│ end_date            │
│ status              │
│ created_at          │
└────────┬────────────┘
         │
         │ has many
         ▼
┌─────────────────────┐
│      Review          │
├─────────────────────┤
│ id (PK)             │
│ tenant_id (FK)      │
│ cycle_id (FK)       │
│ reviewer_id (FK)    │
│ reviewee_id (FK)    │
│ review_type         │
│ rating (1-5)        │
│ strengths           │
│ areas_for_improve.  │
│ goals_next_period   │
│ status              │
│ created_at          │
└─────────────────────┘
```

## Entity Details

### Tenant
The top-level entity. Every customer company is a tenant. All data belongs
to exactly one tenant and is isolated via `tenant_id` on every row.

- **plan**: `free` or `pro`. Free tenants have a 50-employee limit.
- **slug**: URL-safe identifier used in API paths (e.g. `/acme/employees`).

### Employee
The central entity. Represents a person employed by a tenant company.

- **email**: Unique within a tenant (not globally). Used as identity key in
  external systems (SSO, payroll).
- **manager_id**: Self-referencing FK. Nullable for top-level employees (CEO, etc).
- **status**: Lifecycle state. See `EmploymentStatus` enum in
  `src/employees/employees_schemas.py` for the state machine.
- **employment_type**: `full_time`, `part_time`, or `contractor`.

### Department
Organizational unit within a tenant. Each employee belongs to exactly one department.

- **head_id**: FK to Employee. The department head/manager.

### OnboardingPlan
A structured checklist assigned to a new employee during their first 30/60/90 days.

- **status**: `active` → `completed` → `archived`
- **Business rule**: An employee can have at most ONE active plan at a time.
  This is enforced in `OnboardingService.create_plan()`.

### OnboardingTask
Individual items within an onboarding plan.

- **due_day**: Relative to the employee's start date (e.g. `due_day=3` means
  "by day 3 of employment").
- **category**: `compliance`, `engineering`, `knowledge`, `people`, `custom`.

### ReviewCycle
A time-bounded period for performance reviews (usually quarterly).

- **status**: `draft` → `active` → `completed`
- **Business rule**: `end_date` must be after `start_date`.
  ⚠️ **Known bug**: This validation is missing — see issue-003.

### Review
An individual performance review within a cycle.

- **review_type**: `manager` (submitted by the employee's manager) or
  `self` (submitted by the employee themselves).
- **rating**: Integer 1–5 scale.
- **Business rule**: An employee can have at most one manager review and one
  self-review per cycle.

## Important Business Rules Summary

| Rule | Where it's enforced |
|------|-------------------|
| Every query must be scoped to `tenant_id` | `TenantQuery` in `database.py` |
| Email unique per tenant | `EmployeeService.create_employee()` |
| One active onboarding plan per employee | `OnboardingService.create_plan()` |
| Review cycle end_date > start_date | **NOT ENFORCED** — see issue-003 |
| Employee email cannot be changed | `EmployeeService.update_employee()` |
| Manager can only see their department | `employees_router.py` list endpoint |

## Indexing Strategy

Every table has a composite index starting with `tenant_id`:

```sql
CREATE INDEX idx_employees_tenant_dept ON employees (tenant_id, department_id);
CREATE INDEX idx_employees_tenant_email ON employees (tenant_id, email);
CREATE INDEX idx_onboarding_plans_tenant_employee ON onboarding_plans (tenant_id, employee_id);
CREATE INDEX idx_reviews_tenant_cycle ON reviews (tenant_id, cycle_id);
```

This ensures that tenant-scoped queries are fast even as the total data grows.
