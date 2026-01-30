# Test Workflow Auto-Routing

## User Story
As a developer, I want the issue workflow to automatically route clean-verdict issues to filing and auto-revise flagged issues, so that I can submit issues without manual triage overhead.

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
5. If revised issue fails again, cycle repeats (up to **Max Revision Cycles: 3**)
6. Result: Cumulative verdict history is preserved across revisions

### Scenario 3: Multiple Revision Cycles (Fail-Safe)
1. User creates an issue that needs several rounds of feedback
2. Each revision accumulates verdict history
3. If clean verdict is achieved within 3 cycles: auto-filing triggers
4. **If 3 revision cycles are exhausted without a clean verdict: workflow Fails Closed and routes to manual triage with label `needs-manual-review`**
5. Result: Full history of verdicts is visible; system never enters an infinite loop

### Scenario 4: Manual Triage Routing Verification
1. User submits an issue deliberately designed to fail verdict repeatedly
2. Verdict Engine rejects the issue on cycles 1, 2, and 3
3. On cycle 3 exhaustion, router applies label `needs-manual-review` and halts
4. Result: Issue appears in manual triage queue with full verdict history attached; no further automated revision attempts occur

## Requirements

### Auto-Routing
1. Issues with a clean verdict must be auto-filed without manual intervention
2. Issues with feedback must be auto-revised and resubmitted
3. **Maximum of 3 revision cycles before fail-closed routing to manual triage**

### Verdict History
1. Each revision must append to a cumulative verdict log
2. Verdict history must be preserved and accessible after filing

## Technical Approach
- **Verdict Engine:** Gemini (model: `gemini-1.5-flash`) evaluates issue content and returns pass/fail with optional feedback
- **Router:** Reads verdict, branches to file or revise accordingly; enforces max-retry counter
- **History Accumulator:** Appends each verdict to a running log attached to the issue context
- **Fail-Safe Guard:** Counter tracks revision cycles; at limit (3), halts loop and routes to manual triage
- **Offline/Dev Testing Strategy:** Use mocked Verdict Engine responses (stubbed pass/fail/feedback payloads) for initial routing tests to avoid live API calls during development

## Security Considerations
No sensitive data involved. This is a workflow test using only issue metadata.

## Data Processing Declaration
All issue metadata transmitted to Gemini API is non-sensitive test data. Data is processed via Google's Gemini external API (US region). No PII or proprietary content is included in test payloads.

## Budget & Cost Estimate
- **Scope:** Verification task only; no production feature implementation
- **Model:** Gemini 1.5 Flash
- **Estimated Token Usage:** ~2,000 tokens per verdict call × max 4 calls (1 initial + 3 retries) = ~8,000 tokens per test run
- **Effort Estimate:** Small (verification/QA task)

## Files to Create/Modify
- `docs/reports/{IssueID}/test-report.md` — Test report documenting all scenario outcomes
- `docs/reports/{IssueID}/implementation-report.md` — Implementation/verification summary report

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
- [ ] Labels `test`, `workflow`, `type: qa`, and `governance` are applied on filing
- [ ] Workflow halts and routes to manual triage (with `needs-manual-review` label) after 3 failed revision cycles
- [ ] Manual triage routing is verified per Scenario 4
- [ ] Mocked verdict responses can be used for offline development testing

## Definition of Done

### Verification (QA Task)
- [ ] Test report created documenting all scenario outcomes
- [ ] Routing logs verified for each scenario (clean, revision, fail-safe, manual triage)
- [ ] Mocked verdict engine tests executed successfully

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
Submit this issue and observe the workflow. Verify auto-routing by checking whether the issue is filed or a revision is requested. Inspect verdict history after at least one revision cycle to confirm accumulation. To test the fail-safe, submit an issue designed to fail verdict 3+ times and confirm it routes to manual triage with the `needs-manual-review` label. Use mocked verdict responses for repeatable offline testing.

## Original Brief
# Test Workflow Auto-Routing

Simple test issue to verify auto-routing works.

## Goal
Create a minimal GitHub issue to test:
- Auto-routing when verdict is clean
- Cumulative verdict history on revisions

## Requirements
- Should auto-file if Gemini approves
- Should auto-revise if Gemini has feedback

Labels: test, workflow, type: qa, governance