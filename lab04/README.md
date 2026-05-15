# Lab 04 — Context Engineering

**Duration:** ~1 hour  
**SDLC Phase:** Cross-cutting (Standards & Conventions)  
**Autonomy Level:** 🟡 Human configures, Copilot follows rules  
**Prerequisites:** Lab 03 completed, Python 3.10+, VS Code with GitHub Copilot

---

## The Big Idea

Copilot is only as useful as the context you give it. This lab teaches the four layers of context engineering — from a single instruction file all the way to a shared knowledge environment for your team:

| Part | Layer | What It Does | Scope |
|------|-------|-------------|-------|
| **1** | Copilot Instructions | Teach Copilot your project's conventions | This repo |
| **2** | Custom Agents | Give Copilot a persona + tools for specific tasks | This workspace |
| **3** | MCP Servers | Connect Copilot to live external data & APIs | Any tool/service |
| **4** | Copilot Spaces | Package knowledge for your whole team | Organization-wide |

Each layer builds on the previous. By the end, you'll see how they combine to create a system where Copilot genuinely understands your project — not just your code.

---

## The Scenario

**PeopleFlow** — a fictional B2B SaaS HR platform based in Berlin. Python/FastAPI backend, React frontend, PostgreSQL, Celery for async tasks.

A new engineer joins the company on day 1 and needs to get productive. You'll progressively configure Copilot to help them — starting with basic code conventions and ending with a fully curated onboarding Space.

The demo codebase is in `peopleflow/`:

```
peopleflow/
├── src/
│   ├── employees/          # Employee CRUD (router → service → schemas)
│   ├── onboarding/         # Onboarding plans + Celery async tasks
│   ├── performance/        # Review cycles (with an intentional bug!)
│   ├── auth/               # JWT middleware + @require_role decorator
│   └── shared/             # Database, exceptions, structured logging
├── docs/                   # Onboarding docs (architecture, FAQ, recipes)
│   └── issues/             # 3 starter issues for new joiners
└── .github/                # CODEOWNERS, PR template
```

---

## Part 1 — Copilot Instructions (15 min)

### What are they?

Copilot Instructions are markdown files that Copilot reads **automatically** and follows when generating code. They define your project's conventions — coding style, error handling patterns, testing standards — so Copilot doesn't guess.

There are three levels:

| File | Scope | Auto-applied? |
|------|-------|--------------|
| `.github/copilot-instructions.md` | Entire repo | ✅ Yes, always |
| `.github/copilot/prompts/*.prompt.md` | On-demand reusable prompts | Only when invoked via `/` |
| VS Code settings (`github.copilot.chat.codeGeneration.instructions`) | Your local editor | ✅ Yes, for you |

### Task 1a: See instructions change Copilot's output

1. Open `.github/copilot-instructions.md` — it defines Python style, testing, and error handling conventions.

2. **Test without instructions:** Rename the file to `copilot-instructions.md.bak`. Ask Chat:
   > *"Write a function to merge two data pipeline outputs into one"*
   
   Note the style.

3. **Test with instructions:** Rename it back. Ask the same question. Compare:
   - Does it use `pathlib.Path` (not `os.path`)?
   - Does it have Google-style docstrings?
   - Does it use type hints?

### Task 1b: Add a convention and see it enforced

Add this to `.github/copilot-instructions.md`:

```markdown
## Logging
- Use `structlog` instead of `logging` for structured log output
- Always include `event`, `level`, and context fields
```

Then ask Chat: *"Add logging to the DataPipeline.run() method"*. Does it use `structlog`?

### Task 1c: Create a reusable prompt file

Create `.github/copilot/prompts/generate-tests.prompt.md`:

```markdown
---
description: Generate pytest tests following project conventions
---
Generate comprehensive pytest tests for the selected code.

Requirements:
- Use factory fixtures (fixture returns a function)
- Use `tmp_path` for any file system operations
- Use `pytest.mark.parametrize` for edge cases
- Include happy path, error cases, and boundary tests
```

Select `DataPipeline._transform()` → open Chat → type `/` → select your prompt. Compare with a default `/tests` request.

<details>
<summary>💡 Key takeaway</summary>

Instructions are the foundation. They cost nothing to set up and immediately improve every Copilot interaction across your team. Start here for any project.

</details>

---

## Part 2 — Custom Agents (15 min)

### What are they?

Agents are markdown files (`.github/copilot/agents/*.agent.md`) that give Copilot a **persona, a specific task focus, and optionally restricted tool access**. Think of them as specialized coworkers: one agent for code review, another for database work, another for onboarding.

Unlike instructions (which apply globally), agents are **invoked by name** — you choose when to use them.

### How agents differ from instructions

| | Instructions | Agents |
|---|---|---|
| **Activated** | Automatically, always | By user, via `@agent-name` |
| **Purpose** | "Always follow these rules" | "You are an expert at X" |
| **Tool access** | N/A | Can restrict to specific tools |
| **Persona** | No persona | Has identity, tone, focus |

### Task 2a: Create an onboarding agent

Create `.github/copilot/agents/onboarding-buddy.agent.md`:

```markdown
---
description: Helps new PeopleFlow developers get up to speed
tools:
  - read_file
  - grep_search
  - file_search
  - semantic_search
---

You are an onboarding buddy at PeopleFlow. You help new developers
understand the codebase, conventions, and architecture.

Rules:
- Always reference specific files and docs when answering questions.
- Point the developer to `docs/codebase-tour.md` as their starting point.
- When suggesting code, follow the patterns in `src/shared/exceptions.py`
  for error handling and `src/auth/permissions.py` for role checks.
- Remind them that every database query MUST include `tenant_id`
  (see `src/shared/database.py` for the TenantQuery pattern).
- If you don't know the answer, say so and suggest who to ask
  (see `docs/how-we-work.md` for the team directory).
```

### Task 2b: Test the agent

In Chat, invoke your agent with `@onboarding-buddy` and try:

```
I just joined today. Where do I start?
```

```
How does error handling work in this project? Show me the pattern.
```

```
I've been assigned issue-001. What files should I look at?
```

Check: Does the agent reference actual PeopleFlow files? Does it use a helpful, welcoming tone?

### Task 2c: Create a code review agent

Create `.github/copilot/agents/reviewer.agent.md`:

```markdown
---
description: Reviews PeopleFlow code against team conventions
tools:
  - read_file
  - grep_search
---

You are a strict code reviewer at PeopleFlow. Review code against:
1. Multi-tenancy: Every DB query must scope to tenant_id.
2. Error handling: Use PeopleFlowError subclasses, never raw HTTPException.
3. Permissions: Use @require_role() decorator, not FastAPI Depends().
4. Logging: Use structured logger from shared/logger.py, never print().
5. Naming: Branch naming (feature/, fix/, chore/), conventional commits.

For each issue found, cite the specific convention and the file where
the pattern is defined.
```

Test it: `@reviewer Review the create_review_cycle method in src/performance/reviews_service.py`

It should catch the missing date validation (issue-003).

<details>
<summary>💡 Key takeaway</summary>

Agents let you create focused, reusable "roles" that Copilot can assume. They're especially powerful combined with instructions — the agent follows both its own persona AND the project's conventions.

</details>

---

## Part 3 — MCP Servers (15 min)

### What are they?

**Model Context Protocol (MCP) servers** connect Copilot to external tools and live data. Instructions tell Copilot *how* to write code. Agents give it a *persona*. MCP servers give it **access to the outside world** — databases, APIs, CLIs, documentation portals.

```
┌──────────────────────────────────────────────────┐
│                  Copilot Chat                     │
│                                                  │
│  Instructions → "Follow these conventions"       │
│  Agents       → "Act as this persona"            │
│  MCP Servers  → "Use these external tools"       │
└─────────────────────┬────────────────────────────┘
                      │ calls tools via MCP
                      ▼
    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
    │  Database   │  │  REST API   │  │  CLI Tool   │
    │  (read-only │  │  (fetch     │  │  (run       │
    │   queries)  │  │   docs)     │  │   commands) │
    └─────────────┘  └─────────────┘  └─────────────┘
```

### How MCP fits with instructions and agents

An agent can **use** MCP tools. For example, the onboarding buddy agent could query a live database to show real employee counts, or call a documentation API to fetch the latest architecture docs.

### Task 3a: Explore available MCP servers

Open the Command Palette (`Ctrl+Shift+P`) → **MCP: List Servers** to see what's configured.

If none are configured yet, open `.vscode/mcp.json` (or create it) and add:

```json
{
  "servers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@anthropic/mcp-filesystem",
        "${workspaceFolder}/peopleflow"
      ]
    }
  }
}
```

This gives Copilot read/write access to the PeopleFlow directory through a structured MCP interface (rather than raw terminal commands).

### Task 3b: Use MCP tools through an agent

Update your onboarding buddy agent to reference MCP tools. In Chat, try:

```
@onboarding-buddy Using the filesystem tools, find all files that
reference tenant_id and explain the multi-tenancy pattern.
```

```
@onboarding-buddy Search the codebase for TODO comments and list
them with their file locations.
```

### Task 3c: Understand the MCP concept with a real-world example

Even without a live MCP server, understand the pattern by asking Chat:

```
If I had an MCP server connected to our PostgreSQL database, how would
I ask Copilot to check how many employees each tenant has? What would
the MCP tool call look like?
```

This illustrates the key value: Copilot moves from "generate code based on docs" to "query live systems and act on real data."

<details>
<summary>💡 Key takeaway</summary>

MCP servers are the bridge between Copilot and the real world. Instructions and agents make Copilot smart about your code. MCP makes it smart about your infrastructure, databases, and tools.

</details>

---

## Part 4 — Copilot Spaces (15 min)

### What are they?

Everything in Parts 1–3 lives in **your VS Code workspace** — your instructions, your agents, your MCP connections. **Copilot Spaces** package all of this into a **shared, web-accessible knowledge environment** that anyone on your team can use, from anywhere, without any local setup.

Think of it as the difference between "I configured my editor" and "I built an onboarding portal."

### How Spaces connect to everything else

| Layer | Where it lives | Who benefits |
|-------|---------------|-------------|
| Instructions | `.github/copilot-instructions.md` | Devs using this repo locally |
| Agents | `.github/copilot/agents/` | Devs using VS Code |
| MCP Servers | `.vscode/mcp.json` | Devs with tools installed locally |
| **Spaces** | **github.com/copilot/spaces** | **Anyone with a link — no setup** |

A Space takes the best of your instructions and docs and makes them accessible to a new joiner who hasn't even cloned the repo yet.

### Task 4a: Create a PeopleFlow onboarding Space

1. Go to [github.com/copilot/spaces](https://github.com/copilot/spaces) and create a new Space.
2. Name it **"PeopleFlow — New Joiner Onboarding"**.
3. Add knowledge sources — upload from `peopleflow/`:
   - All files under `src/` (the codebase)
   - All files under `docs/` (the onboarding docs)
4. Open `docs/copilot-space-instructions.md` and paste its contents into the Space's instructions field.

### Task 4b: Test the Space as a day-1 engineer

Open your Space in a browser and try these prompts:

**Getting oriented:**
```
I just joined PeopleFlow today. What should I read first?
```

**Understanding a pattern:**
```
Walk me through what happens when a new employee is created via the API.
Start from the HTTP request and follow the code through to the Celery tasks.
```

**Working on a real issue:**
```
I've been assigned issue-003 — the review cycle date validation bug.
Help me understand the bug and write the fix following PeopleFlow's
error handling conventions.
```

### Task 4c: Compare Space vs. bare Copilot

Ask the **same question** in two places — your Space and a regular Copilot Chat:

```
What would happen if I forgot to include tenant_id in a database query?
```

- **Space**: Specific answer referencing `TenantQuery`, `database.py`, the multi-tenancy model, and why it's a data leak.
- **Regular Chat**: Generic answer about multi-tenancy in general.

This is the value of context engineering: the same AI, dramatically different usefulness.

<details>
<summary>💡 Key takeaway</summary>

Spaces are the team-scale payoff. One person writes good docs and instructions, and every team member — present and future — benefits instantly, without any local configuration.

</details>

---

## How the Four Layers Work Together

```
┌─────────────────────────────────────────────────────────────────┐
│                    New developer's day 1                         │
│                                                                 │
│  1. Opens Copilot Space in browser (Part 4)                     │
│     → Reads architecture docs, asks questions, picks an issue   │
│                                                                 │
│  2. Clones repo, opens VS Code                                  │
│     → Instructions auto-apply (Part 1)                          │
│     → All generated code follows team conventions                │
│                                                                 │
│  3. Types @onboarding-buddy in Chat (Part 2)                    │
│     → Agent walks them through issue-001 step by step            │
│                                                                 │
│  4. Agent queries live staging DB via MCP (Part 3)              │
│     → Verifies the fix works against real data                   │
│                                                                 │
│  Result: Productive on day 1 without interrupting senior devs   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Lab Complete!

- ✅ **Instructions** — Taught Copilot your project's coding conventions
- ✅ **Agents** — Created specialized personas (onboarding buddy, reviewer)
- ✅ **MCP Servers** — Connected Copilot to external tools and data
- ✅ **Spaces** — Packaged everything into a shared onboarding environment

### Bonus: Full demo walkthrough

`docs/demo-prompts.md` contains 17 prompts across 5 sections, organized for a live demo or workshop. Use them to showcase the full onboarding story to stakeholders.
