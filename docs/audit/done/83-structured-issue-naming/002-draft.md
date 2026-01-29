# Structured Issue File Naming Scheme for Multi-Repo Workflows

## User Story
As a developer managing dozens of issues across multiple repositories,
I want a structured, collision-free file naming scheme for audit files,
So that I can easily identify, track, and correlate files with their GitHub issues.

## Objective
Implement a new naming convention `{REPO}-{WORD}-{NUM}-{TYPE}.md` that provides unique, memorable identifiers for issue files across multi-repo workflows.

## UX Flow

### Scenario 1: Creating a New Issue (Happy Path)
1. User creates a brief file with issue content
2. System generates slug: extracts repo ID, hashes brief content to select word, assigns next sequential number
3. System creates audit directory: `docs/audit/active/AgentOS-quasar-0042/`
4. System saves files with consistent naming: `AgentOS-quasar-0042-brief.md`, `AgentOS-quasar-0042-draft.md`
5. Result: All files for this issue share the same memorable identifier

### Scenario 2: Word Collision Detection
1. User creates a brief that hashes to word "zenith"
2. System detects "zenith" already exists in `active/` or `done/`
3. System selects next word in deterministic sequence from hash
4. Result: Unique word assigned without collision

### Scenario 3: Filing Issue to GitHub
1. User runs file_issue node on completed draft
2. System creates GitHub issue, receives issue number (e.g., #142)
3. System updates internal tracking but keeps directory name unchanged
4. Result: Files remain at `AgentOS-quasar-0042/` with GitHub issue #142 linked in metadata

### Scenario 4: Multi-Repo Workflow
1. User works on issues across AgentOS, Unleash, and DispatchRepo
2. Each issue has repo prefix: `AgentOS-quasar-0042`, `Unleash-praxis-0015`, `Dispatc-nebula-0003`
3. Result: Clear visual separation of which repo each issue belongs to

## Requirements

### Slug Generation
1. Slug format: `{REPO}-{WORD}-{NUM}` (e.g., `AgentOS-quasar-0042`)
2. Repo ID: Max 7 characters, first letter capitalized, derived from git remote or directory name
3. Word: 4-6 letter English word from curated vocabulary list
4. Number: 4-digit zero-padded sequential number (0001-9999)

### Word Selection
1. Deterministic: MD5 hash of brief content seeds word selection
2. Collision-free: Check against all words in `active/` and `done/` directories
3. Fallback: On collision, try next word in deterministic sequence from hash
4. Curated list: 80+ interesting vocabulary-expanding words

### File Naming
1. Format: `{SLUG}-{TYPE}.md` (e.g., `AgentOS-quasar-0042-draft.md`)
2. Types: brief, draft, verdict, feedback, filed
3. Revisions: Append sequence number (draft2, verdict2)
4. Directory: Named with slug, contains all related files

### Backward Compatibility
1. Existing issues with `NNN-{type}.md` format continue to work
2. New issues use new format exclusively
3. No migration of existing issues required

## Technical Approach

- **`get_repo_short_id()`:** Extract repo name from git remote URL, fallback to directory name, truncate/abbreviate to 7 chars
- **`generate_issue_word(brief_content, existing_words)`:** MD5 hash brief, use as seed to select from wordlist, check collisions, return unique word
- **`generate_slug(brief_file, brief_content)`:** Combine repo ID, word, and next sequential number
- **`save_audit_file(audit_dir, slug, file_type, content, sequence?)`:** Save file with new naming convention
- **IssueWorkflowState:** Add `issue_word` field to track word separately from slug

## Security Considerations
- No security implications: purely local file naming convention
- No external API calls (local wordlist only)
- No sensitive data in filenames

## Files to Create/Modify
- `src/skills/audit/utils.py` — Add `get_repo_short_id()`, `generate_issue_word()`, update `generate_slug()`, update `save_audit_file()`
- `src/skills/audit/wordlist.py` — New file containing curated `ISSUE_WORDS` list (80+ words)
- `src/skills/audit/nodes/load_brief.py` — Use new slug generation
- `src/skills/audit/nodes/draft.py` — Use updated `save_audit_file()` signature
- `src/skills/audit/nodes/review.py` — Use updated `save_audit_file()` signature
- `src/skills/audit/nodes/human_edit_draft.py` — Use updated `save_audit_file()` signature
- `src/skills/audit/nodes/human_edit_verdict.py` — Use updated `save_audit_file()` signature
- `src/skills/audit/nodes/file_issue.py` — Update `done/` directory naming
- `src/skills/audit/state.py` — Add `issue_word` to `IssueWorkflowState`

## Dependencies
- None: self-contained feature

## Out of Scope (Future)
- Web dashboard for browsing issues by word/number
- Search by word: "What's the status of quasar?"
- Cross-repo issue linking
- Wordlist expansion via external API
- Migration of existing issues to new format

## Acceptance Criteria
- [ ] `get_repo_short_id()` returns ≤7 char capitalized repo identifier
- [ ] `generate_issue_word()` produces deterministic word from brief hash
- [ ] Word selection detects and avoids collisions in `active/` and `done/`
- [ ] Slug format matches `{REPO}-{WORD}-{NUM}` pattern
- [ ] All new audit files use `{SLUG}-{TYPE}.md` naming
- [ ] Audit directories named with full slug
- [ ] Revision files append sequence number (draft2, verdict2)
- [ ] Existing old-format issues continue to work unchanged
- [ ] Wordlist contains 80+ curated vocabulary-expanding words
- [ ] `issue_word` tracked in workflow state

## Definition of Done

### Implementation
- [ ] Core slug generation implemented with all three components
- [ ] Wordlist module created with curated words
- [ ] All 5 node files updated to use new naming
- [ ] State schema updated with `issue_word` field
- [ ] Unit tests for slug generation and collision detection
- [ ] Integration tests for full workflow with new naming

### Tools
- [ ] Update any CLI tools that reference audit file paths

### Documentation
- [ ] Document naming scheme in audit skill README
- [ ] Add wordlist documentation with contribution guidelines
- [ ] Update file inventory with new wordlist.py

### Reports (Pre-Merge Gate)
- [ ] `docs/reports/{IssueID}/implementation-report.md` created
- [ ] `docs/reports/{IssueID}/test-report.md` created

### Verification
- [ ] All existing tests pass (backward compatibility)
- [ ] New naming scheme tests pass
- [ ] Manual verification: create issue, verify naming throughout workflow

## Testing Notes

**Testing slug generation:**
```python
# Same brief content should produce same word
brief1 = "Test brief content"
word1 = generate_issue_word(brief1, set())
word2 = generate_issue_word(brief1, set())
assert word1 == word2

# Different content produces different word (usually)
brief2 = "Different brief content"
word3 = generate_issue_word(brief2, set())
# May or may not differ, but deterministic for same input
```

**Testing collision avoidance:**
```python
existing = {"quasar", "zenith", "nebula"}
# Should return word not in existing set
word = generate_issue_word(brief_content, existing)
assert word not in existing
```

**Testing repo ID extraction:**
```bash
# In a git repo with remote git@github.com:owner/AgentOS.git
# get_repo_short_id() should return "AgentOS"

# In a repo with long name "MyVeryLongRepoName"
# Should truncate to "MyVeryL" or intelligently abbreviate
```