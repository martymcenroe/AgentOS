# File: tests/test_issue_78.py

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