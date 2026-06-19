# Lab 08 — The Agentic SDLC Loop (Capstone)

**Duration:** ~1 hour  
**SDLC Phase:** The Full Loop  
**Autonomy Level:** 🔴🔴 Agent runs the full loop autonomously  
**Prerequisites:** Labs 01–07 completed, all tools installed

---

## Learning Objective

Wire up the **complete Agentic SDLC loop**: a feature request comes in → an agent researches → plans → codes → tests → reviews → secures → ships. You are the **architect and approver**. The agent does the work.

This is the capstone. Everything you learned in Labs 01–07 comes together.

---

## What You'll Practice

| Part | SDLC Phase | Time | What Happens |
|------|-----------|------|-------------|
| **1** | Research | 5 min | Agent analyzes the codebase and feature request |
| **2** | Plan | 5 min | Agent creates an implementation plan |
| **3** | Code | 15 min | Agent implements the feature (Agent Mode) |
| **4** | Test | 10 min | Agent writes and runs tests (coverage gate) |
| **5** | Review | 5 min | Agent reviews its own code against standards |
| **6** | Secure | 5 min | Agent runs security scan |
| **7** | Ship | 15 min | CI pipeline + Agentic Workflow ties it all together |

---

## Setup

```bash
cd lab08
pip install pytest pytest-cov
```

---

## The Scenario

You have `feature_tracker.py` — a system that tracks features through SDLC stages. You'll receive a **feature request** and guide an agent through the entire development lifecycle, from research to deployment.

### The Feature Request

> **FEAT-0001: Add a notification system**
>
> When a feature moves between SDLC stages (e.g., from "planned" to "in_progress"),
> notify the requester via email and log the notification. Support multiple
> notification channels (email, Slack, webhook). Include rate limiting to prevent
> notification spam during rapid status changes.

This is deliberately complex enough to require all SDLC phases.

---

## Part 1 — Research (5 min)

The agent needs to understand the codebase before planning.

### Your task

Open **Agent Mode** and prompt:

```
I need to implement a notification system for feature_tracker.py.

Before writing any code, research the existing codebase:
1. What classes and patterns exist?
2. Where are the extension points?
3. What would a notification system need to integrate with?
4. Are there any existing patterns I should follow?

Give me a research summary, not code.
```

### What to observe
- Does the agent read the file before answering?
- Does it identify `advance_to()` and `log_phase()` as integration points?
- Does it note the dataclass + Enum patterns?

### Approve or redirect
If the research is solid, tell the agent: *"Good research. Now create a plan."*

---

## Part 2 — Plan (5 min)

### Your task

Continue in Agent Mode:

```
Create a detailed implementation plan for the notification system.

The plan should include:
1. New classes/models needed (follow the dataclass + Enum patterns)
2. Files to create and modify
3. How notifications integrate with advance_to()
4. Rate limiting strategy (e.g., max 1 notification per feature per 5 minutes)
5. Tests to write (list specific test cases)
6. Security considerations (no credentials in code, etc.)

Output the plan as a structured document. Don't implement yet.
```

### Review the plan
Before saying "implement":
- [ ] Does it create a `NotificationChannel` enum?
- [ ] Does it create `Notification` and `NotificationService` classes?
- [ ] Does it modify `advance_to()` to trigger notifications?
- [ ] Does it include rate limiting logic?
- [ ] Does it list 5+ test cases?
- [ ] Does it mention env vars for credentials?

### Approve
*"Plan looks good. Implement it."*

---

## Part 3 — Code (15 min)

### Your task

The agent should now implement the plan. If it stopped after planning, prompt:

```
Implement the notification system according to the plan.
Create all necessary files and modify feature_tracker.py.
Follow the existing patterns (dataclasses, Enums, type hints).
Use environment variables for any credentials or URLs.
```

### What to observe
- Does it create clean, well-structured code?
- Does it follow the existing patterns?
- Does it handle edge cases (no notification channels configured, rate limited, etc.)?
- Does it modify `advance_to()` to trigger notifications?

If it stops mid-implementation: *"Continue — finish implementing all the classes."*

---

## Part 4 — Test (10 min)

### Your task

```
Write comprehensive tests for the notification system.
Requirements:
- Use pytest with factory fixtures
- Mock external notification channels (don't send real emails/webhooks)
- Test rate limiting (mock time or inject timestamps)
- Test all notification channels
- Test the integration with advance_to()
- Run the tests and fix any failures
- Target 85%+ coverage on the new code
```

### What to observe
- Does the agent write tests, run them, and iterate on failures?
- Does it check coverage and add more tests?
- This is the **run-fix loop** from Lab 06 — the agent's core strength.

### Verify yourself
```bash
pytest tests/ --cov=feature_tracker --cov-report=term-missing -v
```

---

## Part 5 — Review (5 min)

### Your task

Now the agent reviews its own work:

```
Review the notification system you just implemented.
Check against these criteria:
1. Does it follow the existing patterns (dataclasses, Enums, type hints)?
2. Are there any code smells or DRY violations?
3. Is error handling consistent?
4. Are all public methods documented?
5. Would a new developer understand this code?

If you find issues, fix them.
```

### What to observe
- Can the agent critically evaluate its own code?
- Does it find real issues or just say "looks good"?
- Does it actually fix what it finds?

---

## Part 6 — Secure (5 min)

### Your task

```
Perform a security review of the notification system:
1. Are there any hardcoded credentials or API keys?
2. Is user input validated before being used in notifications?
3. Could a malicious feature title cause injection in email/Slack messages?
4. Is rate limiting bypassable?
5. Are there any OWASP Top 10 concerns?

Fix any issues you find.
```

### What to observe
- Does it catch input validation concerns (XSS in notification body)?
- Does it verify credentials are from env vars?
- Does it consider rate limit bypass scenarios?

---

## Part 7 — Ship (15 min)

### 7a: CI Pipeline

Create a GitHub Actions workflow that runs the full quality gate:

```
Create .github/workflows/sdlc-gate.yml that:
1. Runs pytest with coverage (fail under 85%)
2. Runs a basic security scan (check for hardcoded secrets)
3. Runs linting
4. Only passes if ALL gates pass
```

Test it locally:
```bash
pytest tests/ --cov=feature_tracker --cov-fail-under=85 -v
```

### 7b: Agentic Workflow (The Full Loop)

Create `.github/workflows/feature-sdlc.md` — an Agentic Workflow that automates the entire loop:

```markdown
---
name: feature-sdlc
description: >
  Complete SDLC loop: when a new feature issue is created,
  research the codebase, plan the implementation, code it,
  write tests, review, security scan, and open a PR.

triggers:
  - on: issues
    types: [opened]
    labels: [feature-request]

steps:
  - name: Research
    prompt: |
      Read the codebase. Understand the architecture and patterns.
      Summarize what exists and where the new feature should integrate.

  - name: Plan
    prompt: |
      Create an implementation plan for the feature described in the issue.
      Include: new files, modified files, test cases, security considerations.

  - name: Implement
    prompt: |
      Implement the feature according to the plan.
      Follow existing patterns. Use environment variables for secrets.

  - name: Test
    prompt: |
      Write tests. Run them. Fix failures. Target 85% coverage.

  - name: Review
    prompt: |
      Review the implementation against project conventions.
      Fix any issues found.

  - name: Security Scan
    prompt: |
      Check for OWASP Top 10 vulnerabilities.
      Verify no hardcoded secrets. Fix any issues.

  - name: Open PR
    run: |
      git checkout -b feat/${{ issue.number }}
      git add -A
      git commit -m "feat: ${{ issue.title }}"
      git push -u origin feat/${{ issue.number }}
      gh pr create --title "${{ issue.title }}" --body "Closes #${{ issue.number }}"
```

### 7c: Try it

If you have `gh aw` installed:
```bash
gh extension install github/gh-aw
gh aw compile .github/workflows/feature-sdlc.md
gh aw run feature-sdlc
```

Or simulate it by running each step manually through Agent Mode.

---

## The Complete Agentic SDLC Loop

Congratulations — you've wired up the full loop:

```
📋 Feature Request
      ↓
🔍 Research (Agent reads codebase)
      ↓
📝 Plan (Agent creates implementation plan)
      ↓
💻 Code (Agent implements — Agent Mode)
      ↓
🧪 Test (Agent writes tests, runs them, iterates)
      ↓
👀 Review (Agent reviews its own code)
      ↓
🔒 Secure (Agent scans for vulnerabilities)
      ↓
🚀 Ship (CI pipeline validates, PR is opened)
      ↓
🔄 Iterate (if anything fails, agent fixes and re-runs)
```

---

## Lab Complete! Here's What You Practiced Across All 8 Labs:

| Lab | SDLC Phase | Autonomy |
|-----|-----------|----------|
| **01** Code Generation Fundamentals | Code | Human writes, Copilot suggests |
| **02** Testing with Copilot | Test | Human directs, Copilot generates |
| **03** Debugging & Troubleshooting | Debug | Human points, Copilot fixes |
| **04** Context Engineering | Standards | Human configures, Copilot follows |
| **05** Code Review & Refactoring | Review | Human asks, Agent researches |
| **06** Agent Mode | Code+Test+Debug | Human approves, Agent implements |
| **07** Release Workflow and Infrastructure as Code | Integration → Deployment → Release | Human reviews, Copilot automates |
| **08** The Agentic SDLC Loop | Full Loop | Agent runs autonomously |

### The Progression

```
Lab 01-03:  Copilot as a TOOL         → you do the work, Copilot helps
Lab 04-05:  Copilot as a TEAM MEMBER  → you set standards, Copilot follows
Lab 06-07:  Copilot as a DEVELOPER    → you approve, Copilot does the work
Lab 08:     Copilot as a PIPELINE     → the loop runs itself
```

> **The Agentic SDLC isn't about replacing developers. It's about turning the entire development lifecycle into an automated, quality-gated pipeline where AI handles the routine and humans focus on architecture, design, and approval.**
