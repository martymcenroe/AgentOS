# Test Plan Review Prompt

You are a senior QA engineer reviewing a test plan extracted from a Low-Level Design (LLD) document. Your goal is to ensure the test plan provides adequate coverage and uses real, executable tests.

## Pre-Flight Check

Before reviewing, verify these fundamentals:
- [ ] Test plan section exists and is not empty
- [ ] At least one test scenario is defined
- [ ] Test scenarios have names and descriptions

If any pre-flight check fails, immediately return BLOCKED with the specific issue.

## Review Criteria

### 1. Coverage Analysis (CRITICAL - 100% threshold per ADR 0207)

Calculate coverage by mapping test scenarios to requirements:

```
Coverage = (Requirements with tests / Total requirements) * 100
```

For each requirement, identify:
- Which test(s) cover it
- If no test covers it, flag as a gap

**BLOCKING if:** Coverage < 95%

### 2. Test Reality Check (CRITICAL)

Every test MUST be an executable automated test. Flag any test that:
- Delegates to "manual verification" or "human review"
- Says "verify by inspection" or "visual check"
- Has no clear assertions or expected outcomes
- Is vague like "test that it works"

**BLOCKING if:** Any test is not executable

### 3. No Human Delegation

Tests must NOT require human intervention. Flag any test that:
- Requires someone to "observe" behavior
- Needs "judgment" to determine pass/fail
- Says "ask the user" or "get feedback"

**BLOCKING if:** Any test delegates to humans

### 4. Test Type Appropriateness

Validate that test types match the functionality:
- **Unit tests:** Isolated, mock dependencies, test single functions
- **Integration tests:** Test component interactions, may use real DB
- **E2E tests:** Full user flows, minimal mocking
- **Browser tests:** Require real browser (Playwright/Selenium)
- **CLI tests:** Test command-line interfaces

**WARNING (not blocking) if:** Test types seem mismatched

### 5. Edge Cases

Check for edge case coverage:
- Empty inputs
- Invalid inputs
- Boundary conditions
- Error conditions
- Concurrent access (if applicable)

**WARNING (not blocking) if:** Edge cases seem missing

## Output Format

Provide your verdict in this exact format:

```markdown
## Pre-Flight Gate

- [x] PASSED / [ ] FAILED: Test plan exists
- [x] PASSED / [ ] FAILED: Scenarios defined
- [x] PASSED / [ ] FAILED: Scenarios have names

## Coverage Analysis

| Requirement | Test(s) | Status |
|-------------|---------|--------|
| REQ-1       | test_x  | Covered |
| REQ-2       | -       | GAP |

**Coverage: X/Y requirements (Z%)**

## Test Reality Check

| Test | Issue | Status |
|------|-------|--------|
| test_x | None | OK |
| test_y | "Manual check" | FAIL |

## Human Delegation Check

- [ ] PASSED: No human delegation found
- [ ] FAILED: [list tests that delegate to humans]

## Test Type Review

| Test | Declared Type | Appropriate | Notes |
|------|---------------|-------------|-------|
| test_x | unit | Yes | - |
| test_y | integration | No | Should be unit |

## Edge Cases

- [ ] Empty inputs covered
- [ ] Invalid inputs covered
- [ ] Error conditions covered

## Verdict

[x] **APPROVED** - Test plan is ready for implementation

OR

[x] **BLOCKED** - Test plan needs revision

## Required Changes (if BLOCKED)

1. [Specific, actionable change needed]
2. [Specific, actionable change needed]
```

## Important Notes

- Be strict on coverage (95% threshold)
- Be strict on test reality (no manual tests)
- Provide specific, actionable feedback
- Reference specific tests and requirements by name


---

# Test Plan for Issue #78

## Requirements to Cover

- REQ-1: Running workflow in a git repo creates `.agentos/issue_workflow.db` in repo root
- REQ-2: Running workflow in different repos creates separate, independent databases
- REQ-3: Setting `AGENTOS_WORKFLOW_DB` environment variable overrides per-repo default
- REQ-4: Running workflow outside a git repo (without env var) exits with descriptive error (fail closed)
- REQ-5: Git worktrees get independent `.agentos/` directories in their worktree root
- REQ-6: Existing global database at `~/.agentos/` is not modified or deleted
- REQ-7: `.agentos/` pattern is added to `.gitignore`
- REQ-8: Empty `AGENTOS_WORKFLOW_DB` environment variable is treated as unset
- REQ-9: Tilde expansion works correctly in `AGENTOS_WORKFLOW_DB` paths
- REQ-C: **Simplicity:** Similar components collapsed (per 0006 §8.1)
- REQ-C: **No touching:** All elements have visual separation (per 0006 §8.2)
- REQ-C: **No hidden lines:** All arrows fully visible (per 0006 §8.3)
- REQ-C: **Readable:** Labels not truncated, flow direction clear
- REQ-C: **Auto-inspected:** Agent rendered via mermaid.ink and viewed (per 0006 §8.5)
- REQ-C: No PII stored without consent
- REQ-C: All third-party licenses compatible with project license
- REQ-C: External API usage compliant with provider ToS
- REQ-C: Data retention policy documented
- REQ-C: Implementation complete and linted
- REQ-C: Code comments reference this LLD
- REQ-C: All test scenarios pass (12 automated tests)
- REQ-C: Test coverage meets threshold (≥95% requirement coverage)
- REQ-C: LLD updated with any deviations
- REQ-C: Implementation Report (0103) completed
- REQ-C: Test Report (0113) completed if applicable
- REQ-C: `.gitignore` updated with `.agentos/` pattern
- REQ-C: `docs/workflow.md` updated with new behavior and migration guide
- REQ-C: Code review completed
- REQ-C: User approval before closing issue

## Detected Test Types

- browser
- e2e
- integration
- mobile
- performance
- security
- unit

## Required Tools

- appium
- bandit
- detox
- docker-compose
- locust
- playwright
- pytest
- pytest-benchmark
- safety
- selenium

## Mock Guidance

**Browser/UI Tests:** Real browser required, mock backend APIs for isolation
**End-to-End Tests:** Minimal mocking - test against real (sandboxed) systems
**Integration Tests:** Use test doubles for external services, real DB where possible
**Mobile App Tests:** Use emulators/simulators, mock backend services
**Performance Tests:** Test against representative data volumes
**Security Tests:** Never use real credentials, test edge cases thoroughly
**Unit Tests:** Mock external dependencies (APIs, DB, filesystem)

## Coverage Target

95%

## Test Scenarios

### test_010
- **Type:** unit
- **Requirement:** 
- **Description:** Per-repo database creation | Auto | Run workflow in git repo | `.agentos/issue_workflow.db` created in repo root | File exists at expected path
- **Mock needed:** True
- **Assertions:** 

### test_020
- **Type:** unit
- **Requirement:** 
- **Description:** Different repos get different databases | Auto | Run workflow in repo1, then repo2 | Two separate database files | `repo1/.agentos/issue_workflow.db` != `repo2/.agentos/issue_workflow.db`
- **Mock needed:** True
- **Assertions:** 

### test_030
- **Type:** unit
- **Requirement:** 
- **Description:** Environment variable override | Auto | Set `AGENTOS_WORKFLOW_DB=/tmp/custom.db` | Database at `/tmp/custom.db` | File created at env var path, not in repo
- **Mock needed:** True
- **Assertions:** 

### test_040
- **Type:** unit
- **Requirement:** 
- **Description:** Fail closed outside repo | Auto | Run workflow in non-git directory | Exit code 1, error message | Exit code 1; stderr contains "AGENTOS_WORKFLOW_DB"
- **Mock needed:** False
- **Assertions:** 

### test_050
- **Type:** unit
- **Requirement:** 
- **Description:** Worktree isolation | Auto | Create worktree, run workflow | Worktree gets own `.agentos/` | `worktree/.agentos/issue_workflow.db` exists
- **Mock needed:** False
- **Assertions:** 

### test_060
- **Type:** unit
- **Requirement:** 
- **Description:** Global database untouched | Auto | Run workflow in repo | `~/.agentos/issue_workflow.db` unchanged | Global DB not modified (timestamp unchanged)
- **Mock needed:** True
- **Assertions:** 

### test_070
- **Type:** unit
- **Requirement:** 
- **Description:** Nested repo detection (deep subdirectory) | Auto | Run in `repo/src/lib/` subdirectory | Database in repo root, not subdirectory | `repo_root/.agentos/` not `repo_root/src/lib/.agentos/`
- **Mock needed:** True
- **Assertions:** 

### test_080
- **Type:** unit
- **Requirement:** 
- **Description:** .agentos directory creation | Auto | Run in repo without .agentos | Directory created with proper permissions | Directory exists with user read/write
- **Mock needed:** False
- **Assertions:** 

### test_090
- **Type:** unit
- **Requirement:** 
- **Description:** Env var with ~ expansion | Auto | Set `AGENTOS_WORKFLOW_DB=~/custom.db` | Path expanded correctly | File at `$HOME/custom.db`
- **Mock needed:** False
- **Assertions:** 

### test_100
- **Type:** unit
- **Requirement:** 
- **Description:** Empty env var treated as unset | Auto | Set `AGENTOS_WORKFLOW_DB=""` | Falls back to per-repo | Uses repo path, not empty string
- **Mock needed:** False
- **Assertions:** 

### test_110
- **Type:** unit
- **Requirement:** 
- **Description:** .gitignore contains .agentos/ pattern | Auto | Check `.gitignore` after workflow run | `.agentos/` entry exists | Parse `.gitignore`, assert pattern present
- **Mock needed:** False
- **Assertions:** 

### test_120
- **Type:** unit
- **Requirement:** 
- **Description:** Concurrent execution (3 repos) | Auto | Spawn 3 subprocess workflows in parallel | Each repo has independent database, no errors | All 3 processes exit 0; 3 distinct `.agentos/issue_workflow.db` files
- **Mock needed:** True
- **Assertions:** 

## Original Test Plan Section

*Ref: [0005-testing-strategy-and-protocols.md](0005-testing-strategy-and-protocols.md)*

**Testing Philosophy:** All scenarios are fully automated using temporary directories, subprocess spawning, and environment variable manipulation. No manual tests required.

### 10.1 Test Scenarios

| ID | Scenario | Type | Input | Expected Output | Pass Criteria |
|----|----------|------|-------|-----------------|---------------|
| 010 | Per-repo database creation | Auto | Run workflow in git repo | `.agentos/issue_workflow.db` created in repo root | File exists at expected path |
| 020 | Different repos get different databases | Auto | Run workflow in repo1, then repo2 | Two separate database files | `repo1/.agentos/issue_workflow.db` != `repo2/.agentos/issue_workflow.db` |
| 030 | Environment variable override | Auto | Set `AGENTOS_WORKFLOW_DB=/tmp/custom.db` | Database at `/tmp/custom.db` | File created at env var path, not in repo |
| 040 | Fail closed outside repo | Auto | Run workflow in non-git directory | Exit code 1, error message | Exit code 1; stderr contains "AGENTOS_WORKFLOW_DB" |
| 050 | Worktree isolation | Auto | Create worktree, run workflow | Worktree gets own `.agentos/` | `worktree/.agentos/issue_workflow.db` exists |
| 060 | Global database untouched | Auto | Run workflow in repo | `~/.agentos/issue_workflow.db` unchanged | Global DB not modified (timestamp unchanged) |
| 070 | Nested repo detection (deep subdirectory) | Auto | Run in `repo/src/lib/` subdirectory | Database in repo root, not subdirectory | `repo_root/.agentos/` not `repo_root/src/lib/.agentos/` |
| 080 | .agentos directory creation | Auto | Run in repo without .agentos | Directory created with proper permissions | Directory exists with user read/write |
| 090 | Env var with ~ expansion | Auto | Set `AGENTOS_WORKFLOW_DB=~/custom.db` | Path expanded correctly | File at `$HOME/custom.db` |
| 100 | Empty env var treated as unset | Auto | Set `AGENTOS_WORKFLOW_DB=""` | Falls back to per-repo | Uses repo path, not empty string |
| 110 | .gitignore contains .agentos/ pattern | Auto | Check `.gitignore` after workflow run | `.agentos/` entry exists | Parse `.gitignore`, assert pattern present |
| 120 | Concurrent execution (3 repos) | Auto | Spawn 3 subprocess workflows in parallel | Each repo has independent database, no errors | All 3 processes exit 0; 3 distinct `.agentos/issue_workflow.db` files exist |

### 10.2 Test Commands

```bash
# Run all automated tests
poetry run pytest tests/test_checkpoint.py -v

# Run only fast/mocked tests (exclude live)
poetry run pytest tests/test_checkpoint.py -v -m "not live"

# Run specific test scenarios
poetry run pytest tests/test_checkpoint.py::test_per_repo_database_creation -v
poetry run pytest tests/test_checkpoint.py::test_fail_closed_outside_repo -v
poetry run pytest tests/test_checkpoint.py::test_concurrent_execution -v
poetry run pytest tests/test_checkpoint.py::test_gitignore_contains_agentos_pattern -v
```

### 10.3 Manual Tests (Only If Unavoidable)

N/A - All scenarios automated.

*Full test results recorded in Implementation Report (0103) or Test Report (0113).*
