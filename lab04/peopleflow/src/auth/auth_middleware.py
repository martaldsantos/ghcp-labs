"""
Authentication middleware for the PeopleFlow API.

HOW AUTH WORKS AT PEOPLEFLOW:
We have TWO auth middlewares and new joiners always ask why (see faq-new-joiners.md):

1. **TenantAuthMiddleware** (this file) — Runs on EVERY request. Extracts tenant_id
   and user info from the JWT in the Authorization header. Sets context variables
   so that downstream code (services, logging) can access them without passing
   them through every function signature.

2. **permissions.py** — A decorator applied to individual route handlers to check
   role-based access (HR Admin, Manager, Employee). This is NOT middleware — it's
   a dependency injected per-route.

WHY two layers: Tenant identification must happen on every single request (no
exceptions), but role checks vary per endpoint. Combining them would either make
the middleware too complex or require every endpoint to declare its role requirements
in a middleware config — we tried that in v1 and it was error-prone.

JWT structure (decoded payload):
{
    "sub": "user-uuid",
    "tenant_id": "tenant-uuid",
    "email": "ada@acme.com",
    "role": "hr_admin",          # One of: hr_admin, manager, employee
    "exp": 1700000000
}
"""

from typing import Optional
from dataclasses import dataclass

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from src.shared.logger import current_tenant_id, current_user_id, get_logger

logger = get_logger(__name__)


@dataclass
class CurrentUser:
    """Represents the authenticated user for the current request.

    Attached to request.state.user by the auth middleware so that route
    handlers and permission decorators can access it.
    """
    user_id: str
    tenant_id: str
    email: str
    role: str  # "hr_admin" | "manager" | "employee"


class TenantAuthMiddleware(BaseHTTPMiddleware):
    """Extracts tenant and user context from the JWT on every request.

    Skips authentication for:
    - Health check endpoints (/health, /readiness)
    - OpenAPI docs (/docs, /openapi.json)
    """

    SKIP_AUTH_PATHS = {"/health", "/readiness", "/docs", "/openapi.json", "/redoc"}

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.SKIP_AUTH_PATHS:
            return await call_next(request)

        token = self._extract_token(request)
        if token is None:
            raise HTTPException(status_code=401, detail="Missing Authorization header")

        user = self._decode_and_validate(token)
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        # Set context variables for logging and downstream services
        current_tenant_id.set(user.tenant_id)
        current_user_id.set(user.user_id)

        # Attach user to request so route handlers can access it
        request.state.user = user

        response = await call_next(request)
        return response

    @staticmethod
    def _extract_token(request: Request) -> Optional[str]:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header[7:]
        return None

    @staticmethod
    def _decode_and_validate(token: str) -> Optional[CurrentUser]:
        """Decode and validate a JWT token.

        In production, this verifies the signature against our JWKS endpoint.
        For local development, we accept unsigned tokens (controlled by
        the AUTH_SKIP_VERIFICATION env var — never set this in production).
        """
        # NOTE: Actual JWT decoding uses python-jose. Simplified here for clarity.
        # In the real codebase, see src/auth/_jwt.py for the full implementation.
        import json
        import base64

        try:
            # Decode payload (middle segment of the JWT)
            payload_segment = token.split(".")[1]
            # Add padding if needed
            padding = 4 - len(payload_segment) % 4
            if padding != 4:
                payload_segment += "=" * padding
            payload = json.loads(base64.urlsafe_b64decode(payload_segment))

            return CurrentUser(
                user_id=payload["sub"],
                tenant_id=payload["tenant_id"],
                email=payload["email"],
                role=payload["role"],
            )
        except (IndexError, KeyError, Exception) as e:
            logger.warning(f"Token decode failed: {e}")
            return None
