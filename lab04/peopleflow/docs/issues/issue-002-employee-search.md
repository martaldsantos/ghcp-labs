# Issue 002: Add Employee Search Filter

**Type:** Feature  
**Priority:** Medium  
**Labels:** `enhancement`, `employees`  
**Assigned to:** New joiner  

---

## Description

The `GET /employees` endpoint currently only supports filtering by `department_id`
and `status`. Product has requested adding a text search filter so that HR admins
and managers can search employees by name or department name.

## User story

> As an HR admin, I want to search employees by name so that I can quickly find
> a specific person without scrolling through the full employee list.

## Requirements

1. Add a `search` query parameter to `GET /employees`
2. The search should match against:
   - `first_name` (case-insensitive, partial match)
   - `last_name` (case-insensitive, partial match)
   - `department_name` (case-insensitive, partial match)
3. The search parameter should be combinable with existing filters
   (`department_id`, `status`)
4. Empty search string should return all results (same as no filter)

## API design

```
GET /employees?search=ada
GET /employees?search=engineering&status=active
GET /employees?search=smith&page=2&page_size=10
```

## What needs to change

### 1. Router (`src/employees/employees_router.py`)
Add the `search` query parameter:
```python
@router.get("", response_model=EmployeeListResponse)
@require_role("hr_admin", "manager")
async def list_employees(
    request: Request,
    search: Optional[str] = Query(None, description="Search by name or department"),
    # ... existing params
):
```

### 2. Service (`src/employees/employees_service.py`)
Update `list_employees()` to accept and apply the search filter:
```python
async def list_employees(
    self,
    tenant_id: str,
    search: Optional[str] = None,  # NEW
    # ... existing params
) -> dict:
```

### 3. Database query
Use `ILIKE` for case-insensitive partial matching:
```sql
WHERE (first_name ILIKE '%search%' 
   OR last_name ILIKE '%search%'
   OR department_name ILIKE '%search%')
```

## Acceptance criteria

- [ ] `GET /employees?search=ada` returns employees matching "ada" in name
- [ ] Search is case-insensitive
- [ ] Search works with partial matches
- [ ] Search combines correctly with `department_id` and `status` filters
- [ ] Pagination works correctly with search results
- [ ] Tenant isolation is maintained (search only within the tenant's data)
- [ ] Unit tests cover the new search functionality
- [ ] API documentation (docstring) is updated

## Files to look at

- `src/employees/employees_router.py` — route handler
- `src/employees/employees_service.py` — business logic
- `src/shared/database.py` — `TenantQuery` helper (may need extension)
- `docs/common-tasks.md` — Section 1 (Adding a new API endpoint)
