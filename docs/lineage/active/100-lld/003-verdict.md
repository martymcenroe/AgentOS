# LLD Review: 1100-Feature: Lineage Workflow Integration

## Identity Confirmation
I am Gemini 3 Pro, acting as Senior Software Architect & AI Governance Lead.

## Pre-Flight Gate
PASSED

## Review Summary
The LLD proposes a solid filesystem-based approach for lineage tracking, which is robust and simple. However, the document fails the **Requirement Coverage** check (66% < 95%). The Test Plan currently focuses solely on the new `lineage.py` module, neglecting tests for the required changes in `lld-workflow.py` (CLI flags), `new-repo-setup.py` (directory creation), and specific filing metadata requirements. These must be added to Section 10 before approval.

## Open Questions Resolved
- [x] ~~Should we support resuming a partially-completed lineage folder (e.g., if workflow crashed after brief but before filing)?~~ **RESOLVED: Yes. Resumability is critical for workflow robustness and preventing orphaned folders.**
- [x] ~~What happens if an issue is closed without filing (cancelled/abandoned)? Move to `done/` with special status or `abandoned/`?~~ **RESOLVED: Move to `docs/lineage/abandoned/` to distinguish them from shipped features. Ensure `new-repo-setup.py` creates this directory.**

## Requirement Coverage Analysis (MANDATORY)

**Section 3 Requirements:**
| # | Requirement | Test(s) | Status |
|---|-------------|---------|--------|
| 1 | Issue workflow creates `docs/lineage/active/{id}-{slug}/` | T010 / Scen 010 | ✓ Covered |
| 2 | All briefs saved as `001-brief.md` | T050 / Scen 050 | ✓ Covered |
| 3 | All drafts saved as `{NNN}-draft.md` | T060 / Scen 060 | ✓ Covered |
| 4 | All verdicts saved as `{NNN}-verdict.md` | T070 / Scen 070 | ✓ Covered |
| 5 | Filing metadata saved as `{NNN}-filed.json` | - | **GAP** |
| 6 | Folder moves to `docs/lineage/done/` on filing | T080 / Scen 080 | ✓ Covered |
| 7 | LLD workflow accepts `--lineage-folder` flag | - | **GAP** |
| 8 | `new-repo-setup.py` creates `active/` and `done/` | - | **GAP** |
| 9 | Workflow can resume from existing active folder | T110 / Scen 110 | ✓ Covered |

**Coverage Calculation:** 6 requirements covered / 9 total = **66.6%**

**Verdict:** **BLOCK**

**Missing Test Scenarios:**
1.  **Test for Req 5:** Verify `save_artifact` handles JSON content correctly for filing metadata, or adds a specific test for metadata serialization.
2.  **Test for Req 7:** Integration test or argument parsing test for `tools/lld-workflow.py` to verify it accepts and processes `--lineage-folder`.
3.  **Test for Req 8:** Test for `tools/new-repo-setup.py` ensuring it creates the directory structure (including the `abandoned/` folder recommended in Open Questions).

## Tier 1: BLOCKING Issues
No Tier 1 blocking issues found. LLD is approved for safety/cost/security/legal, but blocked on Quality (Tier 2).

### Cost
- No issues found.

### Safety
- No issues found. Worktree scope is respected.

### Security
- No issues found. Path traversal mitigated via slugify (tested in T020).

### Legal
- No issues found.

## Tier 2: HIGH PRIORITY Issues

### Architecture
- [ ] No issues found.

### Observability
- [ ] No issues found.

### Quality
- [ ] **Requirement Coverage Failure:** Coverage is 66.6%, below the 95% threshold. See "Requirement Coverage Analysis" above for specific gaps.
- [ ] **Missing Integration Tests:** The LLD modifies existing tools (`issue-workflow.py`, `lld-workflow.py`) but the test plan only covers the new `lineage.py` module. Add tests to verify the integration points work (e.g., CLI argument parsing).

## Tier 3: SUGGESTIONS
- **Metadata Format:** Explicitly define the JSON schema for `{NNN}-filed.json` in Section 2.3 to ensure downstream tools can parse it reliably.
- **Abandonment Workflow:** Update Section 2.1 (Files Changed) and 2.5 (Logic) to reflect the decision to use an `abandoned/` folder.

## Questions for Orchestrator
1. None.

## Verdict
[ ] **APPROVED** - Ready for implementation
[x] **REVISE** - Fix Tier 1/2 issues first
[ ] **DISCUSS** - Needs Orchestrator decision