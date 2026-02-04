# 184 - Feature: Add [F]ile Option to Issue Workflow Exit

<!-- Template Metadata
Last Updated: 2025-01-XX
Updated By: LLD Creation for Issue #84
Update Reason: Initial LLD creation
-->

## 1. Context & Goal
* **Issue:** #84
* **Objective:** Add a `[F]ile` option to the issue workflow that automatically creates missing labels and files issues to GitHub, eliminating manual `gh` command execution after draft approval.
* **Status:** Draft
* **Related Issues:** None

### Open Questions
*Questions that need clarification before or during implementation. Remove when resolved.*

- [x] Should we support custom label colors via configuration? → Deferred to future enhancement
- [x] What happens if the repo has label creation restrictions? → Fail with clear error, keep user in workflow

## 2. Proposed Changes

*This section is the **source of truth** for implementation. Describe exactly what will be built.*

### 2.1 Files Changed

| File | Change Type | Description |
|------|-------------|-------------|
| `agentos/workflows/issue/run_issue_workflow.py` | Modify | Add `[F]ile` option to menu, integrate filing orchestration |
| `agentos/workflows/issue/file_issue.py` | Add | New module with draft parsing, label management, and issue filing |
| `agentos/workflows/issue/label_colors.py` | Add | Label category to color mapping constants |
| `tests/unit/test_file_issue.py` | Add | Unit tests for draft parsing and label color mapping |
| `tests/unit/test_label_colors.py` | Add | Unit tests for label color resolution |
| `tests/integration/test_file_issue_integration.py` | Add | Integration tests with mock `gh` CLI |

### 2.2 Dependencies

*New packages, APIs, or services required.*

```toml
# pyproject.toml additions (if any)
# None - uses standard library only
```

**External Dependencies:**
- `gh` CLI (GitHub CLI) - must be installed and authenticated
- No new Python packages required

### 2.3 Data Structures

```python
# Pseudocode - NOT implementation
class ParsedDraft(TypedDict):
    title: str           # Extracted from first H1 line
    body: str            # Content between User Story and Labels sections
    labels: list[str]    # Parsed from backtick-delimited list
    parse_errors: list[str]  # Any warnings/errors during parsing

class FilingResult(TypedDict):
    success: bool        # Whether filing succeeded
    issue_url: str | None  # GitHub issue URL if successful
    labels_created: list[str]  # Labels that were created
    error: str | None    # Error message if failed

class LabelInfo(TypedDict):
    name: str            # Label name
    exists: bool         # Whether label exists in repo
    color: str           # Hex color (without #)
```

### 2.4 Function Signatures

```python
# file_issue.py - Signatures only

def verify_gh_auth() -> bool:
    """Verify gh CLI is authenticated. Returns True if auth valid."""
    ...

def parse_draft_for_filing(draft_path: Path) -> ParsedDraft:
    """Extract title, body, and labels from draft markdown file."""
    ...

def get_existing_labels(repo: str | None = None) -> set[str]:
    """Fetch set of existing label names from GitHub repo."""
    ...

def ensure_labels_exist(
    labels: list[str], 
    repo: str | None = None,
    on_created: Callable[[str], None] | None = None
) -> list[str]:
    """Create missing labels with appropriate colors. Returns list of created labels."""
    ...

def file_issue(
    title: str, 
    body: str, 
    labels: list[str], 
    repo: str | None = None
) -> str:
    """File issue via gh CLI. Returns issue URL."""
    ...

def update_metadata_with_issue(
    metadata_path: Path, 
    issue_url: str
) -> None:
    """Update 003-metadata.json with issue URL and timestamp."""
    ...

def run_file_workflow(
    draft_path: Path, 
    metadata_path: Path,
    repo: str | None = None
) -> FilingResult:
    """Orchestrate full filing workflow. Main entry point."""
    ...
```

```python
# label_colors.py - Signatures only

def get_label_color(label_name: str) -> str:
    """Return hex color (without #) for label based on category mapping."""
    ...
```

### 2.5 Logic Flow (Pseudocode)

```
run_file_workflow(draft_path, metadata_path, repo):
    1. Verify gh CLI authentication
       IF not authenticated THEN
         - Return error: "gh CLI not authenticated. Run 'gh auth login' first."
    
    2. Parse draft for title, body, labels
       IF no title (H1) found THEN
         - Return error: "Draft missing title (no H1 found)"
       IF labels line malformed THEN
         - Add warning to result
         - Continue with empty labels list
    
    3. Ensure all labels exist
       - Fetch existing labels from repo
       - FOR each label not existing:
         - Get color from category mapping
         - Create label via gh CLI
         - Report progress via callback
    
    4. File issue via gh CLI
       - Run: gh issue create --title {title} --body {body} --label {labels}
       - Capture issue URL from output
    
    5. Update metadata
       - Add github_issue_url to 003-metadata.json
       - Add filed_at timestamp
    
    6. Return success with issue URL

parse_draft_for_filing(draft_path):
    1. Read draft content
    2. Find first line starting with "# " → title
       IF not found THEN set parse_error
    3. Find content between "## User Story" and "## Labels" → body
       IF User Story not found THEN use content after title
    4. Find "## Labels" line, extract backtick-delimited items → labels
       IF malformed THEN add warning, set labels = []
    5. Return ParsedDraft
```

### 2.6 Technical Approach

* **Module:** `agentos/workflows/issue/`
* **Pattern:** Functional composition with explicit error handling
* **Key Decisions:**
  - Use `subprocess.run()` with list arguments exclusively for shell safety
  - Fail fast on authentication but graceful degradation on label parsing
  - Keep user in workflow on all errors (no workflow exit on failure)
  - Single orchestration function coordinates all steps for testability

### 2.7 Architecture Decisions

| Decision | Options Considered | Choice | Rationale |
|----------|-------------------|--------|-----------|
| Subprocess invocation | `shell=True` with string, `subprocess.run()` with list | List arguments | Security: prevents shell injection from draft content |
| Error handling | Exceptions, Result types, Error codes | Return dataclass with success/error fields | Clear API, easy testing, no exception handling needed by caller |
| Label creation | Batch create, Individual create with progress | Individual with progress callback | Better UX (shows progress), simpler error recovery |
| Draft parsing | Regex, Line-by-line, Markdown parser | Line-by-line with simple rules | Sufficient for structured drafts, no external dependencies |

**Architectural Constraints:**
- Must work with existing workflow loop structure in `run_issue_workflow.py`
- Cannot modify `gh` CLI behavior or require additional configuration
- Must preserve all existing metadata fields when updating JSON

## 3. Requirements

*What must be true when this is done. These become acceptance criteria.*

1. `[F]ile` option appears in workflow exit menu alongside existing options
2. Draft parsing extracts title from first H1, body from content sections, labels from backtick list
3. Missing labels are automatically created with category-appropriate colors
4. Issue is filed via `gh issue create` and URL is displayed to user
5. `003-metadata.json` is updated with `github_issue_url` and `filed_at` timestamp
6. Unauthenticated `gh` CLI produces clear error without crashing workflow
7. Missing title produces clear error and keeps user in workflow
8. Malformed labels line produces warning and files issue without labels
9. All subprocess calls use list arguments (never `shell=True`)

## 4. Alternatives Considered

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Use PyGithub library directly | Full API access, no CLI dependency | New dependency, auth complexity, more code | **Rejected** |
| Shell out to `gh` CLI with list args | No new deps, uses existing auth, simple | Requires `gh` installed | **Selected** |
| Use GitHub REST API with requests | No CLI dependency | Auth token management, more code | Rejected |
| Batch label creation | Fewer API calls | No progress feedback, complex error handling | Rejected |

**Rationale:** The `gh` CLI is already the standard tool for GitHub interaction in this project. It handles authentication, rate limiting, and API versioning. Using list arguments with `subprocess.run()` provides security equivalent to library approaches while minimizing new code.

## 5. Data & Fixtures

### 5.1 Data Sources

| Attribute | Value |
|-----------|-------|
| Source | Local draft files (`active/{project}/001-draft.md`) |
| Format | Markdown with structured sections |
| Size | Typically 1-5 KB per draft |
| Refresh | User-edited during workflow |
| Copyright/License | N/A - user-generated content |

### 5.2 Data Pipeline

```
Draft File ──read──► Parser ──extract──► Structured Data ──subprocess──► GitHub API
                                              │
                                              ▼
                                    003-metadata.json ◄──update
```

### 5.3 Test Fixtures

| Fixture | Source | Notes |
|---------|--------|-------|
| `fixtures/valid_draft.md` | Hardcoded | Complete draft with all sections |
| `fixtures/draft_no_title.md` | Hardcoded | Missing H1 line |
| `fixtures/draft_malformed_labels.md` | Hardcoded | Labels section without backticks |
| `fixtures/draft_shell_injection.md` | Hardcoded | Title with `; rm -rf /` for security testing |
| `mock_gh_responses/` | Hardcoded | Mock `gh` CLI output for integration tests |

### 5.4 Deployment Pipeline

No external data sources. All data is local (draft files, metadata JSON) and GitHub API (via `gh` CLI).

## 6. Diagram

### 6.1 Mermaid Quality Gate

Before finalizing any diagram, verify in [Mermaid Live Editor](https://mermaid.live) or GitHub preview:

- [x] **Simplicity:** Similar components collapsed (per 0006 §8.1)
- [x] **No touching:** All elements have visual separation (per 0006 §8.2)
- [x] **No hidden lines:** All arrows fully visible (per 0006 §8.3)
- [x] **Readable:** Labels not truncated, flow direction clear
- [ ] **Auto-inspected:** Agent rendered via mermaid.ink and viewed (per 0006 §8.5)

**Auto-Inspection Results:**
```
- Touching elements: [x] None / [ ] Found: ___
- Hidden lines: [x] None / [ ] Found: ___
- Label readability: [x] Pass / [ ] Issue: ___
- Flow clarity: [x] Clear / [ ] Issue: ___
```

### 6.2 Diagram

```mermaid
sequenceDiagram
    participant U as User
    participant W as Workflow
    participant P as Parser
    participant L as LabelManager
    participant GH as gh CLI
    participant M as Metadata

    U->>W: Select [F]ile
    W->>GH: verify auth
    GH-->>W: auth OK
    
    W->>P: parse_draft(path)
    P-->>W: {title, body, labels}
    
    W->>L: ensure_labels_exist(labels)
    L->>GH: gh label list
    GH-->>L: existing labels
    
    loop For each missing label
        L->>GH: gh label create
        GH-->>L: created
        L-->>W: progress callback
    end
    
    W->>GH: gh issue create
    GH-->>W: issue URL
    
    W->>M: update metadata
    M-->>W: done
    
    W-->>U: ✓ Created: {URL}
```

## 7. Security & Safety Considerations

### 7.1 Security

| Concern | Mitigation | Status |
|---------|------------|--------|
| Shell injection via draft content | All `subprocess.run()` calls use list arguments, never `shell=True` or string interpolation | Addressed |
| Credential exposure | Uses existing `gh` CLI auth, no credentials stored in code | Addressed |
| Unauthorized label creation | Uses same auth as manual `gh` commands, no privilege escalation | Addressed |

### 7.2 Safety

| Concern | Mitigation | Status |
|---------|------------|--------|
| Data loss on parse failure | Original draft never modified, only read | Addressed |
| Partial filing (labels created but issue fails) | Labels are idempotent, can retry without side effects | Addressed |
| Metadata corruption | Read existing JSON, merge new fields, write atomically | Addressed |

**Fail Mode:** Fail Closed - On any error, user stays in workflow with all options available. No partial state committed.

**Recovery Strategy:** User can retry `[F]ile` option or fall back to `[M]anual` mode. Created labels persist but are harmless duplicates if issue filing is retried.

## 8. Performance & Cost Considerations

### 8.1 Performance

| Metric | Budget | Approach |
|--------|--------|----------|
| Latency | < 10s total | Most time in network calls to GitHub |
| Memory | < 50MB | Only reads single draft file |
| API Calls | 1 + N labels | Minimize by checking existing labels first |

**Bottlenecks:** GitHub API latency for label creation (sequential calls). Acceptable for typical 1-4 labels.

### 8.2 Cost Analysis

| Resource | Unit Cost | Estimated Usage | Monthly Cost |
|----------|-----------|-----------------|--------------|
| GitHub API calls | Free (within limits) | ~10 per issue filed | $0 |

**Cost Controls:**
- [x] Uses authenticated `gh` CLI which handles rate limiting
- [x] Checks existing labels before creating (reduces unnecessary API calls)

**Worst-Case Scenario:** If user creates 100 issues/hour, GitHub API rate limits apply (5000/hour authenticated). Well within limits for intended use.

## 9. Legal & Compliance

| Concern | Applies? | Mitigation |
|---------|----------|------------|
| PII/Personal Data | No | Draft content is user-created, transmitted only to their own repo |
| Third-Party Licenses | No | Uses standard library + `gh` CLI (MIT licensed) |
| Terms of Service | Yes | GitHub API usage compliant with ToS |
| Data Retention | N/A | No data retained beyond user's local files and their GitHub repo |
| Export Controls | No | No restricted algorithms or data |

**Data Classification:** Internal - user's own issue content

**Compliance Checklist:**
- [x] No PII stored without consent (user controls their own data)
- [x] All third-party licenses compatible with project license
- [x] External API usage compliant with provider ToS
- [x] Data retention policy documented (user's local files + GitHub)

## 10. Verification & Testing

### 10.0 Test Plan (TDD - Complete Before Implementation)

**TDD Requirement:** Tests MUST be written and failing BEFORE implementation begins.

| Test ID | Test Description | Expected Behavior | Status |
|---------|------------------|-------------------|--------|
| T010 | Parse valid draft with all sections | Returns title, body, labels correctly | RED |
| T020 | Parse draft missing H1 title | Returns parse error for missing title | RED |
| T030 | Parse draft with malformed labels | Returns warning, empty labels list | RED |
| T040 | Label color for "enhancement" | Returns green (#2ea44f) | RED |
| T050 | Label color for "bug" | Returns red (#d73a4a) | RED |
| T060 | Label color for unknown label | Returns gray (#ededed) | RED |
| T070 | Shell injection in title | Title passed safely, no shell execution | RED |
| T080 | Auth verification when authenticated | Returns True | RED |
| T090 | Auth verification when not authenticated | Returns False | RED |
| T100 | Full filing workflow happy path | Issue created, URL returned | RED |

**Coverage Target:** ≥95% for all new code

**TDD Checklist:**
- [ ] All tests written before implementation
- [ ] Tests currently RED (failing)
- [ ] Test IDs match scenario IDs in 10.1
- [ ] Test file created at: `tests/unit/test_file_issue.py`

### 10.1 Test Scenarios

| ID | Scenario | Type | Input | Expected Output | Pass Criteria |
|----|----------|------|-------|-----------------|---------------|
| 010 | Parse valid draft | Auto | Complete draft with H1, body, labels | ParsedDraft with all fields | All fields populated correctly |
| 020 | Parse draft missing title | Auto | Draft without H1 line | ParsedDraft with error | `parse_errors` contains title error |
| 030 | Parse malformed labels | Auto | Draft with `## Labels: broken` | ParsedDraft with warning | `labels=[]`, warning in errors |
| 040 | Color mapping: enhancement | Auto | "enhancement" | "#2ea44f" | Exact color match |
| 050 | Color mapping: bug | Auto | "bug" | "#d73a4a" | Exact color match |
| 060 | Color mapping: unknown | Auto | "random-label" | "#ededed" | Default gray returned |
| 070 | Shell injection safety | Auto | Title: `test; rm -rf /` | Title passed as literal | No shell execution |
| 080 | Verify auth (authenticated) | Auto-Live | Authenticated gh CLI | True | Returns True |
| 090 | Verify auth (not authenticated) | Auto | Mock unauthenticated | False | Returns False |
| 100 | Full workflow happy path | Auto | Valid draft, mock gh | FilingResult with URL | success=True, URL present |
| 110 | Workflow with missing labels | Auto | Draft with new labels | Labels created | `labels_created` list populated |
| 120 | Workflow auth failure | Auto | Mock unauth gh | FilingResult with error | success=False, error message |
| 130 | Metadata update | Auto | Valid filing result | JSON updated | `github_issue_url` and `filed_at` present |

### 10.2 Test Commands

```bash
# Run all automated tests for this feature
poetry run pytest tests/unit/test_file_issue.py tests/unit/test_label_colors.py -v

# Run only fast/mocked tests (exclude live)
poetry run pytest tests/unit/test_file_issue.py -v -m "not live"

# Run live integration tests (requires gh auth)
poetry run pytest tests/integration/test_file_issue_integration.py -v -m live

# Run with coverage
poetry run pytest tests/unit/test_file_issue.py --cov=agentos/workflows/issue --cov-report=term-missing
```

### 10.3 Manual Tests (Only If Unavoidable)

| ID | Scenario | Why Not Automated | Steps |
|----|----------|-------------------|-------|
| M010 | End-to-end filing to real repo | Requires real GitHub repo state | 1. Run workflow with test draft 2. Select [F]ile 3. Verify issue appears in GitHub UI 4. Verify labels created 5. Delete test issue |

## 11. Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| `gh` CLI not installed | High | Low | Clear error message with installation instructions |
| GitHub API rate limiting | Medium | Low | Use authenticated requests, sequential label creation |
| Draft format changes break parser | Medium | Medium | Graceful degradation, clear error messages |
| Label creation permissions restricted | Medium | Low | Fail with clear error, suggest manual creation |

## 12. Definition of Done

### Code
- [ ] Implementation complete in `file_issue.py` and `label_colors.py`
- [ ] `[F]ile` option integrated into `run_issue_workflow.py`
- [ ] Code comments reference this LLD (#84)
- [ ] All subprocess calls use list arguments (verified)

### Tests
- [ ] All test scenarios pass (010-130)
- [ ] Test coverage ≥95% for new modules
- [ ] Shell injection test (070) explicitly verified

### Documentation
- [ ] LLD updated with any deviations
- [ ] Implementation Report (0103) completed
- [ ] Workflow documentation updated with `[F]ile` option
- [ ] Label color conventions documented
- [ ] New files added to `docs/0003-file-inventory.md`

### Reports (Pre-Merge Gate)
- [ ] `docs/reports/84/implementation-report.md` created
- [ ] `docs/reports/84/test-report.md` created

### Verification
- [ ] Run 0809 Security Audit - PASS
- [ ] Run 0817 Wiki Alignment Audit - PASS

### Review
- [ ] Code review completed
- [ ] User approval before closing issue

---

## Appendix: Review Log

*Track all review feedback with timestamps and implementation status.*

### Review Summary

| Review | Date | Verdict | Key Issue |
|--------|------|---------|-----------|
| - | - | - | - |

**Final Status:** PENDING