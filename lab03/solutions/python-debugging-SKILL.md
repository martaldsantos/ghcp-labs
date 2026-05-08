---
description: >
  Use this skill when debugging Python code, analyzing test failures,
  or troubleshooting runtime errors. Provides patterns for common bugs
  and strategies for systematic debugging.
---

# Python Debugging Skill

## Common Bug Patterns

### Operator Errors
- **Wrong assignment:** `x = value` instead of `x += value` (replaces instead of accumulates)
- **Integer division:** `a * b // 1` truncates decimals — use `a * b` or `round(a * b, 2)`
- **Flipped comparison:** `>` instead of `<` (or vice versa) in filters and conditionals
- **Wrong arithmetic:** `a + b` instead of `a * b` (addition vs multiplication)

### Calculation Errors
- **Percentage math:** dividing by 10 instead of 100 (`pct / 10` → `pct / 100`)
- **Missing operand:** `total += price` instead of `total += price * quantity`
- **Rounding issues:** floating-point comparisons — use `pytest.approx()` or `math.isclose()`

### Type Mismatches
- **String vs datetime:** comparing ISO format strings with `datetime` objects — convert with `.isoformat()` or `datetime.fromisoformat()`
- **String vs int:** forgetting `int()` conversion on user input or config values
- **None checks:** using `if x` instead of `if x is not None` (fails for 0, empty string)

## Reading Pytest Tracebacks

1. **Start from the bottom** — the last line shows the assertion that failed
2. **Read the comparison** — `assert 10 == 60` tells you the actual vs expected values
3. **Check the line above** — the source line shows which variable/expression is wrong
4. **Trace backwards** — follow the variable to where it was assigned to find the bug

## Debugging Strategies

1. **Read the error first** — don't guess, let the traceback guide you
2. **Reproduce minimally** — write the smallest test that triggers the bug
3. **Binary search** — if you can't find the bug, comment out half the code and narrow down
4. **Check types** — use `type()` or `isinstance()` to verify assumptions
5. **Print intermediate values** — add `print(f"{var=}")` at key points (Python 3.8+ f-string debugging)
6. **Compare with known-good** — if a solution exists, diff against it to isolate differences

## Pytest Tips

- `pytest -v` — verbose output shows each test name and result
- `pytest -x` — stop on first failure (useful for fixing one bug at a time)
- `pytest --tb=short` — shorter tracebacks for quick scanning
- `pytest -k "test_name"` — run only matching tests
- `pytest.approx(expected)` — compare floats with tolerance
