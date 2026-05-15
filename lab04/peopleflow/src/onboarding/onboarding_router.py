"""
Onboarding API routes.

The onboarding module manages the structured process that new employees
go through during their first 30/60/90 days. Each employee gets an
OnboardingPlan with a set of tasks (watch training video, meet team lead,
set up dev environment, etc.).

Business rule: An employee can have at most ONE active onboarding plan.
If they leave and rejoin, a new plan is created but the old one is
archived (status = "archived"), not deleted.
"""

from fastapi import APIRouter, Request, Query
from typing import Optional

from src.auth.permissions import require_role
from src.onboarding.onboarding_service import OnboardingService

router = APIRouter(prefix="/onboarding", tags=["onboarding"])
service = OnboardingService()


@router.get("/plans")
@require_role("hr_admin", "manager")
async def list_onboarding_plans(
    request: Request,
    status: Optional[str] = Query(None, description="Filter: active, completed, archived"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """List all onboarding plans for the tenant.

    HR admins see all plans. Managers see plans for their department only.
    """
    tenant_id = request.state.user.tenant_id
    return await service.list_plans(tenant_id, status=status, page=page, page_size=page_size)


@router.get("/plans/{plan_id}")
@require_role("hr_admin", "manager", "employee")
async def get_onboarding_plan(request: Request, plan_id: str):
    """Get a specific onboarding plan with its tasks.

    Employees can only view their own onboarding plan.
    """
    tenant_id = request.state.user.tenant_id
    return await service.get_plan(tenant_id, plan_id)


@router.post("/plans", status_code=201)
@require_role("hr_admin")
async def create_onboarding_plan(request: Request, body: dict):
    """Create a new onboarding plan for an employee.

    Typically this is triggered automatically when an employee is created
    (see onboarding_tasks.py), but HR admins can also create plans manually
    for re-onboarding scenarios (e.g. internal transfers).
    """
    tenant_id = request.state.user.tenant_id
    return await service.create_plan(tenant_id, body)


@router.patch("/plans/{plan_id}/tasks/{task_id}")
@require_role("hr_admin", "manager", "employee")
async def update_task_status(
    request: Request, plan_id: str, task_id: str, body: dict
):
    """Mark an onboarding task as completed.

    Employees can complete their own tasks. Managers and HR admins
    can complete tasks on behalf of employees (e.g. "buddy intro"
    tasks completed by the manager).
    """
    tenant_id = request.state.user.tenant_id
    return await service.update_task(tenant_id, plan_id, task_id, body)
