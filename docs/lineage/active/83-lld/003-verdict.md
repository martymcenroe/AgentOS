# LLD Review: #83-Feature: Structured Issue File Naming Scheme

## Identity Confirmation
I am Gemini 3 Pro, acting as Senior Software Architect & AI Governance Lead.

## Pre-Flight Gate
PASSED

## Review Summary
The design provides a robust, collision-resistant naming scheme using a deterministic repository-word-number format. The sanitization logic is sound, and the architectural decisions regarding dependency-free operation are appropriate. However, the LLD is **BLOCKED** because the Test Plan coverage (84.6%) falls below the strict 95% threshold. Specifically, backward compatibility with existing files is a requirement but lacks a corresponding test scenario.

## Open Questions Resolved
- [x] ~~Should the wordlist be extensible via configuration, or is the embedded 80+ word list sufficient?~~ **RESOLVED: Embedded is sufficient.** Following YAGNI, file I/O for configuration adds unnecessary complexity for an internal tool. 80 words * 9999 issues provides ample headroom (~800k issues).
- [x] ~~What should happen if the wordlist is exhausted (all 80+ words collide for a repo)?~~ **RESOLVED: Raise ValueError.** This is the correct "Fail Closed" behavior. In the unlikely event of 80 active, colliding issues for a single repo, human intervention is required to archive old issues.

## Requirement Coverage Analysis (MANDATORY)

**Section 3 Requirements:**
| # | Requirement | Test(s) | Status |
|---|-------------|---------|--------|
| 1 | `get_repo_short_id()` returns ≤7 char capitalized... | T010, T030, T040 | ✓ Covered |
| 2 | `get_repo_short_id()` follows priority... | T060, T070, T080 | ✓ Covered |
| 3 | `get_repo_short_id()` raises `ValueError` for empty... | T050 | ✓ Covered |
| 4 | `generate_issue_word()` produces deterministic word... | T090 | ✓ Covered |
| 5 | Word selection detects and avoids collisions... | T100, T110 | ✓ Covered |
| 6 | `get_next_issue_number()` scopes counter to Repo ID... | T140 | ✓ Covered |
| 7 | Slug format matches `{REPO}-{WORD}-{NUM}`... | T150 | ✓ Covered |
| 8 | All new audit files use `{SLUG}-{TYPE}.md` naming... | T160 | ✓ Covered |
| 9 | Audit directories named with full slug | T160 | ✓ Covered |
| 10 | Revision files append sequence number... | T170 | ✓ Covered |
| 11 | Existing old-format issues continue to work unchanged | - | **GAP** |
| 12 | Wordlist contains 80+ curated words | T180 | ✓ Covered |
| 13 | `issue_word` tracked in workflow state | - | **GAP** |

**Coverage Calculation:** 11 requirements covered / 13 total = **84.6%**

**Verdict:** BLOCK

**Missing Test Scenarios:**
1.  **Req 11 (Backward Compatibility):** Add `test_get_next_issue_number_ignores_legacy`. Create files named `001-brief.md` in the test fixture and ensure `get_next_issue_number` doesn't crash or miscount them.
2.  **Req 13 (State Tracking):** Add `test_workflow_state_update`. Verify that the operation actually returns/updates the `issue_word` key in the state dictionary, not just the slug string.

## Tier 1: BLOCKING Issues
No blocking issues found in Cost, Safety, Security, or Legal categories. LLD is approved for implementation pending Tier 2 fixes.

### Cost
- [ ] No issues found.

### Safety
- [ ] No issues found. Sanitization of repo IDs effectively prevents path traversal.

### Security
- [ ] No issues found.

### Legal
- [ ] No issues found.

## Tier 2: HIGH PRIORITY Issues

### Architecture
- [ ] No issues found.

### Observability
- [ ] No issues found.

### Quality
- [ ] **Requirement Coverage:** **BLOCK**. Coverage is 84.6% (<95%). You must add tests for backward compatibility (R11) and state updates (R13) to the Test Plan in Section 10.
- [ ] **Test Robustness:** Ensure `T160` explicitly asserts the directory creation, not just the file creation.

## Tier 3: SUGGESTIONS
- **Debug Tooling:** Consider exposing `get_repo_short_id` via a CLI command (e.g., `make audit-id`) to help users debug what their Repo ID resolves to without running a full audit.

## Questions for Orchestrator
1. None.

## Verdict
[ ] **APPROVED** - Ready for implementation
[x] **REVISE** - Fix Tier 1/2 issues first
[ ] **DISCUSS** - Needs Orchestrator decision