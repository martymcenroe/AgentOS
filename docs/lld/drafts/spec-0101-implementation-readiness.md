# Implementation Spec: Test Plan Reviewer - Gemini-Powered Quality Gate

<!-- Metadata -->
| Field | Value |
|-------|-------|
| Issue | #101 |
| LLD | `docs/lld/active/101-test-plan-reviewer.md` |
| Generated | 2026-02-17 |
| Status | DRAFT |

## 1. Overview

*Brief summary of what this implementation achieves.*

**Objective:** Add a Gemini-powered review step that analyzes test plans for coverage completeness, edge cases, and alignment with acceptance criteria before implementation begins.

**Success Criteria:** 
- Test plans reviewed via skill command with structured PASS/REVISE/ERROR/BLOCKED verdicts
- Coverage matrix maps each acceptance criterion to test cases
- Pre-flight secrets scan blocks API submission when credentials detected
- Audit trail captures test plan hash, review verdict, timestamp, and prompt version

## 2. Files to Implement

*Complete list of files from LLD Section 2.1 with implementation order.*

| Order | File | Change Type | Description |
|-------|------|-------------|-------------|
| 1 | `docs/prompts/test-plan-reviewer/` | Add (Directory) | Directory for versioned prompts |
| 2 | `docs/prompts/test-plan-reviewer/v1.0.0.md` | Add | Hard-coded review prompt |
| 3 | `assemblyzero/skills/` | Add (Directory) | Directory for skill implementations |
| 4 | `assemblyzero/skills/__init__.py` | Add | Skills module initialization |
| 5 | `assemblyzero/skills/lib/` | Add (Directory) | Directory for skill library modules |
| 6 | `assemblyzero/skills/lib/__init__.py` | Add | Skills lib module initialization |
| 7 | `assemblyzero/skills/lib/markdown_sanitizer.py` | Add | HTML/script stripping utility |
| 8 | `assemblyzero/skills/lib/secrets_scanner.py` | Add | Pre-flight secrets/credential detection |
| 9 | `assemblyzero/skills/lib/token_counter.py` | Add | Token counting and truncation utilities |
| 10 | `assemblyzero/skills/lib/test_plan_parser.py` | Add | Markdown parsing utilities |
| 11 | `assemblyzero/skills/lib/acceptance_criteria_extractor.py` | Add | GitHub issue AC extraction |
| 12 | `assemblyzero/skills/lib/gemini_reviewer.py` | Add | Gemini API integration for review |
| 13 | `assemblyzero/skills/test_plan_review.py` | Add | Main skill implementation |
| 14 | `docs/skills/test-plan-review.md` | Add | Skill definition and documentation |
| 15 | `tests/fixtures/gemini-test-plan-response.json` | Add | Golden API response fixture |
| 16 | `tests/fixtures/sample-test-plan.md` | Add | Sample test plan for testing |
| 17 | `tests/unit/skills/` | Add (Directory) | Directory for skill unit tests |
| 18 | `tests/unit/skills/__init__.py` | Add | Test module initialization |
| 19 | `tests/unit/skills/test_test_plan_parser.py` | Add | Unit tests for parser |
| 20 | `tests/unit/skills/test_markdown_sanitizer.py` | Add | Unit tests for sanitizer |
| 21 | `tests/unit/skills/test_secrets_scanner.py` | Add | Unit tests for secrets scanner |
| 22 | `tests/unit/skills/test_acceptance_criteria_extractor.py` | Add | Unit tests for AC extractor |
| 23 | `tests/unit/skills/test_token_counter.py` | Add | Unit tests for token counter |
| 24 | `tests/unit/skills/test_test_plan_review.py` | Add | Unit tests for main skill |
| 25 | `tests/integration/test_test_plan_review_integration.py` | Add | Integration tests |
| 26 | `pyproject.toml` | Modify | Add bleach dependency |
| 27 | `docs/0003-file-inventory.md` | Modify | Add new files to inventory |

**Implementation Order Rationale:** 
1. Create directories first (prompts, skills, lib, tests)
2. Implement leaf-level utilities (sanitizer, scanner, token counter) with no internal dependencies
3. Implement parser and extractor that use the utilities
4. Implement Gemini reviewer that orchestrates the review
5. Implement main skill that ties everything together
6. Add documentation and fixtures
7. Add tests after implementation code exists
8. Modify existing files last

## 3. Current State (for Modify/Delete files)

### 3.1 `pyproject.toml`

**Relevant excerpt** (lines 1-47):

```toml
[project]
name = "assemblyzero-tools"
version = "0.1.0"
description = "AssemblyZero configuration and tooling"
authors = [{name = "Marty McEnroe"}]
readme = "README.md"
license = "PolyForm-Noncommercial-1.0.0"
requires-python = "^3.10"
dependencies = [
    "keyring (>=25.7.0,<26.0.0)",
    "anthropic (>=0.78.0,<0.79.0)",
    "langgraph (>=1.0.7,<2.0.0)",
    "langgraph-checkpoint-sqlite (>=3.0.3,<4.0.0)",
    "langchain (>=1.2.8,<2.0.0)",
    "langchain-google-genai (>=4.2.0,<5.0.0)",
    "langchain-anthropic (>=1.3.1,<2.0.0)",
    "watchdog (>=6.0.0,<7.0.0)",
    "google-genai (>=1.60.0,<2.0.0)",
    "pygithub (>=2.8.1,<3.0.0)",
    "tiktoken (>=0.9.0,<1.0.0)",
    "langchain-core (>=1.2.9,<2.0.0)",
    "cryptography (>=46.0.4,<47.0.0)",
    "tenacity (>=9.1.3,<10.0.0)",
    "packaging (>=26.0,<27.0)",
    "pathspec (>=1.0.4,<2.0.0)",
    "aiosqlite (>=0.22.1,<0.23.0)",
    "jiter (>=0.13.0,<0.14.0)",
    "orjson (>=3.11.7,<4.0.0)",
    "langsmith (>=0.6.9,<0.7.0)",
    "google-auth (>=2.48.0,<3.0.0)",
    "pycparser (>=3.0,<4.0)"
]
```

**What changes:** Add `bleach (>=6.1.0,<7.0.0)` to the dependencies list for HTML sanitization. Note that `tiktoken` is already present.

### 3.2 `docs/0003-file-inventory.md`

**Relevant excerpt** (lines 85-130, Skills section):

```markdown
### Skills (06xx) - 28 files

Skill documentation uses the c/p convention (CLI + Prompt pairs).

| File | Status | Description |
|------|--------|-------------|
| `0600-command-index.md` | Stable | All commands documented |
| `0601-gemini-dual-review.md` | Stable | AI-to-AI review |
| `0602-gemini-lld-review.md` | Stable | Design review |
| `0604-gemini-retry.md` | Stable | Exponential backoff for Gemini |
| `0699-skill-instructions-index.md` | Stable | Skill index |
| `0620c-sync-permissions-cli.md` | Stable | CLI: Permission sync |
| `0620p-sync-permissions-prompt.md` | Stable | Prompt: Permission sync |
```

**What changes:** 
1. Add new skill documentation file to the Skills section
2. Add new files to a new "Skills Implementation" section under Tools Inventory
3. Update summary statistics

## 4. Data Structures

### 4.1 ReviewVerdict

**Definition:**

```python
from enum import Enum

class ReviewVerdict(Enum):
    PASS = "PASS"
    REVISE = "REVISE"
    ERROR = "ERROR"
    BLOCKED = "BLOCKED"
```

**Concrete Example:**

```python
ReviewVerdict.PASS  # Test plan passes all criteria
ReviewVerdict.REVISE  # Test plan needs improvements
ReviewVerdict.ERROR  # API or system error occurred
ReviewVerdict.BLOCKED  # Secrets detected, blocked submission
```

### 4.2 CoverageMapping

**Definition:**

```python
from typing import TypedDict

class CoverageMapping(TypedDict):
    ac_id: str
    ac_text: str
    covered: bool
    test_cases: list[str]
```

**Concrete Example:**

```json
{
    "ac_id": "AC-001",
    "ac_text": "User can log in with valid credentials",
    "covered": true,
    "test_cases": ["TC-010", "TC-011", "TC-012"]
}
```

### 4.3 GapFinding

**Definition:**

```python
from typing import TypedDict, Optional

class GapFinding(TypedDict):
    category: str
    line_number: Optional[int]
    description: str
    severity: str
```

**Concrete Example:**

```json
{
    "category": "Edge Cases",
    "line_number": 45,
    "description": "Missing test for empty input validation",
    "severity": "Major"
}
```

### 4.4 ReviewResult

**Definition:**

```python
from typing import TypedDict, Optional

class ReviewResult(TypedDict):
    verdict: str  # ReviewVerdict value
    confidence_score: int
    coverage_matrix: list[CoverageMapping]
    gaps: list[GapFinding]
    summary: str
    prompt_version: str
    model_version: str
    truncated: bool
    truncation_warning: Optional[str]
```

**Concrete Example:**

```json
{
    "verdict": "REVISE",
    "confidence_score": 75,
    "coverage_matrix": [
        {
            "ac_id": "AC-001",
            "ac_text": "Test plan reviewed via skill command",
            "covered": true,
            "test_cases": ["TC-130"]
        },
        {
            "ac_id": "AC-002",
            "ac_text": "Reviewer provides structured feedback",
            "covered": false,
            "test_cases": []
        }
    ],
    "gaps": [
        {
            "category": "Coverage",
            "line_number": 12,
            "description": "AC-002 has no test coverage",
            "severity": "Critical"
        }
    ],
    "summary": "Test plan covers 50% of acceptance criteria. Missing coverage for structured feedback requirement.",
    "prompt_version": "v1.0.0",
    "model_version": "gemini-2.0-flash",
    "truncated": false,
    "truncation_warning": null
}
```

### 4.5 TestPlanMetadata

**Definition:**

```python
from typing import TypedDict

class TestPlanMetadata(TypedDict):
    file_path: str
    content_hash: str
    issue_number: int
    test_case_count: int
    token_count: int
```

**Concrete Example:**

```json
{
    "file_path": "docs/reports/101/test-plan.md",
    "content_hash": "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef12345678",
    "issue_number": 101,
    "test_case_count": 14,
    "token_count": 4250
}
```

### 4.6 SecretsMatch

**Definition:**

```python
from typing import TypedDict

class SecretsMatch(TypedDict):
    line_number: int
    pattern_type: str
    matched_text: str
```

**Concrete Example:**

```json
{
    "line_number": 23,
    "pattern_type": "api_key",
    "matched_text": "API_KEY=sk-****"
}
```

### 4.7 AcceptanceCriterion

**Definition:**

```python
from typing import TypedDict

class AcceptanceCriterion(TypedDict):
    id: str
    text: str
    checked: bool
```

**Concrete Example:**

```json
{
    "id": "AC-001",
    "text": "Test plans reviewed via skill command",
    "checked": false
}
```

### 4.8 TestCase

**Definition:**

```python
from typing import TypedDict, Optional

class TestCase(TypedDict):
    id: str
    title: str
    description: Optional[str]
    line_number: int
```

**Concrete Example:**

```json
{
    "id": "TC-010",
    "title": "Happy path - test plan passes",
    "description": "Valid test plan with all ACs covered should return PASS verdict",
    "line_number": 15
}
```

## 5. Function Specifications

### 5.1 `sanitize_markdown()`

**File:** `assemblyzero/skills/lib/markdown_sanitizer.py`

**Signature:**

```python
def sanitize_markdown(content: str) -> str:
    """Strip executable HTML, script tags, and harmful content from markdown.
    
    Uses bleach library with a strict allowlist to remove potentially
    dangerous HTML elements while preserving markdown formatting.
    """
    ...
```

**Input Example:**

```python
content = """# Test Plan

<script>alert('xss')</script>

## Test Cases

<iframe src="malicious.html"></iframe>

- TC-001: Valid input test
"""
```

**Output Example:**

```python
"""# Test Plan



## Test Cases



- TC-001: Valid input test
"""
```

**Edge Cases:**
- Empty string → returns empty string
- Content with no HTML → returns unchanged content
- Nested scripts `<script><script>` → all removed
- Valid HTML like `<strong>` → preserved if in allowlist

### 5.2 `scan_for_secrets()`

**File:** `assemblyzero/skills/lib/secrets_scanner.py`

**Signature:**

```python
def scan_for_secrets(content: str) -> list[SecretsMatch]:
    """Scan content for potential secrets and credentials.
    
    Detects patterns like API keys, passwords, tokens, and other
    sensitive data that should not be sent to external APIs.
    """
    ...
```

**Input Example:**

```python
content = """# Test Data

API_KEY=sk-abc123xyz789
password: "my_secret_password"
"""
```

**Output Example:**

```python
[
    {
        "line_number": 3,
        "pattern_type": "api_key",
        "matched_text": "API_KEY=sk-****"
    },
    {
        "line_number": 4,
        "pattern_type": "password",
        "matched_text": "password: \"****\""
    }
]
```

**Edge Cases:**
- No secrets → returns empty list `[]`
- Multiple secrets on same line → returns multiple matches with same line number
- Base64-encoded data → detected if matches common key patterns
- False positive like `API_KEY=placeholder` → still flagged (use `--skip-secrets-scan` to override)

### 5.3 `redact_secret()`

**File:** `assemblyzero/skills/lib/secrets_scanner.py`

**Signature:**

```python
def redact_secret(match: str, pattern_type: str) -> str:
    """Create redacted version of matched secret for safe logging."""
    ...
```

**Input Example:**

```python
match = "sk-abc123xyz789"
pattern_type = "api_key"
```

**Output Example:**

```python
"sk-****"
```

**Edge Cases:**
- Short secrets (< 4 chars) → fully redacted as `****`
- Empty string → returns `****`
- Password in quotes → `"****"`

### 5.4 `count_tokens()`

**File:** `assemblyzero/skills/lib/token_counter.py`

**Signature:**

```python
def count_tokens(text: str) -> int:
    """Count tokens in text using tiktoken cl100k_base encoding.
    
    This encoding is compatible with Gemini tokenization for
    accurate truncation decisions.
    """
    ...
```

**Input Example:**

```python
text = "Hello, world! This is a test of token counting."
```

**Output Example:**

```python
11  # Approximate token count
```

**Edge Cases:**
- Empty string → returns `0`
- Unicode characters → counted correctly
- Very long text (100KB) → returns accurate count without memory issues

### 5.5 `truncate_to_limit()`

**File:** `assemblyzero/skills/lib/token_counter.py`

**Signature:**

```python
def truncate_to_limit(
    content: str,
    max_tokens: int,
    preserve_structure: bool = True
) -> tuple[str, str | None]:
    """Truncate content to token limit.
    
    Args:
        content: Text to truncate
        max_tokens: Maximum tokens allowed
        preserve_structure: If True, preserve headers and structure
        
    Returns:
        Tuple of (truncated_content, warning_message or None)
    """
    ...
```

**Input Example:**

```python
content = """# Test Plan

## Section 1
Test content here...

## Section 2
More test content that makes this very long...
"""
max_tokens = 50
preserve_structure = True
```

**Output Example:**

```python
(
    """# Test Plan

## Section 1
Test content here...

[TRUNCATED - Content exceeded 50 token limit]""",
    "Test plan truncated from 120 tokens to 50 tokens. Some test cases may not be reviewed."
)
```

**Edge Cases:**
- Content under limit → returns `(content, None)`
- `preserve_structure=False` → truncates at token boundary without header preservation
- `max_tokens=0` → returns `("", "Content fully truncated")`

### 5.6 `parse_test_plan()`

**File:** `assemblyzero/skills/lib/test_plan_parser.py`

**Signature:**

```python
def parse_test_plan(content: str) -> dict:
    """Parse test plan markdown and extract structured sections.
    
    Returns dict with keys: title, sections, test_cases, metadata
    """
    ...
```

**Input Example:**

```python
content = """# Test Plan for Issue #101

## Overview
This plan covers the test plan reviewer feature.

## Test Cases

### TC-010: Happy path
Valid test plan should pass.

### TC-020: Error handling
API errors should return ERROR verdict.
"""
```

**Output Example:**

```python
{
    "title": "Test Plan for Issue #101",
    "sections": [
        {"heading": "Overview", "content": "This plan covers the test plan reviewer feature."},
        {"heading": "Test Cases", "content": "..."}
    ],
    "test_cases": [
        {"id": "TC-010", "title": "Happy path", "description": "Valid test plan should pass.", "line_number": 9},
        {"id": "TC-020", "title": "Error handling", "description": "API errors should return ERROR verdict.", "line_number": 12}
    ],
    "metadata": {
        "issue_reference": 101
    }
}
```

**Edge Cases:**
- Empty content → returns `{"title": "", "sections": [], "test_cases": [], "metadata": {}}`
- No test cases found → `test_cases` is empty list
- Malformed headers → best-effort parsing, no exception raised

### 5.7 `extract_test_cases()`

**File:** `assemblyzero/skills/lib/test_plan_parser.py`

**Signature:**

```python
def extract_test_cases(content: str) -> list[TestCase]:
    """Extract individual test cases from test plan content.
    
    Looks for patterns like:
    - ### TC-NNN: Title
    - | TC-NNN | Description |
    - - TC-NNN: Description
    """
    ...
```

**Input Example:**

```python
content = """## Test Cases

### TC-010: Valid input test
Tests that valid input is processed correctly.

### TC-020: Invalid input test
Tests error handling for invalid input.
"""
```

**Output Example:**

```python
[
    {
        "id": "TC-010",
        "title": "Valid input test",
        "description": "Tests that valid input is processed correctly.",
        "line_number": 3
    },
    {
        "id": "TC-020",
        "title": "Invalid input test",
        "description": "Tests error handling for invalid input.",
        "line_number": 6
    }
]
```

**Edge Cases:**
- No test cases → returns `[]`
- Table format → extracts from table rows
- Mixed formats → extracts from all recognized patterns

### 5.8 `fetch_issue()`

**File:** `assemblyzero/skills/lib/acceptance_criteria_extractor.py`

**Signature:**

```python
async def fetch_issue(issue_number: int) -> dict:
    """Fetch GitHub issue content via gh CLI.
    
    Raises:
        RuntimeError: If gh CLI returns non-zero exit code
    """
    ...
```

**Input Example:**

```python
issue_number = 101
```

**Output Example:**

```python
{
    "number": 101,
    "title": "Test Plan Reviewer - Gemini-Powered Quality Gate",
    "body": "## Acceptance Criteria\n\n- [ ] Test plans reviewed via skill command\n- [ ] Coverage matrix maps ACs to tests",
    "state": "open",
    "labels": ["feature", "gemini"]
}
```

**Edge Cases:**
- Issue not found → raises `RuntimeError("gh CLI error: issue not found")`
- `gh` not authenticated → raises `RuntimeError("gh CLI error: not authenticated, run 'gh auth login'")`
- Network timeout → raises `RuntimeError("gh CLI error: network timeout")`

### 5.9 `extract_acceptance_criteria()`

**File:** `assemblyzero/skills/lib/acceptance_criteria_extractor.py`

**Signature:**

```python
def extract_acceptance_criteria(issue_body: str) -> list[AcceptanceCriterion]:
    """Parse acceptance criteria from issue body.
    
    Looks for checkbox patterns like:
    - [ ] Unchecked criterion
    - [x] Checked criterion
    """
    ...
```

**Input Example:**

```python
issue_body = """## Description
Feature for test plan review.

## Acceptance Criteria
- [ ] Test plans reviewed via skill command
- [x] Coverage matrix maps ACs to tests
- [ ] Secrets scanner blocks submission
"""
```

**Output Example:**

```python
[
    {"id": "AC-001", "text": "Test plans reviewed via skill command", "checked": False},
    {"id": "AC-002", "text": "Coverage matrix maps ACs to tests", "checked": True},
    {"id": "AC-003", "text": "Secrets scanner blocks submission", "checked": False}
]
```

**Edge Cases:**
- No acceptance criteria section → returns `[]`
- Mixed checkbox styles → all recognized patterns extracted
- Nested checkboxes → flattened to single list

### 5.10 `call_gemini_review()`

**File:** `assemblyzero/skills/lib/gemini_reviewer.py`

**Signature:**

```python
async def call_gemini_review(
    prompt: str,
    test_plan: str,
    acceptance_criteria: list[AcceptanceCriterion],
    max_retries: int = 3
) -> dict:
    """Call Gemini API with retry logic.
    
    Uses exponential backoff on failures: 1s, 2s, 4s.
    
    Raises:
        RuntimeError: If all retries exhausted
    """
    ...
```

**Input Example:**

```python
prompt = "You are a test plan reviewer. Analyze the following test plan..."
test_plan = "# Test Plan\n\n## Test Cases\n..."
acceptance_criteria = [
    {"id": "AC-001", "text": "Test plans reviewed via skill command", "checked": False}
]
max_retries = 3
```

**Output Example:**

```python
{
    "verdict": "REVISE",
    "confidence_score": 75,
    "coverage_analysis": [
        {"ac_id": "AC-001", "covered": True, "test_cases": ["TC-010"]}
    ],
    "gaps": [
        {"category": "Edge Cases", "line_number": 15, "description": "Missing error path test", "severity": "Major"}
    ],
    "summary": "Test plan needs improvement in error handling coverage."
}
```

**Edge Cases:**
- First call succeeds → returns immediately
- API rate limit → retries with backoff, then raises `RuntimeError`
- Invalid API key → raises `RuntimeError` immediately (no retry)
- Network timeout → retries with backoff

### 5.11 `parse_gemini_response()`

**File:** `assemblyzero/skills/lib/gemini_reviewer.py`

**Signature:**

```python
def parse_gemini_response(response: dict) -> ReviewResult:
    """Parse Gemini response into structured ReviewResult.
    
    Validates all required fields are present and correctly typed.
    """
    ...
```

**Input Example:**

```python
response = {
    "verdict": "PASS",
    "confidence_score": 95,
    "coverage_analysis": [
        {"ac_id": "AC-001", "covered": True, "test_cases": ["TC-010", "TC-020"]}
    ],
    "gaps": [],
    "summary": "Excellent test coverage."
}
```

**Output Example:**

```python
{
    "verdict": "PASS",
    "confidence_score": 95,
    "coverage_matrix": [
        {"ac_id": "AC-001", "ac_text": "", "covered": True, "test_cases": ["TC-010", "TC-020"]}
    ],
    "gaps": [],
    "summary": "Excellent test coverage.",
    "prompt_version": "v1.0.0",
    "model_version": "gemini-2.0-flash",
    "truncated": False,
    "truncation_warning": None
}
```

**Edge Cases:**
- Missing required field → raises `ValueError("Missing required field: {field}")`
- Invalid verdict value → raises `ValueError("Invalid verdict: {value}")`
- Malformed JSON → raises `ValueError("Could not parse response")`

### 5.12 `run_test_plan_review()`

**File:** `assemblyzero/skills/test_plan_review.py`

**Signature:**

```python
async def run_test_plan_review(
    issue_number: int,
    dry_run: bool = False,
    skip_secrets_scan: bool = False,
    mock_mode: bool = False
) -> ReviewResult:
    """Execute test plan review for the given issue number.
    
    Args:
        issue_number: GitHub issue number to review
        dry_run: If True, output payload without calling API
        skip_secrets_scan: If True, skip secrets detection
        mock_mode: If True, use golden fixture instead of API
        
    Returns:
        ReviewResult with verdict and analysis
    """
    ...
```

**Input Example:**

```python
issue_number = 101
dry_run = False
skip_secrets_scan = False
mock_mode = True
```

**Output Example:**

```python
{
    "verdict": "PASS",
    "confidence_score": 92,
    "coverage_matrix": [
        {"ac_id": "AC-001", "ac_text": "Test plans reviewed via skill command", "covered": True, "test_cases": ["TC-130"]},
        {"ac_id": "AC-002", "ac_text": "Coverage matrix maps ACs to tests", "covered": True, "test_cases": ["TC-030", "TC-140"]}
    ],
    "gaps": [],
    "summary": "Test plan provides comprehensive coverage of all acceptance criteria.",
    "prompt_version": "v1.0.0",
    "model_version": "gemini-2.0-flash",
    "truncated": False,
    "truncation_warning": None
}
```

**Edge Cases:**
- Test plan file not found → returns `{"verdict": "ERROR", "summary": "Test plan not found at docs/reports/101/test-plan.md", ...}`
- Secrets detected → returns `{"verdict": "BLOCKED", "summary": "Secrets detected on lines: 23, 45", ...}`
- `dry_run=True` → prints payload to console, returns `{"verdict": "DRY_RUN", ...}`
- API failure after retries → returns `{"verdict": "ERROR", "summary": "API call failed after 3 retries", ...}`

### 5.13 `generate_review_report()`

**File:** `assemblyzero/skills/test_plan_review.py`

**Signature:**

```python
def generate_review_report(
    result: ReviewResult,
    metadata: TestPlanMetadata,
    output_path: Path
) -> None:
    """Write structured review output to markdown file.
    
    Creates audit trail with hash, timestamp, verdict, and full analysis.
    """
    ...
```

**Input Example:**

```python
result = {
    "verdict": "PASS",
    "confidence_score": 92,
    "coverage_matrix": [...],
    "gaps": [],
    "summary": "Comprehensive coverage.",
    "prompt_version": "v1.0.0",
    "model_version": "gemini-2.0-flash",
    "truncated": False,
    "truncation_warning": None
}
metadata = {
    "file_path": "docs/reports/101/test-plan.md",
    "content_hash": "a1b2c3d4...",
    "issue_number": 101,
    "test_case_count": 14,
    "token_count": 4250
}
output_path = Path("docs/reports/101/test-plan-review.md")
```

**Output Example:**

The file at `docs/reports/101/test-plan-review.md` contains:

```markdown
# Test Plan Review - Issue #101

| Field | Value |
|-------|-------|
| Verdict | PASS |
| Confidence | 92% |
| Timestamp | 2026-02-17T10:30:00Z |
| Test Plan Hash | a1b2c3d4... |
| Prompt Version | v1.0.0 |
| Model Version | gemini-2.0-flash |

## Summary

Comprehensive coverage.

## Coverage Matrix

| AC ID | Text | Covered | Test Cases |
|-------|------|---------|------------|
| AC-001 | Test plans reviewed | ✓ | TC-130 |

## Gaps

None identified.
```

**Edge Cases:**
- Output directory doesn't exist → creates directory
- File already exists → overwrites
- Write permission denied → raises `PermissionError`

### 5.14 `_error_result()`

**File:** `assemblyzero/skills/test_plan_review.py`

**Signature:**

```python
def _error_result(message: str) -> ReviewResult:
    """Create consistent ERROR response."""
    ...
```

**Input Example:**

```python
message = "Test plan not found at docs/reports/101/test-plan.md"
```

**Output Example:**

```python
{
    "verdict": "ERROR",
    "confidence_score": 0,
    "coverage_matrix": [],
    "gaps": [],
    "summary": "Test plan not found at docs/reports/101/test-plan.md",
    "prompt_version": "v1.0.0",
    "model_version": "gemini-2.0-flash",
    "truncated": False,
    "truncation_warning": None
}
```

**Edge Cases:**
- Empty message → returns result with empty summary
- Very long message → included in full (no truncation)

## 6. Change Instructions

### 6.1 `docs/prompts/test-plan-reviewer/` (Add Directory)

**Action:** Create directory at `docs/prompts/test-plan-reviewer/`

### 6.2 `docs/prompts/test-plan-reviewer/v1.0.0.md` (Add)

**Complete file contents:**

```markdown
# Test Plan Review Prompt v1.0.0

You are an expert test plan reviewer. Analyze the provided test plan for coverage completeness, edge cases, and alignment with acceptance criteria.

## Instructions

1. **Coverage Analysis**: Map each acceptance criterion to test cases that cover it
2. **Gap Identification**: Identify missing test scenarios for:
   - Error handling paths
   - Edge cases (empty input, large input, boundary conditions)
   - Security considerations
   - Performance scenarios
3. **Verdict Determination**:
   - PASS: 100% AC coverage AND no critical/major gaps
   - REVISE: Missing AC coverage OR critical/major gaps found

## Output Format

Respond with JSON in this exact structure:

```json
{
  "verdict": "PASS" | "REVISE",
  "confidence_score": 0-100,
  "coverage_analysis": [
    {
      "ac_id": "AC-NNN",
      "covered": true | false,
      "test_cases": ["TC-NNN", ...]
    }
  ],
  "gaps": [
    {
      "category": "Coverage" | "Edge Cases" | "Security" | "Performance",
      "line_number": N | null,
      "description": "What is missing",
      "severity": "Critical" | "Major" | "Minor"
    }
  ],
  "summary": "2-3 sentence summary of findings"
}
```

## Acceptance Criteria

{acceptance_criteria}

## Test Plan

{test_plan}
```

### 6.3 `assemblyzero/skills/` (Add Directory)

**Action:** Create directory at `assemblyzero/skills/`

### 6.4 `assemblyzero/skills/__init__.py` (Add)

**Complete file contents:**

```python
"""Skills module for AssemblyZero.

Skills are discrete, invocable capabilities that can be triggered
via Claude commands or programmatically.

Issue #101: Test Plan Reviewer skill.
"""

from assemblyzero.skills.test_plan_review import run_test_plan_review

__all__ = ["run_test_plan_review"]
```

### 6.5 `assemblyzero/skills/lib/` (Add Directory)

**Action:** Create directory at `assemblyzero/skills/lib/`

### 6.6 `assemblyzero/skills/lib/__init__.py` (Add)

**Complete file contents:**

```python
"""Library modules for skills.

Issue #101: Test Plan Reviewer utilities.
"""

from assemblyzero.skills.lib.markdown_sanitizer import sanitize_markdown
from assemblyzero.skills.lib.secrets_scanner import scan_for_secrets, redact_secret
from assemblyzero.skills.lib.token_counter import count_tokens, truncate_to_limit
from assemblyzero.skills.lib.test_plan_parser import parse_test_plan, extract_test_cases
from assemblyzero.skills.lib.acceptance_criteria_extractor import (
    fetch_issue,
    extract_acceptance_criteria,
)
from assemblyzero.skills.lib.gemini_reviewer import call_gemini_review, parse_gemini_response

__all__ = [
    "sanitize_markdown",
    "scan_for_secrets",
    "redact_secret",
    "count_tokens",
    "truncate_to_limit",
    "parse_test_plan",
    "extract_test_cases",
    "fetch_issue",
    "extract_acceptance_criteria",
    "call_gemini_review",
    "parse_gemini_response",
]
```

### 6.7 `assemblyzero/skills/lib/markdown_sanitizer.py` (Add)

**Complete file contents:**

```python
"""Markdown sanitization for safe content processing.

Issue #101: Strip executable HTML and scripts before API submission.
"""

import bleach

# Allowlist of safe HTML tags that can appear in markdown
ALLOWED_TAGS = [
    "p", "br", "strong", "em", "code", "pre", "blockquote",
    "ul", "ol", "li", "h1", "h2", "h3", "h4", "h5", "h6",
    "a", "table", "thead", "tbody", "tr", "th", "td",
]

# Allowlist of safe attributes
ALLOWED_ATTRIBUTES = {
    "a": ["href", "title"],
    "code": ["class"],  # For syntax highlighting
}


def sanitize_markdown(content: str) -> str:
    """Strip executable HTML, script tags, and harmful content from markdown.
    
    Uses bleach library with a strict allowlist to remove potentially
    dangerous HTML elements while preserving markdown formatting.
    
    Args:
        content: Raw markdown content that may contain HTML
        
    Returns:
        Sanitized content with dangerous elements removed
    """
    if not content:
        return content
    
    # Clean HTML, stripping disallowed tags entirely
    cleaned = bleach.clean(
        content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True,  # Remove disallowed tags entirely rather than escaping
    )
    
    return cleaned
```

### 6.8 `assemblyzero/skills/lib/secrets_scanner.py` (Add)

**Complete file contents:**

```python
"""Pre-flight secrets scanner for content validation.

Issue #101: Detect and block secrets before API submission.
"""

import re
from typing import TypedDict


class SecretsMatch(TypedDict):
    """Represents a detected secret in content."""
    line_number: int
    pattern_type: str
    matched_text: str


# Patterns for detecting secrets
SECRET_PATTERNS = [
    # API Keys
    (r"(?i)(api[_-]?key|apikey)\s*[=:]\s*['\"]?([a-zA-Z0-9_\-]{20,})['\"]?", "api_key"),
    (r"(?i)sk-[a-zA-Z0-9]{20,}", "openai_key"),
    (r"(?i)AIza[a-zA-Z0-9_\-]{35}", "google_api_key"),
    
    # Tokens
    (r"(?i)(token|bearer)\s*[=:]\s*['\"]?([a-zA-Z0-9_\-\.]{20,})['\"]?", "token"),
    (r"(?i)ghp_[a-zA-Z0-9]{36}", "github_token"),
    (r"(?i)gho_[a-zA-Z0-9]{36}", "github_oauth"),
    
    # Passwords
    (r"(?i)(password|passwd|pwd)\s*[=:]\s*['\"]?(.{8,})['\"]?", "password"),
    
    # AWS
    (r"(?i)AKIA[A-Z0-9]{16}", "aws_access_key"),
    (r"(?i)(aws[_-]?secret|secret[_-]?key)\s*[=:]\s*['\"]?([a-zA-Z0-9/+=]{40})['\"]?", "aws_secret"),
    
    # Private Keys
    (r"-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----", "private_key"),
    
    # Connection Strings
    (r"(?i)(mongodb|postgres|mysql|redis)://[^\s]+", "connection_string"),
]


def scan_for_secrets(content: str) -> list[SecretsMatch]:
    """Scan content for potential secrets and credentials.
    
    Args:
        content: Text content to scan
        
    Returns:
        List of SecretsMatch for each detected secret
    """
    matches: list[SecretsMatch] = []
    lines = content.split("\n")
    
    for line_num, line in enumerate(lines, start=1):
        for pattern, pattern_type in SECRET_PATTERNS:
            if re.search(pattern, line):
                # Find the actual matched text for redaction
                match = re.search(pattern, line)
                if match:
                    matched_text = redact_secret(match.group(0), pattern_type)
                    matches.append({
                        "line_number": line_num,
                        "pattern_type": pattern_type,
                        "matched_text": matched_text,
                    })
    
    return matches


def redact_secret(match: str, pattern_type: str) -> str:
    """Create redacted version of matched secret for safe logging.
    
    Args:
        match: The matched secret text
        pattern_type: Type of secret for context
        
    Returns:
        Redacted string safe for logging
    """
    if not match:
        return "****"
    
    if len(match) < 8:
        return "****"
    
    # For passwords in quotes, preserve quote structure
    if pattern_type == "password":
        if match.startswith('"') or match.startswith("'"):
            quote = match[0]
            return f'{quote}****{quote}'
    
    # For key patterns, preserve prefix
    if pattern_type in ("openai_key", "github_token", "github_oauth", "aws_access_key"):
        # Keep first 4 chars of key prefix
        prefix = match[:4] if len(match) > 4 else ""
        return f"{prefix}****"
    
    # For connection strings, show protocol only
    if pattern_type == "connection_string":
        if "://" in match:
            protocol = match.split("://")[0]
            return f"{protocol}://****"
    
    # Default: show first 3 chars
    return f"{match[:3]}****" if len(match) > 3 else "****"
```

### 6.9 `assemblyzero/skills/lib/token_counter.py` (Add)

**Complete file contents:**

```python
"""Token counting and truncation utilities.

Issue #101: Accurate token counting for Gemini API limits.
"""

import tiktoken

# Use cl100k_base encoding (compatible with Gemini tokenization)
ENCODING_NAME = "cl100k_base"
DEFAULT_MAX_TOKENS = 30000  # Leave room for prompt and response


def count_tokens(text: str) -> int:
    """Count tokens in text using tiktoken cl100k_base encoding.
    
    Args:
        text: Text to count tokens for
        
    Returns:
        Number of tokens
    """
    if not text:
        return 0
    
    encoding = tiktoken.get_encoding(ENCODING_NAME)
    return len(encoding.encode(text))


def truncate_to_limit(
    content: str,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    preserve_structure: bool = True
) -> tuple[str, str | None]:
    """Truncate content to token limit.
    
    Args:
        content: Text to truncate
        max_tokens: Maximum tokens allowed
        preserve_structure: If True, preserve headers and structure
        
    Returns:
        Tuple of (truncated_content, warning_message or None)
    """
    if max_tokens <= 0:
        return "", "Content fully truncated"
    
    current_tokens = count_tokens(content)
    
    if current_tokens <= max_tokens:
        return content, None
    
    encoding = tiktoken.get_encoding(ENCODING_NAME)
    tokens = encoding.encode(content)
    
    if preserve_structure:
        # Try to preserve headers by finding good truncation points
        truncated_tokens = tokens[:max_tokens - 20]  # Leave room for marker
        truncated_text = encoding.decode(truncated_tokens)
        
        # Find last complete line
        last_newline = truncated_text.rfind("\n")
        if last_newline > len(truncated_text) // 2:
            truncated_text = truncated_text[:last_newline]
        
        truncation_marker = f"\n\n[TRUNCATED - Content exceeded {max_tokens} token limit]"
        result = truncated_text + truncation_marker
    else:
        truncated_tokens = tokens[:max_tokens]
        result = encoding.decode(truncated_tokens)
    
    warning = f"Test plan truncated from {current_tokens} tokens to {max_tokens} tokens. Some test cases may not be reviewed."
    
    return result, warning
```

### 6.10 `assemblyzero/skills/lib/test_plan_parser.py` (Add)

**Complete file contents:**

```python
"""Test plan markdown parsing utilities.

Issue #101: Extract structured data from test plan documents.
"""

import re
from typing import TypedDict, Optional


class TestCase(TypedDict):
    """Represents a parsed test case."""
    id: str
    title: str
    description: Optional[str]
    line_number: int


class ParsedSection(TypedDict):
    """Represents a parsed markdown section."""
    heading: str
    content: str


def parse_test_plan(content: str) -> dict:
    """Parse test plan markdown and extract structured sections.
    
    Args:
        content: Raw markdown content
        
    Returns:
        Dict with keys: title, sections, test_cases, metadata
    """
    if not content:
        return {"title": "", "sections": [], "test_cases": [], "metadata": {}}
    
    lines = content.split("\n")
    
    # Extract title (first H1)
    title = ""
    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            break
    
    # Extract sections
    sections: list[ParsedSection] = []
    current_section: Optional[ParsedSection] = None
    section_content: list[str] = []
    
    for line in lines:
        if line.startswith("## "):
            if current_section:
                current_section["content"] = "\n".join(section_content).strip()
                sections.append(current_section)
            current_section = {"heading": line[3:].strip(), "content": ""}
            section_content = []
        elif current_section:
            section_content.append(line)
    
    if current_section:
        current_section["content"] = "\n".join(section_content).strip()
        sections.append(current_section)
    
    # Extract test cases
    test_cases = extract_test_cases(content)
    
    # Extract metadata
    metadata: dict = {}
    issue_match = re.search(r"#(\d+)", title)
    if issue_match:
        metadata["issue_reference"] = int(issue_match.group(1))
    
    return {
        "title": title,
        "sections": sections,
        "test_cases": test_cases,
        "metadata": metadata,
    }


def extract_test_cases(content: str) -> list[TestCase]:
    """Extract individual test cases from test plan content.
    
    Looks for patterns like:
    - ### TC-NNN: Title
    - | TC-NNN | Description |
    - - TC-NNN: Description
    
    Args:
        content: Test plan markdown content
        
    Returns:
        List of TestCase dicts
    """
    test_cases: list[TestCase] = []
    lines = content.split("\n")
    
    # Pattern 1: ### TC-NNN: Title format
    tc_header_pattern = re.compile(r"^###\s+(TC-\d+):\s*(.+)$")
    
    # Pattern 2: | TC-NNN | format (table)
    tc_table_pattern = re.compile(r"\|\s*(TC-\d+)\s*\|([^|]+)\|")
    
    # Pattern 3: - TC-NNN: format (list)
    tc_list_pattern = re.compile(r"^-\s+(TC-\d+):\s*(.+)$")
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check header pattern
        header_match = tc_header_pattern.match(line)
        if header_match:
            tc_id = header_match.group(1)
            tc_title = header_match.group(2).strip()
            
            # Look for description in next lines
            description_lines = []
            j = i + 1
            while j < len(lines) and not lines[j].startswith("#"):
                if lines[j].strip():
                    description_lines.append(lines[j].strip())
                j += 1
            
            test_cases.append({
                "id": tc_id,
                "title": tc_title,
                "description": " ".join(description_lines) if description_lines else None,
                "line_number": i + 1,
            })
            i = j
            continue
        
        # Check table pattern
        table_match = tc_table_pattern.search(line)
        if table_match:
            tc_id = table_match.group(1)
            tc_title = table_match.group(2).strip()
            test_cases.append({
                "id": tc_id,
                "title": tc_title,
                "description": None,
                "line_number": i + 1,
            })
            i += 1
            continue
        
        # Check list pattern
        list_match = tc_list_pattern.match(line)
        if list_match:
            tc_id = list_match.group(1)
            tc_title = list_match.group(2).strip()
            test_cases.append({
                "id": tc_id,
                "title": tc_title,
                "description": None,
                "line_number": i + 1,
            })
            i += 1
            continue
        
        i += 1
    
    return test_cases
```

### 6.11 `assemblyzero/skills/lib/acceptance_criteria_extractor.py` (Add)

**Complete file contents:**

```python
"""GitHub issue acceptance criteria extraction.

Issue #101: Extract ACs from issues for coverage mapping.
"""

import asyncio
import json
import re
import subprocess
from typing import TypedDict


class AcceptanceCriterion(TypedDict):
    """Represents an acceptance criterion from an issue."""
    id: str
    text: str
    checked: bool


async def fetch_issue(issue_number: int) -> dict:
    """Fetch GitHub issue content via gh CLI.
    
    Args:
        issue_number: The issue number to fetch
        
    Returns:
        Dict with issue data (number, title, body, state, labels)
        
    Raises:
        RuntimeError: If gh CLI returns non-zero exit code
    """
    cmd = [
        "gh", "issue", "view", str(issue_number),
        "--json", "number,title,body,state,labels"
    ]
    
    # Run subprocess asynchronously
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    
    stdout, stderr = await process.communicate()
    
    if process.returncode != 0:
        error_msg = stderr.decode().strip()
        if "not authenticated" in error_msg.lower():
            raise RuntimeError("gh CLI error: not authenticated, run 'gh auth login'")
        raise RuntimeError(f"gh CLI error: {error_msg}")
    
    return json.loads(stdout.decode())


def extract_acceptance_criteria(issue_body: str) -> list[AcceptanceCriterion]:
    """Parse acceptance criteria from issue body.
    
    Looks for checkbox patterns like:
    - [ ] Unchecked criterion
    - [x] Checked criterion
    
    Args:
        issue_body: The issue body markdown
        
    Returns:
        List of AcceptanceCriterion dicts
    """
    if not issue_body:
        return []
    
    criteria: list[AcceptanceCriterion] = []
    
    # Find acceptance criteria section
    ac_section_pattern = re.compile(
        r"(?:^|\n)##?\s*(?:Acceptance\s*Criteria|Requirements)\s*\n(.*?)(?=\n##?\s|\Z)",
        re.IGNORECASE | re.DOTALL
    )
    
    section_match = ac_section_pattern.search(issue_body)
    if not section_match:
        # Fall back to searching entire body for checkboxes
        search_text = issue_body
    else:
        search_text = section_match.group(1)
    
    # Pattern for checkboxes
    checkbox_pattern = re.compile(r"^\s*-\s*\[([ xX])\]\s*(.+)$", re.MULTILINE)
    
    for i, match in enumerate(checkbox_pattern.finditer(search_text), start=1):
        checked = match.group(1).lower() == "x"
        text = match.group(2).strip()
        
        criteria.append({
            "id": f"AC-{i:03d}",
            "text": text,
            "checked": checked,
        })
    
    return criteria
```

### 6.12 `assemblyzero/skills/lib/gemini_reviewer.py` (Add)

**Complete file contents:**

```python
"""Gemini API integration for test plan review.

Issue #101: Call Gemini with retry logic and response parsing.
"""

import asyncio
import json
import os
from enum import Enum
from pathlib import Path
from typing import TypedDict, Optional, Any

from google import genai
from google.genai import types


# Constants
PROMPT_VERSION = "v1.0.0"
MODEL_VERSION = "gemini-2.0-flash"
CREDENTIALS_PATH = Path.home() / ".assemblyzero" / "gemini-credentials.json"


class ReviewVerdict(Enum):
    """Possible review verdicts."""
    PASS = "PASS"
    REVISE = "REVISE"
    ERROR = "ERROR"
    BLOCKED = "BLOCKED"


class CoverageMapping(TypedDict):
    """Maps an AC to its test coverage."""
    ac_id: str
    ac_text: str
    covered: bool
    test_cases: list[str]


class GapFinding(TypedDict):
    """Represents a gap found in test coverage."""
    category: str
    line_number: Optional[int]
    description: str
    severity: str


class ReviewResult(TypedDict):
    """Complete review result."""
    verdict: str
    confidence_score: int
    coverage_matrix: list[CoverageMapping]
    gaps: list[GapFinding]
    summary: str
    prompt_version: str
    model_version: str
    truncated: bool
    truncation_warning: Optional[str]


async def call_gemini_review(
    prompt: str,
    test_plan: str,
    acceptance_criteria: list[dict],
    max_retries: int = 3
) -> dict:
    """Call Gemini API with retry logic.
    
    Uses exponential backoff on failures: 1s, 2s, 4s.
    
    Args:
        prompt: System prompt for review
        test_plan: Test plan content
        acceptance_criteria: List of AC dicts
        max_retries: Maximum retry attempts
        
    Returns:
        Parsed JSON response from Gemini
        
    Raises:
        RuntimeError: If all retries exhausted
    """
    # Load credentials
    if not CREDENTIALS_PATH.exists():
        # Check legacy path
        legacy_path = Path.home() / ".agentos" / "gemini-credentials.json"
        if legacy_path.exists():
            creds_path = legacy_path
        else:
            raise RuntimeError(f"Gemini credentials not found at {CREDENTIALS_PATH}")
    else:
        creds_path = CREDENTIALS_PATH
    
    with open(creds_path) as f:
        creds = json.load(f)
    
    api_key = creds.get("api_key")
    if not api_key:
        raise RuntimeError("No api_key found in credentials file")
    
    # Initialize client
    client = genai.Client(api_key=api_key)
    
    # Format acceptance criteria for prompt
    ac_formatted = "\n".join(
        f"- {ac['id']}: {ac['text']}" for ac in acceptance_criteria
    )
    
    # Build full prompt
    full_prompt = prompt.replace("{acceptance_criteria}", ac_formatted)
    full_prompt = full_prompt.replace("{test_plan}", test_plan)
    
    # Retry loop with exponential backoff
    last_error: Optional[Exception] = None
    
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=MODEL_VERSION,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,  # Low temperature for consistent analysis
                    response_mime_type="application/json",
                ),
            )
            
            # Extract and parse JSON response
            response_text = response.text
            
            # Try to parse as JSON
            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                # Try to extract JSON from markdown code block
                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.find("```", json_start)
                    json_str = response_text[json_start:json_end].strip()
                    return json.loads(json_str)
                raise ValueError(f"Could not parse response as JSON: {response_text[:200]}")
                
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                # Exponential backoff: 1s, 2s, 4s
                wait_time = 2 ** attempt
                print(f"[test-plan-review] API call failed, retrying in {wait_time}s: {e}")
                await asyncio.sleep(wait_time)
    
    raise RuntimeError(f"API call failed after {max_retries} retries: {last_error}")


def parse_gemini_response(response: dict) -> ReviewResult:
    """Parse Gemini response into structured ReviewResult.
    
    Args:
        response: Raw response dict from Gemini
        
    Returns:
        Validated ReviewResult
        
    Raises:
        ValueError: If required fields missing or invalid
    """
    # Validate required fields
    required_fields = ["verdict", "confidence_score", "coverage_analysis", "gaps", "summary"]
    for field in required_fields:
        if field not in response:
            raise ValueError(f"Missing required field: {field}")
    
    # Validate verdict
    verdict = response["verdict"]
    if verdict not in ("PASS", "REVISE"):
        raise ValueError(f"Invalid verdict: {verdict}")
    
    # Build coverage matrix
    coverage_matrix: list[CoverageMapping] = []
    for item in response.get("coverage_analysis", []):
        coverage_matrix.append({
            "ac_id": item.get("ac_id", ""),
            "ac_text": "",  # Will be populated from original ACs
            "covered": item.get("covered", False),
            "test_cases": item.get("test_cases", []),
        })
    
    # Build gaps list
    gaps: list[GapFinding] = []
    for item in response.get("gaps", []):
        gaps.append({
            "category": item.get("category", "Unknown"),
            "line_number": item.get("line_number"),
            "description": item.get("description", ""),
            "severity": item.get("severity", "Minor"),
        })
    
    return {
        "verdict": verdict,
        "confidence_score": int(response.get("confidence_score", 0)),
        "coverage_matrix": coverage_matrix,
        "gaps": gaps,
        "summary": response.get("summary", ""),
        "prompt_version": PROMPT_VERSION,
        "model_version": MODEL_VERSION,
        "truncated": False,
        "truncation_warning": None,
    }
```

### 6.13 `assemblyzero/skills/test_plan_review.py` (Add)

**Complete file contents:**

```python
"""Test plan review skill - Gemini-powered quality gate.

Issue #101: Review test plans for coverage completeness and alignment
with acceptance criteria.
"""

import asyncio
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Any

from assemblyzero.skills.lib.markdown_sanitizer import sanitize_markdown
from assemblyzero.skills.lib.secrets_scanner import scan_for_secrets
from assemblyzero.skills.lib.token_counter import count_tokens, truncate_to_limit
from assemblyzero.skills.lib.test_plan_parser import parse_test_plan, extract_test_cases
from assemblyzero.skills.lib.acceptance_criteria_extractor import (
    fetch_issue,
    extract_acceptance_criteria,
)
from assemblyzero.skills.lib.gemini_reviewer import (
    call_gemini_review,
    parse_gemini_response,
    ReviewResult,
    PROMPT_VERSION,
    MODEL_VERSION,
)


# Constants
DEFAULT_MAX_TOKENS = 30000
PROMPT_PATH = Path("docs/prompts/test-plan-reviewer/v1.0.0.md")
FIXTURE_PATH = Path("tests/fixtures/gemini-test-plan-response.json")


class TestPlanMetadata:
    """Metadata about the reviewed test plan."""
    def __init__(
        self,
        file_path: str,
        content_hash: str,
        issue_number: int,
        test_case_count: int,
        token_count: int,
    ):
        self.file_path = file_path
        self.content_hash = content_hash
        self.issue_number = issue_number
        self.test_case_count = test_case_count
        self.token_count = token_count
    
    def to_dict(self) -> dict:
        return {
            "file_path": self.file_path,
            "content_hash": self.content_hash,
            "issue_number": self.issue_number,
            "test_case_count": self.test_case_count,
            "token_count": self.token_count,
        }


def _error_result(message: str) -> ReviewResult:
    """Create consistent ERROR response."""
    return {
        "verdict": "ERROR",
        "confidence_score": 0,
        "coverage_matrix": [],
        "gaps": [],
        "summary": message,
        "prompt_version": PROMPT_VERSION,
        "model_version": MODEL_VERSION,
        "truncated": False,
        "truncation_warning": None,
    }


def _blocked_result(message: str, secrets_lines: list[int]) -> ReviewResult:
    """Create consistent BLOCKED response."""
    return {
        "verdict": "BLOCKED",
        "confidence_score": 0,
        "coverage_matrix": [],
        "gaps": [],
        "summary": f"{message} Lines: {', '.join(map(str, secrets_lines))}",
        "prompt_version": PROMPT_VERSION,
        "model_version": MODEL_VERSION,
        "truncated": False,
        "truncation_warning": None,
    }


async def run_test_plan_review(
    issue_number: int,
    dry_run: bool = False,
    skip_secrets_scan: bool = False,
    mock_mode: bool = False
) -> ReviewResult:
    """Execute test plan review for the given issue number.
    
    Args:
        issue_number: GitHub issue number to review
        dry_run: If True, output payload without calling API
        skip_secrets_scan: If True, skip secrets detection
        mock_mode: If True, use golden fixture instead of API
        
    Returns:
        ReviewResult with verdict and analysis
    """
    print(f"[test-plan-review] Starting review for issue #{issue_number}")
    
    # Step 1: Load test plan
    test_plan_path = Path(f"docs/reports/{issue_number}/test-plan.md")
    if not test_plan_path.exists():
        return _error_result(f"Test plan not found at {test_plan_path}")
    
    content = test_plan_path.read_text(encoding="utf-8")
    print(f"[test-plan-review] Loaded test plan: {len(content)} chars")
    
    # Step 2: Compute content hash
    content_hash = hashlib.sha256(content.encode()).hexdigest()
    
    # Step 3: Secrets scan
    if not skip_secrets_scan:
        print("[test-plan-review] Scanning for secrets...")
        secrets = scan_for_secrets(content)
        if secrets:
            secret_lines = [s["line_number"] for s in secrets]
            print(f"[test-plan-review] BLOCKED - Secrets detected on lines: {secret_lines}")
            return _blocked_result("Secrets detected in test plan.", secret_lines)
        print("[test-plan-review] No secrets detected")
    
    # Step 4: Sanitize content
    sanitized = sanitize_markdown(content)
    
    # Step 5: Token counting and truncation
    token_count = count_tokens(sanitized)
    print(f"[test-plan-review] Token count: {token_count}")
    
    truncated = False
    truncation_warning: Optional[str] = None
    
    if token_count > DEFAULT_MAX_TOKENS:
        sanitized, truncation_warning = truncate_to_limit(sanitized, DEFAULT_MAX_TOKENS)
        truncated = True
        print(f"[test-plan-review] Content truncated: {truncation_warning}")
    
    # Step 6: Fetch issue and extract ACs
    try:
        print(f"[test-plan-review] Fetching issue #{issue_number}...")
        issue = await fetch_issue(issue_number)
    except RuntimeError as e:
        return _error_result(str(e))
    
    acceptance_criteria = extract_acceptance_criteria(issue.get("body", ""))
    print(f"[test-plan-review] Found {len(acceptance_criteria)} acceptance criteria")
    
    # Step 7: Parse test cases
    test_cases = extract_test_cases(sanitized)
    print(f"[test-plan-review] Found {len(test_cases)} test cases")
    
    # Build metadata
    metadata = TestPlanMetadata(
        file_path=str(test_plan_path),
        content_hash=content_hash,
        issue_number=issue_number,
        test_case_count=len(test_cases),
        token_count=token_count,
    )
    
    # Step 8: Load prompt
    if not PROMPT_PATH.exists():
        return _error_result(f"Prompt not found at {PROMPT_PATH}")
    
    prompt = PROMPT_PATH.read_text(encoding="utf-8")
    
    # Step 9: Build payload
    payload = {
        "prompt": prompt,
        "test_plan": sanitized,
        "acceptance_criteria": acceptance_criteria,
    }
    
    # Step 10: Dry run
    if dry_run:
        print("[test-plan-review] DRY RUN - Payload:")
        print(json.dumps(payload, indent=2))
        return {
            "verdict": "DRY_RUN",
            "confidence_score": 0,
            "coverage_matrix": [],
            "gaps": [],
            "summary": "Dry run completed - no API call made",
            "prompt_version": PROMPT_VERSION,
            "model_version": MODEL_VERSION,
            "truncated": truncated,
            "truncation_warning": truncation_warning,
        }
    
    # Step 11: Mock mode or API call
    if mock_mode or os.environ.get("TEST_PLAN_REVIEW_MOCK") == "true":
        print("[test-plan-review] Using mock fixture")
        if not FIXTURE_PATH.exists():
            return _error_result(f"Fixture not found at {FIXTURE_PATH}")
        with open(FIXTURE_PATH) as f:
            response = json.load(f)
    else:
        print("[test-plan-review] Calling Gemini API...")
        try:
            response = await call_gemini_review(
                prompt=prompt,
                test_plan=sanitized,
                acceptance_criteria=acceptance_criteria,
            )
        except RuntimeError as e:
            return _error_result(str(e))
    
    # Step 12: Parse response
    try:
        result = parse_gemini_response(response)
    except ValueError as e:
        return _error_result(f"Failed to parse response: {e}")
    
    # Update result with truncation info
    result["truncated"] = truncated
    result["truncation_warning"] = truncation_warning
    
    # Populate AC text in coverage matrix
    ac_lookup = {ac["id"]: ac["text"] for ac in acceptance_criteria}
    for mapping in result["coverage_matrix"]:
        mapping["ac_text"] = ac_lookup.get(mapping["ac_id"], "")
    
    # Step 13: Write audit trail
    output_path = Path(f"docs/reports/{issue_number}/test-plan-review.md")
    generate_review_report(result, metadata, output_path)
    print(f"[test-plan-review] Audit trail written to: {output_path}")
    
    return result


def generate_review_report(
    result: ReviewResult,
    metadata: TestPlanMetadata,
    output_path: Path
) -> None:
    """Write structured review output to markdown file."""
    # Ensure directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now(timezone.utc).isoformat()
    
    # Build report content
    lines = [
        f"# Test Plan Review - Issue #{metadata.issue_number}",
        "",
        "| Field | Value |",
        "|-------|-------|",
        f"| Verdict | {result['verdict']} |",
        f"| Confidence | {result['confidence_score']}% |",
        f"| Timestamp | {timestamp} |",
        f"| Test Plan Hash | {metadata.content_hash[:16]}... |",
        f"| Prompt Version | {result['prompt_version']} |",
        f"| Model Version | {result['model_version']} |",
        "",
    ]
    
    if result.get("truncation_warning"):
        lines.extend([
            "## ⚠️ Truncation Warning",
            "",
            result["truncation_warning"],
            "",
        ])
    
    lines.extend([
        "## Summary",
        "",
        result["summary"],
        "",
        "## Coverage Matrix",
        "",
        "| AC ID | Text | Covered | Test Cases |",
        "|-------|------|---------|------------|",
    ])
    
    for mapping in result["coverage_matrix"]:
        covered_mark = "✓" if mapping["covered"] else "✗"
        test_cases = ", ".join(mapping["test_cases"]) if mapping["test_cases"] else "-"
        text = mapping["ac_text"][:50] + "..." if len(mapping["ac_text"]) > 50 else mapping["ac_text"]
        lines.append(f"| {mapping['ac_id']} | {text} | {covered_mark} | {test_cases} |")
    
    lines.extend(["", "## Gaps", ""])
    
    if result["gaps"]:
        lines.extend([
            "| Severity | Category | Line | Description |",
            "|----------|----------|------|-------------|",
        ])
        for gap in result["gaps"]:
            line_ref = str(gap["line_number"]) if gap["line_number"] else "-"
            lines.append(
                f"| {gap['severity']} | {gap['category']} | {line_ref} | {gap['description']} |"
            )
    else:
        lines.append("None identified.")
    
    lines.extend(["", "---", f"*Generated by test-plan-review skill at {timestamp}*"])
    
    output_path.write_text("\n".join(lines), encoding="utf-8")
```

### 6.14 `docs/skills/test-plan-review.md` (Add)

**Complete file contents:**

```markdown
# Skill: test-plan-review

**Issue:** #101

## Purpose

Review test plans for coverage completeness, edge cases, and alignment with acceptance criteria using Gemini AI.

## Invocation

```bash
# Basic usage
claude skill:test-plan-review --issue 101

# Dry run (output payload without API call)
claude skill:test-plan-review --issue 101 --dry-run

# Skip secrets scan
claude skill:test-plan-review --issue 101 --skip-secrets-scan

# Use mock fixture (for testing)
TEST_PLAN_REVIEW_MOCK=true claude skill:test-plan-review --issue 101
```

## Input

- Test plan at `docs/reports/{issue}/test-plan.md`
- GitHub issue #{issue} (fetched via `gh` CLI)

## Output

- Verdict: PASS, REVISE, ERROR, or BLOCKED
- Coverage matrix mapping ACs to test cases
- Gap analysis with severity and line references
- Audit trail at `docs/reports/{issue}/test-plan-review.md`

## Verdicts

| Verdict | Meaning |
|---------|---------|
| PASS | 100% AC coverage, no critical gaps |
| REVISE | Missing coverage or critical gaps found |
| ERROR | API or system error occurred |
| BLOCKED | Secrets detected, submission blocked |

## Prerequisites

- `gh` CLI authenticated (`gh auth login`)
- Gemini credentials at `~/.assemblyzero/gemini-credentials.json`
- Test plan exists at expected path
```

### 6.15 `tests/fixtures/gemini-test-plan-response.json` (Add)

**Complete file contents:**

```json
{
  "verdict": "PASS",
  "confidence_score": 92,
  "coverage_analysis": [
    {
      "ac_id": "AC-001",
      "covered": true,
      "test_cases": ["TC-130"]
    },
    {
      "ac_id": "AC-002",
      "covered": true,
      "test_cases": ["TC-020", "TC-030"]
    },
    {
      "ac_id": "AC-003",
      "covered": true,
      "test_cases": ["TC-030", "TC-140"]
    },
    {
      "ac_id": "AC-004",
      "covered": true,
      "test_cases": ["TC-010", "TC-040"]
    },
    {
      "ac_id": "AC-005",
      "covered": true,
      "test_cases": ["TC-050"]
    },
    {
      "ac_id": "AC-006",
      "covered": true,
      "test_cases": ["TC-060"]
    },
    {
      "ac_id": "AC-007",
      "covered": true,
      "test_cases": ["TC-070"]
    },
    {
      "ac_id": "AC-008",
      "covered": true,
      "test_cases": ["TC-020"]
    },
    {
      "ac_id": "AC-009",
      "covered": true,
      "test_cases": ["TC-070", "TC-090"]
    },
    {
      "ac_id": "AC-010",
      "covered": true,
      "test_cases": ["TC-080", "TC-100"]
    },
    {
      "ac_id": "AC-011",
      "covered": true,
      "test_cases": ["TC-110"]
    },
    {
      "ac_id": "AC-012",
      "covered": true,
      "test_cases": ["TC-110", "TC-120"]
    },
    {
      "ac_id": "AC-013",
      "covered": true,
      "test_cases": ["TC-100"]
    },
    {
      "ac_id": "AC-014",
      "covered": true,
      "test_cases": ["TC-120"]
    }
  ],
  "gaps": [],
  "summary": "Test plan provides comprehensive coverage of all 14 acceptance criteria. Each requirement is mapped to at least one test case. No critical gaps identified."
}
```

### 6.16 `tests/fixtures/sample-test-plan.md` (Add)

**Complete file contents:**

```markdown
# Test Plan for Issue #101 - Test Plan Reviewer

## Overview

This test plan covers the Gemini-powered test plan review skill.

## Test Cases

### TC-010: Happy path - test plan passes
Valid test plan with all ACs covered should return PASS verdict.

### TC-020: Structured feedback with line refs
Test plan with gaps should return REVISE verdict with line numbers in gap analysis.

### TC-030: Coverage matrix generation
Review should produce coverage matrix mapping each AC to test cases.

### TC-040: PASS requires full coverage
Test plan covering all ACs with no critical gaps returns PASS.

### TC-050: REVISE includes remediation
Test plan missing 2 ACs returns REVISE with actionable guidance.

### TC-060: ERROR on persistent API failure
Force retry exhaustion should return ERROR verdict, not silent PASS.

### TC-070: Secrets detected - API key
Test plan with `API_KEY=sk-xxx` pattern returns BLOCKED verdict.

### TC-080: Markdown sanitization XSS
Input with `<script>alert('x')</script>` has script stripped.

### TC-090: Secrets scan blocks submission
Test plan with `password: "secret"` pattern blocked before API call.

### TC-100: Retry with exponential backoff
API failure then success shows correct retry timing.

### TC-110: Token limit exceeded
100KB test plan is truncated with warning message.

### TC-120: Golden fixture for offline dev
`TEST_PLAN_REVIEW_MOCK=true` uses fixture response.

### TC-130: Dry run mode
`--dry-run` flag outputs payload without API call.

### TC-140: Audit trail completeness
Review output file contains hash, timestamp, verdict, prompt version.
```

### 6.17 `tests/unit/skills/` (Add Directory)

**Action:** Create directory at `tests/unit/skills/`

### 6.18 `tests/unit/skills/__init__.py` (Add)

**Complete file contents:**

```python
"""Unit tests for skills module."""
```

### 6.19 `tests/unit/skills/test_test_plan_parser.py` (Add)

**Complete file contents:**

```python
"""Tests for test plan parser.

Issue #101: T010 - Test plan parser extracts test cases.
"""

import pytest
from assemblyzero.skills.lib.test_plan_parser import parse_test_plan, extract_test_cases


class TestParseTestPlan:
    """Tests for parse_test_plan function."""
    
    def test_empty_content(self):
        """Empty content returns empty structure."""
        result = parse_test_plan("")
        assert result["title"] == ""
        assert result["sections"] == []
        assert result["test_cases"] == []
        assert result["metadata"] == {}
    
    def test_extracts_title(self):
        """Extracts H1 as title."""
        content = "# Test Plan for Issue #101\n\nContent here."
        result = parse_test_plan(content)
        assert result["title"] == "Test Plan for Issue #101"
    
    def test_extracts_sections(self):
        """Extracts H2 sections."""
        content = """# Title

## Overview
This is the overview.

## Test Cases
List of test cases.
"""
        result = parse_test_plan(content)
        assert len(result["sections"]) == 2
        assert result["sections"][0]["heading"] == "Overview"
        assert result["sections"][1]["heading"] == "Test Cases"
    
    def test_extracts_issue_reference(self):
        """Extracts issue number from title."""
        content = "# Test Plan for Issue #101"
        result = parse_test_plan(content)
        assert result["metadata"]["issue_reference"] == 101


class TestExtractTestCases:
    """Tests for extract_test_cases function."""
    
    def test_no_test_cases(self):
        """Empty list when no test cases found."""
        content = "# Test Plan\n\nNo test cases here."
        result = extract_test_cases(content)
        assert result == []
    
    def test_header_format(self):
        """Extracts test cases in ### TC-NNN: Title format."""
        content = """## Test Cases

### TC-010: Valid input test
Tests that valid input is processed correctly.

### TC-020: Invalid input test
Tests error handling.
"""
        result = extract_test_cases(content)
        assert len(result) == 2
        assert result[0]["id"] == "TC-010"
        assert result[0]["title"] == "Valid input test"
        assert "valid input" in result[0]["description"].lower()
        assert result[1]["id"] == "TC-020"
    
    def test_list_format(self):
        """Extracts test cases in list format."""
        content = """## Test Cases

- TC-010: Valid input test
- TC-020: Invalid input test
"""
        result = extract_test_cases(content)
        assert len(result) == 2
        assert result[0]["id"] == "TC-010"
        assert result[1]["id"] == "TC-020"
    
    def test_includes_line_numbers(self):
        """Each test case includes line number."""
        content = """# Title

## Test Cases

### TC-010: Test
Description.
"""
        result = extract_test_cases(content)
        assert result[0]["line_number"] > 0
```

### 6.20 `tests/unit/skills/test_markdown_sanitizer.py` (Add)

**Complete file contents:**

```python
"""Tests for markdown sanitizer.

Issue #101: T020 - Markdown sanitizer strips script tags.
"""

import pytest
from assemblyzero.skills.lib.markdown_sanitizer import sanitize_markdown


class TestSanitizeMarkdown:
    """Tests for sanitize_markdown function."""
    
    def test_empty_string(self):
        """Empty string returns empty string."""
        assert sanitize_markdown("") == ""
    
    def test_no_html(self):
        """Content with no HTML is unchanged."""
        content = "# Header\n\nSome **bold** text."
        # bleach may slightly modify formatting, so just check key content preserved
        result = sanitize_markdown(content)
        assert "Header" in result
        assert "bold" in result
    
    def test_strips_script_tags(self):
        """Removes script tags."""
        content = "Safe text<script>alert('xss')</script>more text"
        result = sanitize_markdown(content)
        assert "<script>" not in result
        assert "alert" not in result
        assert "Safe text" in result
        assert "more text" in result
    
    def test_strips_iframe(self):
        """Removes iframe tags."""
        content = '<iframe src="evil.html"></iframe>Safe content'
        result = sanitize_markdown(content)
        assert "<iframe" not in result
        assert "Safe content" in result
    
    def test_preserves_allowed_tags(self):
        """Preserves safe HTML tags."""
        content = "<strong>Bold</strong> and <em>italic</em>"
        result = sanitize_markdown(content)
        assert "<strong>" in result or "Bold" in result
        assert "italic" in result
    
    def test_nested_scripts(self):
        """Removes nested script tags."""
        content = "<script><script>nested</script></script>clean"
        result = sanitize_markdown(content)
        assert "<script>" not in result
        assert "clean" in result
```

### 6.21 `tests/unit/skills/test_secrets_scanner.py` (Add)

**Complete file contents:**

```python
"""Tests for secrets scanner.

Issue #101: T030, T040 - Secrets scanner detection.
"""

import pytest
from assemblyzero.skills.lib.secrets_scanner import scan_for_secrets, redact_secret


class TestScanForSecrets:
    """Tests for scan_for_secrets function."""
    
    def test_no_secrets(self):
        """Clean content returns empty list."""
        content = "# Test Plan\n\nJust normal text here."
        result = scan_for_secrets(content)
        assert result == []
    
    def test_detects_api_key(self):
        """Detects API_KEY pattern."""
        content = "Line 1\nAPI_KEY=sk-abc123xyz789xyz789xyz\nLine 3"
        result = scan_for_secrets(content)
        assert len(result) >= 1
        assert any(s["line_number"] == 2 for s in result)
        assert any(s["pattern_type"] == "api_key" for s in result)
    
    def test_detects_password(self):
        """Detects password pattern."""
        content = 'password: "my_secret_password_here"'
        result = scan_for_secrets(content)
        assert len(result) >= 1
        assert any(s["pattern_type"] == "password" for s in result)
    
    def test_detects_github_token(self):
        """Detects GitHub token pattern."""
        content = "token = ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        result = scan_for_secrets(content)
        assert len(result) >= 1
        assert any(s["pattern_type"] == "github_token" for s in result)
    
    def test_detects_aws_key(self):
        """Detects AWS access key pattern."""
        content = "AKIAIOSFODNN7EXAMPLE"
        result = scan_for_secrets(content)
        assert len(result) >= 1
        assert any(s["pattern_type"] == "aws_access_key" for s in result)
    
    def test_multiple_secrets_same_line(self):
        """Multiple patterns on same line detected."""
        content = "API_KEY=sk-xxxxxxxxxxxxxxxxxxxx password: secret123456"
        result = scan_for_secrets(content)
        assert len(result) >= 2
    
    def test_returns_redacted_text(self):
        """Matched text is redacted."""
        content = "API_KEY=sk-abc123xyz789xyz789xyz"
        result = scan_for_secrets(content)
        assert result[0]["matched_text"] != "sk-abc123xyz789xyz789xyz"
        assert "****" in result[0]["matched_text"]


class TestRedactSecret:
    """Tests for redact_secret function."""
    
    def test_empty_string(self):
        """Empty string returns masked."""
        assert redact_secret("", "api_key") == "****"
    
    def test_short_secret(self):
        """Short secrets fully redacted."""
        assert redact_secret("abc", "password") == "****"
    
    def test_preserves_prefix_for_keys(self):
        """Key types preserve prefix."""
        result = redact_secret("sk-abc123xyz789xyz789xyz", "openai_key")
        assert result.startswith("sk-")
        assert "****" in result
    
    def test_connection_string(self):
        """Connection strings show protocol only."""
        result = redact_secret("postgres://user:pass@host/db", "connection_string")
        assert result == "postgres://****"
```

### 6.22 `tests/unit/skills/test_acceptance_criteria_extractor.py` (Add)

**Complete file contents:**

```python
"""Tests for acceptance criteria extractor.

Issue #101: T050 - AC extractor parses checkbox format.
"""

import pytest
from assemblyzero.skills.lib.acceptance_criteria_extractor import extract_acceptance_criteria


class TestExtractAcceptanceCriteria:
    """Tests for extract_acceptance_criteria function."""
    
    def test_empty_body(self):
        """Empty body returns empty list."""
        result = extract_acceptance_criteria("")
        assert result == []
    
    def test_no_ac_section(self):
        """Body without AC section returns empty list."""
        body = "# Description\n\nJust a description, no ACs."
        result = extract_acceptance_criteria(body)
        assert result == []
    
    def test_extracts_unchecked(self):
        """Extracts unchecked checkboxes."""
        body = """## Acceptance Criteria
- [ ] First criterion
- [ ] Second criterion
"""
        result = extract_acceptance_criteria(body)
        assert len(result) == 2
        assert result[0]["text"] == "First criterion"
        assert result[0]["checked"] is False
    
    def test_extracts_checked(self):
        """Extracts checked checkboxes."""
        body = """## Acceptance Criteria
- [x] Done criterion
- [X] Also done
"""
        result = extract_acceptance_criteria(body)
        assert len(result) == 2
        assert result[0]["checked"] is True
        assert result[1]["checked"] is True
    
    def test_mixed_checkboxes(self):
        """Extracts mixed checked/unchecked."""
        body = """## Acceptance Criteria
- [x] Done
- [ ] Not done
- [x] Also done
"""
        result = extract_acceptance_criteria(body)
        assert len(result) == 3
        assert result[0]["checked"] is True
        assert result[1]["checked"] is False
        assert result[2]["checked"] is True
    
    def test_generates_ids(self):
        """Generates sequential AC IDs."""
        body = """## Acceptance Criteria
- [ ] First
- [ ] Second
- [ ] Third
"""
        result = extract_acceptance_criteria(body)
        assert result[0]["id"] == "AC-001"
        assert result[1]["id"] == "AC-002"
        assert result[2]["id"] == "AC-003"
    
    def test_requirements_section_alias(self):
        """Also matches 'Requirements' section."""
        body = """## Requirements
- [ ] A requirement
"""
        result = extract_acceptance_criteria(body)
        assert len(result) == 1
```

### 6.23 `tests/unit/skills/test_token_counter.py` (Add)

**Complete file contents:**

```python
"""Tests for token counter.

Issue #101: T060, T070 - Token counting and truncation.
"""

import pytest
from assemblyzero.skills.lib.token_counter import count_tokens, truncate_to_limit


class TestCountTokens:
    """Tests for count_tokens function."""
    
    def test_empty_string(self):
        """Empty string returns 0."""
        assert count_tokens("") == 0
    
    def test_simple_text(self):
        """Simple text returns non-zero count."""
        result = count_tokens("Hello, world!")
        assert result > 0
    
    def test_longer_text(self):
        """Longer text has more tokens."""
        short = count_tokens("Hello")
        long = count_tokens("Hello, this is a much longer piece of text.")
        assert long > short
    
    def test_unicode(self):
        """Unicode characters handled."""
        result = count_tokens("Hello 世界 🌍")
        assert result > 0


class TestTruncateToLimit:
    """Tests for truncate_to_limit function."""
    
    def test_under_limit_unchanged(self):
        """Content under limit returned unchanged."""
        content = "Short text"
        result, warning = truncate_to_limit(content, 1000)
        assert result == content
        assert warning is None
    
    def test_over_limit_truncated(self):
        """Content over limit is truncated."""
        content = "Word " * 1000  # Generate long content
        result, warning = truncate_to_limit(content, 50)
        assert len(result) < len(content)
        assert warning is not None
        assert "truncated" in warning.lower()
    
    def test_truncation_marker_added(self):
        """Truncated content has marker."""
        content = "Word " * 1000
        result, _ = truncate_to_limit(content, 50, preserve_structure=True)
        assert "[TRUNCATED" in result
    
    def test_zero_limit(self):
        """Zero limit returns empty with warning."""
        content = "Some text"
        result, warning = truncate_to_limit(content, 0)
        assert result == ""
        assert warning is not None
    
    def test_warning_includes_counts(self):
        """Warning message includes token counts."""
        content = "Word " * 1000
        _, warning = truncate_to_limit(content, 50)
        assert "50" in warning
```

### 6.24 `tests/unit/skills/test_test_plan_review.py` (Add)

**Complete file contents:**

```python
"""Tests for test plan review skill.

Issue #101: T080-T140 - Main skill tests.
"""

import pytest
import json
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

from assemblyzero.skills.test_plan_review import (
    run_test_plan_review,
    generate_review_report,
    _error_result,
    _blocked_result,
    TestPlanMetadata,
)


class TestErrorResult:
    """Tests for _error_result helper."""
    
    def test_creates_error_verdict(self):
        """Creates result with ERROR verdict."""
        result = _error_result("Something went wrong")
        assert result["verdict"] == "ERROR"
        assert result["confidence_score"] == 0
        assert result["summary"] == "Something went wrong"
    
    def test_includes_version_info(self):
        """Includes prompt and model version."""
        result = _error_result("Error")
        assert "prompt_version" in result
        assert "model_version" in result


class TestBlockedResult:
    """Tests for _blocked_result helper."""
    
    def test_creates_blocked_verdict(self):
        """Creates result with BLOCKED verdict."""
        result = _blocked_result("Secrets found", [10, 20])
        assert result["verdict"] == "BLOCKED"
        assert "10" in result["summary"]
        assert "20" in result["summary"]


class TestGenerateReviewReport:
    """Tests for generate_review_report function."""
    
    def test_creates_file(self, tmp_path):
        """Creates output file."""
        result = {
            "verdict": "PASS",
            "confidence_score": 95,
            "coverage_matrix": [],
            "gaps": [],
            "summary": "All good",
            "prompt_version": "v1.0.0",
            "model_version": "gemini-2.0-flash",
            "truncated": False,
            "truncation_warning": None,
        }
        metadata = TestPlanMetadata(
            file_path="test.md",
            content_hash="abc123",
            issue_number=101,
            test_case_count=5,
            token_count=1000,
        )
        output_path = tmp_path / "review.md"
        
        generate_review_report(result, metadata, output_path)
        
        assert output_path.exists()
        content = output_path.read_text()
        assert "PASS" in content
        assert "95%" in content
        assert "abc123" in content
    
    def test_includes_coverage_matrix(self, tmp_path):
        """Output includes coverage matrix table."""
        result = {
            "verdict": "PASS",
            "confidence_score": 90,
            "coverage_matrix": [
                {"ac_id": "AC-001", "ac_text": "Test criterion", "covered": True, "test_cases": ["TC-010"]}
            ],
            "gaps": [],
            "summary": "Good",
            "prompt_version": "v1.0.0",
            "model_version": "gemini-2.0-flash",
            "truncated": False,
            "truncation_warning": None,
        }
        metadata = TestPlanMetadata("", "hash", 1, 1, 100)
        output_path = tmp_path / "review.md"
        
        generate_review_report(result, metadata, output_path)
        
        content = output_path.read_text()
        assert "AC-001" in content
        assert "TC-010" in content
        assert "✓" in content
    
    def test_includes_gaps(self, tmp_path):
        """Output includes gaps table."""
        result = {
            "verdict": "REVISE",
            "confidence_score": 60,
            "coverage_matrix": [],
            "gaps": [
                {"category": "Edge Cases", "line_number": 15, "description": "Missing test", "severity": "Major"}
            ],
            "summary": "Needs work",
            "prompt_version": "v1.0.0",
            "model_version": "gemini-2.0-flash",
            "truncated": False,
            "truncation_warning": None,
        }
        metadata = TestPlanMetadata("", "hash", 1, 1, 100)
        output_path = tmp_path / "review.md"
        
        generate_review_report(result, metadata, output_path)
        
        content = output_path.read_text()
        assert "Edge Cases" in content
        assert "15" in content
        assert "Major" in content


@pytest.mark.asyncio
class TestRunTestPlanReview:
    """Tests for run_test_plan_review function."""
    
    async def test_file_not_found(self, tmp_path, monkeypatch):
        """Returns ERROR when test plan not found."""
        monkeypatch.chdir(tmp_path)
        
        result = await run_test_plan_review(999)
        
        assert result["verdict"] == "ERROR"
        assert "not found" in result["summary"].lower()
    
    async def test_dry_run_no_api_call(self, tmp_path, monkeypatch):
        """Dry run doesn't call API."""
        monkeypatch.chdir(tmp_path)
        
        # Create test plan
        plan_dir = tmp_path / "docs" / "reports" / "101"
        plan_dir.mkdir(parents=True)
        (plan_dir / "test-plan.md").write_text("# Test Plan\n\n## Test Cases\n")
        
        # Create prompt
        prompt_dir = tmp_path / "docs" / "prompts" / "test-plan-reviewer"
        prompt_dir.mkdir(parents=True)
        (prompt_dir / "v1.0.0.md").write_text("Prompt template")
        
        with patch("assemblyzero.skills.test_plan_review.fetch_issue") as mock_fetch:
            mock_fetch.return_value = {"body": "## Acceptance Criteria\n- [ ] Test"}
            
            result = await run_test_plan_review(101, dry_run=True)
        
        assert result["verdict"] == "DRY_RUN"
```

### 6.25 `tests/integration/test_test_plan_review_integration.py` (Add)

**Complete file contents:**

```python
"""Integration tests for test plan review skill.

Issue #101: Integration tests with mock mode.
"""

import pytest
import json
from pathlib import Path
from unittest.mock import patch, AsyncMock

from assemblyzero.skills.test_plan_review import run_test_plan_review


@pytest.fixture
def test_environment(tmp_path, monkeypatch):
    """Set up test environment with required files."""
    monkeypatch.chdir(tmp_path)
    
    # Create test plan
    plan_dir = tmp_path / "docs" / "reports" / "101"
    plan_dir.mkdir(parents=True)
    (plan_dir / "test-plan.md").write_text("""# Test Plan for Issue #101

## Test Cases

### TC-010: Happy path
Valid input returns success.
""")
    
    # Create prompt
    prompt_dir = tmp_path / "docs" / "prompts" / "test-plan-reviewer"
    prompt_dir.mkdir(parents=True)
    (prompt_dir / "v1.0.0.md").write_text("Review prompt {acceptance_criteria} {test_plan}")
    
    # Create fixture
    fixture_dir = tmp_path / "tests" / "fixtures"
    fixture_dir.mkdir(parents=True)
    (fixture_dir / "gemini-test-plan-response.json").write_text(json.dumps({
        "verdict": "PASS",
        "confidence_score": 90,
        "coverage_analysis": [{"ac_id": "AC-001", "covered": True, "test_cases": ["TC-010"]}],
        "gaps": [],
        "summary": "Good coverage."
    }))
    
    return tmp_path


@pytest.mark.asyncio
class TestTestPlanReviewIntegration:
    """Integration tests using mock mode."""
    
    async def test_mock_mode_uses_fixture(self, test_environment, monkeypatch):
        """Mock mode uses fixture response."""
        monkeypatch.setenv("TEST_PLAN_REVIEW_MOCK", "true")
        
        # Update paths to use test environment
        monkeypatch.setattr(
            "assemblyzero.skills.test_plan_review.PROMPT_PATH",
            test_environment / "docs" / "prompts" / "test-plan-reviewer" / "v1.0.0.md"
        )
        monkeypatch.setattr(
            "assemblyzero.skills.test_plan_review.FIXTURE_PATH",
            test_environment / "tests" / "fixtures" / "gemini-test-plan-response.json"
        )
        
        with patch("assemblyzero.skills.test_plan_review.fetch_issue") as mock_fetch:
            mock_fetch.return_value = {"body": "## Acceptance Criteria\n- [ ] Test criterion"}
            
            result = await run_test_plan_review(101, mock_mode=True)
        
        assert result["verdict"] == "PASS"
        assert result["confidence_score"] == 90
    
    async def test_secrets_block_submission(self, test_environment, monkeypatch):
        """Secrets in test plan block review."""
        # Add secret to test plan
        plan_path = test_environment / "docs" / "reports" / "101" / "test-plan.md"
        plan_path.write_text("""# Test Plan

## Config
API_KEY=sk-abc123xyz789xyz789xyz

## Test Cases
- TC-010: Test
""")
        
        result = await run_test_plan_review(101)
        
        assert result["verdict"] == "BLOCKED"
        assert "Secrets detected" in result["summary"]
    
    async def test_skip_secrets_scan(self, test_environment, monkeypatch):
        """Skip secrets scan flag works."""
        # Add secret to test plan
        plan_path = test_environment / "docs" / "reports" / "101" / "test-plan.md"
        plan_path.write_text("""# Test Plan

## Config
API_KEY=sk-abc123xyz789xyz789xyz

## Test Cases
- TC-010: Test
""")
        
        monkeypatch.setattr(
            "assemblyzero.skills.test_plan_review.PROMPT_PATH",
            test_environment / "docs" / "prompts" / "test-plan-reviewer" / "v1.0.0.md"
        )
        monkeypatch.setattr(
            "assemblyzero.skills.test_plan_review.FIXTURE_PATH",
            test_environment / "tests" / "fixtures" / "gemini-test-plan-response.json"
        )
        
        with patch("assemblyzero.skills.test_plan_review.fetch_issue") as mock_fetch:
            mock_fetch.return_value = {"body": "## Acceptance Criteria\n- [ ] Test"}
            
            result = await run_test_plan_review(101, skip_secrets_scan=True, mock_mode=True)
        
        # Should not be blocked since we skipped the scan
        assert result["verdict"] != "BLOCKED"
```

### 6.26 `pyproject.toml` (Modify)

**Change 1:** Add bleach dependency at line 22 (after the tiktoken line)

```diff
     "pygithub (>=2.8.1,<3.0.0)",
     "tiktoken (>=0.9.0,<1.0.0)",
+    "bleach (>=6.1.0,<7.0.0)",
     "langchain-core (>=1.2.9,<2.0.0)",
```

### 6.27 `docs/0003-file-inventory.md` (Modify)

**Change 1:** Add new section for Skills Implementation after Tools Inventory (after line ~180)

```diff
 ---

+## 5. Skills Implementation (New)
+
+### Test Plan Reviewer (Issue #101)
+
+| File | Status | Description |
+|------|--------|-------------|
+| `assemblyzero/skills/__init__.py` | Beta | Skills module init |
+| `assemblyzero/skills/test_plan_review.py` | Beta | Main skill implementation |
+| `assemblyzero/skills/lib/__init__.py` | Beta | Lib module init |
+| `assemblyzero/skills/lib/markdown_sanitizer.py` | Beta | HTML/script sanitization |
+| `assemblyzero/skills/lib/secrets_scanner.py` | Beta | Pre-flight secrets detection |
+| `assemblyzero/skills/lib/token_counter.py` | Beta | Token counting and truncation |
+| `assemblyzero/skills/lib/test_plan_parser.py` | Beta | Test plan markdown parsing |
+| `assemblyzero/skills/lib/acceptance_criteria_extractor.py` | Beta | GitHub AC extraction |
+| `assemblyzero/skills/lib/gemini_reviewer.py` | Beta | Gemini API integration |
+| `docs/skills/test-plan-review.md` | Beta | Skill documentation |
+| `docs/prompts/test-plan-reviewer/v1.0.0.md` | Beta | Review prompt v1 |
+
+---
+
```

**Change 2:** Update Summary Statistics (around line 200)

```diff
-## 5. Summary Statistics
+## 6. Summary Statistics

 | Category | Count | Status |
 |----------|-------|--------|
 | Standards | 9 | All stable |
 | Templates | 10 | All stable |
 | ADRs | 6 | All stable |
-| Skills | 28 | All stable |
+| Skills (Docs) | 28 | All stable |
+| Skills (Code) | 11 | All beta |
 | Audits | 34 | 28 stable, 6 stubs |
 | Runbooks | 5 | All stable |
 | Tools | 11 | 9 stable, 2 beta |
 | Commands | 8 | All stable |
-| **Total Docs** | **91** | |
+| **Total Docs** | **93** | |
 | **Total Tools** | **11** | |
+| **Total Skills Code** | **11** | |
```

## 7. Pattern References

### 7.1 Async Subprocess Pattern

**File:** `assemblyzero/workflows/requirements/nodes/fetch_issue.py` (lines 20-60)

```python
async def fetch_issue(state: RequirementsState) -> dict[str, Any]:
    """Fetch GitHub issue content via gh CLI."""
    issue_number = state["issue_number"]
    
    cmd = [
        "gh", "issue", "view", str(issue_number),
        "--json", "number,title,body,state,labels"
    ]
    
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    
    stdout, stderr = await process.communicate()
    
    if process.returncode != 0:
        raise RuntimeError(f"gh CLI error: {stderr.decode()}")
    
    return json.loads(stdout.decode())
```

**Relevance:** The `acceptance_criteria_extractor.py` module should follow this exact pattern for async subprocess calls to `gh` CLI.

### 7.2 TypedDict Pattern for Results

**File:** `assemblyzero/workflows/requirements/state.py` (lines 1-40)

```python
"""State definitions using TypedDict."""

from typing import TypedDict, Optional
from enum import Enum

class WorkflowStatus(Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"

class WorkflowResult(TypedDict):
    status: WorkflowStatus
    output: str
    error_message: Optional[str]
```

**Relevance:** The `ReviewResult` and other TypedDicts should follow this pattern for type safety.

### 7.3 Gemini Client Pattern

**File:** `assemblyzero/workflows/scout/nodes/research.py` (lines 50-90)

```python
from google import genai
from google.genai import types

def call_gemini(prompt: str) -> str:
    """Call Gemini API with standard configuration."""
    client = genai.Client(api_key=api_key)
    
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.1,
        ),
    )
    
    return response.text
```

**Relevance:** The `gemini_reviewer.py` module should follow this pattern for Gemini API calls, adding retry logic and JSON response parsing.

## 8. Dependencies & Imports

| Import | Source | Used In |
|--------|--------|---------|
| `from typing import TypedDict, Optional, Any` | stdlib | All new files |
| `from pathlib import Path` | stdlib | `test_plan_review.py`, `gemini_reviewer.py` |
| `from enum import Enum` | stdlib | `gemini_reviewer.py` |
| `import asyncio` | stdlib | `acceptance_criteria_extractor.py`, `gemini_reviewer.py`, `test_plan_review.py` |
| `import hashlib` | stdlib | `test_plan_review.py` |
| `import json` | stdlib | Multiple files |
| `import re` | stdlib | `secrets_scanner.py`, `test_plan_parser.py`, `acceptance_criteria_extractor.py` |
| `import subprocess` | stdlib | `acceptance_criteria_extractor.py` |
| `import os` | stdlib | `test_plan_review.py` |
| `from datetime import datetime, timezone` | stdlib | `test_plan_review.py` |
| `import bleach` | pypi (new) | `markdown_sanitizer.py` |
| `import tiktoken` | pypi (existing) | `token_counter.py` |
| `from google import genai` | pypi (existing) | `gemini_reviewer.py` |
| `from google.genai import types` | pypi (existing) | `gemini_reviewer.py` |
| `import pytest` | pypi (dev) | All test files |

**New Dependencies:** `bleach (>=6.1.0,<7.0.0)` added to pyproject.toml

## 9. Test Mapping

| Test ID | Tests Function | Input | Expected Output |
|---------|---------------|-------|-----------------|
| T010 | `parse_test_plan()`, `extract_test_cases()` | Valid markdown with TC headers | List of test case dicts with id, title, line_number |
| T020 | `sanitize_markdown()` | HTML with `<script>alert('xss')</script>` | Script tags removed, safe content preserved |
| T030 | `scan_for_secrets()` | Content with `API_KEY=sk-abc123xyz789` | `[{"line_number": 1, "pattern_type": "api_key", ...}]` |
| T040 | `scan_for_secrets()` | Clean content `"# Test Plan\nNormal text"` | `[]` (empty list) |
| T050 | `extract_acceptance_criteria()` | Issue body with `- [ ] First\n- [x] Second` | `[{"id": "AC-001", "text": "First", "checked": False}, ...]` |
| T060 | `count_tokens()` | `"Hello, world! This is a test."` | Integer > 0 (approximately 8-10) |
| T070 | `truncate_to_limit()` | 10KB content, `max_tokens=50` | Truncated content with `[TRUNCATED...]` marker |
| T080 | `call_gemini_review()` | Force 2 failures then success | Success response after 2 retries with backoff timing |
| T090 | `parse_gemini_response()` | Valid JSON with verdict, coverage_analysis | `ReviewResult` dict with all fields populated |
| T100 | `run_test_plan_review()` | `dry_run=True` | Payload printed to stdout, verdict="DRY_RUN" |
| T110 | `run_test_plan_review()` | `mock_mode=True` | Fixture response used, no API call |
| T120 | `generate_review_report()` | ReviewResult + metadata | File created with hash, timestamp, verdict, coverage table |
| T130 | `run_test_plan_review()` | Valid issue number, mock_mode=True | ReviewResult with PASS/REVISE verdict |
| T140 | Coverage matrix | Test plan + 5 ACs | Matrix shows each AC with covered status and test case IDs |

## 10. Implementation Notes

### 10.1 Error Handling Convention

All functions that can fail return structured results rather than raising exceptions at the top level:

- `run_test_plan_review()` returns `ReviewResult` with `verdict=ERROR` on failures
- `_error_result()` helper creates consistent ERROR responses
- `_blocked_result()` helper creates consistent BLOCKED responses
- Helper functions like `fetch_issue()` raise `RuntimeError` which is caught by the main skill
- Inner library functions may raise for validation errors (e.g., `parse_gemini_response()` raises `ValueError`)

### 10.2 Logging Convention

Use `print()` with `[skill-name]` prefix for user-facing output:

```python
print(f"[test-plan-review] Audit trail written to: {output_path}")
print(f"[test-plan-review] Scanning for secrets...")
print(f"[test-plan-review] API call failed, retrying in {wait_time}s: {error}")
```

### 10.3 Constants

| Constant | Value | Rationale |
|----------|-------|-----------|
| `DEFAULT_MAX_TOKENS` | `30000` | Leave room for prompt (~5K) and response (~5K) within 40K context |
| `ENCODING_NAME` | `"cl100k_base"` | Standard tiktoken encoding, compatible with Gemini |
| `PROMPT_VERSION` | `"v1.0.0"` | Semantic versioning for audit trail |
| `MODEL_VERSION` | `"gemini-2.0-flash"` | Current Gemini model in use |
| `max_retries` | `3` | Balance reliability vs. latency |
| `CREDENTIALS_PATH` | `~/.assemblyzero/gemini-credentials.json` | Standard credentials location |

### 10.4 File Paths

| Path | Purpose |
|------|---------|
| `docs/reports/{issue}/test-plan.md` | Input test plan |
| `docs/reports/{issue}/test-plan-review.md` | Output audit trail |
| `docs/prompts/test-plan-reviewer/v1.0.0.md` | Versioned prompt |
| `~/.assemblyzero/gemini-credentials.json` | Gemini API credentials |
| `~/.agentos/gemini-credentials.json` | Legacy credentials path (fallback) |
| `tests/fixtures/gemini-test-plan-response.json` | Mock API response |
| `tests/fixtures/sample-test-plan.md` | Sample test plan for testing |

---

## Completeness Checklist

- [x] Every "Modify" file has a current state excerpt (Section 3)
- [x] Every data structure has a concrete JSON/YAML example (Section 4)
- [x] Every function has input/output examples with realistic values (Section 5)
- [x] Change instructions are diff-level specific (Section 6)
- [x] Pattern references include file:line and are verified to exist (Section 7)
- [x] All imports are listed and verified (Section 8)
- [x] Test mapping covers all LLD test scenarios (Section 9)

---

## Review Log

| Field | Value |
|-------|-------|
| Issue | #101 |
| Verdict | DRAFT |
| Date | 2026-02-17 |
| Iterations | 2 |
| Finalized | — |

---

## Review Log

| Field | Value |
|-------|-------|
| Issue | #101 |
| Verdict | APPROVED |
| Date | 2026-02-17 |
| Iterations | 1 |
| Finalized | 2026-02-17T10:34:16Z |

### Review Feedback Summary

Approved with suggestions:
*   **Configuration:** The spec assumes `gh` CLI is installed and authenticated. The error handling in `acceptance_criteria_extractor.py` correctly catches auth issues, but ensure the agent running the integration tests in the CI environment has these credentials or that the tests are marked to skip if `gh` is missing (though the provided integration test uses mocks, so this is safe).
*   **CLI Output:** The main skill uses `print()` statements for logging. Ensure this...
