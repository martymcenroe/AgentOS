# Test Plan Reviewer - Gemini-Powered Quality Gate

## User Story
As a developer implementing features,
I want automated review of test plans before implementation,
So that test coverage gaps are identified early and quality is consistent across the team.

## Objective
Add a Gemini-powered review step that analyzes test plans for coverage completeness, edge cases, and alignment with acceptance criteria before implementation begins.

## UX Flow

### Scenario 1: Happy Path - Test Plan Passes Review
1. Developer creates test plan markdown file in `docs/reports/{IssueID}/test-plan.md`
2. Developer runs `claude skill:test-plan-review --issue 123`
3. System fetches original issue #123 and extracts acceptance criteria
4. Gemini analyzes test plan against acceptance criteria
5. Review returns PASS verdict with coverage summary
6. Audit trail logged to `docs/reports/{IssueID}/test-plan-review.md`
7. Developer proceeds to implementation

### Scenario 2: Test Plan Needs Revision
1. Developer creates test plan and runs review
2. Gemini identifies missing edge cases for file upload size limits
3. Review returns REVISE verdict with structured feedback:
   - Line 45: Missing boundary test for max file size (10MB)
   - Line 67: No test case for concurrent upload handling
   - Missing: Security test for malicious file detection
4. Developer updates test plan addressing feedback
5. Developer re-runs review, receives PASS verdict

### Scenario 3: Test Plan Missing Acceptance Criteria Coverage
1. Developer creates test plan for issue with 5 acceptance criteria
2. Review identifies only 3 of 5 criteria have corresponding test cases
3. Review returns REVISE with explicit mapping:
   - ✅ AC1: Covered by test cases 1.1, 1.2
   - ✅ AC2: Covered by test case 2.1
   - ❌ AC3: No coverage found
   - ✅ AC4: Covered by test case 3.1
   - ❌ AC5: No coverage found
4. Developer adds missing test cases

### Scenario 4: Integration with Governance Workflow
1. StateGraph workflow reaches `test_plan_created` state
2. Workflow automatically triggers test plan review
3. On PASS: Workflow transitions to `implementation_ready`
4. On REVISE: Workflow transitions to `test_plan_revision_needed`
5. State changes logged to governance audit trail

## Requirements

### Review Analysis
1. Parse test plan markdown and identify test case sections
2. Extract acceptance criteria from linked GitHub issue
3. Map test cases to acceptance criteria (coverage matrix)
4. Identify edge cases and boundary conditions not covered
5. Check for test data requirements documentation
6. Flag security testing gaps for security-relevant features
7. Flag performance testing gaps when applicable

### Structured Output
1. Coverage matrix: AC → Test Cases mapping
2. Gap analysis with specific line references
3. Categorized feedback: Coverage, Edge Cases, Test Data, Security, Performance
4. Clear PASS/REVISE verdict
5. Confidence score for the review (0-100%)

### Audit Trail
1. Log test plan version (git hash or content hash)
2. Log review timestamp and verdict
3. Log Gemini model version used
4. Store full review output in reports directory
5. Track revision history across multiple reviews

### Prompt Management
1. Hard-coded review prompt following 0701c pattern
2. Prompt versioned with semantic versioning
3. Prompt stored in `prompts/test-plan-reviewer/v1.0.0.md`
4. Version included in audit trail

## Technical Approach
- **Skill Implementation:** New skill `test-plan-review` using existing skill infrastructure
- **Gemini Integration:** Use existing Gemini client pattern from `blog-review` skill
- **Issue Fetching:** GitHub CLI (`gh issue view`) to fetch acceptance criteria
- **Markdown Parsing:** Extract test cases using heading/list structure conventions
- **StateGraph Hook:** Optional integration point in governance workflow for auto-trigger
- **Checklist Output:** Structured markdown format for easy scanning

## Security Considerations
- Test plans may contain sensitive implementation details - review output stays local
- GitHub token required for issue fetching (existing `gh` auth)
- No external data transmission beyond Gemini API call
- Audit logs stored in repo, subject to existing access controls

## Files to Create/Modify
- `skills/test-plan-review.md` — Skill definition and invocation
- `prompts/test-plan-reviewer/v1.0.0.md` — Hard-coded review prompt
- `src/skills/test-plan-review.ts` — Skill implementation
- `src/lib/test-plan-parser.ts` — Markdown parsing utilities
- `src/lib/acceptance-criteria-extractor.ts` — GitHub issue AC extraction
- `docs/reports/{IssueID}/test-plan-review.md` — Review output template
- `workflows/governance.ts` — Add optional review state transition (if integrating)

## Dependencies
- Issue #62: Governance Workflow StateGraph (for workflow integration)
- Existing Gemini API integration (from blog-review skill)

## Out of Scope (Future)
- Auto-generation of missing test cases — reviewer only identifies gaps
- Integration with test frameworks to verify test execution — separate concern
- Review of test implementation code — this reviews plans only
- Multi-model review (using multiple LLMs) — single Gemini reviewer for MVP

## Acceptance Criteria
- [ ] Test plans reviewed before implementation begins via skill invocation
- [ ] Reviewer provides structured feedback with specific line references
- [ ] Coverage matrix maps each acceptance criterion to test cases
- [ ] Supports unit test plans (function-level test cases)
- [ ] Supports integration test plans (flow-level test cases)
- [ ] Gemini review prompt hard-coded and versioned in `prompts/` directory
- [ ] Audit trail captures: test plan hash, review verdict, timestamp, prompt version
- [ ] PASS verdict requires 100% AC coverage and no critical gaps
- [ ] REVISE verdict includes actionable remediation guidance
- [ ] Optional StateGraph integration for automated triggering

## Definition of Done

### Implementation
- [ ] Core skill implemented and callable via `claude skill:test-plan-review`
- [ ] Test plan parser handles common markdown structures
- [ ] Acceptance criteria extractor works with GitHub issue format
- [ ] Unit tests written and passing for parser and extractor
- [ ] Integration test with sample test plan and mock issue

### Tools
- [ ] Skill registered in skills directory
- [ ] Document skill usage in skill help text

### Documentation
- [ ] Update wiki with test plan review workflow
- [ ] Document expected test plan format for best results
- [ ] Add prompt versioning guidelines to ADR
- [ ] Add new files to `docs/0003-file-inventory.md`

### Reports (Pre-Merge Gate)
- [ ] `docs/reports/{IssueID}/implementation-report.md` created
- [ ] `docs/reports/{IssueID}/test-report.md` created

### Verification
- [ ] Run 0817 Wiki Alignment Audit - PASS

## Testing Notes

### Testing the Skill
```bash
# Create a sample test plan
cat > docs/reports/999/test-plan.md << 'EOF'
# Test Plan: Sample Feature
## Test Cases
### 1. User Login
- 1.1 Valid credentials → success
- 1.2 Invalid password → error message
EOF

# Run review against a real issue
claude skill:test-plan-review --issue 62

# Verify audit trail created
cat docs/reports/62/test-plan-review.md
```

### Forcing Error States
- Remove acceptance criteria section from test plan → should warn about missing structure
- Reference non-existent issue number → should error gracefully with helpful message
- Provide empty test plan → should return REVISE with "no test cases found"

### Sample Prompt Structure
The review prompt should emphasize negative space:
- "What acceptance criteria have NO corresponding test cases?"
- "What boundary conditions are NOT tested?"
- "What failure modes are NOT covered?"
- "What test data setup is NOT documented?"