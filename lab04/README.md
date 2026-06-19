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


### What are Copilot Instructions?

Copilot Instructions are markdown files that teach Copilot your project's conventions—like coding style, error handling, and testing standards. When present, Copilot reads these files automatically and adapts its code suggestions to match your team's preferences, so you get consistent, high-quality code without having to repeat yourself.

**How are Copilot Instructions different from Agents and Skills?**

- **Instructions**: Set the baseline rules and conventions for your project. They are always applied and affect all Copilot suggestions in the repo.
- **Agents**: Give Copilot a specific persona, task focus, or toolset for specialized workflows (e.g., code review agent, onboarding agent). Agents are invoked for particular tasks and can override or extend instructions.
- **Skills**: Package reusable workflows or capabilities that agents (or Copilot itself) can use. Skills are like modular building blocks for automation or guidance.

Start with Copilot Instructions to ensure everyone codes the same way. Use Agents and Skills to go further with specialized automation and workflows.

---

## Part 2 — Custom Agents (15 min)

### What are they?

Agents are markdown files (`.github/agents/*.agent.md`) that give Copilot a **persona, a specific task focus, and optionally restricted tool access**. Think of them as specialized coworkers: one agent for code review, another for database work, another for onboarding.

Unlike instructions (which apply globally), agents are **invoked by name** — you choose when to use them.

#### How agents differ from instructions

| | Instructions | Agents |
|---|---|---|
| **Activated** | Automatically, always | By user, via `@agent-name` |
| **Purpose** | "Always follow these rules" | "You are an expert at X" |
| **Tool access** | N/A | Can restrict to specific tools |
| **Persona** | No persona | Has identity, tone, focus |

### Task 2a: Create an onboarding agent

Create `.github/agents/onboarding-buddy.agent.md`:

```markdown
---
description: Helps new PeopleFlow developers get up to speed
tools:
  - read
  - web
  - agent

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

### Task 3a: Install the GitHub MCP server

Open the Command Palette (`Ctrl+Shift+P`) → **MCP: List Servers** to see what's configured.

If the GitHub server isn't listed, add it:

1. Open the Command Palette (`Ctrl+Shift+P`) → **MCP: Add Server**
2. Select **Browse MCP Servers...**
3. Search for **GitHub** and install the official GitHub MCP server
4. Create a Personal Access Token (PAT):
   - Go to [github.com/settings/tokens](https://github.com/settings/tokens) → **Generate new token (classic)**
   - Give it a name (e.g. `vscode-mcp`) and set an expiry
   - Select scopes: `repo` (full repo access) and `read:org`
   - Click **Generate token** and copy the value — you won't see it again
5. Back in VS Code, paste the token when prompted for authentication

VS Code will add the server to `.vscode/mcp.json` automatically. This gives Copilot live access to GitHub — issues, PRs, repos, and more — without leaving the editor.


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
| Agents | `.github/agents/` | Devs using VS Code |
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

### Task 4d: Connect your Space to the GitHub MCP server

A Space can go further than static docs — it can call live tools via MCP, giving it access to real issues, PRs, and repo data at query time.

> [!NOTE]
> The MCP connection you set up in VS Code (Task 3a) only applies to your local editor. Spaces run on the web and need their own separate MCP connection — even if you've already connected GitHub MCP in VS Code.

1. Open your Space at [github.com/copilot/spaces](https://github.com/copilot/spaces) and select your Space.
2. Click the **Install MCP** button in the top-right corner of the Space.
3. Search for **GitHub** and select the official GitHub MCP server.
4. When prompted, paste the Personal Access Token you created in Task 3a (needs `repo` and `read:org` scopes).
5. Click **Save** and return to your Space chat.

> [!TIP]
> You can also ask Copilot Chat inside the Space: *"Add the GitHub MCP server to this Space"* and it will walk you through the steps.

Once connected, your Space can answer questions using live GitHub data — not just the static files you uploaded. Try:

```
Using the GitHub tools, list all open issues in this repo labelled "good first issue" and suggest which one a new joiner should pick up.
```

```
Fetch the latest merged PRs and summarise what changed in the employees service this week.
```

<details>
<summary>💡 Key takeaway</summary>

Connecting MCP to a Space bridges static knowledge (your docs and code) with live data (real issues, PRs, and repo activity). A new joiner can get up to speed *and* stay current — all from one place, with no local setup.

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
