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
| `src/agentos/workflow/checkpoint.py` | Modify | Rewrite `get_checkpoint_db_path` to implement priority logic (Env Var > Repo Root > Error). Add logging for observability. |
| `.gitignore` | Modify | Add `.agentos/` to root ignore patterns to prevent committing local workflow state. |
| `docs/workflow.md` | Modify | Update "Configuration" section to explain new per-repo default and environment variable override. |

### 2.2 Dependencies
* **Runtime:** `git` CLI tool must be available in the system PATH (used via `subprocess`).
* **Python:** Standard library (`subprocess`, `pathlib`, `os`).

### 2.3 Data Structures
No changes to SQLite schema or Python data types.

### 2.4 Function Signatures

**File:** `src/agentos/workflow/checkpoint.py`

```python
import os
import subprocess
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def _get_git_repo_root() -> Path:
    """
    Identifies the root of the current git repository or worktree.
    
    Uses `git rev-parse --show-toplevel` to ensure correct handling of 
    git worktrees (returns the worktree root, not the shared .git dir).

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

**get_checkpoint_db_path**
```python
FUNCTION get_checkpoint_db_path():
    # 1. Check Priority Override
    env_path_str = os.getenv("AGENTOS_WORKFLOW_DB")
    
    IF env_path_str IS NOT NONE:
        db_path = Path(env_path_str).resolve()
        logger.info(f"Using workflow database from AGENTOS_WORKFLOW_DB: {db_path}")
        RETURN db_path

    # 2. Check Repository Context
    TRY:
        repo_root = CALL _get_git_repo_root()
        
        # Define standard location
        agentos_dir = repo_root / ".agentos"
        db_path = agentos_dir / "issue_workflow.db"
        
        # Ensure directory exists (Optimization: fail fast if we can't write)
        IF NOT agentos_dir.exists():
            agentos_dir.mkdir(parents=True, exist_ok=True)
            
        logger.info(f"Using per-repo workflow database: {db_path}")
        RETURN db_path
        
    CATCH RuntimeError (Git detection failed):
        # 3. Fail Closed
        error_msg = (
            "Cannot determine workflow database location.\n"
            "Reason: Not running inside a git repository.\n"
            "Action: Set AGENTOS_WORKFLOW_DB environment variable or run within a git repo."
        )
        logger.error(error_msg)
        RAISE RuntimeError(error_msg)
```

**_get_git_repo_root**
```python
FUNCTION _get_git_repo_root():
    TRY:
        # Run git command to find root
        # capture_output=True, text=True, check=True
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"], 
            ...
        )
        output = result.stdout.strip()
        RETURN Path(output)
    CATCH subprocess.CalledProcessError:
        RAISE RuntimeError("Current directory is not a git repository.")
```

### 2.6 Technical Approach
*   **Path Resolution:** We utilize `git rev-parse --show-toplevel`. This is the gold standard for detecting repo roots because it correctly distinguishes between a main clone and a `git worktree`. A worktree has a separate working directory but shares the `.git` folder structure; we want the database in the *working directory* of the worktree to ensure isolation.
*   **Fail-Closed Design:** The previous behavior defaulted to `~/.agentos`. This is risky for concurrency. The new design explicitly raises an error if the context is ambiguous. This prevents "ghost" sessions where a user thinks they are working locally but are actually modifying a global state.
*   **Observability:** Adding logging is crucial here because the DB location changes based on context. Users need to verify which DB is active during debugging.

## 3. Requirements
1.  **Environment Variable Priority:** If `AGENTOS_WORKFLOW_DB` is set, it MUST be used, ignoring git status.
2.  **Repo Root Detection:** If inside a git repo (or worktree), the database MUST be located at `{repo_root}/.agentos/issue_workflow.db`.
3.  **Directory Auto-creation:** The system MUST automatically create the `.agentos/` directory if it doesn't exist.
4.  **Fail Safe:** If not in a git repo and no env var is set, the system MUST raise a `RuntimeError` with a descriptive message.
5.  **Git Ignore:** The `.gitignore` file MUST explicitly ignore `.agentos/`.
6.  **Worktree Isolation:** Workflow runs in different worktrees of the same repo MUST use separate database files.

## 4. Alternatives Considered

| Option | Pros | Cons | Decision |
| :--- | :--- | :--- | :--- |
| **Keep Global (~/.agentos)** | Simplest implementation; centralized history. | Impossible to run concurrent workflows; high risk of context bleeding. | **Rejected** |
| **CWD-based (.agentos/ here)** | Easy to implement (no git dependency). | Fragile; running script from subdir (`src/`) creates DB in wrong place. | **Rejected** |
| **Repo-based with Global Fallback** | Maximum backward compatibility. | Risky; silent fallback might confuse users about where state is saved. | **Rejected** |
| **Repo-based with Fail Closed** | Strict isolation; clear error boundaries; explicit configuration. | Requires users to set env var for non-repo use cases. | **Selected** |

## 5. Data & Fixtures

### 5.1 Data Sources
*   **Environment Variables:** `AGENTOS_WORKFLOW_DB`.
*   **Git State:** Output of `git rev-parse --show-toplevel`.

### 5.2 Data Pipeline
```ascii
Start
  |
  +-- Is AGENTOS_WORKFLOW_DB set?
  |     |
  |     +-- YES -> [Return Env Path]
  |
  +-- NO -> Is CWD inside Git Repo?
        |
        +-- YES -> [Detect Repo Root] -> [Mkdir .agentos] -> [Return {Root}/.agentos/db]
        |
        +-- NO  -> [Raise Error]
```

### 5.3 Test Fixtures
| Fixture Name | Type | Description |
| :--- | :--- | :--- |
| `git_repo_fixture` | `pytest.fixture` | Creates a temp directory, initializes git, yields path. |
| `git_worktree_fixture` | `pytest.fixture` | Creates a main repo and a worktree, yields worktree path. |
| `non_repo_fixture` | `pytest.fixture` | Creates a plain temp directory with no git info. |

### 5.4 Deployment Pipeline
*   **Development only:** This change affects the developer CLI tool behavior. No production deployment changes.

## 6. Diagram

### 6.1 Mermaid Quality Gate
- [x] All nodes defined
- [x] Logic flow direction is clear (Top-Down)
- [x] Decision diamonds labeled
- [x] Error states explicitly shown

### 6.2 Diagram
```mermaid
flowchart TD
    A[Start: get_checkpoint_db_path] --> B{Env Var Defined?}
    B -- Yes --> C[Log: Using Env Var]
    C --> D[Return Path from Env]
    
    B -- No --> E{Git Repo Detected?}
    E -- Yes --> F[Get Repo Root via git rev-parse]
    F --> G[Log: Using Per-Repo Path]
    G --> H[Create .agentos/ dir]
    H --> I[Return {root}/.agentos/issue_workflow.db]
    
    E -- No --> J[Log: Error]
    J --> K[Raise RuntimeError]
```

## 7. Security Considerations

| Concern | Mitigation |
| :--- | :--- |
| **Accidental Commit of DB** | `git check-ignore` verification during tests; `.gitignore` updated. |
| **Directory Permissions** | The `.agentos` directory inherits user permissions (0755 or 0700 typically). No special `chmod` required. |
| **State Leakage** | By isolating DBs per repo, we reduce the security risk of pasting "Client A" data into "Client B" workflow accidentally. |

## 8. Performance Considerations

| Metric | Budget | Estimate |
| :--- | :--- | :--- |
| **Repo Detection Time** | < 100ms | ~5-10ms (shelling out to `git`). |
| **Impact on Workflow** | None | Isolation prevents file lock contention on SQLite. |

## 9. Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
| :--- | :--- | :--- | :--- |
| **User loses access to old notes** | User cannot find previous workflow state. | High (immediate post-update) | Update documentation to explain how to point `AGENTOS_WORKFLOW_DB` to old global path if needed. |
| **Git not installed** | Crash on startup. | Low (Developer Tool) | Error message will indicate git requirement. |

## 10. Verification & Testing

### 10.1 Test Scenarios

| ID | Scenario | Type | Input | Output | Criteria |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TS1** | Happy Path: In Repo | Integration | CWD=`/tmp/repo` (git init) | Returns `/tmp/repo/.agentos/issue_workflow.db` | Directory `.agentos` is created; Path is correct. |
| **TS2** | Override: Env Var | Integration | Env=`/tmp/custom.db`, CWD=`/tmp/repo` | Returns `/tmp/custom.db` | Env var takes precedence over repo location. |
| **TS3** | Failure: No Repo | Unit | CWD=`/tmp/plain` (no git), Env=None | Raises `RuntimeError` | Exception message contains actionable advice. |
| **TS4** | Isolation: Worktree | Integration | Main=`/tmp/main`, Worktree=`/tmp/feat` | Returns `/tmp/feat/.agentos/issue_workflow.db` | Path points to Worktree root, NOT Main root. |
| **TS5** | Subdirectory Exec | Integration | CWD=`/tmp/repo/src` | Returns `/tmp/repo/.agentos/issue_workflow.db` | Correctly traverses up to find root. |

### 10.2 Test Commands

```bash
# Run the specific test file covering these changes
poetry run pytest tests/workflow/test_checkpoint_path.py -v

# Manual verification of worktree isolation
mkdir -p /tmp/wt_test/main
cd /tmp/wt_test/main
git init
git commit --allow-empty -m "init"
git worktree add ../feature
cd ../feature
# This command should output the path ending in /feature/.agentos/...
poetry run python -c "from agentos.workflow.checkpoint import get_checkpoint_db_path; print(get_checkpoint_db_path())"
```

### 10.3 Manual Tests (Only If Unavoidable)
N/A - All scenarios automated.

## 11. Definition of Done

### Code
- [ ] `get_checkpoint_db_path` logic implemented in `src/agentos/workflow/checkpoint.py`.
- [ ] `_get_git_repo_root` helper implemented using `subprocess`.
- [ ] Logging added for resolved paths.
- [ ] `.gitignore` updated with `.agentos/`.

### Tests
- [ ] New test file `tests/workflow/test_checkpoint_path.py` created.
- [ ] Tests TS1 through TS5 passed.
- [ ] Existing tests for workflow execution pass without regression.

### Documentation
- [ ] `docs/workflow.md` updated to reflect new storage behavior.
- [ ] Migration note added for users wishing to keep global state.

### Review
- [ ] Code review completed focusing on `subprocess` usage safety.
- [ ] Verified on Linux/macOS environments (path handling).

---

## Appendix: Review Log

### Review Summary

| Review | Date | Verdict | Key Issue |
|--------|------|---------|-----------|
| - | - | - | - |

**Final Status:** DRAFT - PENDING REVIEW