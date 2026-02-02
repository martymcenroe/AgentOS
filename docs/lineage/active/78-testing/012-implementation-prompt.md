# Implementation Request

## Context

You are implementing code for Issue #78 using TDD.
This is iteration 1 of the implementation.

## Requirements

The tests have been scaffolded and need implementation code to pass.

### LLD Summary

# 0178 - Feature: Per-Repo Workflow Database

## 1. Context & Goal
* **Issue:** #78
* **Objective:** Change the default workflow checkpoint database location from global (`~/.agentos/issue_workflow.db`) to per-repo (`.agentos/issue_workflow.db` in repo root) to enable safe concurrent workflow execution across multiple repositories and worktrees.
* **Status:** Draft
* **Related Issues:** None

### Open Questions
*No open questions - requirements are clear from issue specification.*

## 2. Proposed Changes

*This section is the **source of truth** for implementation. Describes exactly what will be built.*

### 2.1 Files Changed

| File | Change Type | Description |
|------|-------------|-------------|
| `src/agentos/workflow/checkpoint.py` | Modify | Update `get_checkpoint_db_path()` with per-repo logic and fail-closed behavior |
| `.gitignore` | Modify | Add `.agentos/` pattern to ignore per-repo workflow directories |
| `docs/workflow.md` | Modify | Document new default behavior, fail-closed behavior, and migration path |

### 2.2 Dependencies

*No new packages, APIs, or services required.*

```toml
# pyproject.toml additions
# None - using existing standard library and git subprocess
```

### 2.3 Data Structures

```python
# Pseudocode - NOT implementation
# No new data structures required
# Database schema unchanged - only location changes
```

### 2.4 Function Signatures

```python
# Signatures only - implementation in source files
def get_checkpoint_db_path() -> Path:
    """
    Determine the checkpoint database path.
    
    Priority:
    1. AGENTOS_WORKFLOW_DB environment variable (if set and non-empty)
    2. Per-repo: {repo_root}/.agentos/issue_workflow.db
    3. Fail closed with descriptive error if outside git repo
    
    Returns:
        Path to the checkpoint database file.
    
    Raises:
        SystemExit: If not in a git repo and no env var set (fail closed).
    """
    ...

def get_repo_root() -> Path | None:
    """
    Get the root directory...

### Test Scenarios

- **test_010**: Per-repo database creation | Auto | Run workflow in git repo | `.agentos/issue_workflow.db` created in repo root | File exists at expected path
  - Requirement: 
  - Type: unit

- **test_020**: Different repos get different databases | Auto | Run workflow in repo1, then repo2 | Two separate database files | `repo1/.agentos/issue_workflow.db` != `repo2/.agentos/issue_workflow.db`
  - Requirement: 
  - Type: unit

- **test_030**: Environment variable override | Auto | Set `AGENTOS_WORKFLOW_DB=/tmp/custom.db` | Database at `/tmp/custom.db` | File created at env var path, not in repo
  - Requirement: 
  - Type: unit

- **test_040**: Fail closed outside repo | Auto | Run workflow in non-git directory | Exit code 1, error message | Exit code 1; stderr contains "AGENTOS_WORKFLOW_DB"
  - Requirement: 
  - Type: unit

- **test_050**: Worktree isolation | Auto | Create worktree, run workflow | Worktree gets own `.agentos/` | `worktree/.agentos/issue_workflow.db` exists
  - Requirement: 
  - Type: unit

- **test_060**: Global database untouched | Auto | Run workflow in repo | `~/.agentos/issue_workflow.db` unchanged | Global DB not modified (timestamp unchanged)
  - Requirement: 
  - Type: unit

- **test_070**: Nested repo detection (deep subdirectory) | Auto | Run in `repo/src/lib/` subdirectory | Database in repo root, not subdirectory | `repo_root/.agentos/` not `repo_root/src/lib/.agentos/`
  - Requirement: 
  - Type: unit

- **test_080**: .agentos directory creation | Auto | Run in repo without .agentos | Directory created with proper permissions | Directory exists with user read/write
  - Requirement: 
  - Type: unit

- **test_090**: Env var with ~ expansion | Auto | Set `AGENTOS_WORKFLOW_DB=~/custom.db` | Path expanded correctly | File at `$HOME/custom.db`
  - Requirement: 
  - Type: unit

- **test_100**: Empty env var treated as unset | Auto | Set `AGENTOS_WORKFLOW_DB=""` | Falls back to per-repo | Uses repo path, not empty string
  - Requirement: 
  - Type: unit

- **test_110**: .gitignore contains .agentos/ pattern | Auto | Check `.gitignore` after workflow run | `.agentos/` entry exists | Parse `.gitignore`, assert pattern present
  - Requirement: 
  - Type: unit

- **test_120**: Concurrent execution (3 repos) | Auto | Spawn 3 subprocess workflows in parallel | Each repo has independent database, no errors | All 3 processes exit 0; 3 distinct `.agentos/issue_workflow.db` files
  - Requirement: 
  - Type: unit

### Test File: C:\Users\mcwiz\Projects\AgentOS\tests\test_issue_78.py

```python
"""Test file for Issue #78.

Tests for per-repo workflow database functionality.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest import mock

import pytest


# Import the module under test
from agentos.workflow.checkpoint import get_checkpoint_db_path, get_repo_root


@pytest.fixture
def temp_git_repo(tmp_path: Path) -> Path:
    """Create a temporary git repository."""
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    subprocess.run(["git", "init"], cwd=repo_path, capture_output=True, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=repo_path,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_path,
        capture_output=True,
        check=True,
    )
    return repo_path


@pytest.fixture
def mock_external_service():
    """Mock external service for isolation."""
    yield None


@pytest.fixture
def clean_env():
    """Ensure AGENTOS_WORKFLOW_DB is not set during tests."""
    original = os.environ.pop("AGENTOS_WORKFLOW_DB", None)
    yield
    if original is not None:
        os.environ["AGENTOS_WORKFLOW_DB"] = original
    else:
        os.environ.pop("AGENTOS_WORKFLOW_DB", None)


# Unit Tests
# -----------

def test_010(temp_git_repo: Path, clean_env, monkeypatch):
    """
    Per-repo database creation | Auto | Run workflow in git repo |
    `.agentos/issue_workflow.db` created in repo root | File exists at
    expected path
    """
    # TDD: Arrange
    monkeypatch.chdir(temp_git_repo)
    
    # TDD: Act
    db_path = get_checkpoint_db_path()
    
    # TDD: Assert
    expected_path = temp_git_repo / ".agentos" / "issue_workflow.db"
    assert db_path == expected_path
    assert db_path.parent.exists()


def test_020(tmp_path: Path, clean_env, monkeypatch):
    """
    Different repos get different databases | Auto | Run workflow in
    repo1, then repo2 | Two separate database files |
    `repo1/.agentos/issue_workflow.db` !=
    `repo2/.agentos/issue_workflow.db`
    """
    # TDD: Arrange - Create two repos
    repo1 = tmp_path / "repo1"
    repo2 = tmp_path / "repo2"
    repo1.mkdir()
    repo2.mkdir()
    
    for repo in [repo1, repo2]:
        subprocess.run(["git", "init"], cwd=repo, capture_output=True, check=True)
    
    # TDD: Act - Get db path from each repo
    monkeypatch.chdir(repo1)
    db_path1 = get_checkpoint_db_path()
    
    monkeypatch.chdir(repo2)
    db_path2 = get_checkpoint_db_path()
    
    # TDD: Assert
    assert db_path1 != db_path2
    assert db_path1 == repo1 / ".agentos" / "issue_workflow.db"
    assert db_path2 == repo2 / ".agentos" / "issue_workflow.db"


def test_030(temp_git_repo: Path, tmp_path: Path, monkeypatch):
    """
    Environment variable override | Auto | Set
    `AGENTOS_WORKFLOW_DB=/tmp/custom.db` | Database at `/tmp/custom.db` |
    File created at env var path, not in repo
    """
    # TDD: Arrange
    custom_db = tmp_path / "custom_dir" / "custom.db"
    monkeypatch.setenv("AGENTOS_WORKFLOW_DB", str(custom_db))
    monkeypatch.chdir(temp_git_repo)
    
    # TDD: Act
    db_path = get_checkpoint_db_path()
    
    # TDD: Assert
    assert db_path == custom_db
    assert db_path.parent.exists()
    # Verify NOT using repo path
    repo_db = temp_git_repo / ".agentos" / "issue_workflow.db"
    assert db_path != repo_db


def test_040(tmp_path: Path, monkeypatch, clean_env):
    """
    Fail closed outside repo | Auto | Run workflow in non-git directory |
    Exit code 1, error message | Exit code 1; stderr contains
    "AGENTOS_WORKFLOW_DB"
    """
    # TDD: Arrange - Create a non-git directory
    non_git_dir = tmp_path / "not_a_repo"
    non_git_dir.mkdir()
    monkeypatch.chdir(non_git_dir)
    
    # TDD: Act & Assert
    with pytest.raises(SystemExit) as exc_info:
        get_checkpoint_db_path()
    
    assert exc_info.value.code == 1


def test_050(temp_git_repo: Path, clean_env, monkeypatch):
    """
    Worktree isolation | Auto | Create worktree, run workflow | Worktree
    gets own `.agentos/` | `worktree/.agentos/issue_workflow.db` exists
    """
    # TDD: Arrange - Create initial commit and worktree
    monkeypatch.chdir(temp_git_repo)
    
    # Create an initial commit (required for worktrees)
    dummy_file = temp_git_repo / "dummy.txt"
    dummy_file.write_text("initial")
    subprocess.run(["git", "add", "."], cwd=temp_git_repo, capture_output=True, check=True)
    subprocess.run(
        ["git", "commit", "-m", "initial"],
        cwd=temp_git_repo,
        capture_output=True,
        check=True,
    )
    
    # Create worktree
    worktree_path = temp_git_repo.parent / "worktree"
    subprocess.run(
        ["git", "worktree", "add", str(worktree_path), "-b", "test-branch"],
        cwd=temp_git_repo,
        capture_output=True,
        check=True,
    )
    
    # TDD: Act
    monkeypatch.chdir(worktree_path)
    db_path = get_checkpoint_db_path()
    
    # TDD: Assert - Worktree should have its own .agentos directory
    expected_path = worktree_path / ".agentos" / "issue_workflow.db"
    assert db_path == expected_path
    assert db_path.parent.exists()


def test_060(temp_git_repo: Path, tmp_path: Path, clean_env, monkeypatch):
    """
    Global database untouched | Auto | Run workflow in repo |
    `~/.agentos/issue_workflow.db` unchanged | Global DB not modified
    (timestamp unchanged)
    """
    # TDD: Arrange
    # Create a mock global .agentos directory
    fake_home = tmp_path / "fake_home"
    fake_home.mkdir()
    global_agentos = fake_home / ".agentos"
    global_agentos.mkdir()
    global_db = global_agentos / "issue_workflow.db"
    global_db.write_text("original content")
    
    original_mtime = global_db.stat().st_mtime
    time.sleep(0.1)  # Ensure time passes
    
    monkeypatch.chdir(temp_git_repo)
    monkeypatch.setenv("HOME", str(fake_home))
    monkeypatch.setenv("USERPROFILE", str(fake_home))  # Windows
    
    # TDD: Act
    db_path = get_checkpoint_db_path()
    
    # TDD: Assert
    assert db_path != global_db
    assert global_db.read_text() == "original content"
    assert global_db.stat().st_mtime == original_mtime


def test_070(temp_git_repo: Path, clean_env, monkeypatch):
    """
    Nested repo detection (deep subdirectory) | Auto | Run in
    `repo/src/lib/` subdirectory | Database in repo root, not subdirectory
    | `repo_root/.agentos/` not `repo_root/src/lib/.agentos/`
    """
    # TDD: Arrange
    deep_dir = temp_git_repo / "src" / "lib" / "utils"
    deep_dir.mkdir(parents=True)
    monkeypatch.chdir(deep_dir)
    
    # TDD: Act
    db_path = get_checkpoint_db_path()
    
    # TDD: Assert
    expected = temp_git_repo / ".agentos" / "issue_workflow.db"
    assert db_path == expected
    # Ensure it's NOT in the deep directory
    wrong_path = deep_dir / ".agentos" / "issue_workflow.db"
    assert db_path != wrong_path


def test_080(temp_git_repo: Path, clean_env, monkeypatch):
    """
    .agentos directory creation | Auto | Run in repo without .agentos |
    Directory created with proper permissions | Directory exists with user
    read/write
    """
    # TDD: Arrange
    monkeypatch.chdir(temp_git_repo)
    agentos_dir = temp_git_repo / ".agentos"
    assert not agentos_dir.exists()
    
    # TDD: Act
    db_path = get_checkpoint_db_path()
    
    # TDD: Assert
    assert agentos_dir.exists()
    assert agentos_dir.is_dir()
    # Check user has read/write permissions
    assert os.access(agentos_dir, os.R_OK)
    assert os.access(agentos_dir, os.W_OK)


def test_090(tmp_path: Path, monkeypatch):
    """
    Env var with ~ expansion | Auto | Set
    `AGENTOS_WORKFLOW_DB=~/custom.db` | Path expanded correctly | File at
    `$HOME/custom.db`
    """
    # TDD: Arrange
    fake_home = tmp_path / "fake_home"
    fake_home.mkdir()
    monkeypatch.setenv("HOME", str(fake_home))
    monkeypatch.setenv("USERPROFILE", str(fake_home))  # Windows
    monkeypatch.setenv("AGENTOS_WORKFLOW_DB", "~/custom.db")
    
    # TDD: Act
    db_path = get_checkpoint_db_path()
    
    # TDD: Assert
    expected = fake_home / "custom.db"
    assert db_path == expected


def test_100(temp_git_repo: Path, monkeypatch):
    """
    Empty env var treated as unset | Auto | Set `AGENTOS_WORKFLOW_DB=""`
    | Falls back to per-repo | Uses repo path, not empty string
    """
    # TDD: Arrange
    monkeypatch.setenv("AGENTOS_WORKFLOW_DB", "")
    monkeypatch.chdir(temp_git_repo)
    
    # TDD: Act
    db_path = get_checkpoint_db_path()
    
    # TDD: Assert
    expected = temp_git_repo / ".agentos" / "issue_workflow.db"
    assert db_path == expected
    # Ensure it didn't try to create a db at empty path
    assert str(db_path) != ""


def test_110(temp_git_repo: Path):
    """
    .gitignore contains .agentos/ pattern | Auto | Check `.gitignore`
    after workflow run | `.agentos/` entry exists | Parse `.gitignore`,
    assert pattern present
    
    Note: This test verifies that .gitignore in the AgentOS project
    contains the .agentos/ pattern. The test doesn't run a workflow;
    it checks the static configuration.
    """
    # TDD: Arrange
    # The .gitignore should be in the AgentOS repo root
    repo_root = Path(__file__).parent.parent
    gitignore_path = repo_root / ".gitignore"
    
    # TDD: Act
    if gitignore_path.exists():
        content = gitignore_path.read_text()
        lines = [line.strip() for line in content.splitlines()]
    else:
        lines = []
    
    # TDD: Assert
    assert ".agentos/" in lines or ".agentos" in lines, (
        f".gitignore should contain .agentos/ pattern. Found: {lines}"
    )


def test_120(tmp_path: Path, clean_env):
    """
    Concurrent execution (3 repos) | Auto | Spawn 3 subprocess workflows
    in parallel | Each repo has independent database, no errors | All 3
    processes exit 0; 3 distinct `.agentos/issue_workflow.db` files
    """
    # TDD: Arrange - Create 3 repos
    repos = []
    for i in range(3):
        repo = tmp_path / f"repo{i}"
        repo.mkdir()
        subprocess.run(["git", "init"], cwd=repo, capture_output=True, check=True)
        repos.append(repo)
    
    # Create a simple script to call get_checkpoint_db_path
    script = tmp_path / "test_script.py"
    script.write_text("""
import sys
sys.path.insert(0, r"{src_path}")
from agentos.workflow.checkpoint import get_checkpoint_db_path
path = get_checkpoint_db_path()
# Touch the file to prove it was created
path.touch()
print(path)
""".format(src_path=str(Path(__file__).parent.parent / "src")))
    
    def run_in_repo(repo: Path) -> tuple[int, str]:
        result = subprocess.run(
            [sys.executable, str(script)],
            cwd=repo,
            capture_output=True,
            text=True,
        )
        return result.returncode, result.stdout.strip()
    
    # TDD: Act - Run concurrently
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(run_in_repo, repo) for repo in repos]
        results = [f.result() for f in futures]
    
    # TDD: Assert
    return_codes = [r[0] for r in results]
    paths = [r[1] for r in results]
    
    # All should succeed
    assert all(rc == 0 for rc in return_codes), f"Some processes failed: {results}"
    
    # All paths should be distinct
    assert len(set(paths)) == 3, f"Expected 3 distinct paths, got: {paths}"
    
    # All database files should exist
    for repo in repos:
        db_file = repo / ".agentos" / "issue_workflow.db"
        assert db_file.exists(), f"Database file not found at {db_file}"
```

### Previous Test Run (FAILED)

The previous implementation attempt failed. Here's the test output:

```
============================= test session starts =============================
platform win32 -- Python 3.14.0, pytest-9.0.2, pluggy-1.6.0 -- C:\Users\mcwiz\AppData\Local\pypoetry\Cache\virtualenvs\agentos-tools-avX7uQzj-py3.14\Scripts\python.exe
cachedir: .pytest_cache
benchmark: 5.2.3 (defaults: timer=time.perf_counter disable_gc=False min_rounds=5 min_time=0.000005 max_time=1.0 calibration_precision=10 warmup=False warmup_iterations=100000)
rootdir: C:\Users\mcwiz\Projects\AgentOS
configfile: pyproject.toml
plugins: anyio-4.12.1, langsmith-0.6.4, asyncio-1.3.0, benchmark-5.2.3, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 0 items / 1 error

=================================== ERRORS ====================================
___________________ ERROR collecting tests/test_issue_78.py ___________________
ImportError while importing test module 'C:\Users\mcwiz\Projects\AgentOS\tests\test_issue_78.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
..\..\AppData\Local\Programs\Python\Python314\Lib\importlib\__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests\test_issue_78.py:21: in <module>
    from agentos.workflow.checkpoint import get_checkpoint_db_path, get_repo_root
E   ModuleNotFoundError: No module named 'agentos.workflow'
=========================== short test summary info ===========================
ERROR tests/test_issue_78.py
!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
============================== 1 error in 0.17s ===============================


```

Please fix the issues and provide updated implementation.

## Instructions

1. Generate implementation code that makes all tests pass
2. Follow the patterns established in the codebase
3. Ensure proper error handling
4. Add type hints where appropriate
5. Keep the implementation minimal - only what's needed to pass tests

## Output Format

Provide the implementation in a code block with the file path:

```python
# File: path/to/implementation.py

def function_name():
    ...
```

If multiple files are needed, provide each in a separate code block.
