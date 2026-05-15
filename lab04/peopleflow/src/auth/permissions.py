"""
Role-based permission checks for PeopleFlow API endpoints.

THREE ROLES:
- hr_admin:  Full access. Can manage employees across all departments,
             configure onboarding plans, and view all performance reviews.
- manager:   Can view/edit employees in their department, submit and view
             reviews for their direct reports.
- employee:  Can view their own profile and submit self-reviews.

HOW TO USE:
Apply the `require_role` decorator to any route handler. It reads the
CurrentUser from request.state (set by TenantAuthMiddleware) and raises
ForbiddenError if the user's role is insufficient.

Example:
    @router.get("/employees")
    @require_role("hr_admin", "manager")
    async def list_employees(request: Request):
        ...

WHY a decorator instead of FastAPI Depends():
We initially used Depends() but found that it made the function signatures
noisy when combined with other dependencies (db session, pagination, filters).
The decorator approach keeps route signatures clean and makes the required
role immediately visible at the top of the function.
"""

from functools import wraps
from typing import Callable

from fastapi import Request

from src.shared.exceptions import ForbiddenError
from src.shared.logger import get_logger

logger = get_logger(__name__)

# Role hierarchy — higher roles inherit permissions of lower roles.
# hr_admin > manager > employee
ROLE_HIERARCHY = {
    "hr_admin": 3,
    "manager": 2,
    "employee": 1,
}


def require_role(*allowed_roles: str) -> Callable:
    """Decorator that restricts a route handler to specific roles.

    Args:
        *allowed_roles: One or more role names. The user must have at least
            one of these roles (or a higher role in the hierarchy).

    Raises:
        ForbiddenError: If the user's role is not sufficient.

    Usage:
        @router.post("/employees")
        @require_role("hr_admin")
        async def create_employee(request: Request, ...):
            ...

        @router.get("/employees")
        @require_role("hr_admin", "manager")
        async def list_employees(request: Request, ...):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # FastAPI injects `request` as a keyword argument
            request: Request = kwargs.get("request")
            if request is None:
                # Also check positional args for cases where request is first param
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break

            if request is None or not hasattr(request.state, "user"):
                raise ForbiddenError("Authentication required")

            user = request.state.user
            user_level = ROLE_HIERARCHY.get(user.role, 0)

            # Check if user's role is in the allowed list OR if they have
            # a higher role in the hierarchy
            min_required_level = min(
                ROLE_HIERARCHY.get(role, 99) for role in allowed_roles
            )

            if user_level < min_required_level:
                logger.warning(
                    f"Access denied: user {user.user_id} with role '{user.role}' "
                    f"attempted action requiring {allowed_roles}"
                )
                raise ForbiddenError(
                    f"Role '{user.role}' does not have permission for this action. "
                    f"Required: {', '.join(allowed_roles)}"
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator
