# The Janitor: Automated Repository Hygiene Workflow

## User Story
As a developer working in a multi-project codebase,
I want automated background maintenance that fixes mechanical issues and alerts on structural problems,
So that I never encounter broken links, stale worktrees, or accumulated drift from forgotten cleanup tasks.

## Objective
Create `tools/run_janitor_workflow.py`, a LangGraph-based maintenance workflow that continuously monitors and fixes repository hygiene issues, replacing manual audit checklists with automated enforcement.

## UX Flow

### Scenario 1: Automated Link Fixing (Happy Path)
1. Developer renames `docs/old-guide.md` to `docs/new-guide.md`
2. Janitor runs overnight (via cron or scheduled task)
3. Janitor detects broken references to `old-guide.md` in `README.md` and other docs
4. Janitor creates a commit fixing all references automatically
5. Result: Developer pulls next morning, links are already fixed

### Scenario 2: Unfixable Issue Detection
1. Janitor detects architectural drift (e.g., circular dependency introduced)
2. Issue cannot be auto-fixed (requires human judgment)
3. Janitor checks for existing "Janitor Report" issue
4. Janitor creates/updates issue with categorized findings
5. Result: Developer sees actionable issue without running manual audits

### Scenario 3: Worktree Cleanup
1. Developer abandons a feature branch worktree 2 weeks ago
2. Janitor detects stale worktree (no commits in 14+ days, branch merged/deleted)
3. Janitor prunes the worktree automatically
4. Result: Clean workspace, no manual `git worktree prune` needed

### Scenario 4: Silent Mode (CI/Cron)
1. Janitor runs with `--silent` flag
2. Fixes are applied, no output unless errors
3. Exit code 0 = clean, 1 = unfixable issues filed
4. Result: Suitable for cron jobs and CI pipelines

## Requirements

### Probe System (N0_Sweeper)
1. Each probe returns structured JSON: `{status, findings[], fixable}`
2. Probes run in parallel where possible
3. Probe failures are isolated (one failing probe doesn't stop others)
4. Built-in probes:
   - `probe_links` — Broken internal markdown links
   - `probe_worktrees` — Stale/detached git worktrees
   - `probe_harvest` — Cross-project drift via `agentos-harvest.py`
   - `probe_todo` — TODO comments older than 30 days

### Fixer System (N1_Fixer)
1. Only acts on `fixable: true` findings
2. Creates atomic commits per fix category
3. Supports `--dry-run` to preview changes without applying
4. Generates human-readable commit messages explaining the fix
5. Can create PR instead of direct commit (configurable)

### Reporter System (N2_Reporter)
1. Deduplicates against existing open issues (searches by title pattern)
2. Groups findings by category in issue body
3. Updates existing "Janitor Report" issue if one exists
4. Includes severity levels: `info`, `warning`, `critical`

### CLI Interface
1. `--scope {all|links|worktrees|harvest|todo}` — Run specific probes only
2. `--auto-fix {true|false}` — Enable/disable automatic fixing (default: true)
3. `--dry-run` — Show what would be fixed without making changes
4. `--silent` — Suppress output except errors
5. `--create-pr` — Create PR instead of direct commits

## Technical Approach
- **State Graph:** LangGraph workflow in `agentos/workflows/janitor/graph.py` with three nodes (Sweeper → Fixer → Reporter)
- **State Management:** TypedDict-based state in `agentos/workflows/janitor/state.py` tracking probes run, failures found, and actions taken
- **Probe Registry:** Pluggable probe system allowing new probes to be added without modifying core workflow
- **GitHub Integration:** Uses `gh` CLI for issue creation/updates and PR creation
- **Scheduling:** Designed for cron/Task Scheduler; no daemon process required

## Security Considerations
- Janitor only modifies files within the repository (no external writes)
- GitHub operations use existing `gh` CLI authentication (no token storage)
- `--dry-run` mode allows safe preview of all changes
- Worktree pruning only targets detached/stale trees (never active work)
- All fixes create git commits (fully reversible via `git revert`)

## Files to Create/Modify
- `tools/run_janitor_workflow.py` — CLI entry point
- `agentos/workflows/janitor/__init__.py` — Package init
- `agentos/workflows/janitor/graph.py` — LangGraph state graph definition
- `agentos/workflows/janitor/state.py` — JanitorState TypedDict
- `agentos/workflows/janitor/probes/` — Probe implementations directory
- `agentos/workflows/janitor/probes/links.py` — Broken link detection
- `agentos/workflows/janitor/probes/worktrees.py` — Worktree hygiene
- `agentos/workflows/janitor/probes/harvest.py` — Cross-project drift
- `agentos/workflows/janitor/probes/todo.py` — Stale TODO scanner
- `agentos/workflows/janitor/fixers.py` — Auto-fix implementations
- `agentos/workflows/janitor/reporter.py` — GitHub issue creation/updates
- `docs/audits/083x/` — Archive superseded manual audits

## Dependencies
- LangGraph installed and configured
- `gh` CLI authenticated for issue/PR operations
- Existing `agentos-harvest.py` script (for harvest probe)

## Out of Scope (Future)
- **Real-time file watching** — Polling/scheduled runs only for MVP
- **Slack/Discord notifications** — GitHub issues are the notification layer
- **Cross-repository scanning** — Single repository scope for MVP
- **Custom probe plugins** — Future: allow `.janitor/probes/` directory for project-specific probes
- **Metrics dashboard** — Future: track "days since last broken link" over time

## Acceptance Criteria
- [ ] `python tools/run_janitor_workflow.py` runs all probes and reports findings
- [ ] `--dry-run` shows pending fixes without modifying any files
- [ ] Broken markdown links are automatically fixed when `auto_fix=true`
- [ ] Stale worktrees (14+ days inactive, branch merged) are pruned automatically
- [ ] Unfixable issues create/update a "Janitor Report" GitHub issue
- [ ] Existing Janitor Report issue is updated (not duplicated) on subsequent runs
- [ ] `--silent` mode produces no stdout on success, exits cleanly
- [ ] Exit code 0 when all issues fixed, exit code 1 when unfixable issues remain

## Definition of Done

### Implementation
- [ ] Core LangGraph workflow implemented with three nodes
- [ ] All four probe types functional (links, worktrees, harvest, todo)
- [ ] Auto-fix working for links and worktrees
- [ ] GitHub issue integration working for unfixable findings
- [ ] Unit tests for each probe
- [ ] Integration test for full workflow

### Tools
- [ ] `tools/run_janitor_workflow.py` CLI documented with `--help`
- [ ] Example cron/Task Scheduler configuration provided

### Documentation
- [ ] Update wiki with Janitor workflow documentation
- [ ] Archive superseded audit docs (0834, 0838, 0840) with pointer to Janitor
- [ ] Add architectural decision record for probe plugin system
- [ ] Add new files to `docs/0003-file-inventory.md`

### Reports (Pre-Merge Gate)
- [ ] `docs/reports/{IssueID}/implementation-report.md` created
- [ ] `docs/reports/{IssueID}/test-report.md` created

### Verification
- [ ] Manual test: rename a file, run Janitor, confirm links fixed
- [ ] Manual test: create stale worktree, run Janitor, confirm pruned
- [ ] Manual test: introduce unfixable issue, confirm GitHub issue created
- [ ] Run full audit suite to confirm no regressions

## Testing Notes

**To test link fixing:**
1. Create a test markdown file with a valid link
2. Rename the target file
3. Run `python tools/run_janitor_workflow.py --scope links`
4. Verify link is updated in source file

**To test worktree cleanup:**
1. Create a worktree: `git worktree add ../test-worktree -b test-branch`
2. Delete the branch: `git branch -D test-branch`
3. Run `python tools/run_janitor_workflow.py --scope worktrees`
4. Verify worktree is pruned

**To test issue deduplication:**
1. Run Janitor with an unfixable issue present
2. Note the created issue number
3. Run Janitor again
4. Verify the same issue is updated (not a new issue created)

**To force error states:**
- Remove `gh` CLI auth to test GitHub API failures
- Create a circular symlink to test probe error handling
- Run with `--scope invalid` to test CLI validation