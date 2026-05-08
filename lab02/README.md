# Lab 02 — Testing with Copilot

**Duration:** ~1 hour  
**SDLC Phase:** Test  
**Autonomy Level:** 🟢 Human directs, Copilot generates  
**Prerequisites:** Lab 01 completed, Python 3.10+, VS Code with GitHub Copilot

---

## What You'll Practice

| Part | Skill | Time | Copilot Feature |
|------|-------|------|-----------------|
| **1** | Mocking HTTP & DB | 10 min | Chat `/tests` + inline |
| **2** | Fixtures & Parametrize | 15 min | Chat + inline suggestions |
| **3** | Async with `AsyncMock` | 15 min | Chat with explicit prompt |
| **4** | Coverage gap fill | 10 min | Agent Mode (VS Code) + `copilot` CLI |
| **5** | CI gate + Copilot Coding Agent | 10 min | GitHub Actions + coding agent |
| **6** | GitHub Copilot CLI for testing | 10 min | `copilot` interactive + programmatic |
| **7** | E2E testing with MCP servers | 15 min | Playwright MCP + Agent Mode |

---

## Setup

```bash
cd lab02
pip install -r requirements.txt
```

Verify everything is working:

```bash
pytest tests/ -v
```

(All tests should be collected but show as `passed` — they're stubs with `pass`.)

---

## Part 1 — Mocking HTTP & DB (10 min)

**File:** `tests/test_process_order.py`

Open `order_processor.py` and look at `process_order()`. It has **5 code paths**:

| # | Condition | Expected `status` |
|---|-----------|-------------------|
| 1 | Invalid order (no items) | `"invalid"` |
| 2 | DB save fails | `"error"` |
| 3 | Payment succeeds | `"ok"` |
| 4 | Payment HTTP error (402) | `"payment_failed"` |
| 5 | Payment timeout | `"payment_timeout"` |

### Your task

Fill in the 5 test methods in `tests/test_process_order.py` to cover all paths.

**Key techniques:**
- `unittest.mock.patch` to mock `httpx.post` for the payment API
- In-memory SQLite (`:memory:`) for the DB — `save_order` accepts a `conn` parameter
- Create the `orders` table in your test setup

**Try with Copilot:** Open the test file and use **Copilot Chat** → ask it to help implement each test.

<details>
<summary>💡 Hints (click to expand)</summary>

- Patch at the import location: `@patch("order_processor.httpx.post")` not `@patch("httpx.post")`
- For `raise_for_status` on 402: `mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError("402", request=mock_request, response=mock_resp)`
- For timeout: `mock_post.side_effect = httpx.TimeoutException("timed out")`

</details>

### Verify

```bash
pytest tests/test_process_order.py -v
```

---

## Part 2 — Fixtures & Parametrize (15 min)

**Files:** `tests/test_validation.py` + `tests/conftest.py`

`validate_order()` has **8+ conditions**. Writing 8 separate test functions is tedious — use `@pytest.mark.parametrize` instead.

### Your tasks

1. **Fixture factory:** Move the `make_order` fixture into `conftest.py` so it's shared across all test files. The fixture should return a *function* (factory pattern), not an object.

2. **Parametrized tests:** In `test_validation.py`, use `@pytest.mark.parametrize` to test all these cases in ONE test function:

   | `order_kwargs` | Expected error substring |
   |---|---|
   | `order_id=""` | `"order_id is required"` |
   | `order_id="   "` | `"order_id is required"` |
   | `customer_email="no-at"` | `"customer_email is invalid"` |
   | `customer_email=""` | `"customer_email is invalid"` |
   | `items=[]` | `"at least one item"` |
   | `discount_pct=-5` | `"between 0 and 100"` |
   | `discount_pct=101` | `"between 0 and 100"` |

3. **Boundary tests:** Verify that `discount_pct=0` and `discount_pct=100` are VALID (no errors).

4. **Item-level validation:** Test `quantity <= 0` and `unit_price < 0`.

<details>
<summary>💡 Hints (click to expand)</summary>

- Fixture factory: the fixture returns a function, not an object
- For boundary tests (discount=0, discount=100): these should return empty error list
- Use `pytest.mark.parametrize("order_kwargs,expected_errors", [...])`

</details>

### Verify

```bash
pytest tests/test_validation.py -v
```

---

## Part 3 — Async with AsyncMock (15 min)

**File:** `tests/test_notify.py`

`notify_customer()` is fully async with `httpx.AsyncClient`. This forces you to use `AsyncMock` and `pytest-asyncio`.

### Your tasks

1. **Successful notification:** Mock the client, set `status_code = 200`, assert `True`
2. **Non-200 response:** Set `status_code = 500`, assert `False`
3. **Network error:** Set `side_effect = httpx.ConnectError("...")`, assert `False`

<details>
<summary>💡 Hints (click to expand)</summary>

- `AsyncMock` is in `unittest.mock` from Python 3.8+
- Mock the response: `mock_response = MagicMock(); mock_response.status_code = 200; mock_client.post.return_value = mock_response`
- Use `assert_awaited_once_with()` not `assert_called_once_with()` for async
- No context manager dance needed — `httpx.AsyncClient.post()` returns the response directly

</details>

### Verify

```bash
pytest tests/test_notify.py -v
```

---

## Part 4 — Coverage Gap Fill with Agent Mode (10 min)

Now let's see how much coverage you have:

```bash
pytest tests/ --cov=order_processor --cov-report=term-missing -v
```

### Your tasks

1. **Read the report** — which lines/functions are still uncovered?
2. **Use Copilot Agent Mode** (VS Code) — open Agent Mode and prompt:
   > "Run pytest with coverage, identify uncovered lines in order_processor.py, and write tests to cover them."
3. **Or use GitHub Copilot CLI:**
   ```bash
   copilot -p "Run pytest --cov on this project, find uncovered lines, and add tests" --allow-tool='shell(pytest)' --allow-tool='write'
   ```
4. Re-run coverage and aim for **80%+**

<details>
<summary>💡 Hints (click to expand)</summary>

- If Agent Mode stops early, re-prompt: "Continue — run pytest again and fix remaining failures"
- Likely uncovered: `load_order()`, `charge_customer()` standalone, `Order.subtotal`/`total` properties, `get_db_connection()`

</details>

---

## Part 5 — CI Coverage Gate + Agentic Workflows (10 min)

### 5a: Coverage gate in CI

If your repo has a `.github/workflows/tests.yml`, look for the `--cov-fail-under=80` flag — this makes the CI job **fail** if coverage drops below 80%. (If you don't have one yet, just test the flag locally.)

```bash
# Test it locally:
pytest tests/ --cov=order_processor --cov-report=term-missing --cov-fail-under=80 -v
```

If it fails, go back and add more tests until you pass the gate.

### 5b: Copilot Coding Agent (bonus)

GitHub's **Copilot coding agent** can automatically find and fill coverage gaps. You trigger it by assigning Copilot to a GitHub Issue or asking it in a PR review.

**Try it:**
1. Create a GitHub Issue titled: _"Increase test coverage of order_processor.py to 90%"_
2. Assign `@github-copilot` (or use the "Copilot" button in the issue sidebar)
3. Copilot opens a PR with new tests, runs CI, and iterates until the coverage target is met

Alternatively, from the CLI:
```bash
gh copilot "Look at lab02/order_processor.py and add tests to reach 90% coverage"
```

> **Note:** The coding agent requires a GitHub Copilot Enterprise or Pro+ plan and repository-level enablement.

<details>
<summary>💡 Hints (click to expand)</summary>

- `--cov-fail-under=80` exits with code 2 if coverage is below threshold
- The coding agent works best with a CI workflow that runs tests — it uses the CI results as feedback

</details>

---

## Part 6 — GitHub Copilot CLI for Testing (10 min)

So far you've used Copilot inside VS Code. Now let's use it **from the terminal** with **GitHub Copilot CLI** — a standalone AI agent that runs directly in your terminal.

> **Note:** The old `gh copilot` extension is retired. It has been replaced by **GitHub Copilot CLI** (the `copilot` command). See [About GitHub Copilot CLI](https://docs.github.com/en/copilot/concepts/agents/copilot-cli).

### Setup

```bash
# Install GitHub Copilot CLI (see https://docs.github.com/en/copilot/how-tos/set-up/install-copilot-cli)
# On macOS:
brew install gh-copilot

# On Windows (winget):
winget install GitHub.CopilotCLI

# Verify
copilot --version
```

### 6a: Interactive mode — understand & explore (3 min)

Start an interactive session and ask Copilot to explain unfamiliar patterns:

```bash
copilot
```

Once inside the interactive session, try:

```
What does @patch('order_processor.httpx.post') do and why not @patch('httpx.post')?
```

```
What does mock_client.post.return_value.status_code = 200 mean in Python testing with httpx?
```

**When to use:** Onboarding to a new codebase, understanding unfamiliar patterns, quick reference.

Use `Shift+Tab` to switch to **plan mode** for multi-step tasks.

### 6b: Programmatic mode — autonomous test generation (5 min)

Pass a single prompt directly on the command line. Copilot completes the task and exits.

**Step 1:** Check your current coverage gaps:

```bash
pytest tests/ --cov=order_processor --cov-report=term-missing -v
```

**Step 2:** Ask Copilot CLI to fill them:

```bash
copilot -p "Look at lab02/order_processor.py. The functions load_order() and charge_customer() need direct unit tests. Write them in lab02/tests/test_cli_generated.py using in-memory SQLite for DB and unittest.mock.patch for HTTP calls." --allow-tool='shell(pytest)' --allow-tool='write'
```

**Step 3:** Verify the generated tests pass:

```bash
pytest tests/ --cov=order_processor --cov-report=term-missing -v
```

**Step 4:** If coverage is still below target, iterate:

```bash
copilot -p "Coverage is still below 80%. Check the remaining uncovered lines and add tests." --allow-tool='shell(pytest)' --allow-tool='write'
```

### 6c: Useful slash commands (2 min)

In the interactive session, try these slash commands:

| Command | Purpose |
|---------|----------|
| `/model` | Switch the model (e.g., Claude Sonnet 4.5, GPT-4.1) |
| `/mcp` | List configured MCP servers |
| `/compact` | Manually compress context for long sessions |
| `/context` | Show token usage breakdown |

<details>
<summary>💡 Hints (click to expand)</summary>

- Interactive mode is best for exploration — start with `copilot` and have a conversation
- Programmatic mode (`-p`) is best for scripted/CI tasks — include `--allow-tool` flags
- Use `--allow-tool='shell(pytest)'` to let Copilot run pytest without asking each time
- Plan mode (`Shift+Tab`) is great for complex multi-step tasks — Copilot builds a plan before writing code
- If Copilot's output isn't right, refine your prompt with more context

</details>

---

## Part 7 — E2E Testing with MCP Servers (15 min)

So far you've tested at the **unit level** — mocking dependencies and testing functions in isolation. Now let's go beyond unit tests using **MCP (Model Context Protocol) servers** to run **end-to-end browser tests** and **API tests** directly from Agent Mode.

### What is MCP?

MCP servers give Copilot **tools** it can call — like opening a browser, clicking buttons, or making HTTP requests. For testing, this means the agent can interact with a running application just like a real user.

### Setup

1. **Configure Playwright MCP in VS Code:** Add to your `.vscode/mcp.json` (or user settings):
   ```json
   {
     "mcp": {
       "servers": {
         "playwright": {
           "command": "npx",
           "args": ["@playwright/mcp@latest"]
         }
       }
     }
   }
   ```

   > **Note:** Playwright MCP is a [Microsoft open-source project](https://github.com/microsoft/playwright-mcp). The npm package is `@playwright/mcp`.

2. **Restart VS Code** and verify Playwright appears in Agent Mode's tool list (look for the tools icon).

### 7a: Discover available MCP tools (2 min)

Switch to **Agent Mode** and ask:

```
What Playwright MCP tools do you have available? List them briefly.
```

You should see tools like `browser_navigate`, `browser_click`, `browser_snapshot`, `browser_type`, etc. These are the building blocks for browser-based testing.

### 7b: Exploratory API testing with Playwright MCP (5 min)

`order_processor.py` has HTTP calls to a payment API. Let's use MCP to test an API endpoint interactively.

Ask Agent Mode:

```
Use Playwright MCP to navigate to https://httpbin.org/post and take a snapshot.
Then explain what this endpoint does and how I could use it
as a mock payment API for testing order_processor.py.
```

**What to observe:**
- The agent calls `browser_navigate` → `browser_snapshot` in sequence
- Snapshots return an **accessibility tree** (text-based), not a screenshot — ideal for AI analysis
- The agent can reason about what it sees and suggest testing strategies

### 7c: E2E test flow with MCP (5 min)

Now let's combine MCP with the code you already tested. Ask Agent Mode:

```
I want to verify my order processing system works end-to-end.

1. Use Playwright MCP to make a POST request to https://httpbin.org/post
   with a JSON body: {"order_id": "ORD-001", "amount": 99.99}
2. Take a snapshot of the response page
3. Verify the response shows the data was received correctly
4. Based on this, write a pytest test in tests/test_e2e_mcp.py that
   uses httpbin.org as a real payment endpoint (no mocking)
   to test process_order() with a live HTTP call
```

**Key insight:** MCP lets you **explore first, codify later**. The agent discovers how the API behaves interactively, then generates repeatable pytest tests from its findings.

### 7d: Accessibility audit (3 min)

Playwright MCP's snapshot returns an accessibility tree — making it a natural **accessibility auditing tool**. Try it on any web page:

```
Use Playwright MCP to navigate to https://example.com and take a snapshot.
Analyze the accessibility tree:
- Is there a proper heading hierarchy?
- Are all links descriptive?
- Are ARIA roles used correctly?
List any issues.
```

### Adding more MCP servers (optional)

You can extend your testing toolkit with additional MCP servers:

| MCP Server | Use Case | Install |
|-----------|----------|----------|
| `@playwright/mcp` | Browser E2E & a11y testing | `npx @playwright/mcp@latest` |
| `@anthropic/fetch-mcp` | Dedicated HTTP/API testing | `npx @anthropic/fetch-mcp@latest` |

To add **Fetch MCP**, add to your MCP config:
```json
{
  "fetch": {
    "command": "npx",
    "args": ["@anthropic/fetch-mcp@latest"]
  }
}
```

Then ask Agent Mode:
```
Use the fetch tool to POST to https://httpbin.org/post with
{"test": true} and verify the response.
```

### Takeaway

MCP servers turn Agent Mode into a **full testing platform**:
- **Explore** interactively with browser/API tools
- **Discover** bugs and edge cases in real time
- **Generate** repeatable pytest tests from findings
- **Verify** fixes immediately through the same tools

This is the **explore → find → codify** pattern — use MCP for discovery, then lock it down as automated tests.

---

## Final Check

Run the full suite with coverage:

```bash
pytest tests/ --cov=order_processor --cov-report=term-missing -v
```

---

## Lab Complete! Here's What You Practiced:

- ✅ Mocking HTTP clients (`httpx`) and DB layers with `unittest.mock.patch`
- ✅ Fixture factories with `conftest.py` for clean, reusable test data
- ✅ `pytest.mark.parametrize` for data-driven edge case coverage
- ✅ Async testing with `AsyncMock` and `pytest-asyncio`
- ✅ Copilot Agent Mode (VS Code) and CLI `task` agent to identify and fill coverage gaps autonomously
- ✅ CI coverage gate with `--cov-fail-under` to make quality a hard requirement
- ✅ GitHub Copilot coding agent for continuous, automated test improvement
- ✅ GitHub Copilot CLI (`copilot`) for interactive and programmatic terminal-first testing workflows
- ✅ MCP servers (Playwright, Fetch) for E2E browser testing and API validation from Agent Mode

---

## Solutions

Solutions for each part are in the `solutions/` folder:
- `solutions/test_process_order_solution.py` — Part 1
- `solutions/conftest_solution.py` — Part 2 (shared fixtures)
- `solutions/test_validation_solution.py` — Part 2
- `solutions/test_notify_solution.py` — Part 3

---

## Trainer Notes

- The starter code is intentionally injectable — all external deps (DB, HTTP, async session) accept optional parameters so they're easy to mock without monkeypatching globals
- `process_order()` has 5 distinct code paths — ideal for Part 1
- `validate_order()` has 8+ conditions — ideal for parametrize in Part 2
- `notify_customer()` is fully async with httpx.AsyncClient — forces use of AsyncMock in Part 3
- Part 5b references the GitHub Copilot coding agent — participants can try assigning Copilot to an issue as a bonus exercise
- `datetime.datetime.now()` in `Order.__post_init__` is an intentional testability trap — ask participants how they'd mock it (answer: inject `created_at` explicitly in tests, or monkeypatch `datetime.datetime`)
