---
repo: martymcenroe/AgentOS
issue: 292
url: https://github.com/martymcenroe/AgentOS/issues/292
fetched: 2026-02-05T02:38:58.885649Z
---

# Issue #292: feat: Add pytest exit code routing to TDD workflow

## Summary

Add specific pytest exit code handling from the original Issue #87 spec for proper error routing.

## Background

Issue #87 specified routing based on pytest exit codes 0-5. Current implementation only checks pass/fail counts, not specific exit codes.

## Requirements

### Exit Code Routing

| Exit Code | Meaning | Route To |
|-----------|---------|----------|
| 0 | Tests passed | Next phase |
| 1 | Tests failed (assertions) | Valid RED state → N4 |
| 2 | Interrupted | Human Review |
| 3 | Internal error | Human Review |
| 4 | Usage/collection error (syntax) | N2 (re-scaffold) |
| 5 | No tests collected | N2 (re-scaffold) |

### Current Behavior

- Checks `passed_count` and `failed_count` from parsed output
- Treats errors (import errors) same as failures
- No differentiation between exit codes 2,3,4,5

## Implementation

Create `agentos/workflows/testing/exit_code_router.py`:
- `route_by_exit_code(exit_code, phase) -> next_node`
- Update `verify_red_phase()` to use exit codes
- Update `verify_green_phase()` to use exit codes

## Acceptance Criteria

- [ ] Exit code 1 accepted as valid RED state
- [ ] Exit code 4 routes back to scaffold (syntax error)
- [ ] Exit code 5 routes back to scaffold (no tests)
- [ ] Exit codes 2,3 route to human review
- [ ] Exit code stored in state for debugging

## Parent Issue

Extracted from #87 (Implementation Workflow)