# 178 - Feature: Per-Repo Workflow Database

## 1. Context & Goal
* **Issue:** #78
* **Objective:** Change the default workflow checkpoint database location from global (`~/.agentos/`) to per-repo (`.agentos/` in repo root) to enable safe concurrent workflow execution.
* **Status:** Draft
* **Related Issues:** None

### Open Questions
None - requirements are well-defined from issue.

## 2. Proposed Changes

### 2.1 Files Changed
| File Path | Description |
|-----------|-------------|
| `src/agentos/workflow/checkpoint.py` | Modify path resolution logic to prioritize env var, then git repo root, then fail. |
| `.gitignore` | Add `.agentos/` to ignore list to prevent committing local state. |
| `docs/workflow.md` | Update documentation regarding storage location and `AGENTOS_WORKFLOW_DB` variable. |

### 2.2 Dependencies
*   **subproccess** (Standard Lib): Required to execute `git rev-parse --show-toplevel`.
*   **pathlib** (Standard Lib): For robust path handling.
*   **os** (Standard Lib): For environment variable access.

### 2.3 Data Structures
No new data structures required. Existing SQLite schema remains unchanged.

### 2.4 Function Signatures

```python
# src/agentos/workflow/checkpoint.py

def get_repo_root() -> Path:
    """
    Determines the root directory of the current git repository.
    
    Returns:
        Path: The absolute path to the repository root.
        
    Raises:
        FileNotFoundError: If the current directory is not within a git repository.
    """
    pass

def get_checkpoint_db_path() -> str:
    """
    Resolves the absolute path for the workflow checkpoint database.
    
    Logic:
    1. Check AGENTOS_WORKFLOW_DB environment variable.
    2. If not set, attempt to find git repo root.
    3. If repo found, return {repo_root}/.agentos/issue_workflow.db.
    4. If no repo and no env var, raise generic OSError/RuntimeError.
    
    Returns:
        str: Absolute path to the sqlite database file.
    """
    pass
```

### 2.5 Logic Flow (Pseudocode)

**`get_repo_root`**
```python
TRY:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], 
        capture_output=True, 
        check=True, 
        text=True
    )
    RETURN Path(result.stdout.strip())
EXCEPT CalledProcessError:
    RAISE FileNotFoundError("Not a git repository")
```

**`get_checkpoint_db_path`**
```python
# 1. Check Environment Variable
env_path = os.environ.get("AGENTOS_WORKFLOW_DB")
IF env_path:
    db_path = Path(env_path)
    ENSURE_DIR(db_path.parent)
    RETURN str(db_path)

# 2. Check Repository
TRY:
    repo_root = get_repo_root()
    agentos_dir = repo_root / ".agentos"
    ENSURE_DIR(agentos_dir)
    RETURN str(agentos_dir / "issue_workflow.db")

# 3. Fail Closed
EXCEPT FileNotFoundError:
    PRINT_ERROR("Cannot determine repository root. Set AGENTOS_WORKFLOW_DB environment variable to specify database location.")
    EXIT(1)
```

### 2.6 Technical Approach
*   **Module Location:** Logic stays within `src/agentos/workflow/checkpoint.py` to minimize refactoring impact.
*   **Repo Detection:** We rely on `git rev-parse --show-toplevel`. This is robust because it correctly identifies the root even if the user is in a subdirectory, and crucially, it handles **git worktrees** correctly by returning the worktree root, not the main repository root.
*   **Fail Closed:** The system specifically avoids falling back to a global default (like `~/.agentos`) to prevent accidental state corruption or confusion. If context is ambiguous, explicit configuration is required.

## 3. Requirements
1.  **Env Var Priority:** `AGENTOS_WORKFLOW_DB` must override all other logic.
2.  **Repo Isolation:** Default behavior inside a git repo must create `.agentos/issue_workflow.db` at the repository root.
3.  **Worktree Support:** Worktrees must have their own independent `.agentos/` directory (ensured via `git rev-parse`).
4.  **Fail Closed:** Execution outside a git repo without the env var must terminate with a descriptive error.
5.  **Git Ignore:** The `.agentos/` directory must be added to `.gitignore`.
6.  **Directory Creation:** The code must auto-create the `.agentos` directory if it doesn't exist.

## 4. Alternatives Considered

| Alternative | Pros | Cons | Decision |
|-------------|------|------|----------|
| **Keep Global (~/.agentos)** | Simplest implementation. | Race conditions with concurrent workflows; collisions between repos. | **Rejected** |
| **Global DB with Repo Keying** | Centralized storage. | Complex schema changes required to add `repo_id` column; difficult to manage worktrees. | **Rejected** |
| **Per-Repo (Selected)** | strict isolation; naturally handles worktrees; simple cleanup (`rm -rf .agentos`). | Requires git dependency; local clutter (mitigated by .gitignore). | **Accepted** |
| **Cwd Relative (`./.agentos`)** | No git dependency. | Fails if running command from subdirectory; fragments DBs across project folders. | **Rejected** |

## 5. Data & Fixtures

### 5.1 Data Sources
| Source | Type | Attributes |
|--------|------|------------|
| Environment | Variable | `AGENTOS_WORKFLOW_DB` |
| Filesystem | Git Command | Output of `git rev-parse` |

### 5.2 Data Pipeline
```ascii
[Start] 
   |
   +--> Is AGENTOS_WORKFLOW_DB set? 
   |       |
   |       +--[YES]--> Use provided path 
   |
   +--[NO]--> Is CWD inside Git Repo?
           |
           +--[YES]--> Resolve Repo Root 
           |            |
           |            +--> Create/Use {Root}/.agentos/issue_workflow.db
           |
           +--[NO]--> [ERROR] "Set AGENTOS_WORKFLOW_DB" -> [EXIT]
```

### 5.3 Test Fixtures
| Fixture | Description |
|---------|-------------|
| `temp_git_repo` | A temporary directory initialized with `git init`. |
| `temp_git_worktree` | A temporary main repo plus a linked worktree. |
| `temp_non_repo` | A plain temporary directory with no git info. |

### 5.4 Deployment Pipeline
Development only. Changes affect local CLI execution.

## 6. Diagram

### 6.1 Mermaid Quality Gate
- [x] Syntax Valid
- [x] Flow Logical
- [x] Covers Fail-Closed

### 6.2 Diagram
```mermaid
flowchart TD
    A[Start: get_checkpoint_db_path] --> B{Env Var Defined?}
    B -- Yes --> C[Use AGENTOS_WORKFLOW_DB]
    B -- No --> D{Is Git Repo?}
    D -- Yes --> E[Get Repo Root]
    E --> F[Mkdir .agentos]
    F --> G[Return {root}/.agentos/issue_workflow.db]
    D -- No --> H[Error: Cannot determine DB location]
    H --> I[Exit Program]
```

## 7. Security Considerations

| Concern | Mitigation |
|---------|------------|
| **Information Leakage** | Workflow steps might contain sensitive data. Storing per-repo ensures data stays within the project boundary (inheriting directory permissions) rather than a global user folder. |
| **Accidental Commit** | `.agentos/` added to `.gitignore` to prevent pushing local workflow state to remote. |
| **Path Traversal** | `pathlib` usage sanitizes paths; Env var usage assumes user trusts their own environment configuration. |

## 8. Performance Considerations

| Metric | Budget | Impact |
|--------|--------|--------|
| **Startup Time** | < 100ms | Adding `git rev-parse` subprocess call is negligible (< 10ms usually). |
| **Disk I/O** | N/A | No change to DB I/O patterns, only location. |

## 9. Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| **Lost History** | High (User perspective) | High | Users upgrading will "lose" their active workflows because the tool looks in a new place. **Mitigation:** Release notes and error message instructing how to point to legacy DB using Env Var. |
| **Git Dependency** | Low | Low | Tool now requires `git` executable. **Mitigation:** AgentOS is a developer tool heavily integrated with git workflows already. |

## 10. Verification & Testing

### 10.1 Test Scenarios

| ID | Scenario | Type | Input | Output | Criteria |
|----|----------|------|-------|--------|----------|
| **T1** | Happy Path (In Repo) | Integration | CWD = `/tmp/repo` (git initialized) | DB at `/tmp/repo/.agentos/issue_workflow.db` | File is created, directory exists. |
| **T2** | Env Var Override | Integration | `AGENTOS_WORKFLOW_DB=/tmp/custom.db` | DB at `/tmp/custom.db` | Repo location ignored. |
| **T3** | Fail Closed | Integration | CWD = `/tmp/norepo` (no git) | Exit Code > 0 | Stderr contains "Set AGENTOS_WORKFLOW_DB". |
| **T4** | Worktree Isolation | Integration | CWD = `/tmp/main` and `/tmp/feature` | Two distinct DB files | Checkpoints in main do not appear in feature. |
| **T5** | Subdirectory Execution | Integration | CWD = `/tmp/repo/src` | DB at `/tmp/repo/.agentos/issue_workflow.db` | Correctly finds root from subdir. |

### 10.2 Test Commands
```bash
# Unit/Integration Tests
pytest tests/workflow/test_checkpoint_location.py

# Manual Verification (T3 - Fail Closed)
mkdir -p /tmp/test_fail && cd /tmp/test_fail
poetry run python tools/run_issue_workflow.py --brief check
# Expect error
```

### 10.3 Manual Tests
N/A - All scenarios automated via integration tests in `tests/workflow/`.

## 11. Definition of Done

### Code
- [ ] `get_checkpoint_db_path` modified in `src/agentos/workflow/checkpoint.py`.
- [ ] `.gitignore` updated.

### Tests
- [ ] Test T1 (Repo default) passed.
- [ ] Test T2 (Env override) passed.
- [ ] Test T3 (Fail closed) passed.
- [ ] Test T4 (Worktree) passed.

### Documentation
- [ ] `docs/workflow.md` updated with new storage behavior and legacy migration instructions.

### Review
- [ ] Peer review completed.
- [ ] Verified no regression on existing workflows if Env Var is used.

---

## Appendix: Review Log

### Review Summary

| Review | Date | Verdict | Key Issue |
|--------|------|---------|-----------|
| - | - | - | - |

**Final Status:** DRAFT - PENDING REVIEW