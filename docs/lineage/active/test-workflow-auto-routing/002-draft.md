# Test Workflow Auto-Routing

## Objective
Verify that the auto-routing workflow correctly handles clean verdicts and accumulates verdict history across revisions.

## UX Flow

### Scenario 1: Clean Verdict Auto-Route
1. User creates a GitHub issue via `gh issue create`
2. Gemini reviews the issue and returns a clean verdict
3. Result: Issue is automatically filed with appropriate labels

### Scenario 2: Revision Requested
1. User creates a GitHub issue
2. Gemini reviews and provides feedback
3. System auto-revises the issue based on feedback
4. Gemini re-reviews the revised issue
5. Result: Cumulative verdict history is preserved across revisions

### Scenario 3: Multiple Revision Cycles
1. User creates an issue that needs several rounds of feedback
2. Each revision accumulates verdict history
3. Result: Full history of verdicts is visible, final clean verdict triggers auto-filing

## Requirements

### Auto-Routing
1. Issues with a clean verdict must be auto-filed without manual intervention
2. Issues with feedback must be auto-revised and resubmitted

### Verdict History
1. Each revision must append to a cumulative verdict log
2. Verdict history must be preserved and accessible after filing

## Technical Approach
- **Verdict Engine:** Gemini evaluates issue content and returns pass/fail with optional feedback
- **Router:** Reads verdict, branches to file or revise accordingly
- **History Accumulator:** Appends each verdict to a running log attached to the issue context

## Security Considerations
No sensitive data involved. This is a workflow test using only issue metadata.

## Files to Create/Modify
- None — this is a workflow verification issue only

## Dependencies
- None

## Out of Scope (Future)
- Multi-reviewer verdict aggregation — deferred to future issue
- Custom routing rules per label — nice-to-have, not MVP

## Acceptance Criteria
- [ ] Issue with clean verdict is auto-filed without manual intervention
- [ ] Issue with feedback triggers auto-revision
- [ ] Revised issue is resubmitted for verdict
- [ ] Cumulative verdict history is preserved across all revision cycles
- [ ] Labels `test` and `workflow` are applied on filing

## Definition of Done

### Implementation
- [ ] Core feature implemented
- [ ] Unit tests written and passing

### Tools
- [ ] Update/create relevant CLI tools in `tools/` (if applicable)
- [ ] Document tool usage

### Documentation
- [ ] Update wiki pages affected by this change
- [ ] Update README.md if user-facing
- [ ] Update relevant ADRs or create new ones
- [ ] Add new files to `docs/0003-file-inventory.md`

### Reports (Pre-Merge Gate)
- [ ] `docs/reports/{IssueID}/implementation-report.md` created
- [ ] `docs/reports/{IssueID}/test-report.md` created

### Verification
- [ ] Run 0817 Wiki Alignment Audit - PASS (if wiki updated)

## Testing Notes
Submit this issue and observe the workflow. Verify auto-routing by checking whether the issue is filed or a revision is requested. Inspect verdict history after at least one revision cycle to confirm accumulation.