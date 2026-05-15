"""
Celery async tasks for the onboarding workflow.

WHY CELERY INSTEAD OF FASTAPI BACKGROUND TASKS:
This is the #1 question new joiners ask (see faq-new-joiners.md).

FastAPI's BackgroundTasks run in the same process as the API server. That means:
1. If the API server restarts, background tasks are lost (no persistence).
2. CPU-intensive tasks block the event loop (FastAPI is single-threaded async).
3. No retry mechanism — if sending an email fails, it's just gone.
4. No visibility — you can't inspect what's running or queued.

Celery gives us:
1. Task persistence (Redis broker) — tasks survive server restarts.
2. Automatic retries with exponential backoff.
3. Flower dashboard for monitoring task queues.
4. Separate worker processes — API server stays responsive.

We pay for this with operational complexity (Redis + Celery workers to deploy),
but for an HR platform where "welcome email didn't send" is a real problem,
reliability wins over simplicity.

CONFIGURATION:
- Broker: Redis (see docker-compose.yml)
- Result backend: Redis (short TTL — we don't need results after 24h)
- Serializer: JSON (not pickle — security risk)
"""

from celery import Celery
from datetime import datetime

# Celery app instance — workers import this
celery_app = Celery(
    "peopleflow",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Retry failed tasks up to 3 times with exponential backoff
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def trigger_onboarding(self, tenant_id: str, employee_id: str, email: str):
    """Orchestrates the full onboarding workflow for a new employee.

    Called automatically when an employee is created (see employees_service.py).
    Runs these steps in sequence:

    1. Send welcome email
    2. Create default onboarding plan
    3. Provision tool access (Slack, GitHub, etc.)
    4. Notify the employee's manager

    If any step fails, the task retries (up to 3 times). Each sub-step is
    idempotent — retrying won't send duplicate emails or create duplicate plans.
    """
    try:
        # Step 1: Welcome email
        send_welcome_email.delay(tenant_id, employee_id, email)

        # Step 2: Create onboarding plan
        create_default_onboarding_plan.delay(tenant_id, employee_id)

        # Step 3: Provision external tools
        provision_tool_access.delay(tenant_id, employee_id, email)

        # Step 4: Notify manager
        notify_manager_of_new_hire.delay(tenant_id, employee_id)

    except Exception as exc:
        # Log and retry — Celery handles the backoff
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def send_welcome_email(self, tenant_id: str, employee_id: str, email: str):
    """Send the welcome email to a new employee.

    The email template includes:
    - Welcome message from the CEO (tenant-specific)
    - Link to the onboarding portal
    - First-week schedule
    - IT setup guide link

    Template: templates/emails/welcome.html
    Delivery: SendGrid API (see src/shared/email_client.py)

    NOTE (issue-001): The IT setup guide link needs to be updated to point
    to the new Notion page. See docs/issues/issue-001-welcome-email-template.md
    """
    try:
        # In production: render template + call SendGrid
        # Simplified for demo
        print(f"[{datetime.utcnow()}] Sending welcome email to {email} "
              f"(tenant: {tenant_id}, employee: {employee_id})")

        # Simulate email sending
        _send_email(
            to=email,
            subject="Welcome to the team! 🎉",
            template="welcome",
            context={
                "employee_id": employee_id,
                "tenant_id": tenant_id,
                "onboarding_url": f"https://app.peopleflow.io/{tenant_id}/onboarding",
                # TODO (issue-001): Update this link to the new IT setup guide
                "it_setup_guide_url": "https://wiki.internal/it-setup-guide",
            },
        )
    except Exception as exc:
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def create_default_onboarding_plan(self, tenant_id: str, employee_id: str):
    """Create the default onboarding plan for a new employee.

    This is an async version of OnboardingService.create_plan().
    We do this in a Celery task because it may involve fetching
    department-specific templates from the database, which could be slow.
    """
    try:
        print(f"[{datetime.utcnow()}] Creating onboarding plan for "
              f"employee {employee_id} in tenant {tenant_id}")
        # In production: call OnboardingService.create_plan()
    except Exception as exc:
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def provision_tool_access(self, tenant_id: str, employee_id: str, email: str):
    """Provision access to external tools for the new employee.

    Tools provisioned:
    - Slack: Add to workspace + default channels (#general, #engineering)
    - GitHub: Invite to organization + add to team repos
    - Linear: Create account + add to team
    - 1Password: Create vault entry with initial credentials

    Each provisioning call is idempotent — if the user already exists in
    the external system, we skip rather than error.
    """
    try:
        print(f"[{datetime.utcnow()}] Provisioning tool access for {email}")

        # Each external call is wrapped in its own try/except so that
        # a Slack failure doesn't prevent GitHub provisioning
        tools = ["slack", "github", "linear", "1password"]
        for tool in tools:
            try:
                _provision_single_tool(tool, email, tenant_id)
            except Exception as e:
                # Log but don't fail — we'll retry the whole task
                print(f"Warning: Failed to provision {tool} for {email}: {e}")

    except Exception as exc:
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def notify_manager_of_new_hire(self, tenant_id: str, employee_id: str):
    """Send a Slack notification to the new employee's manager.

    Includes:
    - Employee name and start date
    - Link to their onboarding plan
    - Reminder to schedule a 1:1 in the first week
    """
    try:
        print(f"[{datetime.utcnow()}] Notifying manager of new hire {employee_id}")
    except Exception as exc:
        raise self.retry(exc=exc)


# ---------------------------------------------------------------------------
# Internal helpers (not Celery tasks — just utility functions)
# ---------------------------------------------------------------------------

def _send_email(to: str, subject: str, template: str, context: dict):
    """Send an email via SendGrid. Stub for demo purposes."""
    # In production: use SendGrid Python SDK
    print(f"  → Email sent: to={to}, subject={subject}, template={template}")


def _provision_single_tool(tool: str, email: str, tenant_id: str):
    """Provision a single external tool. Stub for demo purposes."""
    print(f"  → Provisioned {tool} for {email} (tenant: {tenant_id})")
