"""FR-001 Manager Approval Reminder — reference solution.

This is the complete working implementation.
Participants should implement reminder_engine.py in the parent folder from scratch.
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
    threshold_hours: int = 48
    cooldown_hours: int = 24


def validate_policy(policy: ReminderPolicy) -> None:
    if policy.threshold_hours <= 0:
        raise ValueError("threshold_hours must be > 0")
    if policy.cooldown_hours < 0:
        raise ValueError("cooldown_hours must be >= 0")


# ─── SCRUM-5: Data model ──────────────────────────────────────────────────────

@dataclass
class Approval:
    approval_id: str
    manager_email: str
    requested_at: datetime
    status: ApprovalStatus = "PENDING"
    last_reminded_at: datetime | None = None


@dataclass
class ReminderAttempt:
    approval_id: str
    recipient: str
    attempted_at: datetime
    outcome: ReminderOutcome
    reason: str


@dataclass
class SchedulerRunResult:
    evaluated: int
    eligible: int
    attempts: list[ReminderAttempt]


# ─── SCRUM-6: Eligibility detection ──────────────────────────────────────────

def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def approval_age(approval: Approval, now: datetime) -> timedelta:
    return now - approval.requested_at


def is_eligible_for_reminder(
    approval: Approval,
    now: datetime,
    policy: ReminderPolicy,
) -> tuple[bool, str]:
    if approval.status != "PENDING":
        return False, "approval is not pending"

    if approval_age(approval, now) < timedelta(hours=policy.threshold_hours):
        return False, "threshold not reached"

    if approval.last_reminded_at is not None:
        cooldown_elapsed = now - approval.last_reminded_at
        if cooldown_elapsed < timedelta(hours=policy.cooldown_hours):
            return False, "cooldown window still active"

    if not approval.manager_email:
        return False, "manager email missing"

    return True, "eligible"


def find_eligible_approvals(
    approvals: Iterable[Approval],
    now: datetime,
    policy: ReminderPolicy,
) -> list[Approval]:
    eligible: list[Approval] = []
    for approval in approvals:
        ok, _ = is_eligible_for_reminder(approval, now, policy)
        if ok:
            eligible.append(approval)
    return eligible


# ─── SCRUM-3: Scheduler ───────────────────────────────────────────────────────

def send_reminder(approval: Approval, now: datetime) -> ReminderAttempt:
    if "@" not in approval.manager_email:
        return ReminderAttempt(
            approval_id=approval.approval_id,
            recipient=approval.manager_email,
            attempted_at=now,
            outcome="FAILED",
            reason="invalid recipient address",
        )

    approval.last_reminded_at = now
    return ReminderAttempt(
        approval_id=approval.approval_id,
        recipient=approval.manager_email,
        attempted_at=now,
        outcome="SENT",
        reason="reminder dispatched",
    )


def run_scheduler_cycle(
    approvals: Iterable[Approval],
    policy: ReminderPolicy,
    now: datetime | None = None,
) -> SchedulerRunResult:
    run_at = now or utc_now()
    validate_policy(policy)

    approval_list = list(approvals)
    eligible = find_eligible_approvals(approval_list, run_at, policy)
    attempts = [send_reminder(approval, run_at) for approval in eligible]

    return SchedulerRunResult(
        evaluated=len(approval_list),
        eligible=len(eligible),
        attempts=attempts,
    )


# ─── SCRUM-4: Evidence payload ────────────────────────────────────────────────

def build_evidence_payload(result: SchedulerRunResult) -> dict:
    return {
        "evaluated": result.evaluated,
        "eligible": result.eligible,
        "sent": sum(1 for a in result.attempts if a.outcome == "SENT"),
        "failed": sum(1 for a in result.attempts if a.outcome == "FAILED"),
        "attempts": [
            {
                "approval_id": attempt.approval_id,
                "recipient": attempt.recipient,
                "attempted_at": attempt.attempted_at.isoformat(),
                "outcome": attempt.outcome,
                "reason": attempt.reason,
            }
            for attempt in result.attempts
        ],
    }
