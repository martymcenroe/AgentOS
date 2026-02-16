# 1292 - Feature: Add pytest exit code routing to TDD workflow

<!-- Template Metadata
Last Updated: 2026-02-02
Updated By: Issue #292 creation
Update Reason: Initial LLD for pytest exit code routing feature
-->

## 1. Context & Goal
* **Issue:** #292
* **Objective:** Add specific pytest exit code handling for proper error routing in the TDD workflow, enabling differentiated responses to test failures vs. syntax errors vs. collection errors.
* **Status:** Draft
* **Related Issues:** #87 (Parent - Implementation Workflow)

### Open Questions
*Questions that need clarification before or during implementation. Remove when resolved.*

- [x] Should exit codes be stored in TDD state for debugging? **Yes - per issue requirements**
- [ ] Should there be a maximum retry count for N2 re-scaffold loops (exit codes 4,5)?
- [ ] What constitutes "Human Review" - pause workflow, create issue, or notification?

## 2. Proposed Changes

*This section is the **source of truth** for implementation. Describe exactly what will be built.*

### 2.1 Files Changed

| File | Change Type | Description |
|------|-------------|-------------|
| `agentos/workflows/testing/exit_code_router.py` | Add | New module for pytest exit code routing logic |
| `agentos/workflows/testing/tdd_state.py` | Modify | Add exit_code field to TDD state |
| `agentos/workflows/testing/verify_phases.py` | Modify | Update verify_red_phase() and verify_green_phase() to use exit codes |
| `tests/unit/test_exit_code_router.py` | Add | Unit tests for exit code router |
| `tests/unit/test_verify_phases_exit_codes.py` | Add | Integration tests for phase verification with exit codes |

### 2.1.1 Path Validation (Mechanical - Auto-Checked)

*Issue #277: Before human or Gemini review, paths are verified programmatically.*

Mechanical validation automatically checks:
- All "Modify" files must exist in repository
- All "Delete" files must exist in repository
- All "Add" files must have existing parent directories
- No placeholder prefixes (`src/`, `lib/`, `app/`) unless directory exists

**If validation fails, the LLD is BLOCKED before reaching review.**

### 2.2 Dependencies

*No new dependencies required.*

```toml
# pyproject.toml additions (if any)
# None - uses existing pytest and standard library
```

### 2.3 Data Structures

```python
# Pseudocode - NOT implementation
from enum import IntEnum
from typing import TypedDict, Literal

class PytestExitCode(IntEnum):
    """Pytest exit codes per pytest documentation."""
    TESTS_PASSED = 0
    TESTS_FAILED = 1
    INTERRUPTED = 2
    INTERNAL_ERROR = 3
    USAGE_ERROR = 4
    NO_TESTS_COLLECTED = 5

class RouteDestination(TypedDict):
    """Routing result for exit code handling."""
    next_node: str  # Node identifier (e.g., "N2", "N4", "HUMAN_REVIEW")
    reason: str  # Human-readable explanation
    requires_human: bool  # Whether human intervention is needed
    retry_allowed: bool  # Whether automatic retry is permitted

class TDDPhase(Literal["RED", "GREEN", "REFACTOR"]):
    """Current phase in TDD cycle."""
    pass

# Extension to existing TDDState
class TDDStateExtension(TypedDict):
    exit_code: int | None  # Last pytest exit code
    exit_code_history: list[int]  # History for debugging
    route_history: list[str]  # History of routing decisions
```

### 2.4 Function Signatures

```python
# Signatures only - implementation in source files

# agentos/workflows/testing/exit_code_router.py
def route_by_exit_code(exit_code: int, phase: str) -> RouteDestination:
    """
    Route to appropriate next node based on pytest exit code and current phase.
    
    Args:
        exit_code: Pytest exit code (0-5)
        phase: Current TDD phase ("RED", "GREEN", "REFACTOR")
    
    Returns:
        RouteDestination with next_node, reason, and flags
    """
    ...

def is_valid_red_state(exit_code: int) -> bool:
    """Check if exit code represents a valid RED state (tests failing as expected)."""
    ...

def is_scaffold_error(exit_code: int) -> bool:
    """Check if exit code indicates a scaffold/syntax error requiring re-scaffold."""
    ...

def requires_human_review(exit_code: int) -> bool:
    """Check if exit code requires human intervention."""
    ...

def get_exit_code_description(exit_code: int) -> str:
    """Get human-readable description for exit code."""
    ...

# agentos/workflows/testing/verify_phases.py (modifications)
def verify_red_phase(test_result: dict, state: dict) -> RouteDestination:
    """
    Verify RED phase using exit code routing.
    
    Updated to use exit_code from test_result instead of just pass/fail counts.
    """
    ...

def verify_green_phase(test_result: dict, state: dict) -> RouteDestination:
    """
    Verify GREEN phase using exit code routing.
    
    Updated to use exit_code from test_result instead of just pass/fail counts.
    """
    ...
```

### 2.5 Logic Flow (Pseudocode)

```
route_by_exit_code(exit_code, phase):
1. Validate exit_code is in range 0-5
2. IF exit_code == 0 (TESTS_PASSED):
   - IF phase == "RED":
     - Return error: tests should fail in RED phase
   - ELSE:
     - Return next_node: next phase
3. IF exit_code == 1 (TESTS_FAILED):
   - IF phase == "RED":
     - Return next_node: "N4" (valid RED state)
   - ELSE IF phase == "GREEN":
     - Return next_node: "N3" (back to implementation)
4. IF exit_code == 2 (INTERRUPTED):
   - Return next_node: "HUMAN_REVIEW"
   - Set requires_human: True
5. IF exit_code == 3 (INTERNAL_ERROR):
   - Return next_node: "HUMAN_REVIEW"
   - Set requires_human: True
6. IF exit_code == 4 (USAGE_ERROR - syntax):
   - Return next_node: "N2" (re-scaffold)
   - Set retry_allowed: True
7. IF exit_code == 5 (NO_TESTS_COLLECTED):
   - Return next_node: "N2" (re-scaffold)
   - Set retry_allowed: True
8. ELSE (unknown exit code):
   - Return next_node: "HUMAN_REVIEW"
   - Set requires_human: True

verify_red_phase(test_result, state):
1. Extract exit_code from test_result
2. Store exit_code in state for debugging
3. Append to exit_code_history
4. Call route_by_exit_code(exit_code, "RED")
5. Log routing decision
6. Return RouteDestination
```

### 2.6 Technical Approach

* **Module:** `agentos/workflows/testing/exit_code_router.py`
* **Pattern:** Strategy pattern for exit code routing
* **Key Decisions:** 
  - Exit codes are treated as authoritative over parsed pass/fail counts
  - Exit code history maintained for debugging workflow issues
  - Clear separation between "retry-able" errors (4,5) and "human required" errors (2,3)

### 2.7 Architecture Decisions

*Document key architectural decisions that affect the design.*

| Decision | Options Considered | Choice | Rationale |
|----------|-------------------|--------|-----------|
| Exit code vs. parsed output priority | Exit code only, Parsed output only, Hybrid | Exit code primary | Exit codes are pytest's contract; parsed output can miss edge cases |
| State storage for exit codes | Single value, History list, Both | Both | Single for current state, history for debugging failed workflows |
| Human review handling | Exception, Special return value, Flag in return | Flag in RouteDestination | Keeps control flow explicit without exception overhead |
| Re-scaffold retry limit | Unlimited, Fixed limit, Configurable | Configurable (default 3) | Prevents infinite loops while allowing customization |

**Architectural Constraints:**
- Must integrate with existing TDD workflow state management
- Cannot change pytest execution - only interpret results
- Must be backwards compatible with existing verify_phases.py consumers

## 3. Requirements

*What must be true when this is done. These become acceptance criteria.*

1. Exit code 1 (tests failed) accepted as valid RED state, routes to N4
2. Exit code 4 (usage/syntax error) routes back to N2 (re-scaffold)
3. Exit code 5 (no tests collected) routes back to N2 (re-scaffold)
4. Exit codes 2,3 (interrupted/internal error) route to HUMAN_REVIEW
5. Exit code stored in TDD state for debugging
6. Exit code history maintained for workflow analysis
7. All routing decisions logged with reason
8. Backwards compatible with existing phase verification

## 4. Alternatives Considered

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Parse pytest output for error type | Rich error information | Fragile to format changes, incomplete coverage | **Rejected** |
| Use exit codes only | Clean contract, official pytest API | Less detail in some cases | **Selected** |
| Hybrid approach (exit code + parsing) | Best of both worlds | Complexity, potential conflicts | Rejected |
| Add custom pytest plugin | Full control | Deployment complexity, maintenance burden | Rejected |

**Rationale:** Exit codes are pytest's official interface contract. They are stable, well-documented, and cover all the routing scenarios needed. Parsing stdout is fragile and may miss edge cases that exit codes capture.

## 5. Data & Fixtures

*Per [0108-lld-pre-implementation-review.md](0108-lld-pre-implementation-review.md) - complete this section BEFORE implementation.*

### 5.1 Data Sources

| Attribute | Value |
|-----------|-------|
| Source | pytest execution return code |
| Format | Integer (0-5) |
| Size | Single integer per test run |
| Refresh | Per test execution |
| Copyright/License | N/A - pytest is MIT licensed |

### 5.2 Data Pipeline

```
pytest execution ──return code──► exit_code_router ──RouteDestination──► TDD workflow
                                        │
                                        ▼
                                   TDD state (exit_code, exit_code_history)
```

### 5.3 Test Fixtures

| Fixture | Source | Notes |
|---------|--------|-------|
| Mock pytest results with each exit code | Generated | Hardcoded exit codes 0-5 plus edge cases |
| TDD state fixture | Generated | Minimal state for testing routing |
| Phase context fixtures | Generated | RED, GREEN, REFACTOR phase contexts |

### 5.4 Deployment Pipeline

No external data - exit codes come from local pytest execution.

**If data source is external:** N/A - all data is from local pytest process.

## 6. Diagram

### 6.1 Mermaid Quality Gate

Before finalizing any diagram, verify in [Mermaid Live Editor](https://mermaid.live) or GitHub preview:

- [x] **Simplicity:** Similar components collapsed (per 0006 §8.1)
- [x] **No touching:** All elements have visual separation (per 0006 §8.2)
- [x] **No hidden lines:** All arrows fully visible (per 0006 §8.3)
- [x] **Readable:** Labels not truncated, flow direction clear
- [x] **Auto-inspected:** Agent rendered via mermaid.ink and viewed (per 0006 §8.5)

**Agent Auto-Inspection (MANDATORY):**

**Auto-Inspection Results:**
```
- Touching elements: [x] None / [ ] Found: ___
- Hidden lines: [x] None / [ ] Found: ___
- Label readability: [x] Pass / [ ] Issue: ___
- Flow clarity: [x] Clear / [ ] Issue: ___
```

*Reference: [0006-mermaid-diagrams.md](0006-mermaid-diagrams.md)*

### 6.2 Diagram

```mermaid
flowchart TD
    subgraph pytest_execution["Pytest Execution"]
        RUN[Run pytest]
        EXIT[Exit Code]
    end
    
    subgraph exit_code_router["Exit Code Router"]
        ROUTE{route_by_exit_code}
        
        EC0[Exit 0: Passed]
        EC1[Exit 1: Failed]
        EC2[Exit 2: Interrupted]
        EC3[Exit 3: Internal Error]
        EC4[Exit 4: Usage Error]
        EC5[Exit 5: No Tests]
    end
    
    subgraph destinations["Route Destinations"]
        NEXT[Next Phase]
        N4[N4: Valid RED]
        N2[N2: Re-scaffold]
        HR[Human Review]
    end
    
    subgraph state_mgmt["State Management"]
        STATE[(TDD State)]
    end
    
    RUN --> EXIT
    EXIT --> ROUTE
    
    ROUTE --> EC0 --> NEXT
    ROUTE --> EC1 --> N4
    ROUTE --> EC2 --> HR
    ROUTE --> EC3 --> HR
    ROUTE --> EC4 --> N2
    ROUTE --> EC5 --> N2
    
    EXIT -.->|store| STATE
```

## 7. Security & Safety Considerations

### 7.1 Security

| Concern | Mitigation | Status |
|---------|------------|--------|
| Exit code spoofing | Exit codes come from subprocess we control | Addressed |
| Invalid exit code injection | Validate exit code is in range 0-5, default to HUMAN_REVIEW | Addressed |

### 7.2 Safety

| Concern | Mitigation | Status |
|---------|------------|--------|
| Infinite re-scaffold loop (exit 4/5) | Configurable retry limit (default 3) | Addressed |
| Lost context on human review | Full state preserved including exit code history | Addressed |
| Silent failures | All routing decisions logged with reason | Addressed |

**Fail Mode:** Fail Closed - Unknown exit codes route to HUMAN_REVIEW

**Recovery Strategy:** Exit code history in state allows debugging; human review can manually override routing

## 8. Performance & Cost Considerations

### 8.1 Performance

| Metric | Budget | Approach |
|--------|--------|----------|
| Routing latency | < 1ms | Simple integer comparison, no I/O |
| Memory | < 1KB per decision | Small TypedDict, bounded history |
| State growth | Bounded | History capped at 100 entries |

**Bottlenecks:** None - this is a simple routing decision, not a performance-critical path

### 8.2 Cost Analysis

| Resource | Unit Cost | Estimated Usage | Monthly Cost |
|----------|-----------|-----------------|--------------|
| Compute | N/A | Negligible | $0 |

**Cost Controls:**
- N/A - No external API calls or significant compute

**Worst-Case Scenario:** N/A - bounded memory, O(1) operations

## 9. Legal & Compliance

| Concern | Applies? | Mitigation |
|---------|----------|------------|
| PII/Personal Data | No | Exit codes contain no personal data |
| Third-Party Licenses | No | pytest is MIT licensed, compatible |
| Terms of Service | N/A | No external services |
| Data Retention | N/A | Ephemeral workflow state |
| Export Controls | No | Simple integer routing logic |

**Data Classification:** Internal

**Compliance Checklist:**
- [x] No PII stored without consent
- [x] All third-party licenses compatible with project license
- [x] External API usage compliant with provider ToS
- [x] Data retention policy documented

## 10. Verification & Testing

*Ref: [0005-testing-strategy-and-protocols.md](0005-testing-strategy-and-protocols.md)*

**Testing Philosophy:** 100% automated test coverage. All scenarios can be tested with mocked exit codes.

### 10.0 Test Plan (TDD - Complete Before Implementation)

**TDD Requirement:** Tests MUST be written and failing BEFORE implementation begins.

| Test ID | Test Description | Expected Behavior | Status |
|---------|------------------|-------------------|--------|
| T010 | test_route_exit_code_0_in_green_phase | Returns next phase | RED |
| T020 | test_route_exit_code_1_in_red_phase | Returns N4 (valid RED) | RED |
| T030 | test_route_exit_code_1_in_green_phase | Returns N3 (back to impl) | RED |
| T040 | test_route_exit_code_2_requires_human | Returns HUMAN_REVIEW | RED |
| T050 | test_route_exit_code_3_requires_human | Returns HUMAN_REVIEW | RED |
| T060 | test_route_exit_code_4_returns_n2 | Returns N2 (re-scaffold) | RED |
| T070 | test_route_exit_code_5_returns_n2 | Returns N2 (re-scaffold) | RED |
| T080 | test_exit_code_stored_in_state | State contains exit_code | RED |
| T090 | test_exit_code_history_maintained | History appended correctly | RED |
| T100 | test_unknown_exit_code_human_review | Exit code 99 → HUMAN_REVIEW | RED |

**Coverage Target:** ≥95% for all new code

**TDD Checklist:**
- [ ] All tests written before implementation
- [ ] Tests currently RED (failing)
- [ ] Test IDs match scenario IDs in 10.1
- [ ] Test file created at: `tests/unit/test_exit_code_router.py`

### 10.1 Test Scenarios

| ID | Scenario | Type | Input | Expected Output | Pass Criteria |
|----|----------|------|-------|-----------------|---------------|
| 010 | Exit 0 in GREEN phase | Auto | exit_code=0, phase="GREEN" | next_node="NEXT_PHASE" | Correct routing |
| 020 | Exit 1 in RED phase (valid RED) | Auto | exit_code=1, phase="RED" | next_node="N4" | Returns N4 |
| 030 | Exit 1 in GREEN phase | Auto | exit_code=1, phase="GREEN" | next_node="N3" | Returns N3 |
| 040 | Exit 2 (interrupted) | Auto | exit_code=2, any phase | requires_human=True | Human review required |
| 050 | Exit 3 (internal error) | Auto | exit_code=3, any phase | requires_human=True | Human review required |
| 060 | Exit 4 (usage error) | Auto | exit_code=4, any phase | next_node="N2" | Re-scaffold |
| 070 | Exit 5 (no tests) | Auto | exit_code=5, any phase | next_node="N2" | Re-scaffold |
| 080 | Exit code stored in state | Auto | exit_code=1 | state.exit_code=1 | State updated |
| 090 | History maintained | Auto | Multiple calls | History contains all | History grows |
| 100 | Unknown exit code | Auto | exit_code=99 | requires_human=True | Safe default |
| 110 | verify_red_phase integration | Auto | test_result with exit_code=1 | RouteDestination | Integration works |
| 120 | verify_green_phase integration | Auto | test_result with exit_code=0 | RouteDestination | Integration works |

### 10.2 Test Commands

```bash
# Run all automated tests
poetry run pytest tests/unit/test_exit_code_router.py tests/unit/test_verify_phases_exit_codes.py -v

# Run only fast/mocked tests (exclude live)
poetry run pytest tests/unit/test_exit_code_router.py -v -m "not live"

# Run with coverage
poetry run pytest tests/unit/test_exit_code_router.py --cov=agentos/workflows/testing/exit_code_router --cov-report=term-missing
```

### 10.3 Manual Tests (Only If Unavoidable)

**N/A - All scenarios automated.** Exit codes can be fully mocked without external dependencies.

## 11. Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| pytest changes exit code semantics | Med | Low | Exit codes are stable; documented since pytest 5.0 |
| Infinite re-scaffold loop | Med | Med | Retry limit (default 3) with human escalation |
| State corruption on crash | Low | Low | Exit code history enables debugging |
| Backwards incompatibility | High | Low | Verify phases still accept original call signature |

## 12. Definition of Done

### Code
- [ ] Implementation complete and linted
- [ ] Code comments reference this LLD (#292)

### Tests
- [ ] All test scenarios pass
- [ ] Test coverage ≥95% for new code

### Documentation
- [ ] LLD updated with any deviations
- [ ] Implementation Report (0103) completed
- [ ] Test Report (0113) completed if applicable

### Review
- [ ] Code review completed
- [ ] User approval before closing issue

### 12.1 Traceability (Mechanical - Auto-Checked)

*Issue #277: Cross-references are verified programmatically.*

Mechanical validation automatically checks:
- Every file mentioned in this section must appear in Section 2.1
- Every risk mitigation in Section 11 should have a corresponding function in Section 2.4 (warning if not)

**If files are missing from Section 2.1, the LLD is BLOCKED.**

---

## Appendix: Review Log

*Track all review feedback with timestamps and implementation status.*

### Review Summary

| Review | Date | Verdict | Key Issue |
|--------|------|---------|-----------|
| - | - | - | Awaiting initial review |

**Final Status:** PENDING