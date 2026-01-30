# Backfill Audit Directory Structure for Existing GitHub Issues

## User Story
As a project maintainer,
I want to automatically generate audit directories for existing GitHub issues,
So that all issues (past and present) have consistent local audit trails matching our governance workflow.

## Objective
Create a Python CLI tool that backfills the `docs/audit/` directory structure for all existing GitHub issues across registered repositories.

## UX Flow

### Scenario 1: Backfill Single Repository
1. User runs `python tools/backfill_issue_audit.py --repo martymcenroe/AgentOS`
2. Tool fetches all issues via `gh issue list --json`
3. Tool generates slug for each issue (e.g., `62-governance-workflow-stategraph`)
4. Tool creates directories under `docs/audit/done/` (closed) or `docs/audit/active/` (open)
5. Tool writes `001-issue.md`, `002-comments.md`, `003-metadata.json` to each directory
6. Result: Complete audit trail for all issues in that repo

### Scenario 2: Dry Run Mode
1. User runs `python tools/backfill_issue_audit.py --repo martymcenroe/AgentOS --dry-run`
2. Tool fetches and processes issues
3. Tool prints what would be created without writing files
4. Result: User previews changes before committing

### Scenario 3: Skip Existing Directories
1. User runs `python tools/backfill_issue_audit.py --repo martymcenroe/AgentOS --skip-existing`
2. Tool encounters issue #62 which already has `docs/audit/done/62-governance-workflow-stategraph/`
3. Tool skips this issue and continues to next
4. Result: Only new issues get backfilled, existing audit trails preserved

### Scenario 4: Backfill All Registered Repos
1. User runs `python tools/backfill_issue_audit.py --all-registered`
2. Tool reads `project-registry.json` for list of repos
3. Tool iterates through each repo and backfills
4. Result: Audit directories created across entire project ecosystem

### Scenario 5: Issue Has No Comments
1. Tool processes issue #45 which has no comments
2. Tool creates `001-issue.md` and `003-metadata.json`
3. Tool skips `002-comments.md` (or creates empty placeholder)
4. Result: Graceful handling of issues without discussion

## Requirements

### CLI Interface
1. Accept `--repo OWNER/REPO` flag for single repository targeting
2. Accept `--all-registered` flag to process all repos in `project-registry.json`
3. Accept `--dry-run` flag to preview without writing
4. Accept `--skip-existing` flag to preserve existing audit directories
5. Accept `--open-only` flag to process only open issues
6. Provide clear progress output showing issues processed

### Slug Generation
1. Implement slug algorithm matching `agentos/workflows/issue/audit.py`
2. Lowercase the title
3. Replace spaces and underscores with hyphens
4. Remove special characters (keep alphanumeric and hyphens only)
5. Collapse multiple consecutive hyphens to single hyphen
6. Prepend issue number: `{number}-{slug}`
7. Handle edge cases: empty titles, all-special-character titles

### File Generation
1. Create `001-issue.md` with issue title as H1 and body as content
2. Create `002-comments.md` with all comments, each prefixed by author and date
3. Create `003-metadata.json` with issue metadata (number, URL, state, labels, timestamps, linked PRs)
4. Place files in `docs/audit/done/{slug}/` for closed issues
5. Place files in `docs/audit/active/{slug}/` for open issues

### Data Fetching
1. Use `gh issue list` with JSON output for issue enumeration
2. Use `gh issue view` with JSON output for full issue details including comments
3. Handle pagination for repos with many issues
4. Include linked PR detection from timeline events or issue body references

## Technical Approach
- **CLI Parsing:** `argparse` for command-line interface
- **GitHub API:** `subprocess` calls to `gh` CLI (avoids auth token management)
- **Slug Generation:** Pure Python string manipulation (no external dependencies)
- **File I/O:** `pathlib` for cross-platform path handling
- **JSON Handling:** Standard library `json` module
- **Date Formatting:** `datetime` for ISO timestamp parsing and formatting

## Security Considerations
- Tool only reads from GitHub API (no write operations to remote)
- Respects existing `gh` CLI authentication
- No sensitive data stored—all content already public in GitHub issues
- Local file writes restricted to `docs/audit/` directory tree

## Files to Create/Modify
- `tools/backfill_issue_audit.py` — Main CLI tool (new file)
- `docs/audit/done/` — Directory for closed issue audits (created by tool)
- `docs/audit/active/` — Directory for open issue audits (created by tool)

## Dependencies
- Requires `gh` CLI installed and authenticated
- Requires `project-registry.json` for `--all-registered` mode

## Out of Scope (Future)
- **Incremental sync** — detecting new comments since last backfill (future enhancement)
- **PR audit backfill** — separate tool for pull request audit trails
- **Cross-repo linking** — detecting references between repos
- **LLM summarization** — generating brief/summary from issue content

## Acceptance Criteria
- [ ] Running `--repo martymcenroe/AgentOS` creates audit directories for all issues
- [ ] Closed issues appear under `docs/audit/done/`
- [ ] Open issues appear under `docs/audit/active/`
- [ ] Slug format matches `{number}-{slugified-title}` pattern
- [ ] `001-issue.md` contains issue title and body
- [ ] `002-comments.md` contains all comments with author and timestamp
- [ ] `003-metadata.json` contains valid JSON with required fields
- [ ] `--dry-run` prints actions without creating files
- [ ] `--skip-existing` preserves directories that already exist
- [ ] `--all-registered` processes multiple repos from registry
- [ ] Tool handles issues with no comments gracefully
- [ ] Tool handles issues with special characters in titles

## Definition of Done

### Implementation
- [ ] Core feature implemented
- [ ] Unit tests written and passing
- [ ] Integration test with real GitHub repo

### Tools
- [ ] `tools/backfill_issue_audit.py` created and executable
- [ ] Tool usage documented in script docstring

### Documentation
- [ ] Update wiki with audit directory structure explanation
- [ ] Update README.md with backfill tool usage
- [ ] Add tool to `docs/0003-file-inventory.md`

### Reports (Pre-Merge Gate)
- [ ] `docs/reports/{IssueID}/implementation-report.md` created
- [ ] `docs/reports/{IssueID}/test-report.md` created

### Verification
- [ ] Run 0817 Wiki Alignment Audit - PASS

## Testing Notes
- Test with a repo that has: 0 issues, 1 issue, 50+ issues
- Test with issues containing markdown, code blocks, images
- Test with issue titles containing emojis, quotes, slashes
- Test `--dry-run` actually creates no files (check filesystem before/after)
- Test `--skip-existing` by pre-creating one directory