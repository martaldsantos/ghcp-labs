# Issue 001: Update Welcome Email Template

**Type:** Task  
**Priority:** Low  
**Labels:** `good-first-issue`, `onboarding`  
**Assigned to:** New joiner  

---

## Description

The welcome email sent to new employees (via `src/onboarding/onboarding_tasks.py`)
currently links to an outdated IT setup guide at `https://wiki.internal/it-setup-guide`.

The IT team has moved their documentation to Notion, and the new link is:
`https://notion.so/peopleflow/it-setup-guide-2025`

## What needs to change

1. Open `src/onboarding/onboarding_tasks.py`
2. Find the `send_welcome_email` function
3. Update the `it_setup_guide_url` in the template context:
   ```python
   # Before:
   "it_setup_guide_url": "https://wiki.internal/it-setup-guide",
   
   # After:
   "it_setup_guide_url": "https://notion.so/peopleflow/it-setup-guide-2025",
   ```
4. Also update the TODO comment that references this issue

## Acceptance criteria

- [ ] The welcome email template context uses the new Notion URL
- [ ] The TODO comment is removed (or updated)
- [ ] Unit test verifies the correct URL is passed to the email template
- [ ] PR follows the conventions in `how-we-work.md`

## Files to look at

- `src/onboarding/onboarding_tasks.py` — the `send_welcome_email` function
- `docs/common-tasks.md` — Section 2 (Adding a Celery task) for patterns

## Hints

This is a great first issue because it:
- Introduces you to the Celery task structure
- Requires reading and understanding existing code
- Has a small, well-defined scope
- Gets you through the full PR process
