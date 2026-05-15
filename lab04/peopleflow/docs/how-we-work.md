# How We Work at PeopleFlow Engineering

> Last updated: 2025-10-20 | Author: @thomas-k

## Branch Naming

We use prefixes to categorize branches. CI pipelines use these prefixes
to determine which checks to run.

| Prefix | Use for | Example |
|--------|---------|---------|
| `feature/` | New functionality | `feature/employee-search-filter` |
| `fix/` | Bug fixes | `fix/review-cycle-date-validation` |
| `chore/` | Maintenance, deps, CI | `chore/upgrade-sqlalchemy-2.1` |
| `docs/` | Documentation only | `docs/update-onboarding-guide` |

**Convention**: Use kebab-case after the prefix. Include the issue number
if there is one: `fix/003-review-cycle-date-validation`.

## Commit Messages

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types**: `feat`, `fix`, `chore`, `docs`, `test`, `refactor`, `perf`

**Scopes**: `employees`, `onboarding`, `performance`, `auth`, `shared`, `infra`

**Examples**:
```
feat(employees): add name/department search filter

Closes #002

fix(performance): validate review cycle end date against start date

The end_date was not being checked against start_date, allowing
invalid review cycles to be created.

Closes #003
```

## Pull Request Process

### Before opening a PR

1. Run the test suite locally: `pytest --cov=src tests/`
2. Run the linter: `ruff check src/`
3. Run the type checker: `mypy src/`
4. Make sure your branch is up to date with `main`

### PR template

We have a PR template at `.github/pull_request_template.md`. Fill it out
completely — PRs without a filled template will be sent back.

### Review process

1. Open a PR against `main`.
2. GitHub Actions runs tests, linting, and type checking automatically.
3. Request a review from the appropriate CODEOWNER (see `.github/CODEOWNERS`).
4. At least **one approval** is required to merge.
5. **Squash merge** — we keep a clean linear history on `main`.

### Code review etiquette

- **Reviewers**: Be specific. Say "this could cause a tenant data leak because
  X" not "this seems wrong".
- **Authors**: Don't take feedback personally. We all write bugs.
- If a review comment starts with `nit:` it's a suggestion, not a blocker.
- If you disagree with feedback, discuss in the PR — don't just ignore it.
- Reviews should be completed within 24 hours. If you're too busy, re-assign.

## Who to Ask for What

| Need | Person | Slack handle |
|------|--------|-------------|
| Technical architecture decisions | Thomas K. | @thomas-k |
| Product requirements, priorities | Lisa P. | @lisa-p |
| Infrastructure, CI/CD, deployments | Ahmed R. | @ahmed-r |
| Database schema changes | Thomas K. + Ahmed R. | @thomas-k @ahmed-r |
| Security review | Sarah M. | @sarah-m |
| HR domain knowledge | Julia S. | @julia-s |
| Frontend (React) questions | Marco D. | @marco-d |

## Definition of Done

A feature is "done" when:

- [ ] Code is written and follows our patterns (see codebase-tour.md)
- [ ] Unit tests are written (aim for >80% coverage on new code)
- [ ] Integration tests pass
- [ ] API documentation is updated (docstrings generate OpenAPI docs)
- [ ] PR is approved and merged
- [ ] Deployed to staging and smoke-tested
- [ ] Product manager has verified the behavior

## Daily Standup

- **Time**: 09:30 CET (Berlin time)
- **Where**: Google Meet (link pinned in #engineering)
- **Format**: Async-first — post your update in #standup by 09:30.
  Join the call only if you have blockers to discuss.

## On-Call

We rotate on-call weekly. The on-call engineer:
- Monitors Datadog alerts
- Responds to P0/P1 incidents within 15 minutes
- Writes a post-mortem for any incident lasting > 30 minutes

New joiners are **not** on the on-call rotation for the first 3 months.
