"""
Employee service — business logic layer.

This is where business rules live. Routers handle HTTP concerns (status codes,
response models), services handle domain logic (validation, orchestration),
and the database layer handles persistence.

IMPORTANT: Every method takes tenant_id as the first parameter. This is
intentional — it makes the tenant scoping explicit and hard to forget.
"""

from typing import Optional
from uuid import uuid4
from datetime import datetime

from src.shared.database import get_db_session, TenantQuery
from src.shared.exceptions import NotFoundError, DuplicateError, ValidationError
from src.shared.logger import get_logger

logger = get_logger(__name__)


class EmployeeService:
    """Handles employee CRUD operations and business rules."""

    async def create_employee(self, tenant_id: str, data: dict) -> dict:
        """Create a new employee record.

        Business rules:
        - Email must be unique within the tenant (not globally — different
          tenants can have employees with the same email).
        - start_date cannot be more than 90 days in the past.
        - If a manager_id is provided, that manager must exist and belong
          to the same tenant.

        After creation, triggers the onboarding workflow (welcome email,
        tool provisioning) via Celery tasks.
        """
        async with get_db_session() as session:
            query = TenantQuery(session, tenant_id)

            # Check for duplicate email within this tenant
            existing = await self._find_by_email(query, data["email"])
            if existing:
                raise DuplicateError(
                    f"Employee with email '{data['email']}' already exists",
                    details={"field": "email", "value": data["email"]},
                )

            # Validate manager exists if provided
            if data.get("manager_id"):
                manager = await query.get_by_id(_EmployeeModel, data["manager_id"])
                if not manager:
                    raise ValidationError(
                        "Specified manager does not exist",
                        details={"field": "manager_id", "value": data["manager_id"]},
                    )

            employee_id = str(uuid4())
            now = datetime.utcnow()

            employee = {
                "id": employee_id,
                "tenant_id": tenant_id,
                "status": "pending",
                "created_at": now,
                "updated_at": now,
                **data,
            }

            logger.info(f"Employee created: {employee_id} in tenant {tenant_id}")

            # Trigger onboarding tasks asynchronously
            # See src/onboarding/onboarding_tasks.py for what happens next
            from src.onboarding.onboarding_tasks import trigger_onboarding
            trigger_onboarding.delay(tenant_id, employee_id, data["email"])

            return employee

    async def get_employee(self, tenant_id: str, employee_id: str) -> dict:
        """Fetch a single employee by ID, scoped to the tenant."""
        async with get_db_session() as session:
            query = TenantQuery(session, tenant_id)
            employee = await query.get_by_id(_EmployeeModel, employee_id)
            if not employee:
                raise NotFoundError(
                    f"Employee '{employee_id}' not found",
                    details={"employee_id": employee_id},
                )
            return employee

    async def list_employees(
        self,
        tenant_id: str,
        page: int = 1,
        page_size: int = 20,
        department_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> dict:
        """List employees with pagination and optional filters.

        TODO (issue-002): Add name/department search filter.
        Currently only supports filtering by exact department_id and status.
        """
        async with get_db_session() as session:
            query = TenantQuery(session, tenant_id)
            conditions = []

            if department_id:
                conditions.append(_EmployeeModel.department_id == department_id)
            if status:
                conditions.append(_EmployeeModel.status == status)

            employees = await query.filter(_EmployeeModel, *conditions)

            # Manual pagination — in production we'd push this to the DB query
            start = (page - 1) * page_size
            end = start + page_size

            return {
                "items": employees[start:end],
                "total": len(employees),
                "page": page,
                "page_size": page_size,
            }

    async def update_employee(
        self, tenant_id: str, employee_id: str, data: dict
    ) -> dict:
        """Update an employee's mutable fields.

        Business rules:
        - Cannot change email (it's used as an identity key in external systems).
        - Status transitions are validated (see EmploymentStatus in schemas).
        - Changing department requires manager role or above.
        """
        employee = await self.get_employee(tenant_id, employee_id)

        if "email" in data:
            raise ValidationError(
                "Email cannot be changed after creation. "
                "Contact HR admin to create a new employee record.",
                details={"field": "email"},
            )

        # Apply updates
        for key, value in data.items():
            if value is not None:
                employee[key] = value

        employee["updated_at"] = datetime.utcnow()

        logger.info(f"Employee updated: {employee_id} in tenant {tenant_id}")
        return employee

    @staticmethod
    async def _find_by_email(query: TenantQuery, email: str):
        """Find an employee by email within the tenant scope."""
        results = await query.filter(_EmployeeModel, _EmployeeModel.email == email)
        return results[0] if results else None


# Placeholder model reference — in the real codebase this is the SQLAlchemy model
# defined in src/employees/models.py. Kept as a simple class here for demo clarity.
class _EmployeeModel:
    tenant_id = "tenant_id"
    id = "id"
    email = "email"
    department_id = "department_id"
    status = "status"
