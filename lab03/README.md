# Lab 03 — Debugging & Troubleshooting

**Duration:** ~1.5 hours  
**SDLC Phase:** Debug  
**Autonomy Level:** 🟡 Human points, Copilot fixes  
**Prerequisites:** Lab 02 completed, Python 3.10+, VS Code with GitHub Copilot

---

## What You'll Practice

| Part | Skill | Time | Copilot Feature |
|------|-------|------|-----------------|
| **1** | Find bugs with Copilot | 15 min | `/fix` + Chat panel |
| **2** | Explain unfamiliar code | 10 min | Chat panel |
| **3** | Generate docstrings & docs | 15 min | Inline Chat + Chat panel |
| **4** | Troubleshoot failing tests | 15 min | Chat + debugger-aware `#` references |
| **5** | Generate a README from code | 10 min | Chat with `@workspace` |
| **6** | Fix all bugs with Agent Mode | 5 min | Agent Mode (bonus) |
| **7** | Create a debugging agent & skill | 15 min | Custom agents & skills |

---

## Setup

```bash
cd lab03
pip install -r requirements.txt
```

---

## The Scenario

You've inherited `inventory.py` — an inventory management system written by a colleague who left the company. It has **7 known bugs** and **no documentation**.

Your job: fix the bugs, add documentation, and write tests.

---

## Part 1 — Find and Fix Bugs (15 min)

**File:** `inventory.py`

There are **7 bugs** hidden in the code. Use Copilot to find them.

### Your tasks

1. **Select the `Inventory` class** → type `/fix` in the inline chat to get a targeted fix suggestion
2. Review each suggestion. Copilot should catch most of the bugs.
3. Alternatively, open the **Chat panel** and ask *"Find and fix bugs in the selected code"*
4. For the ones it misses, try selecting individual methods and using `/fix` again, or ask:
   - *"Is the restock method correct? It seems like stock is being replaced, not added."*
   - *"What's wrong with the get_low_stock filter?"*
   - *"Is the percentage calculation in bulk_update_prices correct?"*

### Bug checklist

Once you've found them, check them off:

- [ ] `restock()` — stock is replaced instead of added (`=` should be `+=`)
- [ ] `sell()` — total uses integer division (`// 1` should be removed or use `round()`)
- [ ] `get_low_stock()` — comparison is backwards (`>` should be `<`)
- [ ] `get_total_value()` — adds only price, not price × stock
- [ ] `bulk_update_prices()` — divides by 10 instead of 100
- [ ] `export_report()` — value is price + stock instead of price × stock
- [ ] `get_transactions()` — compares string timestamp to datetime object

<details>
<summary>💡 Hints</summary>

- Try: select a method → `/fix` for an instant targeted fix
- Try: select the whole class → Chat → *"Fix all bugs in the selected code"* → review all suggestions
- For `get_transactions`: the fix is to compare `t["timestamp"] > since.isoformat()`

</details>

### Verify

After fixing all bugs, create `test_inventory.py` and write at least one test per fix to prove the bug is gone.

---

## Part 2 — Explain Unfamiliar Code (10 min)

Pretend you've never seen this codebase before.

### Why selecting code matters

Copilot works best when you **highlight the specific code** you're asking about. Without a selection, Copilot has to guess what you mean. With a selection, it gets precise context — and you get precise answers.

Right-click any selected code to access four Copilot commands. Here's how they fit together:

```
                        ┌─────────────────────┐
                        │   Select code in     │
                        │   the editor         │
                        └─────────┬───────────┘
                                  │
                           right-click
                                  │
                ┌─────────────────┼─────────────────┐
                │                 │                  │
        ── Read-only ──    ── Interactive ──    ── Contextual ──
                │                 │                  │
       ┌───────┴───────┐         │           ┌──────┴──────┐
       │               │         │           │             │
  ┌────▼────┐   ┌──────▼──┐  ┌──▼───────┐  ┌▼───────────┐│
  │ Explain │   │ Review  │  │ Inline   │  │ Add to     ││
  │         │   │         │  │ Chat     │  │ Chat       ││
  │ "What   │   │ "Any    │  │ Ctrl+I   │  │ Panel      ││
  │ does    │   │ bugs    │  │          │  │            ││
  │ this    │   │ here?"  │  │ "Fix,    │  │ "Let's     ││
  │ do?"    │   │         │  │ refactor,│  │ discuss    ││
  │         │   │         │  │ edit"    │  │ this..."   ││
  └────┬────┘   └────┬────┘  └────┬─────┘  └─────┬─────┘│
       │              │            │               │      │
       ▼              ▼            ▼               ▼      │
   One-click     One-click    Prompt +        Send to     │
   output in     output in    edit in         Chat for    │
   Chat          Chat         place           follow-ups  │
                                                          │
  ◄──── No prompting needed ────►◄── You write a prompt ──►
```

> **Tip:** You can select a single line, an entire method, or a whole class — the scope of your selection controls the scope of Copilot's response.

| Command | What it does | When to use it |
|---------|-------------|----------------|
| **Explain** | Generates a plain-language explanation of the selected code | Onboarding to unfamiliar code, understanding complex logic |
| **Review** | Analyzes the selection for bugs, security issues, and improvements | Code review, validating your own changes before committing |
| **Open Inline Chat** (`Ctrl+I`) | Opens an inline prompt right in the editor over your selection | Quick fixes, refactors, or questions without leaving the code |
| **Add Selection to Chat** | Sends the selected code as context into the Chat panel | When you want to ask follow-up questions or have a conversation about the code |

> **Tip:** You can select a single line, an entire method, or a whole class — the scope of your selection controls the scope of Copilot's response.

### Your tasks

1. Select `export_report()` → right-click → **Explain** — read the generated explanation
2. Select `get_transactions()` → right-click → **Add Selection to Chat** → ask *"Explain the filtering logic and what types the parameters expect"*
3. Select `_record_transaction()` → right-click → **Review** — see if Copilot flags anything
4. Select the `Inventory` class → right-click → **Open Inline Chat** (`Ctrl+I`) → ask *"What design pattern does this class follow?"*

### Takeaway

These four right-click commands are the fastest way to interact with Copilot on specific code. **Explain** and **Review** are zero-prompting — one click and you get results. **Add Selection to Chat** is best for follow-up conversations. **Open Inline Chat** is best when you want to edit the code in place.

---

## Part 3 — Generate Documentation (15 min)

The code has minimal docstrings. Let's fix that.

### Your tasks

1. **Docstrings:** Select each method → `Ctrl+I` → *"Add a docstring to this method"*. Copilot generates Google/NumPy-style docstrings with parameters, return types, and examples.

2. **Type hints:** Ask Chat: *"Add type hints to all methods in the Inventory class"*

3. **Inline comments:** For complex logic (like `get_transactions` filtering), ask: *"Add inline comments explaining each step"*

4. **Module docstring:** At the top of the file, ask Chat: *"Generate a module-level docstring for inventory.py explaining what this module does"*

<details>
<summary>💡 Hints</summary>

- `Ctrl+I` on selected code is the fastest way to add docstrings
- For type hints, Copilot uses the existing code to infer types
- Ask for specific docstring formats: "Use Google-style docstrings"

</details>

---

## Part 4 — Troubleshoot Failing Tests (15 min)

**File:** `tests/test_inventory_starter.py`

The starter test file has tests that **fail due to the original bugs**. Your job: use the failing test output + Copilot to understand and fix each failure.

### Your tasks

1. Run the tests:
   ```bash
   pytest tests/test_inventory_starter.py -v
   ```
2. For each failure, **copy the error traceback** → paste into Chat → ask *"Why is this test failing and how do I fix it?"*
3. Copilot will explain the root cause (the bug) and suggest the fix

### Part 4b — Debugger-Aware Fixing with Copilot

This exercise teaches three debugger-integrated Copilot techniques in VS Code.

#### Technique 1: Inline Chat with Debugger Context

When paused at a breakpoint, VS Code Copilot automatically has access to your **live debugger state** (local variables, call stack) as context:

1. Ask Copilot to generate a debug config: *"Generate a launch.json to debug pytest for this project"*
2. Set a breakpoint on the line `product.price = product.price * (1 + adjustment_pct / 10)` inside `bulk_update_prices`
3. In the Run and Debug panel, launch the pytest config. When paused at the breakpoint, open **inline chat** (`Ctrl+I`) and type:
   ```
   Is this percentage calculation correct? adjustment_pct is supposed to be 10 for a 10% increase.
   ```
4. Copilot automatically sees the local variable values from the debugger. It identifies that `adjustment_pct / 10` yields `1.0` (not `0.1`) and suggests changing `/10` to `/100`.
5. You can also add `#callstack` to explicitly include the full call context in your prompt

#### Technique 2: Rubber Ducking in Chat

Instead of crafting a perfect prompt, just **describe the problem in plain language** — like explaining it to a colleague:

1. Open Chat (`Ctrl+Shift+I`) and type naturally:
   ```
   I'm confused about bulk_update_prices. When I pass 10 for a 10% increase,
   the price goes way too high. I expected 9.99 to become ~10.99 but it
   becomes 19.98. Something is off with the math.
   ```
2. Copilot picks up the context and identifies the `/10` vs `/100` bug — you don't need to be precise or technical in your prompt

#### Technique 3: Conditional Breakpoint Assistance

Copilot can help you define **smart breakpoint conditions** so you only pause when it matters:

1. Right-click the gutter on the `product.stock = quantity` line in `restock()` → **Add Conditional Breakpoint**
2. Not sure what expression to write? Open the **Chat panel** and ask:
   ```
   I want a conditional breakpoint on the restock assignment line that only
   triggers when the stock is being overwritten (item already has stock).
   What Python expression should I use?
   ```
3. Copilot suggests something like `product.stock > 0` — copy and paste it into the breakpoint condition field
4. Now the debugger only pauses when the bug actually manifests (restocking an item that already has stock, so the overwrite loses existing inventory)

You can also do this for other import 

---

## Part 5 — Generate a README from Code (10 min)

### Your tasks

1. In Chat, use `@workspace` context → *"Generate a README.md for the inventory module including: overview, installation, usage examples, and API reference"*
2. Review the output — Copilot will produce a full README with code examples
3. Ask: *"Add a section about known limitations and a changelog template"*

<details>
<summary>💡 Hints</summary>

- `@workspace` gives Copilot full project context without manual file selection
- Be specific about what sections you want in the README
- Ask for "usage examples with expected output" to get runnable code blocks

</details>

---

## Part 6 — Fix All Bugs with Agent Mode (5 min, bonus)

Now that you've fixed bugs one by one, let's see how Agent Mode handles the whole task autonomously.

### Your tasks

1. **Reset** `inventory.py` to the original buggy version (undo your fixes, or `git checkout inventory.py`)
2. Switch to **Agent Mode** in the Chat panel
3. Prompt:
   ```
   Find and fix all bugs in inventory.py, then run pytest tests/test_inventory_starter.py
   to verify all tests pass.
   ```
4. Watch the agent iterate — it will read the code, make a plan, identify bugs, apply fixes, run tests, and fix any remaining failures

### Takeaway

Agent Mode is ideal when you want Copilot to handle the full debug cycle autonomously. Compare the experience: Part 1 (you direct, Copilot suggests) vs Part 6 (Copilot drives, you review).

---

## Part 7 — Create a Debugging Agent & Skill (15 min)

Now that you've learned to debug with Copilot, let's **automate** that expertise by creating a custom **agent** and **skill** that anyone on your team can reuse.

### What are Agents and Skills?

- **Agent** (`.agent.md`): A reusable persona with specific instructions, workflow, and constraints. Lives in `.github/agents/`. Invoked via `@agent-name` in Copilot Chat.
- **Skill** (`SKILL.md`): Domain-specific knowledge that Copilot loads automatically when relevant. Lives in `.github/skills/<name>/SKILL.md`. Triggered by topic keywords — no explicit invocation needed.

### Task A — Create a Bug Hunter Agent (7 min)

Create a file `.github/agents/bug-hunter.agent.md` that instructs Copilot to act as a debugging specialist.

1. Open the Chat panel and ask:
   ```
   Help me create a custom Copilot agent called "bug-hunter" that specializes
   in finding and fixing Python bugs. It should read the code, run pytest,
   analyze failures, and suggest fixes. Put it in .github/agents/bug-hunter.agent.md
   ```

2. Review the generated file. A good agent definition should include:
   - **Role description** — what the agent does
   - **Workflow** — step-by-step process (read code → run tests → analyze → fix)
   - **Tool preferences** — which tools the agent should use (terminal, file reading, grep)
   - **Constraints** — what the agent should NOT do (e.g., don't delete files, don't change test expectations)

3. Compare your result with the solution in `solutions/bug-hunter.agent.md`

4. **Try it out:** In Copilot Chat, type `@bug-hunter Find and fix all bugs in inventory.py` and watch it work

### Task B — Create a Troubleshooting Skill (8 min)

Create a skill that automatically activates when Copilot detects debugging-related questions.

1. Create the folder `.github/skills/python-debugging/` and a file `SKILL.md` inside it

2. Ask Copilot:
   ```
   Help me create a SKILL.md file for a "python-debugging" skill that provides
   Copilot with best practices for debugging Python code, including:
   - Common bug patterns (off-by-one, wrong operators, type mismatches)
   - How to read pytest tracebacks
   - Debugging strategies (binary search, rubber duck, print debugging)
   Put it in .github/skills/python-debugging/SKILL.md
   ```

3. A good skill definition should have YAML frontmatter with:
   ```yaml
   ---
   description: >
     Use this skill when debugging Python code, analyzing test failures,
     or troubleshooting runtime errors. Provides patterns for common bugs
     and strategies for systematic debugging.
   ---
   ```

4. Compare with the solution in `solutions/python-debugging-SKILL.md`

<details>
<summary>💡 Key differences: Agent vs Skill</summary>

| | Agent | Skill |
|---|---|---|
| **Invocation** | Explicit: `@agent-name` | Automatic: triggered by topic |
| **Location** | `.github/agents/*.agent.md` | `.github/skills/<name>/SKILL.md` |
| **Purpose** | Define a workflow/persona | Provide domain knowledge |
| **Scope** | Full task automation | Context enrichment |

</details>

### Task C — Think Like an Enterprise (5 min)

In a real enterprise, repo-specific agents are not just a nice-to-have — they're a force multiplier. Consider the `inventory.py` codebase as if it were a production inventory service maintained by a team of 10.

**When repo-specific agents add value:**

| Benefit | Example for this repo |
|---------|----------------------|
| **Domain-encoded workflows** | An agent that knows "reorder thresholds depend on supplier lead times" — not just generic Python debugging |
| **Guardrails** | "Never modify pricing logic without a corresponding test" enforced by agent constraints |
| **Onboarding** | New engineers type `@bug-hunter` instead of reading 50 pages of runbooks |
| **Consistency** | Everyone follows the same diagnostic steps: run integration tests → check event log → isolate the method |
| **Tribal knowledge capture** | The agent *is* the runbook — it evolves with the code, not a stale wiki page |

**When it's overkill:**

- Trivial repos with a single maintainer who already knows the codebase
- Cases where generic Copilot prompting (`/fix`, `@workspace`) covers 95% of tasks
- If nobody maintains the agent definition — stale instructions are worse than none

**Enterprise best practices for repo agents:**

1. **Scope tightly** — one agent per workflow (debugging, migration, deployment), not one mega-agent
2. **Version with the code** — the `.agent.md` lives in the repo and evolves with the codebase
3. **Reference actual paths/commands** — e.g., `pytest tests/integration/ -v` rather than generic advice
4. **Pair with a SKILL file** — for reusable domain knowledge the agent can draw on
5. **Add tool restrictions** — "Avoid: deleting files, modifying test fixtures" prevents costly mistakes in CI/prod-adjacent contexts

#### Discussion questions

- Would you create one `bug-hunter` agent for the whole org, or one per service repo? Why?
- How would you handle agent drift as the codebase evolves — CI checks? Code review on `.agent.md` changes?
- What sensitive information should you *never* put in an agent file (secrets, internal URLs)?

### Takeaway

Custom agents and skills let you **encode team debugging expertise** into reusable Copilot extensions. An agent automates the workflow ("find bugs, run tests, fix"), while a skill provides the knowledge ("common Python bug patterns"). Together, they make every team member as effective as your best debugger. In enterprise settings, repo-specific agents are a high-leverage investment — they capture tribal knowledge, enforce guardrails, and scale expertise across the team — as long as they're maintained alongside the code they target.

---

## Solutions

- `solutions/inventory_fixed.py` — All 7 bugs fixed with documentation
- `solutions/bug-hunter.agent.md` — Example debugging agent definition
- `solutions/python-debugging-SKILL.md` — Example debugging skill definition

> **Note:** `solutions/test_inventory_solution.py` is not yet provided.

---

## Lab Complete!

- ✅ Found and fixed bugs using `/fix` and Chat panel
- ✅ Used Copilot to explain unfamiliar code
- ✅ Generated docstrings and documentation with inline chat
- ✅ Troubleshot failing tests by pasting tracebacks into Chat
- ✅ Used debugger-aware inline chat with `#` to reference live state
- ✅ Generated a full README from source code using `@workspace`
- ✅ Created a custom debugging agent (`bug-hunter.agent.md`)
- ✅ Created a troubleshooting skill (`python-debugging/SKILL.md`)
- ✅ Used Agent Mode to fix all bugs autonomously (bonus)
