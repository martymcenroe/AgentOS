# Issue Review: Structured Issue File Naming Scheme for Multi-Repo Workflows

## Identity Confirmation
I am Gemini 3 Pro, acting as Senior Technical Product Manager & Governance Lead.

## Pre-Flight Gate
PASSED

## Review Summary
The issue is well-structured and technically detailed. However, it requires specific security controls for filesystem operations and architectural clarification regarding identifier stability before entering the backlog.

## Tier 1: BLOCKING Issues

### Security
- [ ] **Input Sanitization (Filesystem):** The issue derives filenames from `git remote` or directory names (`get_repo_short_id`).
    - **Risk:** Malicious or malformed directory names/git configs could introduce invalid characters or path traversal sequences (e.g., `../`) into the `slug`.
    - **Requirement:** Add an explicit requirement to sanitize the `Repo ID` to alphanumeric characters only (regex `[a-zA-Z0-9]+`) before using it in file path generation.

### Safety
- [ ] No blocking issues found.

### Cost
- [ ] No blocking issues found.

### Legal
- [ ] No blocking issues found.

## Tier 2: HIGH PRIORITY Issues

### Quality
- [ ] **Vague Logic:** The Technical Approach mentions "intelligently abbreviate" for `get_repo_short_id`.
    - **Recommendation:** Replace with a deterministic rule (e.g., "Take first 7 alphanumeric characters") or a hashing strategy. Vague logic leads to inconsistent implementation.

### Architecture
- [ ] **Identifier Stability:** The proposal relies on `directory name` as a fallback for Repo ID.
    - **Risk:** If a developer renames the project directory, the Repo ID changes, potentially breaking the "collision-free" assumption or disconnecting new files from old ones.
    - **Recommendation:** Define the order of precedence strictly (e.g., 1. `.audit-config` file, 2. Git Remote, 3. Dir Name) or acknowledge that directory renaming breaks continuity.
- [ ] **Numbering Scope:** The requirements specify a sequential number (`0042`) but do not define the scope.
    - **Question:** Is the counter global (across all repos) or per-repo? If per-repo, the logic must parse *only* that repo's existing files to find `MAX(id)`. This needs to be explicit in the Technical Approach.

## Tier 3: SUGGESTIONS
- **Taxonomy:** Add `enhancement` and `dx` (Developer Experience) labels.
- **Effort Estimate:** Likely a **Medium (3-5 points)** due to the need for robust regex and regression testing on existing file parsing.
- **Test Plan:** Add a test case for a repo name containing spaces or special characters to ensure sanitization works.

## Questions for Orchestrator
1. Should we enforce a manual override config (e.g., a `.repo-id` file) to ensure stability of the Repo ID across different machines where directory names might differ?

## Verdict
[ ] **APPROVED** - Ready to enter backlog
[x] **REVISE** - Fix Tier 1/2 issues first
[ ] **DISCUSS** - Needs Orchestrator decision