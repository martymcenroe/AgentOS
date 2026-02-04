# 171 - Feature: Add mandatory diff review gate before commit in TDD workflow

<!-- Template Metadata
Last Updated: 2025-01-XX
Updated By: Initial LLD creation
Update Reason: New feature to prevent accidental code destruction during TDD workflow
-->

## 1. Context & Goal
* **Issue:** #171
* **Objective:** Add a mandatory diff review gate that prevents commits without explicit human approval, especially for files with significant changes
* **Status:** Draft
* **Related Issues:** #168 (bug caused by missing gate), PR #165 (the breaking change)

### Open Questions
*All questions resolved during review.*

## 2. Proposed Changes

*This section is the **source of truth** for implementation. Describe exactly what will be built.*

### 2.1 Files Changed

| File | Change Type | Description |
|------|-------------|-------------|
| `src/workflows/tdd/nodes/diff_review_gate.py` | Add | New node implementing the diff review gate |
| `src/workflows/tdd/graph.py` | Modify | Add diff_review_gate node before commit node |
| `src/workflows/tdd/state.py` | Modify | Add diff review state fields |
| `src/workflows/tdd/models.py` | Modify | Add DiffAnalysis and FileChangeReport models |
| `tests/unit/test_diff_review_gate.py` | Add | Unit tests for diff review gate |
| `tests/integration/test_tdd_workflow_diff_gate.py` | Add | Integration tests for workflow with gate |

### 2.2 Dependencies

*New packages, APIs, or services required.*

```toml
# pyproject.toml additions (if any)
# No new dependencies - uses stdlib subprocess for git commands
```

### 2.3 Data Structures

```python
# Pseudocode - NOT implementation
class FileChangeReport(TypedDict):
    filepath: str               # Relative path to changed file
    lines_before: int           # Line count before change
    lines_after: int            # Line count after change
    lines_added: int            # Lines added
    lines_deleted: int          # Lines deleted
    change_ratio: float         # Percentage of file changed (0.0-1.0)
    is_replacement: bool        # True if >80% content replaced
    requires_review: bool       # True if change_ratio > threshold

class DiffReviewState(TypedDict):
    diff_stat: str                          # Raw git diff --stat output
    file_reports: list[FileChangeReport]    # Analysis per file
    flagged_files: list[str]                # Files requiring explicit review
    review_approved: bool                   # Human approval status
    approval_timestamp: str | None          # When approval was given
    approval_message: str | None            # Optional approval comment
```

### 2.4 Function Signatures

```python
# Signatures only - implementation in source files
def diff_review_gate(state: WorkflowState) -> dict:
    """Mandatory diff review node - blocks commit until approved."""
    ...

def analyze_git_diff() -> tuple[str, list[FileChangeReport]]:
    """Run git diff --stat and analyze changes per file."""
    ...

def calculate_change_ratio(filepath: str) -> FileChangeReport:
    """Calculate the change ratio for a single file."""
    ...

def format_diff_report(reports: list[FileChangeReport]) -> str:
    """Format diff analysis for human-readable display."""
    ...

def detect_file_replacement(filepath: str, lines_before: int, lines_after: int) -> bool:
    """Detect if file was replaced rather than modified."""
    ...

async def request_human_approval(
    flagged_files: list[FileChangeReport],
    diff_stat: str
) -> tuple[bool, str]:
    """Display diff and request explicit human approval."""
    ...

def run_git_command(args: list[str]) -> str:
    """Execute git command safely using list-based subprocess call.
    
    SECURITY: Always uses shell=False and list arguments to prevent injection.
    """
    ...
```

### 2.5 Logic Flow (Pseudocode)

```
1. diff_review_gate node triggered before commit
2. Run `git diff --stat --staged` to get overview (via run_git_command with list args)
3. FOR each changed file:
   a. Get line count before (git show HEAD:file | wc -l) via run_git_command
   b. Get line count after (wc -l < file)
   c. Calculate change_ratio = (added + deleted) / max(lines_before, 1)
   d. Detect replacement: ratio > 0.8 AND lines_after < lines_before * 0.5
   e. Flag if change_ratio > 0.5 (hardcoded threshold: CHANGE_RATIO_THRESHOLD = 0.5)
4. IF any flagged files:
   a. Display WARNING banner with file list
   b. For each flagged file, show:
      - "WARNING: 80% of {file} was replaced" (or "REPLACED" for replacement detection)
      - Before/after line counts
      - Full diff for that file
   c. Require explicit approval: "Type APPROVE to continue or REJECT to abort"
5. ELSE (no flagged files):
   a. Display diff stat summary
   b. Still require approval but with softer prompt
6. IF approved:
   a. Record approval timestamp and message
   b. Return state with review_approved=True
   c. Proceed to commit node
7. ELSE:
   a. Return state with review_approved=False
   b. Workflow halts - user must fix and retry
8. CRITICAL: Cannot be bypassed even in --auto mode
   - If --auto flag detected, FAIL with error message
   - "Diff review gate cannot be bypassed. Manual approval required."
```

### 2.6 Technical Approach

* **Module:** `src/workflows/tdd/nodes/`
* **Pattern:** LangGraph interrupt pattern for human-in-the-loop
* **Key Decisions:** 
  - Uses git subprocess calls rather than python git libraries for simplicity
  - **SECURITY:** All subprocess calls use `shell=False` with list-based arguments to prevent command injection
  - Implements as a blocking node that cannot be auto-approved
  - Calculates change ratio based on line counts, not semantic diff

### 2.7 Architecture Decisions

*Document key architectural decisions that affect the design.*

| Decision | Options Considered | Choice | Rationale |
|----------|-------------------|--------|-----------|
| Approval mechanism | Auto-approve below threshold, Always require approval | Always require approval | PR #165 showed even "small" changes can be destructive |
| Change detection | Semantic diff, Line-based diff, File hash comparison | Line-based diff | Simple, fast, sufficient for detecting major changes |
| Bypass behavior | Allow bypass with flag, No bypass possible | No bypass possible | Gate exists specifically to prevent auto-commits |
| Threshold configuration | Hardcoded, Config file, CLI flag | Hardcoded constant (0.5) | Start simple; can add config in future issue |
| Subprocess execution | shell=True with string, shell=False with list | shell=False with list | Eliminates command injection risk by design |

**Architectural Constraints:**
- Must integrate with existing LangGraph workflow structure
- Cannot add external dependencies (use stdlib only)
- Must work with both staged and unstaged changes
- All subprocess calls MUST use `shell=False` with list arguments

## 3. Requirements

*What must be true when this is done. These become acceptance criteria.*

1. Workflow MUST show `git diff --stat` before any commit
2. Files with >50% change ratio MUST be flagged with WARNING banner
3. Human MUST explicitly type "APPROVE" (not auto-skip)
4. Diff review gate MUST NOT be bypassable in --auto mode
5. Files that are REPLACED (>80% change, reduced line count) MUST be specially flagged
6. Gate MUST block workflow until approval or rejection received
7. Rejection MUST halt workflow without committing

## 4. Alternatives Considered

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Pre-commit hook | Standard git pattern, language agnostic | Can be bypassed with --no-verify, not integrated with workflow state | **Rejected** |
| LangGraph interrupt node | Integrated with workflow, cannot bypass, maintains state | Requires workflow modification | **Selected** |
| Separate review step after commit | Doesn't block bad commits | Defeats the purpose - damage already done | **Rejected** |
| AI-powered semantic diff | Could catch logical errors, not just line changes | Complex, slow, may miss obvious issues | **Rejected** |

**Rationale:** LangGraph interrupt node is selected because it's the only option that truly cannot be bypassed and maintains full workflow state. Pre-commit hooks are too easily bypassed, and post-commit review defeats the purpose.

## 5. Data & Fixtures

*Per [0108-lld-pre-implementation-review.md](0108-lld-pre-implementation-review.md) - complete this section BEFORE implementation.*

### 5.1 Data Sources

| Attribute | Value |
|-----------|-------|
| Source | Local git repository (subprocess calls) |
| Format | Git diff output (text), line counts (integers) |
| Size | Varies by changeset, typically <1MB |
| Refresh | Real-time per workflow run |
| Copyright/License | N/A - local repository data |

### 5.2 Data Pipeline

```
git diff --stat ──subprocess──► Parse stats ──python──► FileChangeReport objects
git show HEAD:file ──subprocess──► Line count (before)
wc -l file ──subprocess──► Line count (after)
FileChangeReports ──analysis──► Flagged files list ──display──► Human review
```

### 5.3 Test Fixtures

| Fixture | Source | Notes |
|---------|--------|-------|
| Mock git diff output | Generated | Various scenarios: small change, large change, replacement |
| Sample file states | Generated | Before/after versions of test files |
| Approval responses | Hardcoded | "APPROVE", "REJECT", invalid inputs |
| Malicious filenames | Generated | Files with shell metacharacters for injection testing |

### 5.4 Deployment Pipeline

Test fixtures are self-contained - no external data deployment needed.

**If data source is external:** N/A - all data is local git repository state.

## 6. Diagram

### 6.1 Mermaid Quality Gate

Before finalizing any diagram, verify in [Mermaid Live Editor](https://mermaid.live) or GitHub preview:

- [x] **Simplicity:** Similar components collapsed (per 0006 §8.1)
- [x] **No touching:** All elements have visual separation (per 0006 §8.2)
- [x] **No hidden lines:** All arrows fully visible (per 0006 §8.3)
- [x] **Readable:** Labels not truncated, flow direction clear
- [ ] **Auto-inspected:** Agent rendered via mermaid.ink and viewed (per 0006 §8.5)

**Agent Auto-Inspection (MANDATORY):**

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
flowchart TD
    subgraph TDD["TDD Workflow"]
        A[Write Test] --> B[Run Test - RED]
        B --> C[Implement Code]
        C --> D[Run Test - GREEN]
        D --> E[Refactor]
        E --> F{Ready to Commit?}
    end
    
    subgraph DRG["Diff Review Gate"]
        F -->|Yes| G[git diff --stat]
        G --> H{Files > 50% Changed?}
        H -->|Yes| I[Show WARNING Banner]
        H -->|No| J[Show Summary]
        I --> K[Display Full Diff]
        K --> L{Human Approval}
        J --> L
        L -->|APPROVE| M[Record Approval]
        L -->|REJECT| N[Halt Workflow]
    end
    
    subgraph Commit["Commit Phase"]
        M --> O[git commit]
        O --> P[Continue Workflow]
    end
    
    N --> Q[User Fixes Issues]
    Q --> A
```

```mermaid
sequenceDiagram
    participant W as TDD Workflow
    participant DRG as DiffReviewGate
    participant Git as Git CLI
    participant H as Human

    W->>DRG: Trigger before commit
    DRG->>Git: git diff --stat --staged
    Git-->>DRG: Diff statistics
    
    loop For each changed file
        DRG->>Git: git show HEAD:file
        Git-->>DRG: Original content
        DRG->>DRG: Calculate change ratio
    end
    
    alt Files flagged (>50% change)
        DRG->>H: ⚠️ WARNING: Major changes detected
        DRG->>H: Show file details & full diff
    else No flags
        DRG->>H: Show diff summary
    end
    
    DRG->>H: Request approval (APPROVE/REJECT)
    
    alt Approved
        H-->>DRG: APPROVE
        DRG->>DRG: Record timestamp
        DRG-->>W: review_approved=True
        W->>Git: git commit
    else Rejected
        H-->>DRG: REJECT
        DRG-->>W: review_approved=False
        W->>W: Halt workflow
    end
```

## 7. Security & Safety Considerations

### 7.1 Security

| Concern | Mitigation | Status |
|---------|------------|--------|
| Command injection via filenames | All subprocess calls use `shell=False` with list-based arguments; no shell interpolation possible | Addressed by design |
| Unauthorized approval | Approval requires interactive terminal session | Addressed |

### 7.2 Safety

*Safety concerns focus on preventing data loss, ensuring fail-safe behavior, and protecting system integrity.*

| Concern | Mitigation | Status |
|---------|------------|--------|
| Accidental data loss (PR #165 scenario) | Mandatory review of all changes before commit | Addressed |
| Auto-mode bypass | Explicit check and fail if --auto detected | Addressed |
| False negative (missing dangerous change) | Show full diff for any flagged file, not just stats | Addressed |
| Workflow state corruption | Atomic state updates, clear approval status on error | Addressed |

**Fail Mode:** Fail Closed - If any error occurs during diff analysis, workflow halts rather than allowing commit

**Recovery Strategy:** On failure, workflow state is preserved. User can fix issues and re-run. No partial commits possible.

## 8. Performance & Cost Considerations

### 8.1 Performance

| Metric | Budget | Approach |
|--------|--------|----------|
| Latency | < 5s for typical changeset | Use git subprocess, cache repeated calls |
| Memory | < 50MB | Stream large diffs, don't load entirely into memory |
| Git Calls | 2 + N (N = changed files) | Batch where possible |

**Bottlenecks:** Large files or many changed files may slow analysis. Consider streaming for files > 1MB.

### 8.2 Cost Analysis

| Resource | Unit Cost | Estimated Usage | Monthly Cost |
|----------|-----------|-----------------|--------------|
| Compute | Local | N/A | $0 |
| Storage | Local | N/A | $0 |

**Cost Controls:**
- N/A - All operations are local

**Worst-Case Scenario:** Very large changeset (1000+ files) may take 30+ seconds to analyze. Acceptable for safety-critical gate.

## 9. Legal & Compliance

| Concern | Applies? | Mitigation |
|---------|----------|------------|
| PII/Personal Data | No | Gate only processes code diffs |
| Third-Party Licenses | No | No new dependencies |
| Terms of Service | N/A | Local git operations only |
| Data Retention | No | No persistent storage of diffs |
| Export Controls | No | Standard development tooling |

**Data Classification:** Internal (code under development)

**Compliance Checklist:**
- [x] No PII stored without consent
- [x] All third-party licenses compatible with project license
- [x] External API usage compliant with provider ToS
- [x] Data retention policy documented

## 10. Verification & Testing

*Ref: [0005-testing-strategy-and-protocols.md](0005-testing-strategy-and-protocols.md)*

**Testing Philosophy:** Strive for 100% automated test coverage.

### 10.0 Test Plan (TDD - Complete Before Implementation)

**TDD Requirement:** Tests MUST be written and failing BEFORE implementation begins.

| Test ID | Test Description | Expected Behavior | Status |
|---------|------------------|-------------------|--------|
| T010 | test_diff_stat_parsing | Correctly parse git diff --stat output | RED |
| T015 | test_malicious_filename_handling | Safely handle files with shell metacharacters | RED |
| T020 | test_change_ratio_calculation | Calculate accurate change ratios | RED |
| T030 | test_replacement_detection | Detect replaced vs modified files | RED |
| T040 | test_flagging_threshold | Flag files > 50% changed | RED |
| T050 | test_approval_flow_approve | Approval allows workflow to continue | RED |
| T060 | test_approval_flow_reject | Rejection halts workflow | RED |
| T070 | test_auto_mode_blocked | --auto mode cannot bypass gate | RED |
| T080 | test_no_changes_scenario | Handle no staged changes gracefully | RED |
| T090 | test_report_formatting | Human-readable report format | RED |
| T100 | test_integration_workflow | Full workflow with gate | RED |

**Coverage Target:** ≥95% for all new code

**TDD Checklist:**
- [ ] All tests written before implementation
- [ ] Tests currently RED (failing)
- [ ] Test IDs match scenario IDs in 10.1
- [ ] Test file created at: `tests/unit/test_diff_review_gate.py`

### 10.1 Test Scenarios

| ID | Scenario | Type | Input | Expected Output | Pass Criteria |
|----|----------|------|-------|-----------------|---------------|
| 010 | Parse simple diff stat | Auto | "file.py \| 10 ++--" | Parsed FileChangeReport | Lines parsed correctly |
| 015 | Handle malicious filename | Auto | File named `test; rm -rf.py` or `$(whoami).txt` | Safe execution, no injection | Command executes safely, file processed normally |
| 020 | Calculate 50% change ratio | Auto | File: 100→50 lines, 50 deleted | change_ratio=0.5 | Ratio within 0.01 |
| 030 | Detect file replacement | Auto | File: 270→56 lines, 80% deleted | is_replacement=True | Flag set correctly |
| 040 | Flag file over threshold | Auto | change_ratio=0.6 | requires_review=True | Flag set when >0.5 |
| 050 | Approval continues workflow | Auto | Mocked input returning "APPROVE" | review_approved=True | State updated, no error |
| 060 | Rejection halts workflow | Auto | Mocked input returning "REJECT" | review_approved=False | Workflow halted cleanly |
| 070 | Auto mode raises error | Auto | --auto flag + gate | RuntimeError raised | Error message mentions bypass |
| 080 | No staged changes | Auto | Empty git diff | Empty report, soft prompt | No error, allow proceed |
| 090 | Format multi-file report | Auto | 3 FileChangeReports | Formatted string | Contains all files, warnings |
| 100 | Integration: PR #165 scenario | Auto | 270→56 line state.py | WARNING shown, approval required | Cannot commit without APPROVE |

**Note on Input Mocking (T050/T060):** User input is mocked via `unittest.mock.patch` on the `input()` function or LangGraph interrupt payload mechanism. Tests are fully automated and do not require manual interaction.

### 10.2 Test Commands

```bash
# Run all automated tests
poetry run pytest tests/unit/test_diff_review_gate.py -v

# Run only fast/mocked tests (exclude live)
poetry run pytest tests/unit/test_diff_review_gate.py -v -m "not live"

# Run integration tests
poetry run pytest tests/integration/test_tdd_workflow_diff_gate.py -v

# Run with coverage
poetry run pytest tests/ -v --cov=src/workflows/tdd/nodes/diff_review_gate --cov-report=term-missing
```

### 10.3 Manual Tests (Only If Unavoidable)

**N/A - All scenarios automated.**

## 11. Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Developer friction from mandatory review | Med | Med | Clear messaging explaining why gate exists; fast path for small changes |
| False positives flagging legitimate refactors | Low | Med | Show full diff so human can make informed decision |
| Git subprocess failures | High | Low | Graceful error handling, clear error messages |
| Change ratio calculation edge cases | Med | Med | Comprehensive test coverage, handle division by zero |
| Approval token collision | Low | Low | Use unique token "APPROVE" not likely in normal text |

## 12. Definition of Done

### Code
- [ ] Implementation complete and linted
- [ ] Code comments reference this LLD (#171)

### Tests
- [ ] All test scenarios pass (T010-T100)
- [ ] Test coverage ≥95% for new code

### Documentation
- [ ] LLD updated with any deviations
- [ ] Implementation Report (0103) completed
- [ ] Test Report (0113) completed if applicable

### Review
- [ ] Code review completed
- [ ] User approval before closing issue

---

## Appendix: Review Log

*Track all review feedback with timestamps and implementation status.*

### Gemini Review #1 (REVISE)

**Reviewer:** Gemini 3 Pro
**Verdict:** REVISE

#### Comments

| ID | Comment | Implemented? |
|----|---------|--------------|
| G1.1 | "Unaddressed Command Injection Risk: Section 7.1 lists 'Command injection via filenames' mitigation as 'TODO'. Must mandate shell=False and list-based arguments or add test case T015." | YES - Added T015 test scenario in 10.0/10.1, updated 7.1 Security status to "Addressed by design", added architectural decision in 2.7, added run_git_command signature in 2.4, updated 2.6 Technical Approach |
| G1.2 | "Test Assertion Specificity (T050/T060): Ensure test plan explicitly mocks input() function rather than relying on manual interaction." | YES - Added clarification note in Section 10.1 after the test scenarios table |
| G1.3 | "Open questions should be resolved" | YES - Resolved all three open questions, removed question markers |

### Review Summary

| Review | Date | Verdict | Key Issue |
|--------|------|---------|-----------|
| Gemini #1 | (auto) | REVISE | Command injection risk unaddressed |

**Final Status:** PENDING