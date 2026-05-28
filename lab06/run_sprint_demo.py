"""Generate a runnable FR-001 reminder scenario and evidence output."""

from __future__ import annotations

import json
from datetime import timedelta
from pathlib import Path

from reminder_engine import (
    Approval,
    ReminderPolicy,
    build_evidence_payload,
    run_scheduler_cycle,
    utc_now,
)


def build_demo_dataset(now):
    return [
        Approval(
            approval_id="APR-100",
            manager_email="manager.a@example.com",
            requested_at=now - timedelta(hours=52),
        ),
        Approval(
            approval_id="APR-101",
            manager_email="manager.b@example.com",
            requested_at=now - timedelta(hours=47),
        ),
        Approval(
            approval_id="APR-102",
            manager_email="manager.c@example.com",
            requested_at=now - timedelta(hours=72),
            status="APPROVED",
        ),
    ]


def main() -> None:
    now = utc_now()
    policy = ReminderPolicy(threshold_hours=48, cooldown_hours=24)
    approvals = build_demo_dataset(now)

    result = run_scheduler_cycle(approvals=approvals, policy=policy, now=now)
    payload = {
        "feature_id": "FR-001",
        "story_map": ["SCRUM-2", "SCRUM-5", "SCRUM-6", "SCRUM-3", "SCRUM-4"],
        "run_at": now.isoformat(),
        "policy": {
            "threshold_hours": policy.threshold_hours,
            "cooldown_hours": policy.cooldown_hours,
        },
        "result": build_evidence_payload(result),
    }

    evidence_dir = Path(__file__).parent / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    out_path = evidence_dir / "fr001_scheduler_run.json"
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"Wrote evidence file: {out_path}")


if __name__ == "__main__":
    main()
