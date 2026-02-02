# Extracted Test Plan

## Scenarios

### test_010
- Type: unit
- Requirement: 
- Mock needed: True
- Description: Per-repo database creation | Auto | Run workflow in git repo | `.agentos/issue_workflow.db` created in repo root | File exists at expected path

### test_020
- Type: unit
- Requirement: 
- Mock needed: True
- Description: Different repos get different databases | Auto | Run workflow in repo1, then repo2 | Two separate database files | `repo1/.agentos/issue_workflow.db` != `repo2/.agentos/issue_workflow.db`

### test_030
- Type: unit
- Requirement: 
- Mock needed: True
- Description: Environment variable override | Auto | Set `AGENTOS_WORKFLOW_DB=/tmp/custom.db` | Database at `/tmp/custom.db` | File created at env var path, not in repo

### test_040
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Fail closed outside repo | Auto | Run workflow in non-git directory | Exit code 1, error message | Exit code 1; stderr contains "AGENTOS_WORKFLOW_DB"

### test_050
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Worktree isolation | Auto | Create worktree, run workflow | Worktree gets own `.agentos/` | `worktree/.agentos/issue_workflow.db` exists

### test_060
- Type: unit
- Requirement: 
- Mock needed: True
- Description: Global database untouched | Auto | Run workflow in repo | `~/.agentos/issue_workflow.db` unchanged | Global DB not modified (timestamp unchanged)

### test_070
- Type: unit
- Requirement: 
- Mock needed: True
- Description: Nested repo detection (deep subdirectory) | Auto | Run in `repo/src/lib/` subdirectory | Database in repo root, not subdirectory | `repo_root/.agentos/` not `repo_root/src/lib/.agentos/`

### test_080
- Type: unit
- Requirement: 
- Mock needed: False
- Description: .agentos directory creation | Auto | Run in repo without .agentos | Directory created with proper permissions | Directory exists with user read/write

### test_090
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Env var with ~ expansion | Auto | Set `AGENTOS_WORKFLOW_DB=~/custom.db` | Path expanded correctly | File at `$HOME/custom.db`

### test_100
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Empty env var treated as unset | Auto | Set `AGENTOS_WORKFLOW_DB=""` | Falls back to per-repo | Uses repo path, not empty string

### test_110
- Type: unit
- Requirement: 
- Mock needed: False
- Description: .gitignore contains .agentos/ pattern | Auto | Check `.gitignore` after workflow run | `.agentos/` entry exists | Parse `.gitignore`, assert pattern present

### test_120
- Type: unit
- Requirement: 
- Mock needed: True
- Description: Concurrent execution (3 repos) | Auto | Spawn 3 subprocess workflows in parallel | Each repo has independent database, no errors | All 3 processes exit 0; 3 distinct `.agentos/issue_workflow.db` files

