## Summary
<!-- What does this PR do? Keep it to 1-2 sentences. -->


## Related Issue
<!-- Link to the GitHub issue, e.g. Closes #002 -->


## Changes Made
<!-- List the key changes. Bullet points work well. -->
- 
- 
- 

## Type of Change
<!-- Check the one that applies -->
- [ ] `feat` — New feature
- [ ] `fix` — Bug fix
- [ ] `chore` — Maintenance (deps, CI, config)
- [ ] `docs` — Documentation only
- [ ] `refactor` — Code restructuring (no behavior change)
- [ ] `test` — Adding or updating tests

## Testing
<!-- How did you verify this works? -->
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing on local environment
- [ ] Tested on staging

## Multi-Tenancy Checklist
<!-- If your change touches database queries, verify: -->
- [ ] All new queries are scoped to `tenant_id` (using `TenantQuery`)
- [ ] No raw SQL without `WHERE tenant_id = ...`
- [ ] Tested with multiple tenant contexts

## Screenshots
<!-- If applicable (UI changes, API response changes) -->


## Notes for Reviewers
<!-- Anything reviewers should pay special attention to? -->

