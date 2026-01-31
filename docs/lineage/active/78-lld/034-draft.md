# 178 - Feature: Per-Repo Workflow Database

## 1. Context & Goal
* **Issue:** #78
* **Objective:** Change the default workflow checkpoint database location from global (`~/.agentos/`) to per-repo (`{repo_root}/.agentos/`) to enable safe concurrent workflow execution.
* **Status:** Draft
* **Related Issues:** None.

### Open Questions
None - requirements are well-defined from issue.

## 2. Proposed Changes

### 2.1 Files Changed
| File | Action | Description |
| :--- | :--- | :--- |
| `src/agentos/workflow/checkpoint.py` | Modify | Update `get_checkpoint_db_path` logic to prefer repo root and fail closed if undefined. |
| `.gitignore` | Modify | Add `.agentos/` to ignore local workflow state. |
| `docs/workflow.md` | Modify | Update documentation regarding DB location and `AGENTOS_WORKFLOW_DB` variable. |

### 2.2 Dependencies
* No new package dependencies.
* Requires `git` executable to be present in the environment (standard assumption for this tool).

### 2.3 Data Structures
No new data structures. The SQLite schema remains unchanged.

### 2.4 Function Signatures

**File:** `src/agentos/workflow/checkpoint.py`

```python
def get_repo_root() -> Path:
    """
    Determines the root directory of the current git repository.
    
    Returns:
        Path: The absolute path to the repository root.
        
    Raises:
        RuntimeError: If the current directory is not within a git repository.
    """
    pass

def get_checkpoint_db_path() -> Path:
    """
    Resolves the path to the SQLite checkpoint database.
    
    Priority:
    1. AGENTOS_WORKFLOW_DB environment variable.
    2. .agentos/issue_workflow.db in the current git repository root.
    
    Side Effects:
        Creates the .agentos directory if it does not exist (when resolving to repo root).
        
    Returns:
        Path: The absolute path to the database file.
        
    Raises:
        RuntimeError: If not in a git repo and AGENTOS_WORKFLOW_DB is not set.
    """
    pass
```

### 2.5 Logic Flow (Pseudocode)

**get_checkpoint_db_path**
```python
FUNCTION get_checkpoint_db_path():
    # 1. Check Environment Variable
    IF env_var "AGENTOS_WORKFLOW_DB" IS SET:
        RETURN Path(env_var "AGENTOS_WORKFLOW_DB")

    # 2. Check Git Repository
    TRY:
        # Uses 'git rev-parse --show-toplevel' to handle worktrees correctly
        repo_root = CALL get_repo_root() 
        
        db_dir = repo_root / ".agentos"
        
        # Ensure directory exists
        IF db_dir DOES NOT EXIST:
            CREATE db_dir (parents=True)
            
        RETURN db_dir / "issue_workflow.db"
        
    CATCH GitError/RuntimeError:
        # 3. Fail Closed
        RAISE RuntimeError("Cannot determine repository root. Set AGENTOS_WORKFLOW_DB environment variable to specify database location.")
```

### 2.6 Technical Approach
* **Isolation Strategy:** leveraging `git rev-parse --show-toplevel` ensures that even when using Git Worktrees, the root path returned is specific to that worktree's directory, not the shared `.git` directory. This guarantees true isolation.
* **Fail-Closed:** The system intentionally avoids falling back to a global default (like `~/.agentos`) to prevent accidental state pollution. If the context is ambiguous, the user must be explicit via environment variables.
* **Directory Management:** The application takes responsibility for creating the `.agentos` directory on the fly, reducing setup friction.

## 3. Requirements
1.  **Priority Resolution:** The system MUST use `AGENTOS_WORKFLOW_DB` if set, regardless of git status.
2.  **Repo Detection:** The system MUST detect the root of the current git repository (or worktree) when the env var is not set.
3.  **Directory Creation:** The system MUST create the `.agentos/` directory in the repo root if it does not exist.
4.  **Fail Closed:** The system MUST exit with a specific error message if not in a git repo and no env var is set.
5.  **Persistence:** The database file path MUST be `{repo_root}/.agentos/issue_workflow.db`.
6.  **Git Ignore:** The `.gitignore` file MUST include `.agentos/` to prevent committing local state.

## 4. Alternatives Considered

| Option | Pros | Cons | Decision |
| :--- | :--- | :--- | :--- |
| **Global DB with Table Locks** | Centralized management. | Complex implementation; risk of blocking valid concurrent work. | Rejected |
| **Global DB with Unique Filenames** | Single config directory. | Hard to garbage collect old files; filenames need hashing logic. | Rejected |
| **Current Global Default (`~/.agentos`)** | Simple; existing behavior. | Prevents concurrent workflows; leaks state between projects. | Rejected |
| **Per-Repo (Proposed)** | Native isolation; worktree support; easy cleanup (`git clean -fdx`). | Requires `.gitignore` update; loses history if repo deleted (usually desired). | **Selected** |

## 5. Data & Fixtures

### 5.1 Data Sources
* **Environment:** `os.environ` for overrides.
* **Git Config:** Used implicitly via `git` command to find root.
* **FileSystem:** SQLite database file.

### 5.2 Data Pipeline
```ascii
[User Command] 
      |
      v
[Resolution Logic] --> [Env Var Set?] --Yes--> [Use Custom Path]
      | No
      v
[Git Repo Check] --Yes--> [Resolve Repo Root] --> [Create .agentos/] --> [Use Repo Path]
      | No
      v
[Error / Exit]
```

### 5.3 Test Fixtures
| Fixture | Description |
| :--- | :--- |
| `temp_git_repo` | A temporary directory initialized as a git repository. |
| `temp_worktree` | A temporary directory initialized as a git worktree of a main repo. |
| `non_repo_dir` | A temporary directory with no git initialization. |

### 5.4 Deployment Pipeline
* **Development only:** This change affects the developer CLI tool behavior.

## 6. Diagram

### 6.1 Mermaid Quality Gate
- [x] Diagram follows standard syntax
- [x] Flow logic matches requirements
- [x] Node labels are clear

### 6.2 Diagram

```mermaid
flowchart TD
    Start([Start Workflow]) --> CheckEnv{Is AGENTOS_WORKFLOW_DB set?}
    
    CheckEnv -- Yes --> UseEnv[Use Path defined in Env Var]
    
    CheckEnv -- No --> CheckGit{Is PWD inside Git Repo?}
    
    CheckGit -- Yes --> GetRoot[Get Repo Root\ngit rev-parse --show-toplevel]
    GetRoot --> MkDir[Ensure .agentos/ exists]
    MkDir --> UseRepo[Use {repo_root}/.agentos/issue_workflow.db]
    
    CheckGit -- No --> Error([Error: Cannot determine DB location])
    
    UseEnv --> ConnectDB[(Connect to SQLite)]
    UseRepo --> ConnectDB
```

## 7. Security Considerations

| Concern | Mitigation |
| :--- | :--- |
| **Sensitive Data in DB** | The DB stores workflow checkpoints (prompts, notes). By moving it to per-repo, we ensure project A's sensitive context doesn't accidentally leak into Project B's workflow history. |
| **Git Commit of DB** | The DB is binary and changes frequently. We mitigate accidental commits by adding `.agentos/` to `.gitignore`. |
| **Permissions** | The `.agentos` directory inherits the file permissions of the user running the command/repo, ensuring standard Unix security models apply. |

## 8. Performance Considerations

| Metric | Budget | Impact |
| :--- | :--- | :--- |
| **Path Resolution Latency** | < 50ms | Negligible. `git rev-parse` is extremely fast. |
| **Concurrent Access** | N/A | By isolating DBs per repo, we remove the need for file locking between different project workflows, effectively improving perceived concurrency performance. |

## 9. Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
| :--- | :--- | :--- | :--- |
| **Lost History** | User expects to find old global history. | High (Initial switch) | Documentation explaining how to mount the old DB via env var if needed. |
| **Disk Clutter** | Every repo gets a `.agentos` folder. | Medium | These are small SQLite files. `git clean -xdf` easily removes them. |
| **Not in Repo Error** | User runs tool in a script outside repo. | Low | Error message clearly instructs to use the Env Var override. |

## 10. Verification & Testing

### 10.1 Test Scenarios

| ID | Scenario | Type | Input | Output | Criteria |
| :--- | :--- | :--- | :--- | :--- | :--- |
| T1 | Happy Path (In Repo) | Integration | `cwd` = `/tmp/repo1` (git init) | DB at `/tmp/repo1/.agentos/issue_workflow.db` | File exists; no error. |
| T2 | Env Var Override | Integration | `AGENTOS_WORKFLOW_DB=/tmp/custom.db` | DB at `/tmp/custom.db` | System ignores current repo path; uses env path. |
| T3 | Fail Closed (No Repo) | Unit/Int | `cwd` = `/tmp/norepo` | Exit Code > 0 | Error message mentions `AGENTOS_WORKFLOW_DB`. |
| T4 | Worktree Isolation | Integration | `cwd` = `/tmp/worktree_dir` | DB at `/tmp/worktree_dir/.agentos/issue_workflow.db` | DB is NOT in the main repo dir. |

### 10.2 Test Commands

```bash
# Unit Tests
poetry run pytest tests/workflow/test_checkpoint.py

# Integration Verification Script
#!/bin/bash
set -e

# Setup
mkdir -p /tmp/test_agentos_iso/repo
cd /tmp/test_agentos_iso/repo
git init -q

# Test 1: Default
poetry run python tools/run_issue_workflow.py --brief test_note.md
if [ ! -f ".agentos/issue_workflow.db" ]; then echo "FAIL T1"; exit 1; fi

# Test 2: Env Var
export AGENTOS_WORKFLOW_DB=/tmp/test_agentos_iso/override.db
poetry run python tools/run_issue_workflow.py --brief test_note.md
if [ ! -f "/tmp/test_agentos_iso/override.db" ]; then echo "FAIL T2"; exit 1; fi
unset AGENTOS_WORKFLOW_DB

echo "All Checks Passed"
```

### 10.3 Manual Tests
N/A - All scenarios automated.

## 11. Definition of Done

### Code
- [ ] `get_checkpoint_db_path` modified in `src/agentos/workflow/checkpoint.py`.
- [ ] `.gitignore` updated.
- [ ] Type hints verified (`mypy`).

### Tests
- [ ] Unit tests for `get_checkpoint_db_path` covering Repo, No Repo, and Env Var states.
- [ ] Integration test verifying file creation on disk.

### Documentation
- [ ] `docs/workflow.md` updated with "Storage Location" section.
- [ ] README updated if CLI usage instructions imply global state.

### Review
- [ ] PR reviewed by 1 developer.
- [ ] CI pipeline passes.

---

## Appendix: Review Log

### Review Summary

| Review | Date | Verdict | Key Issue |
|--------|------|---------|-----------|
| - | - | - | - |

**Final Status:** DRAFT - PENDING REVIEW