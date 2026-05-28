"""FR-001 Manager Approval Reminder — starter file.

Complete every function marked with TODO.
Each TODO maps to one of your Jira stories:

  validate_policy          → SCRUM-2  Define reminder policy
  Approval / ReminderAttempt / SchedulerRunResult  → SCRUM-5  Data model
  is_eligible_for_reminder → SCRUM-6  Eligibility detection service
  send_reminder / run_scheduler_cycle              → SCRUM-3  Scheduler job
  build_evidence_payload   → SCRUM-4  Evidence payload

Run tests at any time to check your progress:
  pytest -q tests/test_reminder_engine.py

When all tests pass, run the demo to generate evidence for Jira:
  python run_sprint_demo.py
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterable, Literal


ApprovalStatus = Literal["PENDING", "APPROVED", "REJECTED"]
ReminderOutcome = Literal["SENT", "SKIPPED", "FAILED"]


# ─── SCRUM-2: Policy definition ───────────────────────────────────────────────

@dataclass
class ReminderPolicy:
    """Defines when and how reminders are triggered.

    threshold_hours: approvals pending longer than this value receive a reminder.
    cooldown_hours:  minimum hours between reminders for the same approval.
    """
    threshold_hours: int = 48
    cooldown_hours: int = 24


def validate_policy(policy: ReminderPolicy) -> None:
    """Raise ValueError if the policy contains invalid values.

    TODO (SCRUM-2):
    - Raise ValueError if threshold_hours <= 0.
    - Raise ValueError if cooldown_hours < 0.
    """
    raise NotImplementedError("TODO: implement validate_policy — SCRUM-2")


# ─── SCRUM-5: Data model ──────────────────────────────────────────────────────

@dataclass
class Approval:
    """A pending approval request that may need a manager reminder.

    Fields:
        approval_id:      Unique identifier for the approval request.
        manager_email:    Email address of the approving manager.
        requested_at:     UTC timestamp when the approval was requested.
        status:           Current state (PENDING / APPROVED / REJECTED).
        last_reminded_at: UTC timestamp of the most recent reminder, if any.
    """
    approval_id: str
    manager_email: str
    requested_at: datetime
    status: ApprovalStatus = "PENDING"
    last_reminded_at: datetime | None = None


@dataclass
class ReminderAttempt:
    """Audit record of one reminder dispatch attempt."""
    approval_id: str
    recipient: str
    attempted_at: datetime
    outcome: ReminderOutcome
    reason: str


@dataclass
class SchedulerRunResult:
    """Summary returned after one full scheduler execution cycle."""
    evaluated: int
    eligible: int
    attempts: list[ReminderAttempt]


# ─── SCRUM-6: Eligibility detection ──────────────────────────────────────────

def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def approval_age(approval: Approval, now: datetime) -> timedelta:
    """Return how long the approval has been open."""
    return now - approval.requested_at


def is_eligible_for_reminder(
    approval: Approval,
    now: datetime,
    policy: ReminderPolicy,
) -> tuple[bool, str]:
    """Return (eligible, reason) for a single approval request.

    TODO (SCRUM-6) — check each rule in this order:
    1. If approval.status is not 'PENDING'     → return (False, "approval is not pending")
    2. If age < policy.threshold_hours         → return (False, "threshold not reached")
    3. If reminded within cooldown_hours       → return (False, "cooldown window still active")
    4. If manager_email is empty/missing       → return (False, "manager email missing")
    5. All checks passed                       → return (True,  "eligible")
    """
    raise NotImplementedError("TODO: implement is_eligible_for_reminder — SCRUM-6")


def find_eligible_approvals(
    approvals: Iterable[Approval],
    now: datetime,
    policy: ReminderPolicy,
) -> list[Approval]:
    """Filter the list and return only approvals that are eligible for a reminder."""
    eligible: list[Approval] = []
    for approval in approvals:
        ok, _ = is_eligible_for_reminder(approval, now, policy)
        if ok:
            eligible.append(approval)
    return eligible


# ─── SCRUM-3: Scheduler ───────────────────────────────────────────────────────

def send_reminder(approval: Approval, now: datetime) -> ReminderAttempt:
    """Dispatch a single reminder and return an audit record.

    TODO (SCRUM-3):
    - If manager_email does not contain '@':
        return a ReminderAttempt with outcome='FAILED' and
        reason='invalid recipient address'.
    - Otherwise:
        set approval.last_reminded_at = now, then
        return a ReminderAttempt with outcome='SENT' and
        reason='reminder dispatched'.
    """
    raise NotImplementedError("TODO: implement send_reminder — SCRUM-3")


def run_scheduler_cycle(
    approvals: Iterable[Approval],
    policy: ReminderPolicy,
    now: datetime | None = None,
) -> SchedulerRunResult:
    """Run one full scheduler cycle and return a summary.

    TODO (SCRUM-3):
    1. Resolve run_at = now or utc_now().
    2. Call validate_policy(policy).
    3. Convert approvals to a list.
    4. Call find_eligible_approvals to get eligible items.
    5. Call send_reminder for each eligible approval.
    6. Return SchedulerRunResult(evaluated=..., eligible=..., attempts=...).
    """
    raise NotImplementedError("TODO: implement run_scheduler_cycle — SCRUM-3")


# ─── SCRUM-4: Evidence payload (for validation gate) ─────────────────────────

def build_evidence_payload(result: SchedulerRunResult) -> dict:
    """Build a JSON-serialisable evidence dict from a scheduler run result.

    TODO (SCRUM-4) — include these keys:
    - evaluated: total approvals inspected
    - eligible:  approvals that met the threshold
    - sent:      count of SENT outcomes
    - failed:    count of FAILED outcomes
    - attempts:  list of dicts, each with:
        approval_id, recipient, attempted_at (ISO string), outcome, reason
    """
    raise NotImplementedError("TODO: implement build_evidence_payload — SCRUM-4")
