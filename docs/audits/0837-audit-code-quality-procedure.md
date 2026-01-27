# 0837 - Code Quality Audit Procedure

**Status:** Active
**Created:** 2026-01-27
**Purpose:** Systematic procedure to audit all repos for silent failures, inadequate testing, and dishonest implementation patterns.

---

## Overview

This audit identifies code that:
1. **Fails silently** - Catches exceptions without logging/returning errors
2. **Lies with mocks** - Unit tests pass but real implementation fails
3. **Has no integration tests** - External commands never tested for real
4. **Uses subprocess incorrectly** - Windows .CMD/.BAT issues, missing shell=True
5. **Has misleading comments** - "TODO", "FIXME", "This should work"

---

## Phase 1: Automated Grep Audit

Run these searches from repo root. Save output to `audit-results.txt`.

### 1.1 Find Silent Exception Handlers

```bash
# Pattern 1: Bare except with pass
grep -rn "except.*:" . --include="*.py" | grep -A 1 "pass$"

# Pattern 2: Except returning False/None without logging
grep -rn "except.*:" . --include="*.py" | grep -A 1 "return False"
grep -rn "except.*:" . --include="*.py" | grep -A 1 "return None"

# Pattern 3: Bare Exception catches
grep -rn "except Exception:" . --include="*.py"

# Pattern 4: Try/except with only print (no raise/return)
grep -rn "except.*:" . --include="*.py" | grep -A 2 "print("
```

**For each match:**
- [ ] Does it log the exception details?
- [ ] Does it return an error message?
- [ ] Is the exception type specific enough?
- [ ] Could a user debug this if it fails?

### 1.2 Find Subprocess Calls

```bash
# Find all subprocess.run calls
grep -rn "subprocess\.run" . --include="*.py"

# Find all subprocess.Popen calls
grep -rn "subprocess\.Popen" . --include="*.py"
```

**For each subprocess call, check:**
- [ ] `capture_output=True` or `stdout/stderr` specified?
- [ ] `timeout` specified? (or risk infinite hang)
- [ ] `shell=True` if calling .CMD/.BAT/.sh on Windows?
- [ ] `encoding="utf-8"` if passing text with unicode?
- [ ] Error handling checks `returncode`?
- [ ] Errors include `stderr` in message?

### 1.3 Find Test Mocking Patterns

```bash
# Find @patch decorators
grep -rn "@patch" . --include="test_*.py"

# Find unittest.mock imports
grep -rn "from unittest.mock import" . --include="test_*.py"

# Find MagicMock usage
grep -rn "MagicMock" . --include="test_*.py"
```

**For each mocked function:**
- [ ] Is there an integration test that doesn't mock it?
- [ ] Does the mock accurately simulate real behavior?
- [ ] Could the real implementation be broken while tests pass?

### 1.4 Find TODO/FIXME Comments

```bash
# Find todos
grep -rn "# TODO" . --include="*.py"
grep -rn "# FIXME" . --include="*.py"
grep -rn "# HACK" . --include="*.py"
grep -rn "# XXX" . --include="*.py"
```

**For each comment:**
- [ ] Is this actually a bug?
- [ ] Should it be an issue instead?
- [ ] Has it been there for >6 months?

---

## Phase 2: Test Coverage Audit

### 2.1 Count Unit vs Integration Tests

```bash
# Count test files
find . -name "test_*.py" -o -name "*_test.py" | wc -l

# Count tests using @patch (mocked)
grep -r "@patch" tests/ --include="*.py" | wc -l

# Count tests NOT using @patch (potentially integration)
grep -L "@patch" tests/test_*.py | wc -l
```

**Red flags:**
- 100% of tests use @patch
- No `test_integration_*.py` files exist
- Tests never import `subprocess` or real external modules

### 2.2 Check What's Actually Tested

For each critical function (especially I/O):

```bash
# Example: Find tests for specific function
grep -rn "def test.*vscode" tests/ --include="*.py"
grep -rn "def test.*subprocess" tests/ --include="*.py"
grep -rn "def test.*claude" tests/ --include="*.py"
```

**Questions:**
- [ ] Does test call the real function or mock it?
- [ ] Does test verify actual behavior or just that it was called?
- [ ] Would test fail if implementation is broken?

### 2.3 Run Tests and Check Exit Codes

```bash
# Run all tests
pytest tests/ -v

# Run only integration tests (if tagged)
pytest tests/ -v -m integration

# Run tests without mocks
pytest tests/ -v -k "not mock"
```

**Check:**
- [ ] Do all tests pass?
- [ ] Are there skipped tests? Why?
- [ ] Are there xfail (expected failure) tests? Why?

---

## Phase 3: Manual Code Review

### 3.1 Review Subprocess Calls on Windows

**File:** `{file with subprocess.run}`

**Check:**

```python
# BAD - Will fail on Windows for .CMD files
subprocess.run(["code", "--wait", file])

# GOOD - Works on Windows
subprocess.run(["code", "--wait", file], shell=True)

# BETTER - Handle both
import platform
if platform.system() == "Windows":
    subprocess.run(["code", "--wait", file], shell=True)
else:
    subprocess.run(["code", "--wait", file])
```

**Audit questions:**
- [ ] Was this tested on Windows?
- [ ] Does it handle .CMD/.BAT files?
- [ ] Is there a Linux alternative?

### 3.2 Review Error Messages

**File:** `{file with error handling}`

**Check:**

```python
# BAD - User can't debug
except Exception:
    return False

# BETTER - User sees what failed
except Exception as e:
    return False, f"Failed: {e}"

# BEST - User sees full context
except FileNotFoundError as e:
    return False, f"File not found: {file_path}. Error: {e}"
except subprocess.CalledProcessError as e:
    return False, f"Command failed: {e.cmd}\nExit code: {e.returncode}\nStderr: {e.stderr}"
```

**Audit questions:**
- [ ] Does error message include what failed?
- [ ] Does it include how to fix it?
- [ ] Is exception type specific?

### 3.3 Review Return Values

**Check for inconsistent return types:**

```python
# BAD - Sometimes returns bool, sometimes tuple
def check_status():
    if ok:
        return True
    else:
        return False, "error"  # Type mismatch!

# GOOD - Always returns same type
def check_status() -> tuple[bool, str]:
    if ok:
        return True, ""
    else:
        return False, "error"
```

**Audit questions:**
- [ ] Are return types consistent?
- [ ] Is return type annotated?
- [ ] Do callers check the right type?

---

## Phase 4: Integration Test Writing

For every subprocess call, write an integration test:

### Template: Test Real Subprocess Call

```python
# tests/test_integration_{module}.py
import subprocess
import pytest

class TestRealSubprocessCalls:
    """Integration tests - no mocks, real commands."""

    def test_command_exists(self):
        """Verify command is in PATH."""
        import shutil
        cmd_path = shutil.which("command")
        assert cmd_path is not None, "'command' not found in PATH"

    def test_command_runs(self):
        """Test that command actually executes."""
        result = subprocess.run(
            ["command", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        assert result.returncode == 0, f"Command failed: {result.stderr}"
        assert len(result.stdout) > 0, "No output from command"

    def test_command_with_real_file(self):
        """Test command with actual file."""
        import tempfile
        from pathlib import Path

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            temp_path = f.name

        try:
            result = subprocess.run(
                ["command", temp_path],
                capture_output=True,
                text=True,
                timeout=5,
            )
            assert result.returncode == 0, f"Failed: {result.stderr}"
        finally:
            Path(temp_path).unlink(missing_ok=True)
```

**Run with:**
```bash
pytest tests/test_integration_*.py -v
```

---

## Phase 5: Reporting

### 5.1 Create Audit Report

**File:** `docs/reports/active/audit-{repo}-{date}.md`

**Template:**

```markdown
# Code Quality Audit - {Repo} - {Date}

## Summary

- **Total Python files:** X
- **Files with subprocess:** X
- **Files with exception handling:** X
- **Unit tests:** X
- **Integration tests:** X
- **Critical bugs found:** X

## Critical Issues

### 1. [Issue Title]

**File:** `path/to/file.py:123`
**Severity:** CRITICAL | HIGH | MEDIUM | LOW
**Impact:** [What breaks? Who is affected?]

**Root Cause:**
[code block showing bad code]

**Fix:**
[code block showing good code]

**Test That Should Have Caught This:**
[code block showing integration test]

## Silent Failures Found

| File | Line | Pattern | Severity | Fixed? |
|------|------|---------|----------|--------|
| file.py | 123 | except: pass | HIGH | [ ] |

## Missing Integration Tests

| Feature | Current Tests | Integration Tests Needed |
|---------|---------------|--------------------------|
| VS Code launch | Unit (mocked) | Real subprocess test |

## Recommendations

1. **Immediate:**
   - Fix critical bugs
   - Add integration tests for subprocess calls

2. **Short term:**
   - Review all exception handlers
   - Add error message improvements

3. **Long term:**
   - Establish integration test policy
   - Add CI integration test runs
```

### 5.2 Prioritize Fixes

**Severity levels:**

1. **CRITICAL** - Feature never worked, blocks users
   - Example: VS Code never launches
   - Fix: Immediately

2. **HIGH** - Silent failure, no error message
   - Example: Exception caught but not logged
   - Fix: Within 1 week

3. **MEDIUM** - Works but error messages unclear
   - Example: Returns False without explanation
   - Fix: Within 1 month

4. **LOW** - Works but could be better
   - Example: TODO comments, minor code smell
   - Fix: Backlog

---

## Phase 6: Prevention

### 6.1 Add Pre-commit Checks

**File:** `.pre-commit-config.yaml`

```yaml
repos:
  - repo: local
    hooks:
      - id: check-silent-failures
        name: Check for silent exception handlers
        entry: bash -c 'grep -rn "except.*:" . --include="*.py" | grep -A 1 "pass$" && exit 1 || exit 0'
        language: system
        pass_filenames: false
```

### 6.2 Add Test Coverage Requirements

**File:** `pyproject.toml`

```toml
[tool.pytest.ini_options]
# Fail if coverage drops below 80%
addopts = "--cov=. --cov-report=term-missing --cov-fail-under=80"

# Mark integration tests
markers = [
    "integration: marks tests as integration tests (no mocks)",
    "unit: marks tests as unit tests (may use mocks)"
]
```

### 6.3 Document Testing Policy

**File:** `docs/standards/testing-policy.md`

```markdown
# Testing Policy

## Required Tests

1. **Unit tests** - Mock external dependencies
2. **Integration tests** - No mocks, real commands
3. **Error path tests** - What happens when it fails?

## Rules

- Every subprocess call MUST have an integration test
- Exception handlers MUST log or return error messages
- Tests MUST fail when implementation is broken
- CI MUST run both unit and integration tests
```

---

## Quick Audit Checklist

Run this on any repo:

```bash
# 1. Count files with issues
echo "=== Silent Failures ==="
grep -r "except.*:" . --include="*.py" | grep -c "pass$"

echo "=== Subprocess Calls ==="
grep -r "subprocess\.run" . --include="*.py" | wc -l

echo "=== Mocked Tests ==="
grep -r "@patch" tests/ --include="*.py" | wc -l

echo "=== Integration Tests ==="
find tests/ -name "*integration*.py" | wc -l

# 2. Run tests
pytest tests/ -v --tb=short

# 3. Check for Windows compatibility
grep -rn "subprocess\.run" . --include="*.py" | grep -v "shell=True"
```

---

## Example: Full Repo Audit Script

Save this as `audit.sh`:

```bash
#!/bin/bash
set -e

REPO=$1
DATE=$(date +%Y-%m-%d)
OUTPUT="audit-${REPO}-${DATE}.txt"

echo "Auditing ${REPO}..." > $OUTPUT

echo "=== Phase 1: Grep Audit ===" >> $OUTPUT
echo "Silent failures:" >> $OUTPUT
grep -rn "except.*:" . --include="*.py" | grep "pass$" >> $OUTPUT || true

echo "Subprocess calls:" >> $OUTPUT
grep -rn "subprocess\.run" . --include="*.py" >> $OUTPUT || true

echo "=== Phase 2: Test Coverage ===" >> $OUTPUT
pytest tests/ -v --tb=short >> $OUTPUT 2>&1 || true

echo "=== Phase 3: Integration Tests ===" >> $OUTPUT
find tests/ -name "*integration*.py" >> $OUTPUT || true

echo "Audit complete. See: $OUTPUT"
```

**Usage:**
```bash
chmod +x audit.sh
./audit.sh myrepo
```

---

## Success Criteria

Audit is complete when:

- [ ] All subprocess calls have integration tests
- [ ] No silent exception handlers remain
- [ ] All tests pass (unit + integration)
- [ ] Error messages are actionable
- [ ] Windows compatibility verified
- [ ] Report documents all findings
- [ ] Critical bugs have issues filed
- [ ] Prevention measures in place
