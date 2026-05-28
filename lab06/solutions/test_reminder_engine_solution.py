from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from reminder_engine import (
    Approval,
    ReminderPolicy,
    build_evidence_payload,
    is_eligible_for_reminder,
    run_scheduler_cycle,
    validate_policy,
)


def fixed_now() -> datetime:
    return datetime(2026, 5, 27, 12, 0, 0, tzinfo=timezone.utc)


def test_validate_policy_rejects_invalid_threshold() -> None:
    with pytest.raises(ValueError):
        validate_policy(ReminderPolicy(threshold_hours=0, cooldown_hours=24))


def test_eligibility_true_at_48h_boundary() -> None:
    now = fixed_now()
    approval = Approval(
        approval_id="APR-200",
        manager_email="manager@example.com",
        requested_at=now - timedelta(hours=48),
        status="PENDING",
    )

    ok, reason = is_eligible_for_reminder(approval, now, ReminderPolicy())

    assert ok is True
    assert reason == "eligible"


def test_scheduler_processes_only_eligible_items() -> None:
    now = fixed_now()
    approvals = [
        Approval(
            approval_id="APR-201",
            manager_email="manager-a@example.com",
            requested_at=now - timedelta(hours=60),
            status="PENDING",
        ),
        Approval(
            approval_id="APR-202",
            manager_email="manager-b@example.com",
            requested_at=now - timedelta(hours=10),
            status="PENDING",
        ),
        Approval(
            approval_id="APR-203",
            manager_email="manager-c@example.com",
            requested_at=now - timedelta(hours=70),
            status="APPROVED",
        ),
    ]

    result = run_scheduler_cycle(approvals, ReminderPolicy(), now=now)

    assert result.evaluated == 3
    assert result.eligible == 1
    assert len(result.attempts) == 1
    assert result.attempts[0].approval_id == "APR-201"
    assert result.attempts[0].outcome == "SENT"


def test_evidence_payload_summarizes_attempts() -> None:
    now = fixed_now()
    approvals = [
        Approval(
            approval_id="APR-204",
            manager_email="manager@example.com",
            requested_at=now - timedelta(hours=55),
            status="PENDING",
        )
    ]

    result = run_scheduler_cycle(approvals, ReminderPolicy(), now=now)
    payload = build_evidence_payload(result)

    assert payload["evaluated"] == 1
    assert payload["eligible"] == 1
    assert payload["sent"] == 1
    assert payload["failed"] == 0
    assert payload["attempts"][0]["approval_id"] == "APR-204"
