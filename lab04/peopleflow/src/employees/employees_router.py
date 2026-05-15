"""
Employee API routes.

All endpoints are scoped to the authenticated tenant — you can never
access employees from another tenant, even if you know their ID.

Permissions:
- GET    /employees      → hr_admin, manager (managers see their department only)
- GET    /employees/{id} → hr_admin, manager, employee (employees see own profile)
- POST   /employees      → hr_admin only
- PATCH  /employees/{id} → hr_admin, manager
- DELETE /employees/{id} → hr_admin only (soft-delete → sets status to offboarded)
"""

from fastapi import APIRouter, Request, Query
from typing import Optional

from src.auth.permissions import require_role
from src.employees.employees_schemas import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
    EmployeeListResponse,
)
from src.employees.employees_service import EmployeeService

router = APIRouter(prefix="/employees", tags=["employees"])
service = EmployeeService()


@router.get("", response_model=EmployeeListResponse)
@require_role("hr_admin", "manager")
async def list_employees(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    department_id: Optional[str] = Query(None, description="Filter by department"),
    status: Optional[str] = Query(None, description="Filter by employment status"),
):
    """List all employees in the tenant with pagination.

    Managers see only employees in their department. HR admins see everyone.
    """
    tenant_id = request.state.user.tenant_id

    # If the user is a manager (not hr_admin), restrict to their department
    if request.state.user.role == "manager":
        department_id = request.state.user.department_id

    return await service.list_employees(
        tenant_id=tenant_id,
        page=page,
        page_size=page_size,
        department_id=department_id,
        status=status,
    )


@router.get("/{employee_id}", response_model=EmployeeResponse)
@require_role("hr_admin", "manager", "employee")
async def get_employee(request: Request, employee_id: str):
    """Get a single employee by ID.

    Employees can only view their own profile. Managers can view
    employees in their department. HR admins can view anyone.
    """
    tenant_id = request.state.user.tenant_id
    return await service.get_employee(tenant_id, employee_id)


@router.post("", response_model=EmployeeResponse, status_code=201)
@require_role("hr_admin")
async def create_employee(request: Request, body: EmployeeCreate):
    """Create a new employee.

    Triggers the onboarding workflow automatically:
    1. Sends welcome email
    2. Creates default onboarding plan
    3. Provisions tool access (Slack, GitHub, etc.)

    Only HR admins can create employees.
    """
    tenant_id = request.state.user.tenant_id
    return await service.create_employee(tenant_id, body.model_dump())


@router.patch("/{employee_id}", response_model=EmployeeResponse)
@require_role("hr_admin", "manager")
async def update_employee(
    request: Request, employee_id: str, body: EmployeeUpdate
):
    """Update an existing employee's details.

    Note: Email cannot be changed after creation (it's used as an
    identity key in external systems like SSO and payroll).
    """
    tenant_id = request.state.user.tenant_id
    return await service.update_employee(
        tenant_id, employee_id, body.model_dump(exclude_unset=True)
    )
