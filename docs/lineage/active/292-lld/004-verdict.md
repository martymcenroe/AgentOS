# LLD Review: 1292 - Feature: Add pytest exit code routing to TDD workflow

## Identity Confirmation
I am Gemini 3 Pro, acting as Senior Software Architect & AI Governance Lead.

## Pre-Flight Gate
PASSED

## Review Summary
The LLD provides a clear strategy for handling pytest exit codes using a dedicated router module. However, there is a critical disconnect between the Safety/Architecture sections (which promise a retry limit) and the Logic Flow/Function Signatures (which are stateless and cannot enforce that limit). This presents a Tier 1 Safety risk of infinite loops. Additionally, requirement coverage falls below the 95% threshold due to missing tests for logging.

## Open Questions Resolved
- [x] ~~Should exit codes be stored in TDD state for debugging?~~ **RESOLVED: Yes - per issue requirements**
- [x] ~~Should there be a maximum retry count for N2 re-scaffold loops (exit codes 4,5)?~~ **RESOLVED: Yes. However, the current logic design (Section 2.5) lacks the implementation for this. It must be added to the `verify_phases` logic using the state history.**
- [x] ~~What constitutes "Human Review" - pause workflow, create issue, or notification?~~ **RESOLVED: Routing to the `HUMAN_REVIEW` node, which pauses the workflow and flags `requires_human: True` in the `RouteDestination`.**

## Requirement Coverage Analysis (MANDATORY)

**Section 3 Requirements:**
| # | Requirement | Test(s) | Status |
|---|-------------|---------|--------|
| 1 | Exit code 1 (tests failed) accepted as valid RED state, routes to N4 | T020 | ✓ Covered |
| 2 | Exit code 4 (usage/syntax error) routes back to N2 (re-scaffold) | T060 | ✓ Covered |
| 3 | Exit code 5 (no tests collected) routes back to N2 (re-scaffold) | T070 | ✓ Covered |
| 4 | Exit codes 2,3 (interrupted/internal error) route to HUMAN_REVIEW | T040, T050 | ✓ Covered |
| 5 | Exit code stored in TDD state for debugging | T080 | ✓ Covered |
| 6 | Exit code history maintained for workflow analysis | T090 | ✓ Covered |
| 7 | All routing decisions logged with reason | - | **GAP** |
| 8 | Backwards compatible with existing phase verification | T110, T120 | ✓ Covered |

**Coverage Calculation:** 7 requirements covered / 8 total = **87.5%**

**Verdict:** **BLOCK** (<95%)

**Missing Test Scenarios:**
- **Scenario for Req 7:** A test utilizing the `caplog` fixture to verify that `route_by_exit_code` or `verify_red_phase` emits a log record with the correct level and message containing the decision reason.

## Tier 1: BLOCKING Issues

### Cost
- [ ] **Infinite Loop Risk (Loop Bounds):** Section 2.7 and Section 11 mention a "Configurable (default 3)" retry limit to prevent infinite re-scaffold loops on exit codes 4 and 5. However, the Logic Flow (Section 2.5) and Function Signatures (Section 2.4) do **not** implement this. `route_by_exit_code` is defined as stateless (inputs: `exit_code`, `phase`), so it cannot count retries.
    - **Recommendation:** Update `verify_red_phase` (which has access to `state`) to check `state.exit_code_history`. If the last 3 exit codes were 4 or 5, override the router's decision and route to `HUMAN_REVIEW`. Update the Pseudocode in 2.5 to reflect this check.

### Safety
- [ ] No additional issues found.

### Security
- [ ] No issues found.

### Legal
- [ ] No issues found.

## Tier 2: HIGH PRIORITY Issues

### Architecture
- [ ] No issues found.

### Observability
- [ ] No issues found.

### Quality
- [ ] **Requirement Coverage:** Coverage is 87.5% due to missing logging tests. Add a test case specifically for Requirement 7.

## Tier 3: SUGGESTIONS
- **Maintainability:** Consider defining the `RouteDestination` TypedDict in a shared types module if it needs to be consumed by the workflow engine, rather than just inside the router module.
- **Resilience:** In `verify_red_phase`, ensure `exit_code` extraction handles cases where the test runner crashes before producing a result (try/except block defaulting to exit code 3).

## Questions for Orchestrator
1. None.

## Verdict
[ ] **APPROVED** - Ready for implementation
[x] **REVISE** - Fix Tier 1/2 issues first
[ ] **DISCUSS** - Needs Orchestrator decision