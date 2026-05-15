"""
Performance review service — business logic for review cycles and reviews.

Key concepts:
- ReviewCycle: A company-wide or department-wide review period (e.g. "Q2 2025
  Performance Review"). Has a start_date, end_date, and status.
- Review: An individual review within a cycle, linking a reviewer (manager)
  to a reviewee (employee).

Business rules:
- A review cycle's end_date must be after its start_date.
  BUG (issue-003): This validation is currently missing — see
  docs/issues/issue-003-review-cycle-bug.md
- An employee can only have one review per cycle.
- Only managers can submit reviews for their direct reports.
- Employees can submit self-reviews (separate from manager reviews).
"""

from typing import Optional
from uuid import uuid4
from datetime import date, datetime

from src.shared.database import get_db_session, TenantQuery
from src.shared.exceptions import NotFoundError, ValidationError, DuplicateError
from src.shared.logger import get_logger

logger = get_logger(__name__)


class ReviewService:
    """Handles performance review cycles and individual reviews."""

    async def create_review_cycle(self, tenant_id: str, data: dict) -> dict:
        """Create a new performance review cycle.

        A review cycle defines the time window during which reviews
        can be submitted. Typically created by HR admins quarterly.

        BUG (issue-003): The end_date vs start_date validation is missing.
        Currently you can create a cycle where end_date < start_date,
        which causes confusing errors downstream when calculating
        review deadlines.
        """
        cycle_id = str(uuid4())
        now = datetime.utcnow()

        # TODO: Add validation that end_date > start_date (issue-003)
        cycle = {
            "id": cycle_id,
            "tenant_id": tenant_id,
            "title": data.get("title", "Performance Review"),
            "start_date": data.get("start_date"),
            "end_date": data.get("end_date"),
            "status": "draft",  # draft → active → completed
            "created_at": now,
            "updated_at": now,
        }

        logger.info(f"Review cycle created: {cycle_id} for tenant {tenant_id}")
        return cycle

    async def get_review_cycle(self, tenant_id: str, cycle_id: str) -> dict:
        """Fetch a single review cycle by ID."""
        raise NotFoundError(f"Review cycle '{cycle_id}' not found")

    async def list_review_cycles(
        self,
        tenant_id: str,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """List review cycles with optional status filter."""
        return {"items": [], "total": 0, "page": page, "page_size": page_size}

    async def submit_review(self, tenant_id: str, cycle_id: str, data: dict) -> dict:
        """Submit a performance review for an employee.

        Business rules:
        - The review cycle must be in 'active' status.
        - The reviewer must be the employee's manager (or the employee
          themselves for a self-review).
        - An employee can only have one manager review per cycle.
        - Self-reviews and manager reviews are tracked separately.
        """
        review_id = str(uuid4())
        now = datetime.utcnow()

        review_type = data.get("review_type", "manager")  # "manager" or "self"

        review = {
            "id": review_id,
            "tenant_id": tenant_id,
            "cycle_id": cycle_id,
            "reviewer_id": data.get("reviewer_id"),
            "reviewee_id": data.get("reviewee_id"),
            "review_type": review_type,
            "rating": data.get("rating"),  # 1-5 scale
            "strengths": data.get("strengths", ""),
            "areas_for_improvement": data.get("areas_for_improvement", ""),
            "goals_for_next_period": data.get("goals_for_next_period", ""),
            "status": "submitted",
            "created_at": now,
            "updated_at": now,
        }

        logger.info(
            f"Review submitted: {review_id} (type: {review_type}) "
            f"in cycle {cycle_id}"
        )
        return review
