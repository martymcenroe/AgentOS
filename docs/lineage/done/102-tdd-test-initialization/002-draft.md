# TDD Test Initialization Gate

## User Story
As a developer practicing Test-Driven Development,
I want the system to enforce writing failing tests before implementation,
So that I follow the red-green-refactor cycle and build reliable, well-tested code.

## Objective
Enforce TDD discipline by gating implementation work behind verified failing tests, ensuring the red-green-refactor cycle is followed for every feature.

## UX Flow

### Scenario 1: Happy Path - TDD Workflow
1. Developer creates a new feature branch
2. Developer writes test file with tests that define expected behavior
3. System runs tests and verifies they fail (red phase)
4. System records red phase completion, unlocks implementation
5. Developer writes implementation code
6. System runs tests and verifies they pass (green phase)
7. Developer refactors with confidence
8. PR is created with full TDD audit trail

### Scenario 2: Missing Tests - Implementation Blocked
1. Developer attempts to create PR without test file
2. System detects no corresponding test file exists
3. System blocks PR creation with clear error message
4. Developer is directed to write tests first

### Scenario 3: Tests Don't Fail Initially
1. Developer writes tests that already pass (or are skipped)
2. System runs tests and detects no failures
3. System blocks implementation phase with warning: "Tests must fail first (red phase)"
4. Developer must write meaningful failing tests

### Scenario 4: Hotfix Override
1. Developer needs emergency hotfix
2. Developer uses explicit override flag: `--skip-tdd-gate`
3. System logs override with reason and timestamp
4. PR is flagged for follow-up test coverage
5. Technical debt issue is auto-created

## Requirements

### Test Existence Gate
1. Test file must exist before implementation PR is allowed
2. Test file naming convention enforced (e.g., `test_*.py`, `*.test.js`)
3. Tests must reference the feature/issue being implemented
4. Minimum test count threshold (configurable, default: 1)

### Red Phase Verification
1. All new tests must fail on first run
2. Failure reasons must be meaningful (not syntax errors)
3. System captures test failure output as baseline
4. Red phase timestamp recorded in audit trail

### Green Phase Tracking
1. Tests must pass after implementation
2. System compares red → green transition
3. No test deletions allowed between phases (without justification)
4. Coverage delta reported (new code must be covered)

### Audit Trail
1. Record red phase: timestamp, test names, failure messages
2. Record green phase: timestamp, test names, pass confirmation
3. Record refactor phase: any test modifications post-green
4. Generate TDD compliance report per PR

### Framework Support
1. Python: pytest with standard discovery
2. JavaScript: Jest with standard discovery
3. Configurable test commands per project
4. Extensible for additional frameworks

## Technical Approach
- **Pre-commit Hook:** Verify test file exists for changed implementation files
- **CI Gate:** Run tests in red-phase mode before allowing implementation merge
- **State Tracking:** Store TDD phase state in `.tdd-state.json` per branch
- **Audit Logger:** Append to `docs/reports/{IssueID}/tdd-audit.md`
- **Override System:** Explicit flag with required justification logged

## Security Considerations
- Override flag usage is logged and visible in PR
- No secrets or sensitive data in test failure output logging
- State files excluded from sensitive data scans
- Audit trail is append-only (no retroactive modifications)

## Files to Create/Modify
- `hooks/pre-commit-tdd-gate.sh` — Pre-commit hook for test existence check
- `tools/tdd-gate.py` — Main TDD enforcement CLI tool
- `tools/tdd-audit.py` — Audit trail generation and reporting
- `.tdd-config.json` — Project-specific TDD configuration
- `docs/standards/0065-tdd-enforcement.md` — Standard documenting TDD gate rules
- `CLAUDE.md` — Add TDD workflow section

## Dependencies
- Issue #62: Governance Workflow StateGraph (may integrate with state machine)

## Out of Scope (Future)
- IDE integration for real-time TDD feedback — separate tooling issue
- Automatic test generation suggestions — AI enhancement, not MVP
- Cross-repository test dependency tracking — complex, defer
- Test quality scoring beyond pass/fail — enhancement

## Acceptance Criteria
- [ ] Pre-commit hook blocks commits without corresponding test files
- [ ] `tdd-gate --verify-red` confirms tests fail and records red phase
- [ ] `tdd-gate --verify-green` confirms tests pass and records green phase
- [ ] Implementation PR is blocked if red phase not recorded
- [ ] `--skip-tdd-gate` override works with required justification
- [ ] Override creates follow-up issue for test coverage debt
- [ ] Audit trail generates at `docs/reports/{IssueID}/tdd-audit.md`
- [ ] Works with pytest: `test_*.py` pattern detection
- [ ] Works with Jest: `*.test.js` and `*.spec.js` pattern detection
- [ ] Configuration via `.tdd-config.json` for custom patterns

## Definition of Done

### Implementation
- [ ] Core TDD gate tool implemented
- [ ] Pre-commit hook implemented
- [ ] CI integration documented
- [ ] Unit tests written and passing (yes, TDD for the TDD tool)

### Tools
- [ ] `tools/tdd-gate.py` CLI documented with examples
- [ ] `tools/tdd-audit.py` reporting tool documented

### Documentation
- [ ] Standard 0065 created for TDD enforcement rules
- [ ] CLAUDE.md updated with TDD workflow section
- [ ] README updated with TDD gate setup instructions
- [ ] Add new files to `docs/0003-file-inventory.md`

### Reports (Pre-Merge Gate)
- [ ] `docs/reports/{IssueID}/implementation-report.md` created
- [ ] `docs/reports/{IssueID}/test-report.md` created

### Verification
- [ ] Run 0809 Security Audit - PASS
- [ ] Run 0817 Wiki Alignment Audit - PASS

## Testing Notes

### Force Red Phase Failure
```bash
# Create test that passes immediately (should be blocked)
echo "def test_always_passes(): assert True" > test_feature.py
tdd-gate --verify-red  # Should fail with "tests must fail first"
```

### Force Override Path
```bash
# Test hotfix override flow
tdd-gate --skip-tdd-gate --reason "P0 production outage"
# Verify: override logged, follow-up issue created
```

### Verify Audit Trail
```bash
# After full TDD cycle, check audit file contains:
# - Red phase entry with failure output
# - Green phase entry with pass confirmation
# - Timestamps for both phases
cat docs/reports/ISSUE-XX/tdd-audit.md
```