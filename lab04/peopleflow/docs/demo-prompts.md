# Demo Prompts for the PeopleFlow Copilot Space

> Use these prompts during the workshop to demonstrate how a Copilot Space
> accelerates onboarding. Each section builds on the previous one, simulating
> a new joiner's first day.

---

## Section 1: Getting Oriented (First 30 minutes)

These prompts show how a new joiner uses the Space to understand the codebase
without interrupting senior developers.

### Prompt 1 — "Where do I start?"
```
I just joined PeopleFlow today. What should I read first to understand the
codebase? Give me a prioritized reading list for my first day.
```

### Prompt 2 — Understanding the architecture
```
Can you explain the overall architecture of PeopleFlow? How do the frontend,
API, database, and task queue fit together? I'm a visual learner — include
a diagram if you can.
```

### Prompt 3 — Why multi-tenancy matters
```
I keep seeing tenant_id everywhere in the code. Why? What would happen if I
forgot to include it in a database query?
```

### Prompt 4 — Understanding auth
```
How does authentication work in this codebase? I see two things related to
auth — auth_middleware.py and permissions.py. What's the difference and why
are they separate?
```

---

## Section 2: Understanding Patterns (Next hour)

These prompts demonstrate the Space's ability to teach team conventions.

### Prompt 5 — Exception handling
```
How should I handle errors in PeopleFlow? I see a shared/exceptions.py file.
Walk me through the pattern and show me an example of raising a custom error
in a service.
```

### Prompt 6 — Following the data flow
```
Walk me through what happens when a new employee is created via the API.
Start from the HTTP request and follow the code all the way through to the
Celery tasks that get triggered.
```

### Prompt 7 — Why Celery?
```
Why does PeopleFlow use Celery for background tasks instead of FastAPI's
built-in BackgroundTasks? When should I use one vs the other?
```

---

## Section 3: Working on a Real Issue (Hands-on)

These prompts show the Space helping a new joiner complete their first task.

### Prompt 8 — Picking up an issue
```
I've been assigned issue-001 (update the welcome email template). Can you
explain what needs to change and which files I should look at?
```

### Prompt 9 — Writing the fix
```
Can you help me write the code change for issue-001? I need to update the
IT setup guide URL in the welcome email. Show me the exact change and explain
what conventions I should follow.
```

### Prompt 10 — Writing tests
```
I've made the change for issue-001. Now I need to write a test for it.
How do we test Celery tasks at PeopleFlow? Show me a test that verifies
the welcome email contains the correct URL.
```

### Prompt 11 — PR process
```
I'm ready to submit my first PR. What's PeopleFlow's PR process? What should
I include in the PR description? Who needs to review it?
```

---

## Section 4: Tackling a Feature (Advanced)

These prompts show the Space helping with a more complex, feature-level task.

### Prompt 12 — Planning a feature
```
I've been assigned issue-002 — adding search/filter to the employees endpoint.
Help me plan the implementation. What files need to change, and in what order
should I make the changes?
```

### Prompt 13 — Generating code
```
Based on issue-002, write the code changes needed to add a search query
parameter to GET /employees. Include the router, service, and any schema
changes. Follow PeopleFlow's conventions.
```

### Prompt 14 — Bug investigation
```
I'm looking at issue-003 — the review cycle date validation bug. Can you
help me understand what's going wrong and write the fix? Make sure it follows
PeopleFlow's error handling pattern.
```

---

## Section 5: Advanced Questions (Deep Dive)

These prompts test the Space's ability to handle nuanced questions.

### Prompt 15 — Making a design decision
```
I need to add a feature that sends a daily summary email to managers
listing their team's onboarding progress. Should this be a Celery task,
a FastAPI background task, or something else? What does our codebase
suggest?
```

### Prompt 16 — Security considerations
```
I'm adding a new endpoint that lets managers export their team's data
as CSV. What security considerations should I keep in mind, given
PeopleFlow's multi-tenant architecture?
```

### Prompt 17 — Understanding business rules
```
What are the key business rules in the PeopleFlow data model? List them
and tell me where each one is enforced in the code.
```

---

## Facilitator Notes

- **Prompts 1-4**: Good for showing the Space to non-technical stakeholders.
  They demonstrate knowledge retrieval.
- **Prompts 5-7**: Show pattern understanding — the Space doesn't just retrieve
  docs, it synthesizes knowledge from code and documentation.
- **Prompts 8-11**: The money demo — show a real workflow from issue to PR.
  Most impactful for developer audiences.
- **Prompts 12-17**: Advanced scenarios for skeptical senior engineers. These
  test whether the Space can handle nuance and context.
