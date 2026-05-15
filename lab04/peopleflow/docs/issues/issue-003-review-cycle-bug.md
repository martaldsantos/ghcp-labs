# Issue 003: Review Cycle End Date Not Validated

**Type:** Bug  
**Priority:** High  
**Labels:** `bug`, `performance`  
**Assigned to:** New joiner  

---

## Description

When creating a performance review cycle via `POST /reviews/cycles`, the API
does not validate that `end_date` is after `start_date`. This allows creating
invalid review cycles where the end date is before the start date.

## Steps to reproduce

```bash
curl -X POST https://api-staging.peopleflow.io/reviews/cycles \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Q2 2025 Review",
    "start_date": "2025-06-30",
    "end_date": "2025-04-01"
  }'
```

**Expected**: 422 error — "end_date must be after start_date"  
**Actual**: 201 Created — the invalid cycle is created successfully

## Impact

- Downstream code that calculates review deadlines produces negative durations.
- The frontend shows confusing "X days remaining" with negative numbers.
- Managers receive incorrect reminder emails.

## Root cause

The `create_review_cycle` method in `src/performance/reviews_service.py` is
missing the date validation. There's even a TODO comment marking where it
should go:

```python
# TODO: Add validation that end_date > start_date (issue-003)
```

## Fix

### 1. Add validation in the service layer
```python
# src/performance/reviews_service.py — in create_review_cycle()

from datetime import date

start = date.fromisoformat(data["start_date"])
end = date.fromisoformat(data["end_date"])

if end <= start:
    raise ValidationError(
        "Review cycle end_date must be after start_date",
        details={
            "start_date": str(start),
            "end_date": str(end),
        },
    )
```

### 2. Add Pydantic schema validation (optional, extra safety)
Consider creating a `ReviewCycleCreate` schema in a new schemas file with
a model validator that checks the dates.

### 3. Write tests
```python
async def test_create_review_cycle_end_before_start_fails():
    response = await client.post("/reviews/cycles", json={
        "title": "Invalid Cycle",
        "start_date": "2025-06-30",
        "end_date": "2025-04-01",
    })
    assert response.status_code == 422
    assert "end_date must be after start_date" in response.json()["error"]["message"]

async def test_create_review_cycle_valid_dates_succeeds():
    response = await client.post("/reviews/cycles", json={
        "title": "Valid Cycle",
        "start_date": "2025-04-01",
        "end_date": "2025-06-30",
    })
    assert response.status_code == 201
```

## Acceptance criteria

- [ ] `POST /reviews/cycles` returns 422 when `end_date <= start_date`
- [ ] Error response follows our standard format (`{"error": {"code": "VALIDATION_ERROR", ...}}`)
- [ ] Valid date combinations still work
- [ ] Same-day start and end is rejected (`end_date` must be strictly after)
- [ ] Unit tests cover both valid and invalid cases
- [ ] The TODO comment in `reviews_service.py` is removed

## Files to look at

- `src/performance/reviews_service.py` — the `create_review_cycle` method
- `src/shared/exceptions.py` — `ValidationError` class
- `docs/data-model.md` — ReviewCycle entity description
