# 0111 - Template: Manual Test Script

## Usage
Copy this template when creating a reproducible manual test procedure.
Target Location: `docs/tests/` (create if missing) or `tests/manual/`.

## Numbering Convention

**Test IDs use 3-digit numbers with gaps of 10:**
- 010, 020, 030, 040, 050...
- Gaps allow inserting new tests (e.g., 015 between 010 and 020)
- Never renumber existing tests (breaks traceability)

**Scenario naming:**
- Prefix with test ID: "010: Happy Path"
- Reference in test reports by ID

---

## Template

# Test Script: {Feature Name}

**ID:** TS-{IssueID}
**Feature Ref:** Issue #{IssueID}
**LLD Ref:** docs/1{IssueID}-{feature-name}.md
**Date Created:** {YYYY-MM-DD}
**Last Updated:** {YYYY-MM-DD}

## 1. Objective
{Brief one-sentence description of what we are verifying.}

## 2. Prerequisites
- [ ] **Environment:** {e.g., Local, Dev, Prod}
- [ ] **State:** {e.g., User logged in, Database empty}
- [ ] **Config:** {e.g., Lambda Concurrency set to 1}
- [ ] **Dependencies:** {e.g., Extension installed, allowlist configured}

## 3. Test Scenarios

### 010: {Happy Path}
| Step | Action | Expected Behavior | Check |
|:-----|:-------|:------------------|:------|
| 1 | {User Action} | {System Response} | [ ] |
| 2 | {User Action} | {System Response} | [ ] |
| 3 | {User Action} | {System Response} | [ ] |

**Result:** PASS / FAIL / BLOCKED
**Notes:** {Any observations}

---

### 020: {Edge Case}
| Step | Action | Expected Behavior | Check |
|:-----|:-------|:------------------|:------|
| 1 | {Setup condition} | {System state} | [ ] |
| 2 | {User Action} | {System Response} | [ ] |

**Result:** PASS / FAIL / BLOCKED
**Notes:** {Any observations}

---

### 030: {Error/Failure Case}
| Step | Action | Expected Behavior | Check |
|:-----|:-------|:------------------|:------|
| 1 | {Force Failure} | {UI shows Error State} | [ ] |
| 2 | {Retry} | {System recovers} | [ ] |

**Result:** PASS / FAIL / BLOCKED
**Notes:** {Any observations}

---

## 4. Post-Condition Verification
- [ ] {Database record exists/doesn't exist?}
- [ ] {Logs show expected entries?}
- [ ] {State cleaned up properly?}

## 5. Test Summary

| Test ID | Scenario | Result | Notes |
|---------|----------|--------|-------|
| 010 | {Happy Path} | PASS/FAIL | |
| 020 | {Edge Case} | PASS/FAIL | |
| 030 | {Error Case} | PASS/FAIL | |

**Overall Result:** PASS / FAIL
**Tested By:** {Name/Model}
**Date Executed:** {YYYY-MM-DD}

## 6. Notes / Observations
- {Log any oddities, unexpected behavior, or improvement suggestions}
- {Reference related issues if bugs found}
