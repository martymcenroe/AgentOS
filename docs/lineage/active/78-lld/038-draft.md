# 178 - Feature: Per-Repo Workflow Database

## 1. Context & Goal
* **Issue:** #78
* **Objective:** Change the default workflow checkpoint database location from global (`~/.agentos/issue_workflow.db`) to per-repo (`{repo_root}/.agentos/issue_workflow.db`) to enable safe concurrent workflow execution.
* **Status:** Draft
* **Related Issues:** None.

### Open Questions
None - requirements are well-defined from issue.

## 2. Proposed Changes

### 2.1 Files Changed
| File | Action | Description |
| :--- | :--- | :--- |
| `src/agentos/workflow/checkpoint.py` | Modify | Rewrite `get_checkpoint_db_path` to implement priority logic (Env Var > Repo Root > Error). Add caching to minimize git subprocess calls. |
| `.gitignore` | Modify | Add `.agentos/` to root ignore patterns to prevent committing local workflow state. |
| `docs/workflow.md` | Modify | Update "Configuration" section to explain new per-repo default and environment variable override. |

### 2.2 Dependencies
* **Runtime:** `git` CLI tool must be available in the system PATH.
* **Python:** `functools.lru_cache` (for performance optimization), `subprocess`, `pathlib`.

### 2.3 Data Structures
No changes to SQLite schema or Python data types.

### 2.4 Function Signatures

**File:** `src/agentos/workflow/checkpoint.py`

```python
import os
import subprocess
import logging
from functools import lru_cache
from pathlib import Path

logger = logging.getLogger(__name__)

@lru_cache(maxsize=1)
def _get_git_repo_root() -> Path:
    """
    Identifies the root of the current git repository or worktree.
    Cached to prevent repeated subprocess calls during execution.

    Returns:
        Path: Absolute path to the repository root.

    Raises:
        RuntimeError: If the current directory is not part of a git repository
                      or if the git command fails.
    """
    pass

def get_checkpoint_db_path() -> Path:
    """
    Resolves the final path for the SQLite checkpoint database.

    Resolution Priority:
    1. Environment Variable: AGENTOS_WORKFLOW_DB
    2. Repository Local: {repo_root}/.agentos/issue_workflow.db
    
    Observability:
        Logs the resolved path at INFO level.

    Returns:
        Path: Absolute path to the database file.

    Raises:
        RuntimeError: If AGENTOS_WORKFLOW_DB is unset AND the current 
                      execution is outside of a git repository.
    """
    pass
```

### 2.5 Logic Flow (Pseudocode)

**_get_git_repo_root**
```python
FUNCTION _get_git_repo_root():
    TRY:
        # Use --show-toplevel to get the root of repo OR worktree
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        return Path(result.stdout.strip())
    CATCH subprocess.CalledProcessError:
        RAISE RuntimeError("Current directory is not a git repository.")
    CATCH FileNotFoundError:
        RAISE RuntimeError("Git command not found. Please install git.")
```

**get_checkpoint_db_path**
```python
FUNCTION get_checkpoint_db_path():
    # 1. Check Priority Override (Environment Variable)
    env_path = os.getenv("AGENTOS_WORKFLOW_DB")
    IF env_path IS NOT NONE:
        db_path = Path(env_path).resolve()
        logger.info(f"Using workflow database from AGENTOS_WORKFLOW_DB: {db_path}")
        RETURN db_path

    # 2. Check Repository Context
    TRY:
        repo_root = CALL _get_git_repo_root()
        
        # Define standard location
        agentos_dir = repo_root / ".agentos"
        db_path = agentos_dir / "issue_workflow.db"
        
        # 3. Directory Creation
        IF NOT agentos_dir.exists():
            agentos_dir.mkdir(parents=True, exist_ok=True)
            
        logger.info(f"Using per-repo workflow database: {db_path}")
        RETURN db_path
        
    CATCH RuntimeError as e:
        # 4. Fail Closed
        error_msg = (
            "Cannot determine workflow database location.\n"
            "Reason: Not running inside a git repository.\n"
            "Action: Set AGENTOS_WORKFLOW_DB environment variable or run within a git repo."
        )
        logger.error(error_msg)
        RAISE RuntimeError(error_msg) from e
```

### 2.6 Technical Approach
*   **Git Root Detection:** We use `git rev-parse --show-toplevel`. This is robust for detecting both standard clones and `git worktree` directories. Pure Python directory traversal is error-prone for worktrees (which use a `.git` file rather than a directory).
*   **Performance Optimization:** Since checking the git root involves a subprocess call (approx 5-10ms), we wrap `_get_git_repo_root` with `@lru_cache(maxsize=1)`. The repo root cannot change during the lifecycle of a single process execution.
*   **Fail-Closed Security:** The system will explicitly crash with a helpful message if the location is ambiguous (not in a repo, no env var). This prevents silent data loss or corruption of global state.

## 3. Requirements
1.  **Priority:** `AGENTOS_WORKFLOW_DB` environment variable MUST supersede any repository detection logic.
2.  **Repo Detection:** The system MUST identify the root of the current git repository or worktree using `git` commands.
3.  **Default Path:** If in a repo, the database MUST be created at `{repo_root}/.agentos/issue_workflow.db`.
4.  **Directory Creation:** The `.agentos/` directory MUST be created automatically if it does not exist.
5.  **Fail Safe:** If the repo root cannot be detected and the env var is unset, the application MUST raise a `RuntimeError` and exit.
6.  **Git Ignore:** The `.gitignore` file MUST include `.agentos/`.
7.  **Performance:** The git detection result MUST be cached in memory to prevent multiple subprocess calls.

## 4. Alternatives Considered

| Option | Pros | Cons | Decision |
| :--- | :--- | :--- | :--- |
| **Keep Global (~/.agentos)** | Simplest implementation. | Concurrency impossible; worktree conflicts. | **Rejected** |
| **Pure Python Traversal** | Faster than `subprocess`. | Complex to handle git worktrees correctly (`.git` file vs dir). | **Rejected** |
| **Local ./.agentos (CWD)** | No git dependency. | Fragile; executing from `src/` puts DB in `src/`. | **Rejected** |
| **Repo + Env Var + Cache** | Robust isolation; fast; explicit overrides. | Requires git installed. | **Selected** |

## 5. Data & Fixtures

### 5.1 Data Sources
*   **Environment Variables:** `AGENTOS_WORKFLOW_DB`
*   **Git Command:** `git rev-parse --show-toplevel`

### 5.2 Data Pipeline
```ascii
Start -> Check Env Var -> (If Set) -> Return Env Path
            |
         (If Unset)
            v
       Check Git Root (Cached)
            |
      (Success) -> Create .agentos dir -> Return {Root}/.agentos/db
            |
       (Failure) -> Raise RuntimeError
```

### 5.3 Test Fixtures
| Fixture Name | Type | Description |
| :--- | :--- | :--- |
| `temp_git_repo` | `pytest.fixture` | Creates a temp dir, runs `git init`, sets user config (to ensure stability in CI), yields path. |
| `temp_git_worktree` | `pytest.fixture` | Creates main repo, commits once, adds worktree, yields worktree path. |
| `non_repo_dir` | `pytest.fixture` | Creates a temp dir with no git initialization. |

### 5.4 Deployment Pipeline
*   **Development Only:** Changes affect the CLI tool used by developers.

## 6. Diagram

### 6.1 Mermaid Quality Gate
- [x] All nodes defined
- [x] Logic flow direction is clear
- [x] Subprocess caching indicated
- [x] Error paths explicit

### 6.2 Diagram
```mermaid
flowchart TD
    A[get_checkpoint_db_path called] --> B{Env Var Set?}
    B -- Yes --> C[Return Env Path]
    B -- No --> D{Cache Hit?}
    D -- Yes --> E[Return Cached Root]
    D -- No --> F[Run: git rev-parse --show-toplevel]
    F --> G{Command Success?}
    G -- No --> H[Raise RuntimeError]
    G -- Yes --> I[Store in Cache]
    I --> J[Construct Path: {Root}/.agentos/db]
    J --> K[Ensure Directory Exists]
    K --> L[Return Path]
```

## 7. Security Considerations

| Concern | Mitigation |
| :--- | :--- |
| **Accidental Commit of DB** | `.gitignore` updated; Developers should use global gitignore patterns as backup. |
| **Permissions** | `.agentos` directory inherits standard user permissions. No sensitive data in checkpoint DB (only workflow state). |

## 8. Performance Considerations

| Metric | Budget | Estimate |
| :--- | :--- | :--- |
| **Startup Overhead** | < 50ms | ~10ms (one git call). |
| **Repeated Calls** | < 0.1ms | ~0.001ms (due to `@lru_cache`). |

## 9. Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
| :--- | :--- | :--- | :--- |
| **CI Git Config Missing** | Tests fail in CI because `git commit` requires user config. | Medium | Test fixtures explicitly set `git config user.email/name` locally. |
| **Git Not Installed** | Runtime crash. | Low | Catch `FileNotFoundError` in subprocess call and provide clear error message. |

## 10. Verification & Testing

### 10.1 Test Scenarios

| ID | Scenario | Type | Input | Output | Criteria |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TS1** | Happy Path: Repo Root | Unit | CWD=RepoRoot | Path=`{RepoRoot}/.agentos/issue_workflow.db` | Directory created. |
| **TS2** | Subdirectory Traversal | Unit | CWD=`{RepoRoot}/src/lib` | Path=`{RepoRoot}/.agentos/issue_workflow.db` | Correctly finds root from subdir. |
| **TS3** | Git Worktree | Integration | CWD=WorktreeRoot | Path=`{WorktreeRoot}/.agentos/issue_workflow.db` | Distinguishes worktree from main repo. |
| **TS4** | Env Var Override | Unit | Env=`/tmp/foo.db`, CWD=Repo | Path=`/tmp/foo.db` | Env var ignores git context. |
| **TS5** | Fail Closed (No Repo) | Unit | CWD=PlainDir | Raises `RuntimeError` | Descriptive error message. |
| **TS6** | Cache Performance | Unit | Call function 10 times | `subprocess.run` called 1 time | Cache functions correctly. |

### 10.2 Test Commands
```bash
# Run unit tests
poetry run pytest tests/workflow/test_checkpoint_path.py

# Verify worktree isolation manually
mkdir -p /tmp/test_project
cd /tmp/test_project
git init
git config user.email "test@example.com"
git config user.name "Test"
git commit --allow-empty -m "Initial commit"
git worktree add ../test_worktree
cd ../test_worktree
poetry run python -c "from agentos.workflow.checkpoint import get_checkpoint_db_path; print(get_checkpoint_db_path())"
# Expected output: .../test_worktree/.agentos/issue_workflow.db
```

### 10.3 Manual Tests
N/A - All scenarios automated.

## 11. Definition of Done

### Code
- [ ] `src/agentos/workflow/checkpoint.py` updated with cached git detection.
- [ ] `.gitignore` updated.
- [ ] Type hints verified with `mypy`.

### Tests
- [ ] Unit tests for priority logic (Env vs Repo).
- [ ] Integration test for Git Worktree support.
- [ ] Integration test for Subdirectory execution.
- [ ] CI tests pass with proper git configuration.

### Documentation
- [ ] `docs/workflow.md` updated with "Storage Location" section.
- [ ] CHANGELOG updated (if applicable).

### Review
- [ ] Verified performance impact is negligible.
- [ ] Verified fail-closed behavior on non-git folders.

---

## Appendix: Review Log

### Review Summary

| Review | Date | Verdict | Key Issue |
|--------|------|---------|-----------|
| - | - | - | - |

**Final Status:** DRAFT - PENDING REVIEW