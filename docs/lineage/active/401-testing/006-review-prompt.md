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

# Test Plan for Issue #401

## Requirements to Cover

- REQ-1: Requirements workflow reads key project files (CLAUDE.md, README.md, pyproject.toml/package.json) before drafting the LLD
- REQ-2: Existing code patterns (naming, state management, frameworks, test conventions) are detected and injected into the drafter prompt
- REQ-3: Files related to the issue topic are identified and their excerpts included in context
- REQ-4: LLDs generated for unfamiliar projects reference real file paths and real patterns from the target codebase
- REQ-5: The analysis works cross-repo — when `--repo` points to an external project, that project's files are read
- REQ-6: Token budget prevents context from exceeding reasonable limits (default 15,000 tokens total)
- REQ-7: Graceful degradation: if key files are missing, the workflow proceeds with whatever context is available (never crashes)
- REQ-8: The `analyze_codebase` node produces a `codebase_context` state key consumable by the drafter node
- REQ-9: Sensitive files (.env, .secrets, .key, .pem, credentials) are never read

## Detected Test Types

- browser
- e2e
- integration
- mobile
- performance
- security
- terminal
- unit

## Required Tools

- appium
- bandit
- click.testing
- detox
- docker-compose
- locust
- pexpect
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
**Terminal/CLI Tests:** Use CliRunner or capture stdout/stderr
**Unit Tests:** Mock external dependencies (APIs, DB, filesystem)

## Coverage Target

95%

## Test Scenarios

### test_id
- **Type:** unit
- **Requirement:** 
- **Description:** Test Description | Expected Behavior | Status
- **Mock needed:** False
- **Assertions:** 

### test_t010
- **Type:** unit
- **Requirement:** 
- **Description:** `test_read_file_with_budget_normal` | Reads file content within budget, `truncated=False` | RED
- **Mock needed:** False
- **Assertions:** 

### test_t020
- **Type:** unit
- **Requirement:** 
- **Description:** `test_read_file_with_budget_truncated` | Truncates large file, `truncated=True` | RED
- **Mock needed:** False
- **Assertions:** 

### test_t030
- **Type:** unit
- **Requirement:** 
- **Description:** `test_read_file_with_budget_binary_skip` | Returns empty content for binary files | RED
- **Mock needed:** False
- **Assertions:** 

### test_t040
- **Type:** unit
- **Requirement:** 
- **Description:** `test_read_file_with_budget_missing_file` | Returns empty content, no crash | RED
- **Mock needed:** False
- **Assertions:** 

### test_t050
- **Type:** unit
- **Requirement:** 
- **Description:** `test_read_files_within_budget_respects_total` | Stops reading when total budget exhausted | RED
- **Mock needed:** False
- **Assertions:** 

### test_t055
- **Type:** unit
- **Requirement:** 
- **Description:** `test_read_files_within_budget_respects_per_file` | Individual file capped at per_file_budget | RED
- **Mock needed:** False
- **Assertions:** 

### test_t060
- **Type:** unit
- **Requirement:** 
- **Description:** `test_parse_project_metadata_pyproject` | Extracts name, deps from pyproject.toml | RED
- **Mock needed:** False
- **Assertions:** 

### test_t070
- **Type:** unit
- **Requirement:** 
- **Description:** `test_parse_project_metadata_package_json` | Extracts name, deps from package.json | RED
- **Mock needed:** False
- **Assertions:** 

### test_t080
- **Type:** unit
- **Requirement:** 
- **Description:** `test_parse_project_metadata_missing` | Returns empty dict when no config found | RED
- **Mock needed:** False
- **Assertions:** 

### test_t090
- **Type:** unit
- **Requirement:** 
- **Description:** `test_scan_patterns_detects_naming` | Identifies snake_case module naming | RED
- **Mock needed:** False
- **Assertions:** 

### test_t100
- **Type:** unit
- **Requirement:** 
- **Description:** `test_scan_patterns_detects_typeddict` | Finds TypedDict state pattern | RED
- **Mock needed:** False
- **Assertions:** 

### test_t105
- **Type:** unit
- **Requirement:** 
- **Description:** `test_scan_patterns_unknown_defaults` | Returns "unknown" for undetectable fields | RED
- **Mock needed:** False
- **Assertions:** 

### test_t110
- **Type:** unit
- **Requirement:** 
- **Description:** `test_detect_frameworks_from_deps` | Identifies LangGraph, pytest from dependency list | RED
- **Mock needed:** False
- **Assertions:** 

### test_t115
- **Type:** unit
- **Requirement:** 
- **Description:** `test_detect_frameworks_from_imports` | Detects frameworks from import statements in file contents | RED
- **Mock needed:** False
- **Assertions:** 

### test_t120
- **Type:** unit
- **Requirement:** 
- **Description:** `test_extract_conventions_from_claude_md` | Extracts bullet-point conventions from CLAUDE.md | RED
- **Mock needed:** False
- **Assertions:** 

### test_t130
- **Type:** unit
- **Requirement:** 
- **Description:** `test_extract_conventions_empty` | Returns empty list for CLAUDE.md without conventions | RED
- **Mock needed:** False
- **Assertions:** 

### test_t140
- **Type:** unit
- **Requirement:** 
- **Description:** `test_analyze_codebase_happy_path` | Produces full CodebaseContext from mock repo | RED
- **Mock needed:** True
- **Assertions:** 

### test_t145
- **Type:** unit
- **Requirement:** 
- **Description:** `test_analyze_codebase_context_has_real_paths` | Generated context references real file paths and patterns from target codebase | RED
- **Mock needed:** False
- **Assertions:** 

### test_t150
- **Type:** unit
- **Requirement:** 
- **Description:** `test_analyze_codebase_no_repo_path` | Returns empty context, logs warning | RED
- **Mock needed:** False
- **Assertions:** 

### test_t160
- **Type:** unit
- **Requirement:** 
- **Description:** `test_analyze_codebase_missing_repo` | Returns empty context when repo_path doesn't exist | RED
- **Mock needed:** False
- **Assertions:** 

### test_t170
- **Type:** unit
- **Requirement:** 
- **Description:** `test_find_related_files_keyword_match` | Finds auth.py when issue mentions "authentication" | RED
- **Mock needed:** False
- **Assertions:** 

### test_t180
- **Type:** unit
- **Requirement:** 
- **Description:** `test_find_related_files_no_match` | Returns empty list for unrelated issue text | RED
- **Mock needed:** False
- **Assertions:** 

### test_t185
- **Type:** unit
- **Requirement:** 
- **Description:** `test_find_related_files_max_five` | Returns at most 5 results even with many matches | RED
- **Mock needed:** False
- **Assertions:** 

### test_t190
- **Type:** unit
- **Requirement:** 
- **Description:** `test_analyze_codebase_produces_state_key` | Node returns dict with `codebase_context` key matching CodebaseContext shape | RED
- **Mock needed:** False
- **Assertions:** 

### test_t200
- **Type:** unit
- **Requirement:** 
- **Description:** `test_sensitive_file_not_read_env` | `.env` file content never appears in any read result | RED
- **Mock needed:** False
- **Assertions:** 

### test_t205
- **Type:** unit
- **Requirement:** 
- **Description:** `test_sensitive_file_not_read_pem` | `.pem` file content never appears in any read result | RED
- **Mock needed:** False
- **Assertions:** 

### test_t210
- **Type:** unit
- **Requirement:** 
- **Description:** `test_select_key_files_priority_order` | CLAUDE.md before README.md before pyproject.toml | RED
- **Mock needed:** False
- **Assertions:** 

### test_t220
- **Type:** unit
- **Requirement:** 
- **Description:** `test_sensitive_file_exclusion` | .env, .secrets files are not read | RED
- **Mock needed:** False
- **Assertions:** 

### test_t225
- **Type:** unit
- **Requirement:** 
- **Description:** `test_is_sensitive_file` | Correctly identifies sensitive file patterns | RED
- **Mock needed:** False
- **Assertions:** 

### test_t230
- **Type:** unit
- **Requirement:** 
- **Description:** `test_symlink_outside_repo_blocked` | Symlink pointing outside repo is not read | RED
- **Mock needed:** False
- **Assertions:** 

### test_010
- **Type:** unit
- **Requirement:** 
- **Description:** Read file within budget (REQ-1) | Auto | Small text file, budget=2000 | Full content, truncated=False | Content matches file, token_estimate < 2000
- **Mock needed:** False
- **Assertions:** 

### test_020
- **Type:** unit
- **Requirement:** 
- **Description:** Read file exceeding budget (REQ-6) | Auto | 10KB file, budget=500 | Partial content, truncated=True | Content length ≈ 500×4 chars, truncated=True
- **Mock needed:** False
- **Assertions:** 

### test_030
- **Type:** unit
- **Requirement:** 
- **Description:** Read binary file gracefully (REQ-7) | Auto | PNG file path | Empty content, no exception | Returns FileReadResult with empty content
- **Mock needed:** False
- **Assertions:** 

### test_040
- **Type:** unit
- **Requirement:** 
- **Description:** Read missing file gracefully (REQ-7) | Auto | Non-existent path | Empty content, no exception | Returns FileReadResult with empty content
- **Mock needed:** False
- **Assertions:** 

### test_050
- **Type:** unit
- **Requirement:** 
- **Description:** Total budget enforcement (REQ-6) | Auto | 10 files, total_budget=5000 | First N files read, rest skipped | Sum of token_estimates ≤ 5000
- **Mock needed:** False
- **Assertions:** 

### test_055
- **Type:** unit
- **Requirement:** 
- **Description:** Per-file budget enforcement (REQ-6) | Auto | 1 large file, per_file_budget=500 | Single file truncated | token_estimate ≤ 500
- **Mock needed:** False
- **Assertions:** 

### test_060
- **Type:** unit
- **Requirement:** 
- **Description:** Parse pyproject.toml (REQ-1) | Auto | Valid pyproject.toml | Dict with name, dependencies | Keys present, deps list non-empty
- **Mock needed:** False
- **Assertions:** 

### test_070
- **Type:** unit
- **Requirement:** 
- **Description:** Parse package.json (REQ-1) | Auto | Valid package.json | Dict with name, dependencies | Keys present, deps list non-empty
- **Mock needed:** False
- **Assertions:** 

### test_080
- **Type:** unit
- **Requirement:** 
- **Description:** Parse missing config (REQ-7) | Auto | Repo with no config file | Empty dict | Returns {}
- **Mock needed:** False
- **Assertions:** 

### test_090
- **Type:** unit
- **Requirement:** 
- **Description:** Detect naming conventions (REQ-2) | Auto | Python files with snake_case | PatternAnalysis.naming_convention set | Contains "snake_case"
- **Mock needed:** False
- **Assertions:** 

### test_100
- **Type:** unit
- **Requirement:** 
- **Description:** Detect TypedDict pattern (REQ-2) | Auto | File with TypedDict import | PatternAnalysis.state_pattern set | Contains "TypedDict"
- **Mock needed:** False
- **Assertions:** 

### test_105
- **Type:** unit
- **Requirement:** 
- **Description:** Unknown pattern defaults (REQ-7) | Auto | Empty file_contents dict | All fields "unknown" | All PatternAnalysis values == "unknown"
- **Mock needed:** False
- **Assertions:** 

### test_110
- **Type:** unit
- **Requirement:** 
- **Description:** Detect frameworks from deps (REQ-2) | Auto | deps=["langgraph", "pytest"] | ["LangGraph", "pytest"] | Both detected
- **Mock needed:** False
- **Assertions:** 

### test_115
- **Type:** unit
- **Requirement:** 
- **Description:** Detect frameworks from imports (REQ-2) | Auto | File with `from fastapi import` | ["FastAPI"] in result | FastAPI detected
- **Mock needed:** True
- **Assertions:** 

### test_120
- **Type:** unit
- **Requirement:** 
- **Description:** Extract CLAUDE.md conventions (REQ-1) | Auto | CLAUDE.md with rule bullets | List of convention strings | Non-empty list, strings match rules
- **Mock needed:** False
- **Assertions:** 

### test_130
- **Type:** unit
- **Requirement:** 
- **Description:** Extract empty conventions (REQ-7) | Auto | CLAUDE.md with no rules section | Empty list | Returns []
- **Mock needed:** False
- **Assertions:** 

### test_140
- **Type:** unit
- **Requirement:** 
- **Description:** Full analysis happy path (REQ-4) | Auto | Mock repo with all key files, issue text referencing existing modules | Complete CodebaseContext with real file paths and patterns | All fields populated; fil
- **Mock needed:** True
- **Assertions:** 

### test_145
- **Type:** unit
- **Requirement:** 
- **Description:** Context references real paths and patterns (REQ-4) | Auto | Mock repo with known structure + specific issue text | CodebaseContext.key_file_excerpts keys are real file paths; conventions match CLAUDE.
- **Mock needed:** True
- **Assertions:** 

### test_150
- **Type:** unit
- **Requirement:** 
- **Description:** Analysis with no repo_path (REQ-7) | Auto | State with repo_path=None | Empty CodebaseContext | All fields empty/default
- **Mock needed:** False
- **Assertions:** 

### test_160
- **Type:** unit
- **Requirement:** 
- **Description:** Analysis with bad repo_path (REQ-7) | Auto | State with non-existent path | Empty CodebaseContext | All fields empty/default
- **Mock needed:** False
- **Assertions:** 

### test_170
- **Type:** unit
- **Requirement:** 
- **Description:** Find related files - match (REQ-3) | Auto | Issue "fix auth", repo has auth.py | [auth.py] | auth.py in results
- **Mock needed:** False
- **Assertions:** 

### test_180
- **Type:** unit
- **Requirement:** 
- **Description:** Find related files - no match (REQ-3) | Auto | Issue "fix auth", repo has no auth | [] | Empty list
- **Mock needed:** False
- **Assertions:** 

### test_185
- **Type:** unit
- **Requirement:** 
- **Description:** Find related files - max results (REQ-3) | Auto | Issue matching 10+ files | At most 5 paths | len(result) <= 5
- **Mock needed:** False
- **Assertions:** 

### test_190
- **Type:** unit
- **Requirement:** 
- **Description:** Node produces codebase_context state key (REQ-8) | Auto | Mock repo with CLAUDE.md and source files | Dict with `codebase_context` key; value is dict matching CodebaseContext shape | Return dict has k
- **Mock needed:** True
- **Assertions:** 

### test_200
- **Type:** unit
- **Requirement:** 
- **Description:** Sensitive .env file never read (REQ-9) | Auto | Repo with `.env` file containing `SECRET=abc123` | `.env` not in any read results; `abc123` not in any content | No FileReadResult.path ends with `.env`
- **Mock needed:** False
- **Assertions:** 

### test_205
- **Type:** unit
- **Requirement:** 
- **Description:** Sensitive .pem file never read (REQ-9) | Auto | Repo with `server.pem` file containing certificate data | `server.pem` not in any read results | No FileReadResult.path contains `server.pem`
- **Mock needed:** False
- **Assertions:** 

### test_210
- **Type:** unit
- **Requirement:** 
- **Description:** Key file priority ordering (REQ-1) | Auto | Repo with CLAUDE.md + README | CLAUDE.md before README | Index of CLAUDE.md < index of README
- **Mock needed:** False
- **Assertions:** 

### test_220
- **Type:** unit
- **Requirement:** 
- **Description:** Sensitive file exclusion via is_sensitive_file (REQ-9) | Auto | Repo with .env file | .env not in read results | .env path not in any FileReadResult
- **Mock needed:** False
- **Assertions:** 

### test_225
- **Type:** unit
- **Requirement:** 
- **Description:** is_sensitive_file detection (REQ-9) | Auto | Various sensitive paths (.env, .pem, credentials/db.yml, main.py) | True for .env, .pem, credentials/db.yml; False for main.py | Correct bool for each inpu
- **Mock needed:** False
- **Assertions:** 

### test_230
- **Type:** unit
- **Requirement:** 
- **Description:** Symlink outside repo blocked (REQ-9) | Auto | Symlink to /tmp/secret.txt in repo | Empty content returned | FileReadResult.content == ""
- **Mock needed:** False
- **Assertions:** 

### test_240
- **Type:** unit
- **Requirement:** 
- **Description:** Cross-repo analysis via repo_path (REQ-5) | Auto | State with repo_path pointing to a second mock repo in fixtures | CodebaseContext populated from second repo's files | key_file_excerpts contain cont
- **Mock needed:** True
- **Assertions:** 

## Original Test Plan Section

*Ref: [0005-testing-strategy-and-protocols.md](0005-testing-strategy-and-protocols.md)*

**Testing Philosophy:** Strive for 100% automated test coverage. All tests use mock repos from fixtures — no live filesystem dependencies outside the test fixtures directory.

### 10.0 Test Plan (TDD - Complete Before Implementation)

**TDD Requirement:** Tests MUST be written and failing BEFORE implementation begins.

| Test ID | Test Description | Expected Behavior | Status |
|---------|------------------|-------------------|--------|
| T010 | `test_read_file_with_budget_normal` | Reads file content within budget, `truncated=False` | RED |
| T020 | `test_read_file_with_budget_truncated` | Truncates large file, `truncated=True` | RED |
| T030 | `test_read_file_with_budget_binary_skip` | Returns empty content for binary files | RED |
| T040 | `test_read_file_with_budget_missing_file` | Returns empty content, no crash | RED |
| T050 | `test_read_files_within_budget_respects_total` | Stops reading when total budget exhausted | RED |
| T055 | `test_read_files_within_budget_respects_per_file` | Individual file capped at per_file_budget | RED |
| T060 | `test_parse_project_metadata_pyproject` | Extracts name, deps from pyproject.toml | RED |
| T070 | `test_parse_project_metadata_package_json` | Extracts name, deps from package.json | RED |
| T080 | `test_parse_project_metadata_missing` | Returns empty dict when no config found | RED |
| T090 | `test_scan_patterns_detects_naming` | Identifies snake_case module naming | RED |
| T100 | `test_scan_patterns_detects_typeddict` | Finds TypedDict state pattern | RED |
| T105 | `test_scan_patterns_unknown_defaults` | Returns "unknown" for undetectable fields | RED |
| T110 | `test_detect_frameworks_from_deps` | Identifies LangGraph, pytest from dependency list | RED |
| T115 | `test_detect_frameworks_from_imports` | Detects frameworks from import statements in file contents | RED |
| T120 | `test_extract_conventions_from_claude_md` | Extracts bullet-point conventions from CLAUDE.md | RED |
| T130 | `test_extract_conventions_empty` | Returns empty list for CLAUDE.md without conventions | RED |
| T140 | `test_analyze_codebase_happy_path` | Produces full CodebaseContext from mock repo | RED |
| T145 | `test_analyze_codebase_context_has_real_paths` | Generated context references real file paths and patterns from target codebase | RED |
| T150 | `test_analyze_codebase_no_repo_path` | Returns empty context, logs warning | RED |
| T160 | `test_analyze_codebase_missing_repo` | Returns empty context when repo_path doesn't exist | RED |
| T170 | `test_find_related_files_keyword_match` | Finds auth.py when issue mentions "authentication" | RED |
| T180 | `test_find_related_files_no_match` | Returns empty list for unrelated issue text | RED |
| T185 | `test_find_related_files_max_five` | Returns at most 5 results even with many matches | RED |
| T190 | `test_analyze_codebase_produces_state_key` | Node returns dict with `codebase_context` key matching CodebaseContext shape | RED |
| T200 | `test_sensitive_file_not_read_env` | `.env` file content never appears in any read result | RED |
| T205 | `test_sensitive_file_not_read_pem` | `.pem` file content never appears in any read result | RED |
| T210 | `test_select_key_files_priority_order` | CLAUDE.md before README.md before pyproject.toml | RED |
| T220 | `test_sensitive_file_exclusion` | .env, .secrets files are not read | RED |
| T225 | `test_is_sensitive_file` | Correctly identifies sensitive file patterns | RED |
| T230 | `test_symlink_outside_repo_blocked` | Symlink pointing outside repo is not read | RED |

**Coverage Target:** ≥95% for all new code

**TDD Checklist:**
- [ ] All tests written before implementation
- [ ] Tests currently RED (failing)
- [ ] Test IDs match scenario IDs in 10.1
- [ ] Test files created at: `tests/unit/test_analyze_codebase.py`, `tests/unit/test_codebase_reader.py`, `tests/unit/test_pattern_scanner.py`

### 10.1 Test Scenarios

| ID | Scenario | Type | Input | Expected Output | Pass Criteria |
|----|----------|------|-------|-----------------|---------------|
| 010 | Read file within budget (REQ-1) | Auto | Small text file, budget=2000 | Full content, truncated=False | Content matches file, token_estimate < 2000 |
| 020 | Read file exceeding budget (REQ-6) | Auto | 10KB file, budget=500 | Partial content, truncated=True | Content length ≈ 500×4 chars, truncated=True |
| 030 | Read binary file gracefully (REQ-7) | Auto | PNG file path | Empty content, no exception | Returns FileReadResult with empty content |
| 040 | Read missing file gracefully (REQ-7) | Auto | Non-existent path | Empty content, no exception | Returns FileReadResult with empty content |
| 050 | Total budget enforcement (REQ-6) | Auto | 10 files, total_budget=5000 | First N files read, rest skipped | Sum of token_estimates ≤ 5000 |
| 055 | Per-file budget enforcement (REQ-6) | Auto | 1 large file, per_file_budget=500 | Single file truncated | token_estimate ≤ 500 |
| 060 | Parse pyproject.toml (REQ-1) | Auto | Valid pyproject.toml | Dict with name, dependencies | Keys present, deps list non-empty |
| 070 | Parse package.json (REQ-1) | Auto | Valid package.json | Dict with name, dependencies | Keys present, deps list non-empty |
| 080 | Parse missing config (REQ-7) | Auto | Repo with no config file | Empty dict | Returns {} |
| 090 | Detect naming conventions (REQ-2) | Auto | Python files with snake_case | PatternAnalysis.naming_convention set | Contains "snake_case" |
| 100 | Detect TypedDict pattern (REQ-2) | Auto | File with TypedDict import | PatternAnalysis.state_pattern set | Contains "TypedDict" |
| 105 | Unknown pattern defaults (REQ-7) | Auto | Empty file_contents dict | All fields "unknown" | All PatternAnalysis values == "unknown" |
| 110 | Detect frameworks from deps (REQ-2) | Auto | deps=["langgraph", "pytest"] | ["LangGraph", "pytest"] | Both detected |
| 115 | Detect frameworks from imports (REQ-2) | Auto | File with `from fastapi import` | ["FastAPI"] in result | FastAPI detected |
| 120 | Extract CLAUDE.md conventions (REQ-1) | Auto | CLAUDE.md with rule bullets | List of convention strings | Non-empty list, strings match rules |
| 130 | Extract empty conventions (REQ-7) | Auto | CLAUDE.md with no rules section | Empty list | Returns [] |
| 140 | Full analysis happy path (REQ-4) | Auto | Mock repo with all key files, issue text referencing existing modules | Complete CodebaseContext with real file paths and patterns | All fields populated; file paths in key_file_excerpts and related_code exist in mock repo |
| 145 | Context references real paths and patterns (REQ-4) | Auto | Mock repo with known structure + specific issue text | CodebaseContext.key_file_excerpts keys are real file paths; conventions match CLAUDE.md content | Every path in context exists in mock_repo; every convention string traceable to CLAUDE.md |
| 150 | Analysis with no repo_path (REQ-7) | Auto | State with repo_path=None | Empty CodebaseContext | All fields empty/default |
| 160 | Analysis with bad repo_path (REQ-7) | Auto | State with non-existent path | Empty CodebaseContext | All fields empty/default |
| 170 | Find related files - match (REQ-3) | Auto | Issue "fix auth", repo has auth.py | [auth.py] | auth.py in results |
| 180 | Find related files - no match (REQ-3) | Auto | Issue "fix auth", repo has no auth | [] | Empty list |
| 185 | Find related files - max results (REQ-3) | Auto | Issue matching 10+ files | At most 5 paths | len(result) <= 5 |
| 190 | Node produces codebase_context state key (REQ-8) | Auto | Mock repo with CLAUDE.md and source files | Dict with `codebase_context` key; value is dict matching CodebaseContext shape | Return dict has key `codebase_context`; nested dict has all CodebaseContext keys; no unexpected keys |
| 200 | Sensitive .env file never read (REQ-9) | Auto | Repo with `.env` file containing `SECRET=abc123` | `.env` not in any read results; `abc123` not in any content | No FileReadResult.path ends with `.env`; `abc123` absent from all content strings |
| 205 | Sensitive .pem file never read (REQ-9) | Auto | Repo with `server.pem` file containing certificate data | `server.pem` not in any read results | No FileReadResult.path contains `server.pem` |
| 210 | Key file priority ordering (REQ-1) | Auto | Repo with CLAUDE.md + README | CLAUDE.md before README | Index of CLAUDE.md < index of README |
| 220 | Sensitive file exclusion via is_sensitive_file (REQ-9) | Auto | Repo with .env file | .env not in read results | .env path not in any FileReadResult |
| 225 | is_sensitive_file detection (REQ-9) | Auto | Various sensitive paths (.env, .pem, credentials/db.yml, main.py) | True for .env, .pem, credentials/db.yml; False for main.py | Correct bool for each input path |
| 230 | Symlink outside repo blocked (REQ-9) | Auto | Symlink to /tmp/secret.txt in repo | Empty content returned | FileReadResult.content == "" |
| 240 | Cross-repo analysis via repo_path (REQ-5) | Auto | State with repo_path pointing to a second mock repo in fixtures | CodebaseContext populated from second repo's files | key_file_excerpts contain content from second mock repo, not from primary project |

### 10.2 Test Commands

```bash
# Run all new unit tests
poetry run pytest tests/unit/test_analyze_codebase.py tests/unit/test_codebase_reader.py tests/unit/test_pattern_scanner.py -v

# Run only codebase reader tests
poetry run pytest tests/unit/test_codebase_reader.py -v

# Run only pattern scanner tests
poetry run pytest tests/unit/test_pattern_scanner.py -v

# Run only analysis node tests
poetry run pytest tests/unit/test_analyze_codebase.py -v

# Run with coverage
poetry run pytest tests/unit/test_analyze_codebase.py tests/unit/test_codebase_reader.py tests/unit/test_pattern_scanner.py -v --cov=assemblyzero/utils/codebase_reader --cov=assemblyzero/utils/pattern_scanner --cov=assemblyzero/workflows/requirements/nodes/analyze_codebase --cov-report=term-missing
```

### 10.3 Manual Tests (Only If Unavoidable)

N/A - All scenarios automated.
