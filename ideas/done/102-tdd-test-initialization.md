# TDD Test Initialization

## Problem

Developers often skip writing tests first, violating Test-Driven Development (TDD) principles:
- Implementation code is written before tests
- Tests are added as an afterthought (if at all)
- Test coverage is inconsistent
- Red-green-refactor cycle is not enforced

Without enforcement, the "red phase" (failing tests) never happens, which means:
- Requirements aren't validated before coding
- Edge cases are discovered late
- Refactoring is risky due to poor test coverage

## Proposed Solution

Require failing tests to exist before implementation code is written:

### Phase 1: Test Existence Gate
1. Developer creates test file with failing tests
2. System verifies tests exist for the issue/feature
3. Implementation PR cannot be created until test file exists

### Phase 2: Red Phase Verification
1. Tests must fail initially (red phase)
2. System runs tests and verifies they fail with expected reasons
3. Only then can implementation begin

### Phase 3: Green Phase Tracking
1. After implementation, tests must pass (green phase)
2. System tracks transition from red to green
3. Audit trail captures the TDD cycle

## Acceptance Criteria

- [ ] Pre-commit hook verifies test existence for new features
- [ ] Tests must fail initially (red phase gate)
- [ ] Implementation blocked until red phase passes
- [ ] Audit trail captures red/green/refactor cycle
- [ ] Works with pytest (Python) and Jest (JavaScript)
- [ ] Escape hatch for hotfixes with explicit override

## Technical Considerations

- Could integrate with existing worktree isolation rules
- Hook into PR creation workflow
- May need project-specific test naming conventions
- Consider test coverage thresholds (e.g., 80% minimum)

## Related

- CLAUDE.md: Worktree isolation rules
- Issue #62: Governance Workflow StateGraph
- Standard 0008: Documentation convention (test docs)
