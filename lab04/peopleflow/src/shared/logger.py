"""
Structured logging configuration.

WHY structured logs: We ship logs to Datadog. Structured JSON logs let us
filter and alert on fields like tenant_id, user_id, and action without
writing fragile regex parsers.

Every log entry automatically includes the tenant context when available,
so you don't need to manually add tenant_id to every log call.
"""

import logging
import json
import sys
from contextvars import ContextVar
from typing import Optional

# Context variables — set by the auth middleware on each request
current_tenant_id: ContextVar[Optional[str]] = ContextVar("current_tenant_id", default=None)
current_user_id: ContextVar[Optional[str]] = ContextVar("current_user_id", default=None)


class StructuredFormatter(logging.Formatter):
    """Formats log records as single-line JSON for log aggregation."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "tenant_id": current_tenant_id.get(),
            "user_id": current_user_id.get(),
        }
        if record.exc_info and record.exc_info[0] is not None:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)


def get_logger(name: str) -> logging.Logger:
    """Create a logger with our standard structured formatter.

    Usage:
        from src.shared.logger import get_logger
        logger = get_logger(__name__)
        logger.info("Employee created", extra={"employee_id": emp.id})
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
