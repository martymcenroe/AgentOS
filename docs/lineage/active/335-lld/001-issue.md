---
repo: martymcenroe/AgentOS
issue: 335
url: https://github.com/martymcenroe/AgentOS/issues/335
fetched: 2026-02-05T14:31:54.918413Z
---

# Issue #335: bug: Scaffold node generates stub tests (assert False) instead of real TDD tests

## Summary

The TDD workflow scaffold node generates placeholder tests with `assert False, 'TDD RED: not implemented'` instead of real tests that call functions and make assertions. This breaks the entire TDD loop.

## Current Behavior

LLD contains test scenario:
```markdown
| T010 | test_normalize_add_directory | "Add (Directory)" → ("add", True) | R010 |
```

Scaffold generates:
```python
def test_t010():
    assert False, 'TDD RED: test_t010 not implemented'
```

## Expected Behavior

Scaffold should generate:
```python
def test_t010_normalize_add_directory():
    """R010: Normalize 'Add (Directory)' to ('add', True)"""
    from agentos.workflows.requirements.nodes.validate_mechanical import normalize_change_type
    
    result = normalize_change_type("Add (Directory)")
    
    assert result == ("add", True)
```

## Why This Matters

- Stub tests **always fail** regardless of implementation quality
- The RED→GREEN loop becomes meaningless
- Workflow iterates forever (observed: 10+ iterations with no progress)
- Coverage stays at ~11% because tests don't exercise any code

## Root Cause

The scaffold node (`agentos/workflows/testing/nodes/scaffold_tests.py`) doesn't parse LLD test scenarios into real test code. It just generates templated stubs.

## Proposed Fix

### 1. Parse LLD Section 11 properly

Extract:
- Test ID (T010)
- Function/method being tested
- Input values
- Expected output

### 2. Generate real tests

Use Claude to generate tests that:
- Import from the target module
- Call the function with test inputs
- Assert expected outputs

### 3. Add mechanical validation (LangGraph node)

After scaffolding, validate tests are real:

```python
def validate_tests_mechanical(test_content: str, lld_scenarios: list) -> list[str]:
    errors = []
    
    # Reject stub pattern
    if re.search(r"assert False.*not implemented", test_content):
        errors.append("Stub tests detected - must have real assertions")
    
    # AST: verify imports, function calls, comparisons
    tree = ast.parse(test_content)
    # ... check each test has real assertions
    
    return errors
```

### 4. LangGraph integration

```
scaffold_tests → validate_tests_mechanical → implement_code
                         ↓
              (reject stubs, regenerate)
```

## Files to Modify

| File | Change |
|------|--------|
| `agentos/workflows/testing/nodes/scaffold_tests.py` | Generate real tests from LLD |
| `agentos/workflows/testing/nodes/validate_tests.py` | NEW: Mechanical test validation |
| `agentos/workflows/testing/graph.py` | Add validation node after scaffold |

## Impact

Without this fix, the implementation workflow cannot produce working code through TDD. Every issue will loop until max iterations.

## Related Issues

- #334 - Blocked by this issue (had to implement manually)