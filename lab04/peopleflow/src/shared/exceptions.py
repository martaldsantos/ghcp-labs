"""
Centralised exception handling for the PeopleFlow API.

WHY THIS EXISTS:
We want every error returned by the API to follow the same JSON structure so
that frontend and mobile clients can rely on a single error-parsing path.
All routers re-use these exceptions via the FastAPI exception handlers
registered in main.py.

PATTERN:
  1. Define domain exceptions as subclasses of PeopleFlowError.
  2. Raise them freely in service code — never return raw HTTP responses
     from service functions.
  3. The exception handlers in main.py catch them and produce the standard
     JSON envelope: {"error": {"code": "...", "message": "...", "details": ...}}

Adding a new exception:
  1. Create a subclass of PeopleFlowError with a unique `code` and default
     `status_code`.
  2. That's it — the global handler picks it up automatically.
"""

from typing import Any


class PeopleFlowError(Exception):
    """Base exception for all PeopleFlow domain errors.

    Subclass this for every new error category. The global exception handler
    in main.py will catch it and return a structured JSON response.
    """

    code: str = "INTERNAL_ERROR"
    status_code: int = 500

    def __init__(self, message: str, details: Any = None):
        self.message = message
        self.details = details
        super().__init__(message)

    def to_dict(self) -> dict:
        payload = {"code": self.code, "message": self.message}
        if self.details is not None:
            payload["details"] = self.details
        return {"error": payload}


# ---------------------------------------------------------------------------
# 4xx — Client errors
# ---------------------------------------------------------------------------

class NotFoundError(PeopleFlowError):
    """Raised when a requested resource does not exist (or is not visible to the tenant)."""
    code = "NOT_FOUND"
    status_code = 404


class ValidationError(PeopleFlowError):
    """Raised when request data fails business-rule validation.

    Use this for domain validation (e.g. "review end date before start date"),
    NOT for schema validation — Pydantic handles that automatically.
    """
    code = "VALIDATION_ERROR"
    status_code = 422


class DuplicateError(PeopleFlowError):
    """Raised when creating a resource that already exists (e.g. duplicate email)."""
    code = "DUPLICATE"
    status_code = 409


class ForbiddenError(PeopleFlowError):
    """Raised when the user's role does not permit the requested action."""
    code = "FORBIDDEN"
    status_code = 403


class UnauthorizedError(PeopleFlowError):
    """Raised when authentication is missing or invalid."""
    code = "UNAUTHORIZED"
    status_code = 401


# ---------------------------------------------------------------------------
# 5xx — Server errors
# ---------------------------------------------------------------------------

class ExternalServiceError(PeopleFlowError):
    """Raised when a call to an external service (email provider, SSO, etc.) fails.

    We wrap external failures so that callers get a consistent error shape
    instead of random HTTP/connection errors bubbling up.
    """
    code = "EXTERNAL_SERVICE_ERROR"
    status_code = 502
