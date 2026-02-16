---
repo: martymcenroe/AgentOS
issue: 188
url: https://github.com/martymcenroe/AgentOS/issues/188
fetched: 2026-02-04T01:28:44.498274Z
---

# Issue #188: Implementation workflow should enforce file paths from LLD

## Problem

The implementation workflow (TDD) allows Claude to place files in arbitrary locations, ignoring the paths specified in the LLD.

### Evidence from #177

The LLD specified:
```
agentos/utils/lld_verification.py
```

But across 10 iterations, Claude wrote to:
- `agentos/utils/lld_verification.py` (correct)
- `agentos/core/lld_verification.py` (wrong)
- `tests/test_lld_verification.py` (blocked by protection)

This inconsistency caused:
1. Wasted iterations
2. Orphaned files in wrong locations
3. Coverage measurement issues (wrong module path)

## Root Cause

The implementation prompt doesn't enforce file paths from the LLD. It just says "implement the feature" without specifying exact output locations.

## Proposed Fix

In `implement_code.py`, the implementation prompt should include:

```
REQUIRED FILE PATHS (from LLD - do not deviate):
- agentos/utils/lld_verification.py  # Main implementation
- tests/test_issue_177.py  # Tests (already scaffolded, DO NOT MODIFY)

Any files written to other paths will be rejected.
```

## Acceptance Criteria

- [ ] Implementation prompt includes file paths from LLD
- [ ] File path validator rejects writes to non-LLD paths
- [ ] Iteration count decreases for typical implementations