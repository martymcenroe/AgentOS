# Test Workflow End-to-End Issue Creation

## Objective
Verify that the issue creation workflow executes without preamble, displays Gemini verdicts in terminal, shows progress indicators with timestamps, and provides visibility into all LLM calls.

## UX Flow

### Scenario 1: Successful Workflow Execution
1. User initiates issue creation workflow with test brief
2. Claude generates draft markdown starting with `#` title, no preamble text
3. System displays Gemini verdict in terminal with timestamp
4. System shows progress indicators with timestamps for each LLM call
5. Result: Complete issue created with all workflow improvements verified

### Scenario 2: Workflow Monitoring
1. User observes terminal output during execution
2. Each LLM call displays timestamp and duration
3. Progress indicators appear within 5 seconds of each step
4. Result: User has complete visibility into workflow execution

## Requirements

### Output Format
1. Draft must start with `#` title on first line
2. No preamble text like "I'll create" or "Here is"
3. Clean markdown following template structure

### Terminal Feedback
1. Gemini verdict must print to terminal/console
2. Verdict must be clearly labeled and readable
3. Verdict timing must be visible to user

### Progress Tracking
1. Every LLM call must show timestamp when initiated
2. Every LLM call must show duration when completed
3. Progress indicators must appear within 5 seconds of any action
4. User never waits more than 5 seconds without feedback

## Technical Approach
- **Claude Output:** Configure to output only markdown content, suppress system messages
- **Gemini Integration:** Capture verdict and pipe to stdout with timestamp prefix
- **Progress Indicators:** Add timestamp logging wrapper around all LLM API calls
- **Node Execution:** Add logging for each workflow step with elapsed time

## Security Considerations
This is a workflow testing issue with no security implications. No sensitive data is processed, no permissions are modified, and no external systems are accessed beyond standard LLM API calls.

## Files to Create/Modify
- `workflow/issue-creation.js` — Add timestamp logging to LLM calls
- `workflow/claude-config.js` — Configure output suppression for preamble
- `workflow/gemini-integration.js` — Add terminal output for verdict
- `workflow/progress-logger.js` — New utility for timestamped progress tracking

## Dependencies
None - this is a standalone workflow verification issue.

## Out of Scope (Future)
- Persistent logging to file — this issue focuses on terminal output only
- Configurable verbosity levels — defer to future enhancement
- Progress bar UI — text-based indicators sufficient for MVP

## Acceptance Criteria
- [ ] Draft output starts with `#` title with no preceding text
- [ ] Gemini verdict appears in terminal/console output
- [ ] Each LLM call displays timestamp when initiated (format: `YYYY-MM-DD HH:MM:SS`)
- [ ] Each LLM call displays duration when completed (format: `Completed in X.XXs`)
- [ ] No gap longer than 5 seconds exists without user feedback
- [ ] All workflow steps show execution visibility

## Definition of Done

### Implementation
- [ ] Core workflow improvements implemented
- [ ] Unit tests written and passing for logging utilities

### Tools
- [ ] No CLI tools required for this issue

### Documentation
- [ ] Update workflow documentation with new logging behavior
- [ ] Add example terminal output to workflow docs
- [ ] Document timestamp format standards

### Reports (Pre-Merge Gate)
- [ ] `docs/reports/test-workflow/implementation-report.md` created
- [ ] `docs/reports/test-workflow/test-report.md` created

### Verification
- [ ] Run workflow end-to-end and verify terminal output
- [ ] Verify timestamps are accurate within 1 second
- [ ] Verify no preamble text appears in draft output

## Testing Notes
To test this workflow:
1. Run issue creation workflow with this brief as input
2. Monitor terminal output for Gemini verdict display
3. Verify timestamps appear for each LLM call
4. Check that draft starts with `#` and has no preamble
5. Measure gaps between progress indicators (should be <5s)
6. Save terminal output for verification in test report

Force error state testing:
- Simulate slow LLM response (>10s) to verify progress indicators still appear
- Test with network latency to ensure timeout handling shows progress