"""FR-001 Manager Approval Reminder — test file.

Write one test per story as you work through the sprint.
Each stub below maps to a Jira story / Azure DevOps work item.
Fill in the test body, make it fail first, then implement the function until it passes.

Run all tests at any time:
    pytest -q tests/test_reminder_engine.py

Reference solution (peek only if stuck):
    solutions/test_reminder_engine_solution.py
"""

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
    """Return a fixed UTC timestamp to use in tests so results are deterministic."""
    return datetime(2026, 5, 27, 12, 0, 0, tzinfo=timezone.utc)


# ─── SCRUM-2 / Story 1: Policy validation ─────────────────────────────────────

def test_validate_policy_rejects_invalid_threshold() -> None:
    """validate_policy should raise ValueError when threshold_hours <= 0."""
    with pytest.raises(ValueError):
        validate_policy(ReminderPolicy(threshold_hours=0))


def test_validate_policy_rejects_negative_cooldown() -> None:
    """validate_policy should raise ValueError when cooldown_hours < 0."""
    with pytest.raises(ValueError):
        validate_policy(ReminderPolicy(cooldown_hours=-1))


# ─── SCRUM-6 / Story 3: Eligibility detection ─────────────────────────────────

def test_eligibility_true_at_48h_boundary() -> None:
    """An approval exactly 48 hours old should be eligible."""
    now = fixed_now()
    approval = Approval(
        approval_id="A1",
        manager_email="manager@example.com",
        requested_at=now - timedelta(hours=48),
    )
    eligible, reason = is_eligible_for_reminder(approval, now, ReminderPolicy())
    assert eligible is True
    assert reason == "eligible"


def test_eligibility_false_before_threshold() -> None:
    """An approval less than 48 hours old should not be eligible."""
    now = fixed_now()
    approval = Approval(
        approval_id="A2",
        manager_email="manager@example.com",
        requested_at=now - timedelta(hours=47),
    )
    eligible, reason = is_eligible_for_reminder(approval, now, ReminderPolicy())
    assert eligible is False
    assert reason == "threshold not reached"


def test_eligibility_false_for_non_pending() -> None:
    """An APPROVED or REJECTED approval should never be eligible."""
    now = fixed_now()
    approval = Approval(
        approval_id="A3",
        manager_email="manager@example.com",
        requested_at=now - timedelta(hours=72),
        status="APPROVED",
    )
    eligible, reason = is_eligible_for_reminder(approval, now, ReminderPolicy())
    assert eligible is False
    assert reason == "approval is not pending"


# ─── SCRUM-3 / Story 4: Scheduler ─────────────────────────────────────────────

def test_scheduler_processes_only_eligible_items() -> None:
    """The scheduler should send reminders only to approvals that meet the policy threshold."""
    now = fixed_now()
    approvals = [
        Approval("A1", "mgr@example.com", now - timedelta(hours=49)),         # eligible
        Approval("A2", "mgr@example.com", now - timedelta(hours=10)),         # too recent
        Approval("A3", "mgr@example.com", now - timedelta(hours=72), status="APPROVED"),  # not pending
    ]
    result = run_scheduler_cycle(approvals, ReminderPolicy(), now=now)
    assert result.evaluated == 3
    assert result.eligible == 1
    assert len(result.attempts) == 1
    assert result.attempts[0].approval_id == "A1"
    assert result.attempts[0].outcome == "SENT"


def test_scheduler_records_failed_attempt_for_bad_email() -> None:
    """send_reminder should record a FAILED attempt when manager_email has no '@'."""
    now = fixed_now()
    approvals = [Approval("A1", "not-an-email", now - timedelta(hours=49))]
    result = run_scheduler_cycle(approvals, ReminderPolicy(), now=now)
    assert result.attempts[0].outcome == "FAILED"
    assert result.attempts[0].reason == "invalid recipient address"


# ─── SCRUM-4 / Story 5: Evidence payload ──────────────────────────────────────

def test_evidence_payload_summarizes_attempts() -> None:
    """build_evidence_payload should return a dict with counts and attempt details."""
    now = fixed_now()
    approvals = [Approval("A1", "mgr@example.com", now - timedelta(hours=49))]
    result = run_scheduler_cycle(approvals, ReminderPolicy(), now=now)
    payload = build_evidence_payload(result)
    assert payload["evaluated"] == 1
    assert payload["eligible"] == 1
    assert payload["sent"] == 1
    assert payload["failed"] == 0
    assert payload["attempts"][0]["approval_id"] == "A1"

