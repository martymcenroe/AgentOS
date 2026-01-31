# Issue Review: TDD Test Initialization Gate

## Identity Confirmation
I am Gemini 3 Pro, acting as Senior Technical Product Manager & Governance Lead.

## Pre-Flight Gate
PASSED

## Review Summary
This is a highly sophisticated and detailed specification for enforcing TDD discipline. The workflows for "Hotfix" and "Offline" scenarios are particularly well-thought-out. However, there is a critical Blocking issue regarding the scope of test execution within git hooks (Safety) and high-priority architectural concerns regarding hook distribution and git history preservation.

## Tier 1: BLOCKING Issues

### Security
- [ ] No blocking issues found. Input sanitization and secret handling are explicitly addressed.

### Safety
- [ ] **Performance/Friction (Critical):** The issue proposes running tests within `prepare-commit-msg` or `pre-commit` hooks. If the hook triggers "Standard discovery" (as mentioned in Framework Support), it could run the *entire* test suite on every commit, effectively freezing the developer's terminal.
    - **Recommendation:** You must explicitly restrict the test execution in the hook to **only the specific test file associated with the current change**. Add a requirement that the tool passes the specific file path to the test runner (e.g., `pytest tests/test_new_feature.py`), preventing a full suite run.

### Cost
- [ ] No blocking issues found.

### Legal
- [ ] No blocking issues found.

## Tier 2: HIGH PRIORITY Issues

### Quality
- [ ] **Squash/Rebase Fragility:** The "Green Phase" verification relies on comparing the current state to a "Red Phase" footer in the commit history. If a developer performs an interactive rebase or "Squash and Merge" (common in GitHub workflows), the commit containing the `TDD-Red-Phase` footer may be lost or combined, causing the CI gate to fail incorrectly.
    - **Recommendation:** Define behavior for squashed commits. Alternatively, allow the "Green" check to scan the PR conversation/checks history rather than just git log, or accept that `TDD-Red-Phase` proof might be lost on squash and allow a "Green Only" pass if coverage is adequate.
- **Scope of Blocking:** The pre-commit hook blocks changes to implementation files without tests. Clarify if this applies to *all* file types (e.g., documentation `*.md`, configuration `*.json`, legacy scripts).
    - **Recommendation:** Explicitly exclude documentation and config files from the "Blocker" logic to prevent unnecessary friction.

### Architecture
- [ ] **Hook Distribution:** The dependency on `husky` or `pre-commit` is listed as "(optional)". If these tools are not mandatory, new developers cloning the repo will not have the hooks installed, rendering the enforcement mechanism null.
    - **Recommendation:** Move `husky` (or equivalent) to a **Required** dependency and include a setup step (e.g., `npm install` lifecycle script) to ensure hooks are automatically provisioned.
- [ ] **Commit Signing Conflict:** Modifying the commit message via `prepare-commit-msg` *after* the user issues the commit command can invalidate GPG/SSH signatures if the modification happens post-signing, or confuse the editor flow.
    - **Recommendation:** Verify the sequence: `prepare-commit-msg` runs -> Editor opens -> User saves -> Signing happens. Ensure the footer injection doesn't interfere with this flow, particularly for users with `commit.gpgsign = true`.

## Tier 3: SUGGESTIONS
- **Constraint:** Consider adding a "Time Limit" to the Red-Green cycle. If the Red phase was recorded 3 weeks ago, is it still valid?
- **Debt Management:** The `~/.tdd-pending-issues.json` concept is excellent. Consider adding a `tdd-gate --flush` command to manually force the upload of pending issues.
- **Effort Estimate:** Add a T-shirt size (likely XL given the cross-platform hooks and CLI work).

## Questions for Orchestrator
1. Does the team use "Squash and Merge" for Pull Requests? If so, the Commit Footer strategy for CI verification needs significant rethinking.

## Verdict
[ ] **APPROVED** - Ready to enter backlog
[x] **REVISE** - Fix Tier 1/2 issues first
[ ] **DISCUSS** - Needs Orchestrator decision