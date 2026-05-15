"""
Pydantic schemas for the Employees module.

These schemas serve as the API contract. The frontend team uses them to
generate TypeScript types (via openapi-typescript-codegen), so changing
field names or types is a BREAKING CHANGE — coordinate with frontend first.

Naming convention:
- *Create  → request body for POST
- *Update  → request body for PATCH (all fields optional)
- *Response → response body (includes server-generated fields like id, created_at)
"""

from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class EmploymentStatus(str, Enum):
    """Tracks the employee's current lifecycle stage.

    State transitions:
      pending → active → on_leave → active (can toggle)
      active → offboarding → offboarded (terminal)
    """
    pending = "pending"          # Offer accepted, not yet started
    active = "active"
    on_leave = "on_leave"
    offboarding = "offboarding"  # Notice period
    offboarded = "offboarded"    # No longer with the company


class EmployeeCreate(BaseModel):
    """Request body for creating a new employee.

    Note: tenant_id is NOT in the request body — it comes from the JWT
    via the auth middleware. This prevents tenants from creating employees
    in other tenants' data.
    """
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    department_id: str
    manager_id: Optional[str] = None
    job_title: str = Field(..., max_length=200)
    start_date: date
    employment_type: str = Field(
        default="full_time",
        description="One of: full_time, part_time, contractor",
    )


class EmployeeUpdate(BaseModel):
    """Request body for updating an employee. All fields optional."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    department_id: Optional[str] = None
    manager_id: Optional[str] = None
    job_title: Optional[str] = Field(None, max_length=200)
    employment_type: Optional[str] = None
    status: Optional[EmploymentStatus] = None


class EmployeeResponse(BaseModel):
    """Response body for employee endpoints.

    Includes server-generated fields. This is what the frontend receives.
    """
    id: str
    tenant_id: str
    email: str
    first_name: str
    last_name: str
    department_id: str
    department_name: Optional[str] = None  # Populated via join
    manager_id: Optional[str] = None
    job_title: str
    status: EmploymentStatus
    start_date: date
    employment_type: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EmployeeListResponse(BaseModel):
    """Paginated list of employees."""
    items: list[EmployeeResponse]
    total: int
    page: int
    page_size: int
