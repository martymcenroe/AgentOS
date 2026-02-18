# Test Plan Review Prompt

You are a senior QA engineer reviewing a test plan extracted from a Low-Level Design (LLD) document. Your goal is to ensure the test plan provides adequate coverage and uses real, executable tests.

## Pre-Flight Check

Before reviewing, verify these fundamentals:
- [ ] Test plan section exists and is not empty
- [ ] At least one test scenario is defined
- [ ] Test scenarios have names and descriptions

If any pre-flight check fails, immediately return BLOCKED with the specific issue.

## Review Criteria

### 1. Coverage Analysis (CRITICAL - 100% threshold per ADR 0207)

Calculate coverage by mapping test scenarios to requirements:

```
Coverage = (Requirements with tests / Total requirements) * 100
```

For each requirement, identify:
- Which test(s) cover it
- If no test covers it, flag as a gap

**BLOCKING if:** Coverage < 95%

### 2. Test Reality Check (CRITICAL)

Every test MUST be an executable automated test. Flag any test that:
- Delegates to "manual verification" or "human review"
- Says "verify by inspection" or "visual check"
- Has no clear assertions or expected outcomes
- Is vague like "test that it works"

**BLOCKING if:** Any test is not executable

### 3. No Human Delegation

Tests must NOT require human intervention. Flag any test that:
- Requires someone to "observe" behavior
- Needs "judgment" to determine pass/fail
- Says "ask the user" or "get feedback"

**BLOCKING if:** Any test delegates to humans

### 4. Test Type Appropriateness

Validate that test types match the functionality:
- **Unit tests:** Isolated, mock dependencies, test single functions
- **Integration tests:** Test component interactions, may use real DB
- **E2E tests:** Full user flows, minimal mocking
- **Browser tests:** Require real browser (Playwright/Selenium)
- **CLI tests:** Test command-line interfaces

**WARNING (not blocking) if:** Test types seem mismatched

### 5. Edge Cases

Check for edge case coverage:
- Empty inputs
- Invalid inputs
- Boundary conditions
- Error conditions
- Concurrent access (if applicable)

**WARNING (not blocking) if:** Edge cases seem missing

## Output Format

Provide your verdict in this exact format:

```markdown
## Pre-Flight Gate

- [x] PASSED / [ ] FAILED: Test plan exists
- [x] PASSED / [ ] FAILED: Scenarios defined
- [x] PASSED / [ ] FAILED: Scenarios have names

## Coverage Analysis

| Requirement | Test(s) | Status |
|-------------|---------|--------|
| REQ-1       | test_x  | Covered |
| REQ-2       | -       | GAP |

**Coverage: X/Y requirements (Z%)**

## Test Reality Check

| Test | Issue | Status |
|------|-------|--------|
| test_x | None | OK |
| test_y | "Manual check" | FAIL |

## Human Delegation Check

- [ ] PASSED: No human delegation found
- [ ] FAILED: [list tests that delegate to humans]

## Test Type Review

| Test | Declared Type | Appropriate | Notes |
|------|---------------|-------------|-------|
| test_x | unit | Yes | - |
| test_y | integration | No | Should be unit |

## Edge Cases

- [ ] Empty inputs covered
- [ ] Invalid inputs covered
- [ ] Error conditions covered

## Verdict

[x] **APPROVED** - Test plan is ready for implementation

OR

[x] **BLOCKED** - Test plan needs revision

## Required Changes (if BLOCKED)

1. [Specific, actionable change needed]
2. [Specific, actionable change needed]
```

## Important Notes

- Be strict on coverage (95% threshold)
- Be strict on test reality (no manual tests)
- Provide specific, actionable feedback
- Reference specific tests and requirements by name


---

# Test Plan for Issue #56

## Requirements to Cover

- REQ-1: All 5 nav tabs testable with no blank screens
- REQ-2: Tab persistence across hard refresh verified
- REQ-3: Query string preserved with hash fragments
- REQ-4: Conversation detail interactions (rate, label, back) verified
- REQ-5: Admin bulk actions (filter, select, poke, re-init) verified
- REQ-6: STARRED filter bug specifically regression-tested
- REQ-7: Auto-polling starts/stops correctly on tab navigation
- REQ-8: Tests run in CI on every PR
- REQ-9: Tests complete in under 5 minutes
- REQ-10: Flaky test rate < 5%

## Detected Test Types

- browser
- e2e
- integration
- mobile
- performance
- security
- terminal
- unit

## Required Tools

- appium
- bandit
- click.testing
- detox
- docker-compose
- locust
- pexpect
- playwright
- pytest
- pytest-benchmark
- safety
- selenium

## Mock Guidance

**Browser/UI Tests:** Real browser required, mock backend APIs for isolation
**End-to-End Tests:** Minimal mocking - test against real (sandboxed) systems
**Integration Tests:** Use test doubles for external services, real DB where possible
**Mobile App Tests:** Use emulators/simulators, mock backend services
**Performance Tests:** Test against representative data volumes
**Security Tests:** Never use real credentials, test edge cases thoroughly
**Terminal/CLI Tests:** Use CliRunner or capture stdout/stderr
**Unit Tests:** Mock external dependencies (APIs, DB, filesystem)

## Coverage Target

95%

## Test Scenarios

### test_id
- **Type:** unit
- **Requirement:** 
- **Description:** Test Description | Expected Behavior | Status
- **Mock needed:** False
- **Assertions:** 

### test_t010
- **Type:** unit
- **Requirement:** 
- **Description:** Tab navigation test | All tabs navigate without blank screens | RED
- **Mock needed:** False
- **Assertions:** 

### test_t020
- **Type:** unit
- **Requirement:** 
- **Description:** Tab persistence test | Hash and query params persist on refresh | RED
- **Mock needed:** False
- **Assertions:** 

### test_t030
- **Type:** unit
- **Requirement:** 
- **Description:** Conversation detail test | Rate, label, back button work correctly | RED
- **Mock needed:** False
- **Assertions:** 

### test_t040
- **Type:** unit
- **Requirement:** 
- **Description:** Admin bulk actions test | Filter, select, poke, re-init work | RED
- **Mock needed:** False
- **Assertions:** 

### test_t050
- **Type:** unit
- **Requirement:** 
- **Description:** STARRED filter test | STARRED chip returns STARRED results | RED
- **Mock needed:** False
- **Assertions:** 

### test_t060
- **Type:** unit
- **Requirement:** 
- **Description:** Auto-polling test | Polling starts/stops on tab change | RED
- **Mock needed:** False
- **Assertions:** 

### test_t070
- **Type:** unit
- **Requirement:** 
- **Description:** Edge cases test | Empty state, deep links, rapid switching | RED
- **Mock needed:** True
- **Assertions:** 

### test_010
- **Type:** unit
- **Requirement:** 
- **Description:** Nav to each tab | Auto | Click each tab | Content loads, no blank | Tab container visible
- **Mock needed:** False
- **Assertions:** 

### test_020
- **Type:** unit
- **Requirement:** 
- **Description:** Conversation nav returns to list | Auto | Click conv, then nav | List visible, not blank | #conv-list displayed
- **Mock needed:** False
- **Assertions:** 

### test_030
- **Type:** unit
- **Requirement:** 
- **Description:** URL hash updates | Auto | Switch tabs | Hash matches tab name | location.hash correct
- **Mock needed:** False
- **Assertions:** 

### test_040
- **Type:** unit
- **Requirement:** 
- **Description:** Refresh preserves tab | Auto | Refresh on #admin | Admin tab active | #admin in URL, admin visible
- **Mock needed:** False
- **Assertions:** 

### test_050
- **Type:** unit
- **Requirement:** 
- **Description:** Refresh preserves query | Auto | Refresh with ?key= | Key preserved | Query param intact
- **Mock needed:** False
- **Assertions:** 

### test_060
- **Type:** unit
- **Requirement:** 
- **Description:** Conv detail shows data | Auto | Click conversation | Messages, labels, rating | Detail panel populated
- **Mock needed:** False
- **Assertions:** 

### test_070
- **Type:** unit
- **Requirement:** 
- **Description:** Rate conversation | Auto | Click rating | Toast appears, rating saved | API called, toast visible
- **Mock needed:** True
- **Assertions:** 

### test_080
- **Type:** unit
- **Requirement:** 
- **Description:** Back refreshes list | Auto | Rate then back | Updated rating in list | Rating visible in row
- **Mock needed:** False
- **Assertions:** 

### test_090
- **Type:** unit
- **Requirement:** 
- **Description:** Add label | Auto | Add label to conv | Label appears | Label in DOM
- **Mock needed:** False
- **Assertions:** 

### test_100
- **Type:** unit
- **Requirement:** 
- **Description:** Remove label | Auto | Remove label | Label disappears | Label not in DOM
- **Mock needed:** False
- **Assertions:** 

### test_110
- **Type:** unit
- **Requirement:** 
- **Description:** Filter by state | Auto | Select state filter | List updates | Only matching convs
- **Mock needed:** False
- **Assertions:** 

### test_120
- **Type:** unit
- **Requirement:** 
- **Description:** Filter by label | Auto | Select label filter | List updates | Only matching convs
- **Mock needed:** False
- **Assertions:** 

### test_130
- **Type:** unit
- **Requirement:** 
- **Description:** Admin auto-load | Auto | Open admin tab | Convs load without click | Preview populated
- **Mock needed:** False
- **Assertions:** 

### test_140
- **Type:** unit
- **Requirement:** 
- **Description:** State chip toggle | Auto | Click chip | Selected style | CSS class applied
- **Mock needed:** False
- **Assertions:** 

### test_150
- **Type:** unit
- **Requirement:** 
- **Description:** STARRED filter works | Auto | STARRED chip + Load | STARRED convs shown | STARRED in results
- **Mock needed:** False
- **Assertions:** 

### test_160
- **Type:** unit
- **Requirement:** 
- **Description:** Multi-chip filter | Auto | Select multiple | AND filter applied | Intersection shown
- **Mock needed:** False
- **Assertions:** 

### test_170
- **Type:** unit
- **Requirement:** 
- **Description:** Label dropdown populated | Auto | Open admin | Labels with counts | Dropdown has options
- **Mock needed:** False
- **Assertions:** 

### test_180
- **Type:** unit
- **Requirement:** 
- **Description:** Time filter recent | Auto | 30 min filter | Recent convs only | Filtered by time
- **Mock needed:** False
- **Assertions:** 

### test_190
- **Type:** unit
- **Requirement:** 
- **Description:** Time filter blank | Auto | Clear time filter | All convs shown | No time filtering
- **Mock needed:** False
- **Assertions:** 

### test_200
- **Type:** unit
- **Requirement:** 
- **Description:** Checkbox selection | Auto | Check boxes | Bulk bar appears | Bulk bar with count
- **Mock needed:** False
- **Assertions:** 

### test_210
- **Type:** unit
- **Requirement:** 
- **Description:** Select all | Auto | Click select all | All rows selected | All checkboxes checked
- **Mock needed:** False
- **Assertions:** 

### test_220
- **Type:** unit
- **Requirement:** 
- **Description:** Poke selected | Auto | Poke action | Working state, then refresh | States updated
- **Mock needed:** False
- **Assertions:** 

### test_230
- **Type:** unit
- **Requirement:** 
- **Description:** Auto | States reset to INITIAL | States are INITIAL
- **Mock needed:** False
- **Assertions:** 

### test_240
- **Type:** unit
- **Requirement:** 
- **Description:** Polling starts after poke | Auto | Poke then wait | Requests every 3s | Network activity
- **Mock needed:** True
- **Assertions:** 

### test_250
- **Type:** unit
- **Requirement:** 
- **Description:** Polling stops on tab change | Auto | Poke, switch tab | No more requests | No network activity
- **Mock needed:** True
- **Assertions:** 

### test_260
- **Type:** unit
- **Requirement:** 
- **Description:** Polling stops on nav away | Auto | Navigate away | No background requests | No network activity
- **Mock needed:** True
- **Assertions:** 

### test_270
- **Type:** unit
- **Requirement:** 
- **Description:** Empty state message | Auto | Filter no matches | Message shown | "No matching" text
- **Mock needed:** False
- **Assertions:** 

### test_280
- **Type:** unit
- **Requirement:** 
- **Description:** Deep link conv | Auto | ?conv=123 | Detail opens | Detail visible
- **Mock needed:** False
- **Assertions:** 

### test_290
- **Type:** unit
- **Requirement:** 
- **Description:** Deep link invalid | Auto | ?conv=999 | Graceful handling | No crash, error shown
- **Mock needed:** False
- **Assertions:** 

### test_300
- **Type:** unit
- **Requirement:** 
- **Description:** Rapid tab switching | Auto | Click tabs fast | No stale content | Correct content
- **Mock needed:** True
- **Assertions:** 

## Original Test Plan Section

### 10.0 Test Plan (TDD - Complete Before Implementation)

**TDD Requirement:** Tests in this case ARE the implementation. The test specs are the deliverable.

| Test ID | Test Description | Expected Behavior | Status |
|---------|------------------|-------------------|--------|
| T010 | Tab navigation test | All tabs navigate without blank screens | RED |
| T020 | Tab persistence test | Hash and query params persist on refresh | RED |
| T030 | Conversation detail test | Rate, label, back button work correctly | RED |
| T040 | Admin bulk actions test | Filter, select, poke, re-init work | RED |
| T050 | STARRED filter test | STARRED chip returns STARRED results | RED |
| T060 | Auto-polling test | Polling starts/stops on tab change | RED |
| T070 | Edge cases test | Empty state, deep links, rapid switching | RED |

**Coverage Target:** 100% of scenarios from issue #56

**TDD Checklist:**
- [ ] All tests written before implementation - Tests ARE the implementation
- [ ] Tests currently RED (failing)
- [ ] Test IDs match scenario IDs in 10.1
- [ ] Test files created at: `tests/e2e/dashboard/`

### 10.1 Test Scenarios

| ID | Scenario | Type | Input | Expected Output | Pass Criteria |
|----|----------|------|-------|-----------------|---------------|
| 010 | Nav to each tab | Auto | Click each tab | Content loads, no blank | Tab container visible |
| 020 | Conversation nav returns to list | Auto | Click conv, then nav | List visible, not blank | #conv-list displayed |
| 030 | URL hash updates | Auto | Switch tabs | Hash matches tab name | location.hash correct |
| 040 | Refresh preserves tab | Auto | Refresh on #admin | Admin tab active | #admin in URL, admin visible |
| 050 | Refresh preserves query | Auto | Refresh with ?key= | Key preserved | Query param intact |
| 060 | Conv detail shows data | Auto | Click conversation | Messages, labels, rating | Detail panel populated |
| 070 | Rate conversation | Auto | Click rating | Toast appears, rating saved | API called, toast visible |
| 080 | Back refreshes list | Auto | Rate then back | Updated rating in list | Rating visible in row |
| 090 | Add label | Auto | Add label to conv | Label appears | Label in DOM |
| 100 | Remove label | Auto | Remove label | Label disappears | Label not in DOM |
| 110 | Filter by state | Auto | Select state filter | List updates | Only matching convs |
| 120 | Filter by label | Auto | Select label filter | List updates | Only matching convs |
| 130 | Admin auto-load | Auto | Open admin tab | Convs load without click | Preview populated |
| 140 | State chip toggle | Auto | Click chip | Selected style | CSS class applied |
| 150 | STARRED filter works | Auto | STARRED chip + Load | STARRED convs shown | STARRED in results |
| 160 | Multi-chip filter | Auto | Select multiple | AND filter applied | Intersection shown |
| 170 | Label dropdown populated | Auto | Open admin | Labels with counts | Dropdown has options |
| 180 | Time filter recent | Auto | 30 min filter | Recent convs only | Filtered by time |
| 190 | Time filter blank | Auto | Clear time filter | All convs shown | No time filtering |
| 200 | Checkbox selection | Auto | Check boxes | Bulk bar appears | Bulk bar with count |
| 210 | Select all | Auto | Click select all | All rows selected | All checkboxes checked |
| 220 | Poke selected | Auto | Poke action | Working state, then refresh | States updated |
| 230 | Re-init selected | Auto | Re-init action | States reset to INITIAL | States are INITIAL |
| 240 | Polling starts after poke | Auto | Poke then wait | Requests every 3s | Network activity |
| 250 | Polling stops on tab change | Auto | Poke, switch tab | No more requests | No network activity |
| 260 | Polling stops on nav away | Auto | Navigate away | No background requests | No network activity |
| 270 | Empty state message | Auto | Filter no matches | Message shown | "No matching" text |
| 280 | Deep link conv | Auto | ?conv=123 | Detail opens | Detail visible |
| 290 | Deep link invalid | Auto | ?conv=999 | Graceful handling | No crash, error shown |
| 300 | Rapid tab switching | Auto | Click tabs fast | No stale content | Correct content |

### 10.2 Test Commands

```bash
# Install Playwright browsers (first time)
npx playwright install

# Run all E2E tests
npx playwright test tests/e2e/dashboard/

# Run with UI mode for debugging
npx playwright test tests/e2e/dashboard/ --ui

# Run specific test file
npx playwright test tests/e2e/dashboard/navigation.spec.ts

# Run headed (see browser)
npx playwright test --headed

# Generate test report
npx playwright show-report
```

### 10.3 Manual Tests (Only If Unavoidable)

**N/A - All scenarios automated.**

The Playwright suite covers all scenarios. Visual appearance testing could be added via Playwright's screenshot comparison if needed in future.
