# Lab 01 — Code Generation Fundamentals

**Duration:** ~1 hour (plus ~10 min for initial setup)  
**SDLC Phase:** Code  
**Autonomy Level:** 🟢 Human writes, Copilot suggests

---

## Learning Objective

Master the fundamentals of GitHub Copilot as a **code generation tool**: inline completions, Chat interactions, and slash commands. By the end, you'll be fluent in the core features that every subsequent lab builds on.

---

## What You'll Practice

| Part | Skill | Time | Copilot Feature |
|------|-------|------|-----------------|
| **1** | Inline completions (ghost text) | 10 min | Tab to accept suggestions |
| **2** | Chat for code generation | 15 min | Copilot Chat sidebar |
| **3** | Slash commands | 10 min | `/explain`, `/fix`, `/tests`, `/doc` |
| **4** | Prompt crafting techniques | 15 min | Chat with refined prompts |
| **5** | GitHub Copilot CLI | 10 min | `gh copilot explain/suggest` |

---

## Setup

```bash
cd lab01
pip install pytest
```

---

## The Scenario

You have `library.py` — a library management system with the core structure in place but several **TODO methods** that need to be implemented. This is your playground for learning Copilot's code generation features.

---

## Part 1 — Inline Completions (10 min)

Inline completions are the "ghost text" that appears as you type. This is Copilot's most basic — and often most useful — feature.

### Your tasks

1. **Complete a TODO method:** Go to the first TODO in `library.py`:
   ```python
   # TODO: Add a method to search books by genre
   ```
   Start typing `def search_by_genre(self` and **wait** — Copilot will suggest the rest. Press `Tab` to accept.

2. **Complete more TODOs:** Work through each TODO comment. For each one:
   - Start typing the method signature
   - Let Copilot suggest the body
   - Press `Tab` to accept, or `Esc` to reject and type your own

3. **Multi-line completions:** After completing one method, press `Enter` twice. Copilot may suggest the next logical method. Try it on the report method at the bottom.

4. **Partial accept:** Press `Ctrl+→` (Cmd+→ on Mac) to accept **word by word** instead of the full suggestion. Useful when Copilot gets the start right but the end wrong.

### Tips
- Copilot reads the surrounding code — the more context (docstrings, type hints, method names), the better the suggestions
- If the suggestion is wrong, keep typing — Copilot will adjust
- Press `Alt+]` / `Alt+[` to cycle through alternative suggestions

### ✅ Verify

Run the existing tests to confirm your TODO implementations work:
```bash
pytest tests/ -v
```
All tests should pass. If any fail, review your implementations and try again.

---

## Part 2 — Chat for Code Generation (15 min)

Open Copilot Chat (`Ctrl+Alt+I`) for longer, more complex generation tasks.

### Your tasks

1. **Generate a full method:** Ask Chat:
   ```
   Write a method for the Library class that calculates late fees.
   Fee is $0.25 per day overdue, capped at the book's replacement cost of $25.
   ```
   Review the output and paste it into the class.

2. **Generate from description:** Ask Chat:
   ```
   Add a reservation system to the Library class. Members should be able
   to reserve a book that's currently checked out. When the book is returned,
   the first member in the reservation queue gets notified.
   ```
   Note how Chat produces a complete implementation with a data structure.

3. **Ask for alternatives:** If you don't like the first approach:
   ```
   Show me a different approach using a deque instead of a list for the queue.
   ```

4. **Context-aware generation:** Select the `checkout_book` method → ask Chat:
   ```
   Write a similar method called renew_book that extends the due date
   by 7 days. Follow the same patterns and return format.
   ```
   Copilot uses the selected code as context.

---

## Part 3 — Slash Commands (10 min)

Slash commands are shortcuts for common tasks.

### Your tasks

1. **`/explain`** — Select the `checkout_book` method → type `/explain` in Chat. Read the explanation. Does it match your understanding?

2. **`/doc`** — Select `Library` class → type `/doc`. Copilot generates docstrings for every method. Review and accept.

3. **`/tests`** — Select `checkout_book` → type `/tests`. Copilot generates a test file. Save it as `tests/test_checkout.py` and run:
   ```bash
   pytest tests/test_checkout.py -v
   ```

4. **`/fix`** — Intentionally break something (e.g., change `>=` to `>` in `is_overdue`). Select the code → type `/fix`. Does Copilot catch it?

### Takeaway

Slash commands are the fastest path for common tasks. They're the building blocks for everything you'll do in later labs.

---

## Part 4 — Prompt Crafting (15 min)

The quality of Copilot's output depends on the quality of your prompt. Learn the difference.

### Your tasks

**Bad prompt vs. good prompt:**

1. **Vague:** Ask Chat: *"Add a statistics feature"* — note how generic the output is.

2. **Specific:** Ask Chat:
   ```
   Add a get_statistics method to Library that returns a dict with:
   - total_books: int (count of unique ISBNs)
   - total_copies: int (sum of copies_total)
   - available_copies: int (sum of copies_available)  
   - active_members: int (count of active members)
   - active_loans: int (count of unreturned loans)
   - overdue_loans: int (count of overdue unreturned loans)
   - most_popular_genre: str (genre with most loans)
   All numeric values should be ints. Follow existing patterns.
   ```
   Compare the two outputs.

**Iterative prompting:**

3. Take the output from step 2 and refine:
   ```
   Good, but also add:
   - average_loan_duration_days for returned loans
   - member_with_most_loans as a tuple (member_id, count)
   ```

4. Then ask for tests:
   ```
   Write parametrized pytest tests for get_statistics covering:
   - empty library
   - library with books but no loans
   - library with active and overdue loans
   ```

### Key principles
- **Be specific** about inputs, outputs, types, and edge cases
- **Reference existing patterns** ("follow the same return format")
- **Iterate** — refine in follow-up messages, don't try to get it perfect in one prompt

---

## Part 5 — GitHub Copilot CLI (10 min)

Use Copilot from the terminal.

### Setup
```bash
gh extension install github/gh-copilot
```

### Your tasks

1. **Explain code:**
   ```bash
   gh copilot explain "What does the checkout_book method in lab01/library.py do?"
   ```

2. **Get command suggestions:**
   ```bash
   gh copilot suggest "run only the tests in lab01 that match 'checkout'"
   ```

3. **Understand a pattern:**
   ```bash
   gh copilot explain "Why is @property used on is_overdue instead of a regular method?"
   ```

4. **Git workflow suggestion:**
   ```bash
   gh copilot suggest "create a new branch called lab01-solution, stage my changes, and commit with a descriptive message"
   ```
   Copilot will give you the exact git commands. Review them before running.

---

## Checkpoint

Run a final verification to confirm everything works:
```bash
pytest tests/ -v
```

By now you should have:
- [ ] Completed all TODO methods using inline completions
- [ ] Generated at least 2 new features via Chat
- [ ] Used all 4 slash commands (`/explain`, `/doc`, `/tests`, `/fix`)
- [ ] Experienced the difference between vague and specific prompts
- [ ] Tried `gh copilot explain` and `suggest`
- [ ] All tests passing ✅

---

## Lab Complete!

- ✅ Inline completions — Tab/Esc/Ctrl+→ for accepting suggestions
- ✅ Chat — longer code generation with context awareness
- ✅ Slash commands — `/explain`, `/doc`, `/tests`, `/fix` for fast workflows
- ✅ Prompt crafting — specific, iterative prompts for better output
- ✅ CLI — `gh copilot explain` and `suggest` for terminal workflows

### What's Next

In **Lab 02**, you'll use these skills to write comprehensive unit tests — the first phase of the SDLC where Copilot acts as your testing partner.
