"""
Performance review API routes.

Endpoints for managing review cycles and individual performance reviews.
Review cycles are time-bounded periods (usually quarterly) during which
managers submit reviews for their direct reports.
"""

from fastapi import APIRouter, Request, Query
from typing import Optional

from src.auth.permissions import require_role
from src.performance.reviews_service import ReviewService

router = APIRouter(prefix="/reviews", tags=["performance"])
service = ReviewService()


@router.get("/cycles")
@require_role("hr_admin", "manager")
async def list_review_cycles(
    request: Request,
    status: Optional[str] = Query(None, description="Filter: draft, active, completed"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """List all review cycles for the tenant.

    HR admins see all cycles. Managers see only active and completed cycles
    (drafts are hidden until published).
    """
    tenant_id = request.state.user.tenant_id
    return await service.list_review_cycles(
        tenant_id, status=status, page=page, page_size=page_size
    )


@router.get("/cycles/{cycle_id}")
@require_role("hr_admin", "manager")
async def get_review_cycle(request: Request, cycle_id: str):
    """Get details of a specific review cycle."""
    tenant_id = request.state.user.tenant_id
    return await service.get_review_cycle(tenant_id, cycle_id)


@router.post("/cycles", status_code=201)
@require_role("hr_admin")
async def create_review_cycle(request: Request, body: dict):
    """Create a new performance review cycle.

    Only HR admins can create cycles. New cycles start in 'draft' status
    and must be explicitly activated.

    Required fields:
    - title: Human-readable name (e.g. "Q2 2025 Performance Review")
    - start_date: When reviews can begin being submitted
    - end_date: Deadline for review submissions
    """
    tenant_id = request.state.user.tenant_id
    return await service.create_review_cycle(tenant_id, body)


@router.post("/cycles/{cycle_id}/reviews", status_code=201)
@require_role("hr_admin", "manager", "employee")
async def submit_review(request: Request, cycle_id: str, body: dict):
    """Submit a performance review within a cycle.

    Managers submit reviews for their direct reports.
    Employees can submit self-reviews.

    Required fields:
    - reviewee_id: The employee being reviewed
    - review_type: "manager" or "self"
    - rating: 1-5 scale
    - strengths: Free text
    - areas_for_improvement: Free text
    """
    tenant_id = request.state.user.tenant_id
    return await service.submit_review(tenant_id, cycle_id, body)
