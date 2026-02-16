# Implementation Request: tests/unit/test_completeness_gate.py

## Task

Write the complete contents of `tests/unit/test_completeness_gate.py`.

Change type: Add
Description: Unit and integration tests for completeness gate

## LLD Specification

# 147 - Feature: Implementation Completeness Gate (Anti-Stub Detection)

## 1. Context & Goal
* **Issue:** #147
* **Objective:** Add a completeness gate (N4b) between implementation and verification nodes to detect semantically incomplete implementations that pass mechanical tests but fail to fulfill LLD requirements.
* **Status:** Approved (gemini-3-pro-preview, 2026-02-16)
* **Related Issues:** #181 (subsumed - Implementation Report), #335 (N2.5 precedent), #225 (skipped test enforcement), #354 (mutation testing - future), #149-#156 (codebase scan findings - closed)

### Open Questions
*All questions resolved per Gemini review.*

- [x] ~~Should the Gemini semantic review have a configurable timeout for budget control?~~ **RESOLVED: Yes. Implement a default timeout (30s) in the Gemini client configuration to prevent hanging processes and budget drain.**
- [x] ~~What is the maximum number of N4→N4b→N4 iterations before escalating to human review vs hard stop?~~ **RESOLVED: Set a hard limit of 3 iterations. If the loop persists, route to `end` (Fail) to force manual intervention rather than spiraling costs.**

## 2. Proposed Changes

*This section is the **source of truth** for implementation. Describe exactly what will be built.*

### 2.1 Files Changed

| File | Change Type | Description |
|------|-------------|-------------|
| `assemblyzero/workflows/testing/completeness/` | Add (Directory) | Package directory for completeness analysis |
| `assemblyzero/workflows/testing/completeness/__init__.py` | Add | Package init with exports |
| `assemblyzero/workflows/testing/completeness/ast_analyzer.py` | Add | Layer 1 AST-based analysis functions |
| `assemblyzero/workflows/testing/completeness/report_generator.py` | Add | Generate implementation verification reports |
| `assemblyzero/workflows/testing/nodes/completeness_gate.py` | Add | N4b workflow node implementation |
| `tests/unit/test_completeness_gate.py` | Add | Unit and integration tests for completeness gate |
| `assemblyzero/workflows/testing/graph.py` | Modify | Insert N4b node between N4 and N5, add routing |
| `assemblyzero/workflows/testing/state.py` | Modify | Add completeness_verdict and completeness_issues fields |
| `assemblyzero/workflows/testing/nodes/__init__.py` | Modify | Export completeness_gate node |

### 2.1.1 Path Validation (Mechanical - Auto-Checked)

*Issue #277: Before human or Gemini review, paths are verified programmatically.*

Mechanical validation automatically checks:
- All "Modify" files must exist in repository
- All "Delete" files must exist in repository
- All "Add" files must have existing parent directories
- No placeholder prefixes (`src/`, `lib/`, `app/`) unless directory exists

**If validation fails, the LLD is BLOCKED before reaching review.**

### 2.2 Dependencies

*No new packages required. Uses standard library `ast` module.*

```toml
# pyproject.toml additions (if any)
# None - uses stdlib ast module
```

### 2.3 Data Structures

```python
# Pseudocode - NOT implementation
from enum import Enum

class CompletenessCategory(Enum):
    """Categories of completeness issues for type safety."""
    DEAD_CLI_FLAG = "dead_cli_flag"
    EMPTY_BRANCH = "empty_branch"
    DOCSTRING_ONLY = "docstring_only"
    TRIVIAL_ASSERTION = "trivial_assertion"
    UNUSED_IMPORT = "unused_import"

class CompletenessIssue(TypedDict):
    """Single completeness issue detected by analysis."""
    category: CompletenessCategory
    file_path: str
    line_number: int
    description: str
    severity: Literal["ERROR", "WARNING"]

class CompletenessResult(TypedDict):
    """Result of completeness analysis."""
    verdict: Literal["PASS", "WARN", "BLOCK"]
    issues: list[CompletenessIssue]
    ast_analysis_ms: int
    gemini_review_ms: int | None

class RequirementVerification(TypedDict):
    """Single LLD requirement verification status."""
    requirement_id: int
    requirement_text: str
    status: Literal["IMPLEMENTED", "PARTIAL", "MISSING"]
    evidence: str  # File:line or explanation

class ImplementationReport(TypedDict):
    """Full implementation verification report."""
    issue_number: int
    requirements: list[RequirementVerification]
    completeness_result: CompletenessResult
    generated_at: str  # ISO timestamp

class ReviewMaterials(TypedDict):
    """Materials prepared for Gemini semantic review."""
    lld_requirements: list[tuple[int, str]]  # (id, text) pairs
    code_snippets: dict[str, str]  # file_path -> relevant code
    issue_number: int

# State additions
class TestingState(TypedDict):
    # ... existing fields ...
    completeness_verdict: Literal["PASS", "WARN", "BLOCK", ""]
    completeness_issues: list[CompletenessIssue]
    implementation_report_path: str  # From #181
    review_materials: ReviewMaterials | None  # For Gemini Layer 2
```

### 2.4 Function Signatures

```python
# assemblyzero/workflows/testing/completeness/ast_analyzer.py

def analyze_dead_cli_flags(source_code: str, file_path: str) -> list[CompletenessIssue]:
    """Detect argparse add_argument calls with no corresponding usage."""
    ...

def analyze_empty_branches(source_code: str, file_path: str) -> list[CompletenessIssue]:
    """Detect if/elif/else branches with only pass, return None, or trivial bodies."""
    ...

def analyze_docstring_only_functions(source_code: str, file_path: str) -> list[CompletenessIssue]:
    """Detect functions with docstring + pass/return None only."""
    ...

def analyze_trivial_assertions(source_code: str, file_path: str) -> list[CompletenessIssue]:
    """Detect test functions where sole assertion is 'is not None' or similar."""
    ...

def analyze_unused_imports(source_code: str, file_path: str) -> list[CompletenessIssue]:
    """Detect imports with no usage in function bodies."""
    ...

def run_ast_analysis(files: list[Path], max_file_size_bytes: int = 1_000_000) -> CompletenessResult:
    """Run all AST checks on provided files. Skip files exceeding max_file_size_bytes."""
    ...


# assemblyzero/workflows/testing/completeness/report_generator.py

def generate_implementation_report(
    issue_number: int,
    lld_path: Path,
    implementation_files: list[Path],
    completeness_result: CompletenessResult,
) -> Path:
    """Generate implementation report to docs/reports/active/{issue}-implementation-report.md."""
    ...

def extract_lld_requirements(lld_path: Path) -> list[tuple[int, str]]:
    """Parse Section 3 requirements from LLD markdown."""
    ...

def prepare_review_materials(
    issue_number: int,
    lld_path: Path,
    implementation_files: list[Path],
) -> ReviewMaterials:
    """Prepare materials for Gemini semantic review submission by orchestrator."""
    ...


# assemblyzero/workflows/testing/nodes/completeness_gate.py

def completeness_gate(state: TestingState) -> TestingState:
    """N4b: Verify implementation completeness before proceeding to test verification."""
    ...

def route_after_completeness_gate(state: TestingState) -> Literal["N5_verify_green", "N4_implement_code", "end"]:
    """Route based on completeness verdict and iteration count."""
    ...
```

### 2.5 Logic Flow (Pseudocode)

```
N4b_completeness_gate:
1. Receive state from N4_implement_code
2. Collect modified/created files from state.files_changed

3. LAYER 1: AST Analysis
   FOR each file in implementation files:
     - Skip if file exceeds max_file_size_bytes (1MB default)
     - Run analyze_dead_cli_flags()
     - Run analyze_empty_branches()
     - Run analyze_docstring_only_functions()
     - Run analyze_unused_imports()
   FOR each test file:
     - Run analyze_trivial_assertions()
   
   Aggregate issues with severity

4. IF Layer 1 has BLOCK-level issues:
   - Set verdict = "BLOCK"
   - Skip Layer 2
   ELSE:
   
5. LAYER 2: Gemini Semantic Review (orchestrator-controlled)
   - Extract requirements from LLD Section 3
   - Prepare review materials via prepare_review_materials()
   - Set state.review_materials with prepared materials
   - Return state with review_materials for orchestrator
   - Orchestrator submits to Gemini (with 30s timeout)
   - Receive Gemini verdict

6. Generate implementation report
   - Write to docs/reports/active/{issue}-implementation-report.md
   - Set state.implementation_report_path

7. Update state:
   - state.completeness_verdict = verdict
   - state.completeness_issues = all_issues

8. Return state

route_after_completeness_gate:
1. IF verdict == "BLOCK":
   - IF iteration_count >= 3: return "end"  # Hard limit
   - ELSE: return "N4_implement_code"
2. ELSE:
   - return "N5_verify_green"
```

### 2.6 Technical Approach

* **Module:** `assemblyzero/workflows/testing/completeness/`
* **Pattern:** Two-layer validation (fast deterministic → slow semantic)
* **Key Decisions:**
  - AST analysis runs first as a fast, deterministic gate
  - Gemini review only triggers if AST passes (cost control)
  - Orchestrator controls Gemini submission per WORKFLOW.md
  - Report generation is a side effect, not blocking
  - File size limit (1MB) prevents memory spikes on large generated files

### 2.7 Architecture Decisions

| Decision | Options Considered | Choice | Rationale |
|----------|-------------------|--------|-----------|
| Analysis ordering | Parallel layers, Sequential layers | Sequential (AST then Gemini) | AST is fast/free; skip expensive Gemini if AST fails |
| AST implementation | Tree-sitter, Python ast, LibCST | Python ast | Zero dependencies, sufficient for our patterns |
| Report storage | Database, S3, Local markdown | Local markdown | Consistent with existing report patterns |
| Loop limit | Hardcoded, Configurable, Unlimited | Hardcoded at 3 | Prevents cost spiral; simple to understand |
| Issue categories | String literals, Enum | Enum (CompletenessCategory) | Type safety, IDE support, refactoring ease |
| File size limit | None, Configurable, Hardcoded | Configurable with 1MB default | Prevents memory spikes while allowing override |

**Architectural Constraints:**
- Must integrate with existing LangGraph workflow structure
- Gemini calls must go through orchestrator (not direct from node)
- Cannot modify N4 or N5 node logic (only add N4b between them)

## 3. Requirements

*What must be true when this is done. These become acceptance criteria.*

1. N4b node inserted into workflow graph between N4 and N5
2. AST analyzer detects dead CLI flags (add_argument without usage)
3. AST analyzer detects empty conditional branches (if x: pass)
4. AST analyzer detects docstring-only functions
5. AST analyzer detects trivial assertions in test files
6. AST analyzer detects unused imports from implementation
7. BLOCK verdict routes back to N4 for re-implementation
8. PASS/WARN verdict routes forward to N5
9. Implementation report generated at docs/reports/active/{issue}-implementation-report.md
10. Report includes LLD requirement verification table
11. Report includes completeness analysis summary
12. Max iteration limit (3) prevents infinite loops
13. Layer 2 Gemini review materials prepared correctly for orchestrator submission (not direct call)

## 4. Alternatives Considered

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| AST-only gate (no Gemini) | Fast, deterministic, zero cost | Misses semantic incompleteness | **Rejected** |
| Gemini-only gate (no AST) | Catches semantic issues | Expensive, slow, non-deterministic | **Rejected** |
| Two-layer approach | Best of both, cost-controlled | More complex implementation | **Selected** |
| Integrate into N4 node | Simpler graph | Violates single-responsibility | **Rejected** |
| Post-N5 check | Catches test-passing stubs | Late in pipeline, wastes test runs | **Rejected** |

**Rationale:** Two-layer approach provides deterministic fast-fail for obvious issues while preserving expensive semantic review for subtle completeness problems. Inserting as N4b maintains node separation.

## 5. Data & Fixtures

*Per [0108-lld-pre-implementation-review.md](0108-lld-pre-implementation-review.md) - complete this section BEFORE implementation.*

### 5.1 Data Sources

| Attribute | Value |
|-----------|-------|
| Source | Local filesystem (implementation files, LLD) |
| Format | Python source code, Markdown |
| Size | ~10-50 files per workflow run |
| Refresh | Per-workflow-run |
| Copyright/License | N/A - internal project files |

### 5.2 Data Pipeline

```
Implementation Files ──ast.parse──► AST Trees ──analyze──► CompletenessIssues
LLD Markdown ──parse──► Requirements ──compare──► RequirementVerification
CompletenessIssues + RequirementVerification ──format──► Implementation Report (Markdown)
LLD + Code ──prepare_review_materials──► ReviewMaterials (for Orchestrator)
```

### 5.3 Test Fixtures

| Fixture | Source | Notes |
|---------|--------|-------|
| Dead CLI flag example | Generated | Synthetic argparse code with unused flags |
| Empty branch example | Generated | if/else with pass bodies |
| Docstring-only function | Generated | Functions with docstring + return None |
| Trivial assertion test | Generated | Test with only `assert x is not None` |
| Valid implementation | Generated | Code with no issues (negative test) |
| Patterns from #149-#156 | Extracted | Real issues from codebase scan |
| Sample LLD with requirements | Generated | Markdown with Section 3 requirements |

### 5.4 Deployment Pipeline

Report files are written to local `docs/reports/active/` directory. No external deployment required.

**If data source is external:** N/A - all sources are internal.

## 6. Diagram

### 6.1 Mermaid Quality Gate

Before finalizing any diagram, verify in [Mermaid Live Editor](https://mermaid.live) or GitHub preview:

- [x] **Simplicity:** Similar components collapsed (per 0006 §8.1)
- [x] **No touching:** All elements have visual separation (per 0006 §8.2)
- [x] **No hidden lines:** All arrows fully visible (per 0006 §8.3)
- [x] **Readable:** Labels not truncated, flow direction clear
- [ ] **Auto-inspected:** Agent rendered via mermaid.ink and viewed (per 0006 §8.5)

**Agent Auto-Inspection (MANDATORY):**

AI agents MUST render and view the diagram before committing:
1. Base64 encode diagram → fetch PNG from `https://mermaid.ink/img/{base64}`
2. Read the PNG file (multimodal inspection)
3. Document results below

**Auto-Inspection Results:**
```
- Touching elements: [ ] None / [ ] Found: ___
- Hidden lines: [ ] None / [ ] Found: ___
- Label readability: [ ] Pass / [ ] Issue: ___
- Flow clarity: [ ] Clear / [ ] Issue: ___
```

*Reference: [0006-mermaid-diagrams.md](0006-mermaid-diagrams.md)*

### 6.2 Diagram

```mermaid
flowchart TB
    subgraph Workflow["Testing Workflow"]
        N4["N4: implement_code"]
        N4b["N4b: completeness_gate"]
        N5["N5: verify_green"]
        END["end"]
    end
    
    subgraph N4b_Internal["Completeness Gate Details"]
        L1["Layer 1: AST Analysis"]
        L2["Layer 2: Gemini Review"]
        RPT["Generate Report"]
    end
    
    N4 --> N4b
    N4b --> L1
    L1 -->|"BLOCK"| RPT
    L1 -->|"PASS"| L2
    L2 --> RPT
    RPT --> ROUTE{"Route"}
    
    ROUTE -->|"verdict=BLOCK & iter<3"| N4
    ROUTE -->|"verdict=BLOCK & iter>=3"| END
    ROUTE -->|"verdict=PASS/WARN"| N5
```

## 7. Security & Safety Considerations

### 7.1 Security

| Concern | Mitigation | Status |
|---------|------------|--------|
| Code injection via AST parsing | ast.parse is read-only, no exec | Addressed |
| Path traversal in file collection | Validate files within project root | Addressed |
| Gemini prompt injection | Review materials are code excerpts, not user input | Addressed |

### 7.2 Safety

| Concern | Mitigation | Status |
|---------|------------|--------|
| Infinite loop in N4↔N4b cycle | Hard limit of 3 iterations | Addressed |
| False positive blocks valid code | WARN severity for uncertain detections, only ERROR blocks | Addressed |
| Report overwrite data loss | Reports use unique issue number in filename | Addressed |
| AST parse failure on syntax errors | Catch SyntaxError, report as separate issue | Addressed |
| Memory spike on large files | Skip files exceeding 1MB size limit | Addressed |
| Gemini timeout causing budget drain | 30s timeout configured in Gemini client | Addressed |

**Fail Mode:** Fail Open - If AST analysis fails unexpectedly, proceed to N5 with warning rather than blocking indefinitely.

**Recovery Strategy:** If N4b crashes, state contains completeness_issues=[], verdict="" allowing manual inspection and re-run.

## 8. Performance & Cost Considerations

### 8.1 Performance

| Metric | Budget | Approach |
|--------|--------|----------|
| AST analysis latency | < 500ms for 50 files | Python ast is fast, no I/O; skip files >1MB |
| Gemini review latency | < 30s | Only runs if AST passes; timeout enforced |
| Memory | < 50MB | AST trees are small, process sequentially; skip large files |

**Bottlenecks:** Gemini API call is the slowest component; mitigated by Layer 1 filtering.

### 8.2 Cost Analysis

| Resource | Unit Cost | Estimated Usage | Monthly Cost |
|----------|-----------|-----------------|--------------|
| Gemini API calls | ~$0.01 per review | ~100 reviews/month | ~$1 |
| Local compute | $0 | N/A | $0 |

**Cost Controls:**
- [x] Layer 1 AST analysis gates expensive Gemini calls
- [x] Gemini only called when AST analysis passes
- [x] Hard iteration limit (3) prevents cost spiral
- [x] 30s timeout prevents hanging/runaway Gemini calls

**Worst-Case Scenario:** If Layer 1 has bugs allowing all implementations through, Gemini costs increase proportionally. At $0.01/call, even 10x usage is $10/month. Hard iteration limit caps max calls per issue to 3.

## 9. Legal & Compliance

| Concern | Applies? | Mitigation |
|---------|----------|------------|
| PII/Personal Data | No | Only analyzes code, no user data |
| Third-Party Licenses | No | Uses stdlib ast only |
| Terms of Service | Yes | Gemini usage within existing API agreement |
| Data Retention | No | Reports are project artifacts, not sensitive |
| Export Controls | No | No restricted algorithms |

**Data Classification:** Internal

**Compliance Checklist:**
- [x] No PII stored without consent
- [x] All third-party licenses compatible with project license
- [x] External API usage compliant with provider ToS
- [x] Data retention policy documented (reports persist with project)

## 10. Verification & Testing

*Ref: [0005-testing-strategy-and-protocols.md](0005-testing-strategy-and-protocols.md)*

**Testing Philosophy:** Strive for 100% automated test coverage. Manual tests are a last resort for scenarios that genuinely cannot be automated.

### 10.0 Test Plan (TDD - Complete Before Implementation)

**TDD Requirement:** Tests MUST be written and failing BEFORE implementation begins.

| Test ID | Test Description | Expected Behavior | Status |
|---------|------------------|-------------------|--------|
| T010 | test_detect_dead_cli_flags | Returns issue for unused argparse arg | RED |
| T020 | test_detect_empty_branch_pass | Returns issue for `if x: pass` | RED |
| T030 | test_detect_empty_branch_return_none | Returns issue for `if x: return None` | RED |
| T040 | test_detect_docstring_only_function | Returns issue for func with docstring+pass | RED |
| T050 | test_detect_trivial_assertion | Returns issue for `assert x is not None` only | RED |
| T060 | test_detect_unused_import | Returns issue for import not used in functions | RED |
| T070 | test_valid_code_no_issues | Returns empty issues list for clean code | RED |
| T080 | test_completeness_gate_block_routing | BLOCK verdict routes to N4 | RED |
| T090 | test_completeness_gate_pass_routing | PASS verdict routes to N5 | RED |
| T100 | test_max_iterations_ends | BLOCK at max iterations (3) routes to end | RED |
| T110 | test_report_generation | Report file created with correct structure | RED |
| T120 | test_lld_requirement_extraction | Requirements parsed from Section 3 | RED |
| T130 | test_prepare_review_materials | ReviewMaterials correctly populated with LLD requirements and code snippets | RED |

**Coverage Target:** ≥95% for all new code

**TDD Checklist:**
- [ ] All tests written before implementation
- [ ] Tests currently RED (failing)
- [ ] Test IDs match scenario IDs in 10.1
- [ ] Test file created at: `tests/unit/test_completeness_gate.py`

### 10.1 Test Scenarios

| ID | Scenario | Type | Input | Expected Output | Pass Criteria |
|----|----------|------|-------|-----------------|---------------|
| 010 | Dead CLI flag detection | Auto | Code with `add_argument('--foo')` unused | CompletenessIssue with category=DEAD_CLI_FLAG | Issue returned with correct file/line |
| 020 | Empty branch (pass) detection | Auto | Code with `if x: pass` | CompletenessIssue with category=EMPTY_BRANCH | Issue identifies branch location |
| 030 | Empty branch (return None) detection | Auto | Code with `if mock: return None` | CompletenessIssue with category=EMPTY_BRANCH | Issue identifies branch location |
| 040 | Docstring-only function detection | Auto | `def foo(): """Doc.""" pass` | CompletenessIssue with category=DOCSTRING_ONLY | Issue identifies function |
| 050 | Trivial assertion detection | Auto | Test with only `assert result is not None` | CompletenessIssue with category=TRIVIAL_ASSERTION | Issue warns about assertion quality |
| 060 | Unused import detection | Auto | `import os` with no usage | CompletenessIssue with category=UNUSED_IMPORT | Issue identifies import |
| 070 | Valid implementation (negative) | Auto | Complete implementation code | Empty issues list | No false positives |
| 080 | BLOCK routes to N4 | Auto | State with verdict='BLOCK', iter<3 | Route returns 'N4_implement_code' | Correct routing |
| 090 | PASS routes to N5 | Auto | State with verdict='PASS' | Route returns 'N5_verify_green' | Correct routing |
| 100 | Max iterations ends workflow | Auto | State with verdict='BLOCK', iter>=3 | Route returns 'end' | Prevents infinite loop |
| 110 | Report file generation | Auto | Issue #999, results | File at docs/reports/active/999-implementation-report.md | File exists with correct structure |
| 120 | LLD requirement parsing | Auto | LLD with Section 3 requirements | List of (id, text) tuples | All requirements extracted |
| 130 | Review materials preparation | Auto | LLD path + implementation files | ReviewMaterials with requirements and code snippets | Materials correctly formatted for orchestrator |

### 10.2 Test Commands

```bash
# Run all automated tests
poetry run pytest tests/unit/test_completeness_gate.py -v

# Run only fast/mocked tests (exclude live)
poetry run pytest tests/unit/test_completeness_gate.py -v -m "not live"

# Run with coverage
poetry run pytest tests/unit/test_completeness_gate.py -v --cov=assemblyzero/workflows/testing/completeness --cov-report=term-missing
```

### 10.3 Manual Tests (Only If Unavoidable)

N/A - All scenarios automated.

## 11. Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| False positives block valid implementations | Med | Med | WARN severity for uncertain patterns; review false positive rate in first sprint |
| AST analysis misses edge cases | Low | Med | Start with high-confidence patterns; add patterns iteratively |
| Gemini semantic review gives inconsistent results | Med | Low | Layer 1 catches most issues; Layer 2 is enhancement |
| Integration breaks existing workflow | High | Low | Comprehensive integration tests; feature flag for rollout |
| Report generation fails silently | Low | Low | Log errors; proceed with verdict regardless of report |
| Memory spike on large files | Med | Low | File size limit (1MB) in run_ast_analysis |

## 12. Definition of Done

### Code
- [ ] Implementation complete and linted
- [ ] Code comments reference this LLD

### Tests
- [ ] All test scenarios pass
- [ ] Test coverage meets threshold (≥95%)

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

## Reviewer Suggestions

*Non-blocking recommendations from the reviewer.*

- Ensure the `max_file_size_bytes` check logs a warning when a file is skipped, so the user knows why analysis might be missing for that file.

## Appendix: Review Log

*Track all review feedback with timestamps and implementation status.*

<!-- Note: Timestamps are auto-generated by the workflow. Do not fill in manually. -->

### Gemini Review #1 (REVISE)

**Reviewer:** Gemini 3 Pro
**Verdict:** REVISE

#### Comments

| ID | Comment | Implemented? |
|----|---------|--------------|
| G1.1 | "Coverage is 92.3%. You must add a test case for Requirement 13 (Gemini material preparation) to reach >95%." | YES - Added T130 test scenario for prepare_review_materials |
| G1.2 | "Requirement 13 involves parsing LLDs and formatting code for a prompt. This is error-prone string manipulation that requires a dedicated unit test." | YES - Added prepare_review_materials function signature and T130 test |
| G1.3 | "Consider implementing a size limit on the files sent to ast.parse to prevent memory spikes" | YES - Added max_file_size_bytes parameter to run_ast_analysis (1MB default) |
| G1.4 | "Ensure CompletenessIssue categories are defined as an Enum for better type safety" | YES - Added CompletenessCategory Enum in Section 2.3 |
| G1.5 | "Open question: Gemini timeout" | YES - Resolved: 30s default timeout documented |
| G1.6 | "Open question: Max iterations" | YES - Resolved: Hard limit of 3, routes to end |

### Review Summary

| Review | Date | Verdict | Key Issue |
|--------|------|---------|-----------|
| 2 | 2026-02-16 | APPROVED | `gemini-3-pro-preview` |
| Gemini #1 | 2026-02-16 | REVISE | Test coverage 92.3% - missing REQ-13 test |

**Final Status:** APPROVED

## Tests That Must Pass

```python
# From C:\Users\mcwiz\Projects\AssemblyZero-147\tests\test_issue_147.py
"""Test file for Issue #147.

Generated by AssemblyZero TDD Testing Workflow.
Tests will fail with ImportError until implementation exists (TDD RED phase).
"""

import pytest


# Fixtures for mocking
@pytest.fixture
def mock_external_service():
    """Mock external service for isolation."""
    # TODO: Implement mock
    yield None


# Unit Tests
# -----------

def test_id():
    """
    Test Description | Expected Behavior | Status
    """
    # TDD: Arrange
    # Set up test data

    # TDD: Act
    # Call the function under test

    # TDD: Assert
    # Verify test_id works correctly
    assert False, 'TDD RED: test_id not implemented'


def test_t010():
    """
    test_detect_dead_cli_flags | Returns issue for unused argparse arg |
    RED
    """
    # TDD: Arrange
    # Set up test data

    # TDD: Act
    # Call the function under test

    # TDD: Assert
    # Verify test_t010 works correctly
    assert False, 'TDD RED: test_t010 not implemented'


def test_t020():
    """
    test_detect_empty_branch_pass | Returns issue for `if x: pass` | RED
    """
    # TDD: Arrange
    # Set up test data

    # TDD: Act
    # Call the function under test

    # TDD: Assert
    # Verify test_t020 works correctly
    assert False, 'TDD RED: test_t020 not implemented'


def test_t030():
    """
    test_detect_empty_branch_return_none | Returns issue for `if x:
    return None` | RED
    """
    # TDD: Arrange
    # Set up test data

    # TDD: Act
    # Call the function under test

    # TDD: Assert
    # Verify test_t030 works correctly
    assert False, 'TDD RED: test_t030 not implemented'


def test_t040():
    """
    test_detect_docstring_only_function | Returns issue for func with
    docstring+pass | RED
    """
    # TDD: Arrange
    # Set up test data

    # TDD: Act
    # Call the function under test

    # TDD: Assert
    # Verify test_t040 works correctly
    assert False, 'TDD RED: test_t040 not implemented'


def test_t050():
    """
    test_detect_trivial_assertion | Returns issue for `assert x is not
    None` only | RED
    """
    # TDD: Arrange
    # Set up test data

    # TDD: Act
    # Call the function under test

    # TDD: Assert
    # Verify test_t050 works correctly
    assert False, 'TDD RED: test_t050 not implemented'


def test_t060():
    """
    test_detect_unused_import | Returns issue for import not used in
    functions | RED
    """
    # TDD: Arrange
    # Set up test data

    # TDD: Act
    # Call the function under test

    # TDD: Assert
    # Verify test_t060 works correctly
    assert False, 'TDD RED: test_t060 not implemented'


def test_t070():
    """
    test_valid_code_no_issues | Returns empty issues list for clean code
    | RED
    """
    # TDD: Arrange
    # Set up test data

    # TDD: Act
    # Call the function under test

    # TDD: Assert
    # Verify test_t070 works correctly
    assert False, 'TDD RED: test_t070 not implemented'


def test_t080():
    """
    test_completeness_gate_block_routing | BLOCK verdict routes to N4 |
    RED
    """
    # TDD: Arrange
    # Set up test data

    # TDD: Act
    # Call the function under test

    # TDD: Assert
    # Verify test_t080 works correctly
    assert False, 'TDD RED: test_t080 not implemented'


def test_t090():
    """
    test_completeness_gate_pass_routing | PASS verdict routes to N5 | RED
    """
    # TDD: Arrange
    # Set up test data

    # TDD: Act
    # Call the function under test

    # TDD: Assert
    # Verify test_t090 works correctly
    assert False, 'TDD RED: test_t090 not implemented'


def test_t100():
    """
    test_max_iterations_ends | BLOCK at max iterations (3) routes to end
    | RED
    """
    # TDD: Arrange
    # Set up test data

    # TDD: Act
    # Call the function under test

    # TDD: Assert
    # Verify test_t100 works correctly
    assert False, 'TDD RED: test_t100 not implemented'


def test_t110():
    """
    test_report_generation | Report file created with correct structure |
    RED
    """
    # TDD: Arrange
    # Set up test data

    # TDD: Act
    # Call the function under test

    # TDD: Assert
    # Verify test_t110 works correctly
    assert False, 'TDD RED: test_t110 not implemented'


def test_t120():
    """
    test_lld_requirement_extraction | Requirements parsed from Section 3
    | RED
    """
    # TDD: Arrange
    # Set up test data

    # TDD: Act
    # Call the function under test

    # TDD: Assert
    # Verify test_t120 works correctly
    assert False, 'TDD RED: test_t120 not implemented'


def test_t130():
    """
    test_prepare_review_materials | ReviewMaterials correctly populated
    with LLD requirements and code snippets | RED
    """
    # TDD: Arrange
    # Set up test data

    # TDD: Act
    # Call the function under test

    # TDD: Assert
    # Verify test_t130 works correctly
    assert False, 'TDD RED: test_t130 not implemented'


def test_010():
    """
    Dead CLI flag detection | Auto | Code with `add_argument('--foo')`
    unused | CompletenessIssue with category=DEAD_CLI_FLAG | Issue
    returned with correct file/line
    """
    # TDD: Arrange
    # Set up test data

    # TDD: Act
    # Call the function under test

    # TDD: Assert
    # Verify test_010 works correctly
    assert False, 'TDD RED: test_010 not implemented'


def test_020():
    """
    Empty branch (pass) detection | Auto | Code with `if x: pass` |
    CompletenessIssue with category=EMPTY_BRANCH | Issue identifies branch
    location
    """
    # TDD: Arrange
    # Set up test data

    # TDD: Act
    # Call the function under test

    # TDD: Assert
    # Verify test_020 works correctly
    assert False, 'TDD RED: test_020 not implemented'


def test_030(mock_external_service):
    """
    Empty branch (return None) detection | Auto | Code with `if mock:
    return None` | CompletenessIssue with category=EMPTY_BRANCH | Issue
    identifies branch location
    """
    # TDD: Arrange
    # Set up test data

    # TDD: Act
    # Call the function under test

    # TDD: Assert
    # Verify test_030 works correctly
    assert False, 'TDD RED: test_030 not implemented'


def test_040():
    """
    Docstring-only function detection | Auto | `def foo(): """Doc."""
    pass` | CompletenessIssue with category=DOCSTRING_ONLY | Issue
    identifies function
    """
    # TDD: Arrange
    # Set up test data

    # TDD: Act
    # Call the function under test

    # TDD: Assert
    # Verify test_040 works correctly
    assert False, 'TDD RED: test_040 not implemented'


def test_050():
    """
    Trivial assertion detection | Auto | Test with only `assert result is
    not None` | CompletenessIssue with category=TRIVIAL_ASSERTION | Issue
    warns about assertion quality
    """
    # TDD: Arrange
    # Set up test data

    # TDD: Act
    # Call the function under test

    # TDD: Assert
    # Verify test_050 works correctly
    assert False, 'TDD RED: test_050 not implemented'


def test_060():
    """
    Unused import detection | Auto | `import os` with no usage |
    CompletenessIssue with category=UNUSED_IMPORT | Issue identifies
    import
    """
    # TDD: Arrange
    # Set up test data

    # TDD: Act
    # Call the function under test

    # TDD: Assert
    # Verify test_060 works correctly
    assert False, 'TDD RED: test_060 not implemented'


def test_070():
    """
    Valid implementation (negative) | Auto | Complete implementation code
    | Empty issues list | No false positives
    """
    # TDD: Arrange
    # Set up test data

    # TDD: Act
    # Call the function under test

    # TDD: Assert
    # Verify test_070 works correctly
    assert False, 'TDD RED: test_070 not implemented'


def test_080():
    """
    BLOCK routes to N4 | Auto | State with verdict='BLOCK', iter<3 |
    Route returns 'N4_implement_code' | Correct routing
    """
    # TDD: Arrange
    # Set up test data

    # TDD: Act
    # Call the function under test

    # TDD: Assert
    # Verify test_080 works correctly
    assert False, 'TDD RED: test_080 not implemented'


def test_090():
    """
    PASS routes to N5 | Auto | State with verdict='PASS' | Route returns
    'N5_verify_green' | Correct routing
    """
    # TDD: Arrange
    # Set up test data

    # TDD: Act
    # Call the function under test

    # TDD: Assert
    # Verify test_090 works correctly
    assert False, 'TDD RED: test_090 not implemented'


def test_100():
    """
    Max iterations ends workflow | Auto | State with verdict='BLOCK',
    iter>=3 | Route returns 'end' | Prevents infinite loop
    """
    # TDD: Arrange
    # Set up test data

    # TDD: Act
    # Call the function under test

    # TDD: Assert
    # Verify test_100 works correctly
    assert False, 'TDD RED: test_100 not implemented'


def test_110():
    """
    Report file generation | Auto | Issue #999, results | File at
    docs/reports/active/999-implementation-report.md | File exists with
    correct structure
    """
    # TDD: Arrange
    # Set up test data

    # TDD: Act
    # Call the function under test

    # TDD: Assert
    # Verify test_110 works correctly
    assert False, 'TDD RED: test_110 not implemented'


def test_120():
    """
    LLD requirement parsing | Auto | LLD with Section 3 requirements |
    List of (id, text) tuples | All requirements extracted
    """
    # TDD: Arrange
    # Set up test data

    # TDD: Act
    # Call the function under test

    # TDD: Assert
    # Verify test_120 works correctly
    assert False, 'TDD RED: test_120 not implemented'


def test_130():
    """
    Review materials preparation | Auto | LLD path + implementation files
    | ReviewMaterials with requirements and code snippets | Materials
    correctly formatted for orchestrator
    """
    # TDD: Arrange
    # Set up test data

    # TDD: Act
    # Call the function under test

    # TDD: Assert
    # Verify test_130 works correctly
    assert False, 'TDD RED: test_130 not implemented'




```

## Previously Implemented Files

These files have already been implemented. Use them for imports and references:

### assemblyzero/workflows/testing/completeness/__init__.py (signatures)

```python
"""Completeness analysis for implementation verification.

Issue #147: Implementation Completeness Gate (Anti-Stub Detection)
Related: #181 (Implementation Report), #335 (N2.5 precedent)

This package provides two-layer completeness analysis:
- Layer 1: AST-based deterministic analysis (fast, free)
- Layer 2: Gemini semantic review materials preparation (orchestrator-controlled)

Modules:
- ast_analyzer: Layer 1 AST-based analysis functions
- report_generator: Implementation verification report generation
"""

from assemblyzero.workflows.testing.completeness.ast_analyzer import (
    analyze_dead_cli_flags,
    analyze_docstring_only_functions,
    analyze_empty_branches,
    analyze_trivial_assertions,
    analyze_unused_imports,
    run_ast_analysis,
)

from assemblyzero.workflows.testing.completeness.report_generator import (
    extract_lld_requirements,
    generate_implementation_report,
    prepare_review_materials,
)
```

### assemblyzero/workflows/testing/completeness/ast_analyzer.py (signatures)

```python
"""Layer 1 AST-based analysis functions for implementation completeness.

Issue #147: Implementation Completeness Gate (Anti-Stub Detection)

Provides deterministic, fast AST-based checks that detect semantically
incomplete implementations:
- Dead CLI flags (argparse add_argument with no usage)
- Empty conditional branches (if/elif/else with only pass/return None)
- Docstring-only functions (functions with docstring + pass/return None)
- Trivial assertions in tests (sole assertion is 'is not None' or similar)
- Unused imports (imports not referenced in function bodies)

These checks form Layer 1 of the two-layer completeness gate. Layer 2
(Gemini semantic review) only runs if Layer 1 passes, for cost control.
"""

from __future__ import annotations

import ast

import logging

import time

from enum import Enum

from pathlib import Path

from typing import Literal, TypedDict

class CompletenessCategory(Enum):

    """Categories of completeness issues for type safety."""

class CompletenessIssue(TypedDict):

    """Single completeness issue detected by analysis."""

class CompletenessResult(TypedDict):

    """Result of completeness analysis."""

def _is_trivial_body(body: list[ast.stmt]) -> bool:
    """Check if a function/branch body is trivial (pass, return None, or ellipsis).

A body is trivial if it contains only:"""
    ...

def _has_docstring(body: list[ast.stmt]) -> bool:
    """Check if a function body starts with a docstring.

Args:"""
    ...

def _collect_name_references(node: ast.AST) -> set[str]:
    """Collect all Name references within an AST subtree.

Args:"""
    ...

def _extract_argparse_flag_names(call_node: ast.Call) -> list[str]:
    """Extract flag names from an argparse add_argument call.

Handles patterns like:"""
    ...

def analyze_dead_cli_flags(
    source_code: str, file_path: str
) -> list[CompletenessIssue]:
    """Detect argparse add_argument calls with no corresponding usage.

Issue #147, Requirement 2: Detects dead CLI flags where argparse"""
    ...

def analyze_empty_branches(
    source_code: str, file_path: str
) -> list[CompletenessIssue]:
    """Detect if/elif/else branches with only pass, return None, or trivial bodies.

Issue #147, Requirement 3: Detects conditional branches that contain"""
    ...

def analyze_docstring_only_functions(
    source_code: str, file_path: str
) -> list[CompletenessIssue]:
    """Detect functions with docstring + pass/return None only.

Issue #147, Requirement 4: Detects functions that have a docstring"""
    ...

def analyze_trivial_assertions(
    source_code: str, file_path: str
) -> list[CompletenessIssue]:
    """Detect test functions where sole assertion is 'is not None' or similar.

Issue #147, Requirement 5: Detects test functions that technically"""
    ...

def _is_trivial_assertion(assertion: ast.Assert) -> bool:
    """Check if an assertion is trivial.

Trivial patterns:"""
    ...

def analyze_unused_imports(
    source_code: str, file_path: str
) -> list[CompletenessIssue]:
    """Detect imports with no usage in function bodies.

Issue #147, Requirement 6: Detects import statements where the"""
    ...

def run_ast_analysis(
    files: list[Path],
    max_file_size_bytes: int = 1_000_000,
) -> CompletenessResult:
    """Run all AST checks on provided files.

Issue #147: Orchestrates all Layer 1 AST-based checks across a set"""
    ...

def _determine_verdict(
    issues: list[CompletenessIssue],
) -> Literal["PASS", "WARN", "BLOCK"]:
    """Determine the overall verdict from a list of issues.

- BLOCK: Any ERROR-severity issue exists"""
    ...

logger = logging.getLogger(__name__)
```

### assemblyzero/workflows/testing/completeness/report_generator.py (signatures)

```python
"""Generate implementation verification reports.

Issue #147: Implementation Completeness Gate (Anti-Stub Detection)
Related: #181 (Implementation Report)

Provides functions to:
- Generate implementation reports to docs/reports/active/{issue}-implementation-report.md
- Extract LLD requirements from Section 3
- Prepare review materials for Gemini semantic review (Layer 2)

Report generation is a side effect of the completeness gate — it does not
block the workflow. If report generation fails, the gate proceeds with
a warning logged.
"""

from __future__ import annotations

import logging

import re

from datetime import datetime, timezone

from pathlib import Path

from typing import TypedDict

from assemblyzero.workflows.testing.completeness.ast_analyzer import (
    CompletenessCategory,
    CompletenessResult,
)

class RequirementVerification(TypedDict):

    """Single LLD requirement verification status."""

class ImplementationReport(TypedDict):

    """Full implementation verification report."""

class ReviewMaterials(TypedDict):

    """Materials prepared for Gemini semantic review."""

def extract_lld_requirements(lld_path: Path) -> list[tuple[int, str]]:
    """Parse Section 3 requirements from LLD markdown.

Issue #147, Requirement 10: Extracts numbered requirements from the"""
    ...

def _verify_requirements(
    requirements: list[tuple[int, str]],
    implementation_files: list[Path],
    completeness_result: CompletenessResult,
) -> list[RequirementVerification]:
    """Verify each LLD requirement against implementation files.

Uses a simple heuristic: searches implementation file contents for"""
    ...

def generate_implementation_report(
    issue_number: int,
    lld_path: Path,
    implementation_files: list[Path],
    completeness_result: CompletenessResult,
    repo_root: Path | None = None,
) -> Path:
    """Generate implementation report to docs/reports/active/{issue}-implementation-report.md.

Issue #147, Requirement 9: Creates a markdown report containing:"""
    ...

def _find_repo_root(start_path: Path) -> Path:
    """Walk up from start_path to find the repository root.

Looks for a directory containing pyproject.toml or .git as indicators."""
    ...

def _format_report(
    *,
    issue_number: int,
    lld_path: Path,
    implementation_files: list[Path],
    completeness_result: CompletenessResult,
    verifications: list[RequirementVerification],
    generated_at: str,
) -> str:
    """Format the implementation report as markdown.

Args:"""
    ...

def _status_icon(status: str) -> str:
    """Return a text icon for requirement verification status.

Args:"""
    ...

def prepare_review_materials(
    issue_number: int,
    lld_path: Path,
    implementation_files: list[Path],
) -> ReviewMaterials:
    """Prepare materials for Gemini semantic review submission by orchestrator.

Issue #147, Requirement 13: Collects LLD requirements and relevant"""
    ...

logger = logging.getLogger(__name__)

REPORTS_ACTIVE_DIR = Path("docs/reports/active")

MAX_SNIPPET_SIZE = 50_000
```

### assemblyzero/workflows/testing/nodes/completeness_gate.py (full)

```python
"""N4b: Implementation Completeness Gate node for TDD Testing Workflow.

Issue #147: Implementation Completeness Gate (Anti-Stub Detection)
Related: #181 (Implementation Report), #335 (N2.5 precedent)

Two-layer validation between N4 (implement_code) and N5 (verify_green):
- Layer 1: AST-based deterministic analysis (fast, free)
- Layer 2: Gemini semantic review materials preparation (orchestrator-controlled)

Fail Mode: Fail Open — if AST analysis fails unexpectedly, proceed to N5
with a warning rather than blocking indefinitely.

Architectural Constraints:
- Cannot modify N4 or N5 node logic (only add N4b between them)
- Gemini calls go through orchestrator (not direct from node)
- Hard iteration limit of 3 prevents infinite N4↔N4b loops
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Literal

from assemblyzero.workflows.testing.audit import (
    get_repo_root,
    log_workflow_execution,
    next_file_number,
    save_audit_file,
)
from assemblyzero.workflows.testing.completeness.ast_analyzer import (
    CompletenessResult,
    run_ast_analysis,
)
from assemblyzero.workflows.testing.completeness.report_generator import (
    generate_implementation_report,
    prepare_review_materials,
)
from assemblyzero.workflows.testing.state import TestingWorkflowState

logger = logging.getLogger(__name__)


# =============================================================================
# Constants
# =============================================================================

# Issue #147, Section 2.5: Hard limit of 3 iterations before routing to end
MAX_COMPLETENESS_ITERATIONS = 3


# =============================================================================
# N4b Node Implementation
# =============================================================================


def completeness_gate(state: TestingWorkflowState) -> dict[str, Any]:
    """N4b: Verify implementation completeness before proceeding to test verification.

    Issue #147: Two-layer completeness gate that detects semantically
    incomplete implementations (stubs, dead flags, trivial assertions)
    before they reach the test verification phase.

    Layer 1 (AST analysis) runs first as a fast, deterministic check.
    If Layer 1 has BLOCK-level issues, Layer 2 is skipped (cost control).
    If Layer 1 passes, Layer 2 materials are prepared for the orchestrator
    to submit to Gemini.

    Fail Mode: If AST analysis raises an unexpected exception, the node
    proceeds with verdict="WARN" to avoid blocking the pipeline.

    Args:
        state: Current workflow state from N4_implement_code.

    Returns:
        State updates with completeness_verdict, completeness_issues,
        implementation_report_path, and review_materials.
    """
    iteration_count = state.get("iteration_count", 0)
    print(f"\n[N4b] Completeness gate (iteration {iteration_count})...")

    # Extract required state
    repo_root_str = state.get("repo_root", "")
    repo_root = Path(repo_root_str) if repo_root_str else get_repo_root()
    issue_number = state.get("issue_number", 0)
    lld_path_str = state.get("lld_path", "")
    implementation_files_strs = state.get("implementation_files", [])
    test_files_strs = state.get("test_files", [])
    audit_dir_str = state.get("audit_dir", "")
    audit_dir = Path(audit_dir_str) if audit_dir_str else None

    # Convert string paths to Path objects
    implementation_files = [Path(f) for f in implementation_files_strs]
    test_files = [Path(f) for f in test_files_strs]
    lld_path = Path(lld_path_str) if lld_path_str else None

    # Combine implementation and test files for analysis
    all_files = implementation_files + test_files

    if not all_files:
        print("    [WARN] No implementation files to analyze — passing through")
        return {
            "completeness_verdict": "PASS",
            "completeness_issues": [],
            "error_message": "",
        }

    print(f"    Analyzing {len(implementation_files)} implementation + {len(test_files)} test files...")

    # =========================================================================
    # Layer 1: AST Analysis
    # =========================================================================

    try:
        ast_result: CompletenessResult = run_ast_analysis(all_files)
    except Exception as e:
        # Fail Open: proceed with warning rather than blocking
        logger.warning(
            "AST analysis failed unexpectedly: %s — proceeding with WARN verdict", e
        )
        print(f"    [WARN] AST analysis failed: {e} — fail open, proceeding")
        ast_result = CompletenessResult(
            verdict="WARN",
            issues=[],
            ast_analysis_ms=0,
            gemini_review_ms=None,
        )

    verdict = ast_result["verdict"]
    issues = ast_result["issues"]
    ast_ms = ast_result["ast_analysis_ms"]

    # Log AST results
    error_count = sum(1 for i in issues if i["severity"] == "ERROR")
    warn_count = sum(1 for i in issues if i["severity"] == "WARNING")
    print(f"    Layer 1 (AST): {verdict} — {error_count} errors, {warn_count} warnings ({ast_ms}ms)")

    for issue in issues:
        severity = issue["severity"]
        category = issue["category"]
        cat_value = category.value if hasattr(category, "value") else str(category)
        print(f"      [{severity}] {cat_value}: {issue['description']}")

    # Save AST analysis to audit trail
    if audit_dir and audit_dir.exists():
        file_num = next_file_number(audit_dir)
        ast_audit = _format_ast_audit(ast_result)
        save_audit_file(
            audit_dir,
            file_num,
            "completeness-ast-analysis.md",
            ast_audit,
        )

    # =========================================================================
    # Layer 2: Gemini Semantic Review (preparation only)
    # =========================================================================

    review_materials = None

    if verdict != "BLOCK" and lld_path and lld_path.exists():
        # Layer 1 passed — prepare materials for orchestrator to submit to Gemini
        print("    Layer 2: Preparing review materials for Gemini...")
        try:
            review_materials = prepare_review_materials(
                issue_number=issue_number,
                lld_path=lld_path,
                implementation_files=implementation_files,
            )
            req_count = len(review_materials.get("lld_requirements", []))
            snippet_count = len(review_materials.get("code_snippets", {}))
            print(f"    Layer 2: Prepared {req_count} requirements, {snippet_count} code snippets")
        except Exception as e:
            # Fail Open: if material preparation fails, log and continue
            logger.warning(
                "Review materials preparation failed: %s — skipping Layer 2", e
            )
            print(f"    [WARN] Layer 2 preparation failed: {e} — skipping")
    elif verdict == "BLOCK":
        print("    Layer 2: Skipped (Layer 1 BLOCK)")
    else:
        print("    Layer 2: Skipped (no LLD path available)")

    # =========================================================================
    # Report Generation (side effect — does not block)
    # =========================================================================

    implementation_report_path = ""

    if lld_path and lld_path.exists():
        print("    Generating implementation report...")
        try:
            report_path = generate_implementation_report(
                issue_number=issue_number,
                lld_path=lld_path,
                implementation_files=implementation_files,
                completeness_result=ast_result,
                repo_root=repo_root,
            )
            implementation_report_path = str(report_path)
            print(f"    Report: {report_path}")
        except Exception as e:
            # Report generation is a side effect — log and continue
            logger.warning(
                "Report generation failed: %s — continuing without report", e
            )
            print(f"    [WARN] Report generation failed: {e}")
    else:
        print("    [WARN] No LLD path — skipping report generation")

    # Save report path to audit
    if audit_dir and audit_dir.exists() and implementation_report_path:
        file_num = next_file_number(audit_dir)
        save_audit_file(
            audit_dir,
            file_num,
            "completeness-report-path.txt",
            implementation_report_path,
        )

    # =========================================================================
    # Log to workflow execution audit
    # =========================================================================

    log_workflow_execution(
        target_repo=repo_root,
        issue_number=issue_number,
        workflow_type="testing",
        event="completeness_gate",
        details={
            "verdict": verdict,
            "error_count": error_count,
            "warning_count": warn_count,
            "ast_ms": ast_ms,
            "iteration": iteration_count,
            "report_path": implementation_report_path,
            "layer2_prepared": review_materials is not None,
        },
    )

    # =========================================================================
    # Return state updates
    # =========================================================================

    result: dict[str, Any] = {
        "completeness_verdict": verdict,
        "completeness_issues": issues,
        "implementation_report_path": implementation_report_path,
        "error_message": "",
    }

    # Include review materials if prepared (for orchestrator to submit to Gemini)
    if review_materials is not None:
        result["review_materials"] = review_materials

    print(f"    Completeness gate verdict: {verdict}")
    return result


# =============================================================================
# Routing Function
# =============================================================================


def route_after_completeness_gate(
    state: TestingWorkflowState,
) -> Literal["N5_verify_green", "N4_implement_code", "end"]:
    """Route based on completeness verdict and iteration count.

    Issue #147, Requirements 7, 8, 12:
    - BLOCK verdict: route back to N4 for re-implementation (up to 3 iterations)
    - PASS/WARN verdict: route forward to N5
    - BLOCK at max iterations (3): route to end (hard stop)

    Args:
        state: Current workflow state with completeness_verdict set.

    Returns:
        Next node name: "N5_verify_green", "N4_implement_code", or "end".
    """
    error = state.get("error_message", "")
    if error:
        return "end"

    verdict = state.get("completeness_verdict", "")
    iteration_count = state.get("iteration_count", 0)

    if verdict == "BLOCK":
        if iteration_count >= MAX_COMPLETENESS_ITERATIONS:
            print(
                f"    [N4b] BLOCK at iteration {iteration_count} "
                f"(max {MAX_COMPLETENESS_ITERATIONS}) — routing to end"
            )
            return "end"
        print(
            f"    [N4b] BLOCK — routing back to N4 "
            f"(iteration {iteration_count}/{MAX_COMPLETENESS_ITERATIONS})"
        )
        return "N4_implement_code"

    # PASS or WARN — proceed to N5
    print(f"    [N4b] {verdict} — routing to N5_verify_green")
    return "N5_verify_green"


# =============================================================================
# Audit Formatting
# =============================================================================


def _format_ast_audit(result: CompletenessResult) -> str:
    """Format AST analysis result as a markdown audit entry.

    Args:
        result: CompletenessResult from Layer 1 analysis.

    Returns:
        Formatted markdown string.
    """
    lines = [
        "# Completeness Gate: AST Analysis",
        "",
        f"**Verdict:** {result['verdict']}",
        f"**Analysis Time:** {result['ast_analysis_ms']}ms",
        f"**Issues Found:** {len(result['issues'])}",
        "",
    ]

    if result["issues"]:
        lines.append("## Issues")
        lines.append("")
        lines.append("| Severity | Category | File | Line | Description |")
        lines.append("|----------|----------|------|------|-------------|")

        for issue in result["issues"]:
            category = issue["category"]
            cat_value = category.value if hasattr(category, "value") else str(category)
            file_name = Path(issue["file_path"]).name
            desc = issue["description"].replace("|", "\\|")
            lines.append(
                f"| {issue['severity']} "
                f"| {cat_value} "
                f"| `{file_name}` "
                f"| {issue['line_number']} "
                f"| {desc} |"
            )
        lines.append("")
    else:
        lines.append("*No issues detected.*")
        lines.append("")

    return "\n".join(lines)
```

## Output Format

Output ONLY the file contents. No explanations, no markdown headers, just the code.

```python
# Your implementation here
```

IMPORTANT:
- Output the COMPLETE file contents
- Do NOT output a summary or description
- Do NOT say "I've implemented..."
- Just output the code in a single code block
