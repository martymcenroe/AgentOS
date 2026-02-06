# LLD Review: 119 - Chore: Review and Rearrange Audit Classes/Tiers

## Identity Confirmation
I am Gemini 3 Pro, acting as Senior Software Architect & AI Governance Lead.

## Pre-Flight Gate
PASSED

## Review Summary
The LLD provides a clear plan for reorganizing documentation, which is necessary for scaling the audit system. However, the Test Plan (Section 10) relies entirely on manual verification, which violates the strict "No Human Delegation" protocol. Even for documentation changes, structural integrity (link validity, table formatting, ID uniqueness) must be verified via automated scripts to prevent regression.

## Open Questions Resolved
- [x] ~~Should `--ultimate` tier audits be excluded from `--all` runs?~~ **RESOLVED: YES. The `--ultimate` tier must be opt-in (e.g., via `--ultimate` or `--all --include-ultimate`) to prevent accidental high costs or latency during standard development loops.**
- [x] ~~What cost threshold qualifies an audit as "ultimate" (e.g., >$1 API call, >5 min runtime)?~~ **RESOLVED: >$0.10 USD per run or >2 minutes execution time. Any audit requiring non-deterministic LLM calls (vs. deterministic AST/Regex analysis) should also be considered for this tier.**
- [x] ~~Are there audits that should be deprecated rather than recategorized?~~ **RESOLVED: Yes. Do not delete them (to preserve ID history). Create a "Deprecated" category or status column in the index so tooling can automatically skip them.**

## Requirement Coverage Analysis (MANDATORY)

**Section 3 Requirements:**
| # | Requirement | Test(s) | Status |
|---|-------------|---------|--------|
| 1 | All 33 audits are reviewed and assigned | Test 010 (Manual) | **GAP** (Not Automated) |
| 2 | Each category has a clear, documented definition | Test 020 (Manual) | **GAP** (Not Automated) |
| 3 | `--ultimate` tier is defined with explicit criteria | Test 030 (Manual) | **GAP** (Not Automated) |
| 4 | At least 2-5 audits identified as candidates | Test 030 (Manual) | **GAP** (Not Automated) |
| 5 | Frequency matrix updated with tier | Test 050 (Manual) | **GAP** (Not Automated) |
| 6 | No existing audit references are broken | Test 040 (Manual) | **GAP** (Not Automated) |

**Coverage Calculation:** 0 requirements covered (by valid automated tests) / 6 total = **0%**

**Verdict:** **BLOCK**

**Missing Test Scenarios:**
- A script (e.g., `scripts/validate_docs.py`) is required to:
    - Parse `docs/0800-audit-index.md` and count audit rows (Assertion: Count == 33).
    - Verify every audit ID matches regex `08\d{2}`.
    - Verify no duplicate IDs exist.
    - Check that all links in the index point to existing files.
    - Verify the "Category" column only contains values from the allowed list.

## Tier 1: BLOCKING Issues
No blocking issues found. LLD is approved for implementation regarding Cost, Safety, Security, and Legal, provided the Open Questions are resolved as recommended.

### Cost
- [ ] No issues found. (Resolved by answering Question 1).

### Safety
- [ ] No issues found.

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
- [ ] **Requirement Coverage:** **BLOCK**. Coverage is effectively 0% because all tests rely on "Manual" verification.
- [ ] **Test Plan Violation (No Human Delegation):** Section 10.3 explicitly states "Manual Tests (Only If Unavoidable)". For a project of this maturity, structural documentation validation *is* avoidable and should be automated.
    - **Recommendation:** Create a simple validation script (e.g., using Python's `re` or `pandas`) to verify the integrity of `docs/0800-audit-index.md`. The script should exit with status 1 if:
        - The number of audits != 33.
        - Table formatting is broken.
        - Links are dead.
        - Categories do not match the defined schema.
    - This script serves as the "Test" for TDD.

## Tier 3: SUGGESTIONS
- **Automation:** Consider adding a GitHub Action that runs this validation script on future PRs to `docs/`.
- **Formatting:** Ensure the markdown tables use consistent alignment (left-aligned usually reads best for text).

## Questions for Orchestrator
1. None.

## Verdict
[ ] **APPROVED** - Ready for implementation
[x] **REVISE** - Fix Tier 1/2 issues first
[ ] **DISCUSS** - Needs Orchestrator decision