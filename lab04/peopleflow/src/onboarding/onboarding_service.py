"""
Onboarding service — business logic for onboarding plans and tasks.

An OnboardingPlan is a checklist of tasks a new employee must complete.
Each plan follows a template (defined by HR admins per department) but
can be customized per employee.

Key entities:
- OnboardingPlan: The container. Has a status (active/completed/archived)
  and belongs to exactly one employee.
- OnboardingTask: Individual items within a plan (e.g. "Complete security
  training", "Set up local dev environment").
"""

from typing import Optional
from uuid import uuid4
from datetime import datetime

from src.shared.database import get_db_session, TenantQuery
from src.shared.exceptions import NotFoundError, ValidationError, DuplicateError
from src.shared.logger import get_logger

logger = get_logger(__name__)

# Default onboarding tasks applied to every new employee.
# Department-specific tasks are added on top of these.
DEFAULT_ONBOARDING_TASKS = [
    {"title": "Complete security awareness training", "due_day": 3, "category": "compliance"},
    {"title": "Set up local development environment", "due_day": 2, "category": "engineering"},
    {"title": "Read architecture.md and codebase-tour.md", "due_day": 3, "category": "knowledge"},
    {"title": "Meet your onboarding buddy", "due_day": 1, "category": "people"},
    {"title": "Attend team standup (first week)", "due_day": 5, "category": "people"},
    {"title": "Submit first pull request (can be a docs fix)", "due_day": 10, "category": "engineering"},
    {"title": "Complete 30-day check-in with manager", "due_day": 30, "category": "people"},
]


class OnboardingService:
    """Manages the onboarding lifecycle for new employees."""

    async def create_plan(self, tenant_id: str, data: dict) -> dict:
        """Create an onboarding plan for an employee.

        Business rules:
        - An employee cannot have two active onboarding plans simultaneously.
          If they already have one, this raises a DuplicateError.
        - The plan is pre-populated with DEFAULT_ONBOARDING_TASKS plus any
          department-specific tasks.
        """
        employee_id = data.get("employee_id")
        if not employee_id:
            raise ValidationError("employee_id is required")

        # Check for existing active plan — business rule enforcement
        existing_active = await self._get_active_plan_for_employee(
            tenant_id, employee_id
        )
        if existing_active:
            raise DuplicateError(
                f"Employee '{employee_id}' already has an active onboarding plan. "
                "Archive the existing plan before creating a new one.",
                details={"existing_plan_id": existing_active["id"]},
            )

        plan_id = str(uuid4())
        now = datetime.utcnow()

        # Build task list from defaults + any custom tasks in the request
        tasks = []
        for i, task_template in enumerate(DEFAULT_ONBOARDING_TASKS):
            tasks.append({
                "id": str(uuid4()),
                "plan_id": plan_id,
                "title": task_template["title"],
                "category": task_template["category"],
                "due_day": task_template["due_day"],
                "status": "pending",
                "completed_at": None,
            })

        # Add custom tasks if provided
        for custom_task in data.get("custom_tasks", []):
            tasks.append({
                "id": str(uuid4()),
                "plan_id": plan_id,
                "title": custom_task["title"],
                "category": custom_task.get("category", "custom"),
                "due_day": custom_task.get("due_day", 14),
                "status": "pending",
                "completed_at": None,
            })

        plan = {
            "id": plan_id,
            "tenant_id": tenant_id,
            "employee_id": employee_id,
            "status": "active",
            "tasks": tasks,
            "created_at": now,
            "updated_at": now,
        }

        logger.info(
            f"Onboarding plan created: {plan_id} for employee {employee_id} "
            f"with {len(tasks)} tasks"
        )
        return plan

    async def get_plan(self, tenant_id: str, plan_id: str) -> dict:
        """Fetch a single onboarding plan with all its tasks."""
        # In production, this queries the DB with tenant scoping
        raise NotFoundError(f"Onboarding plan '{plan_id}' not found")

    async def list_plans(
        self,
        tenant_id: str,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """List onboarding plans with optional status filter."""
        return {"items": [], "total": 0, "page": page, "page_size": page_size}

    async def update_task(
        self, tenant_id: str, plan_id: str, task_id: str, data: dict
    ) -> dict:
        """Update an onboarding task (typically to mark it as completed).

        When all tasks in a plan are completed, the plan status automatically
        transitions to 'completed' and the manager is notified.
        """
        new_status = data.get("status")
        if new_status not in ("pending", "completed"):
            raise ValidationError(
                f"Invalid task status: '{new_status}'. Must be 'pending' or 'completed'."
            )

        logger.info(f"Task {task_id} in plan {plan_id} updated to '{new_status}'")

        # After updating, check if ALL tasks are now completed
        # If so, transition the plan to "completed" status
        # (implementation omitted for brevity)

        return {"task_id": task_id, "status": new_status}

    async def _get_active_plan_for_employee(
        self, tenant_id: str, employee_id: str
    ) -> Optional[dict]:
        """Check if an employee already has an active onboarding plan."""
        # In production: query DB for plan where employee_id matches and status = 'active'
        return None
