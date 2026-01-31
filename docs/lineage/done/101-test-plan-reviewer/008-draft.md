# Test Plan Reviewer - Gemini-Powered Quality Gate

## User Story
As a developer implementing features,
I want automated review of test plans before implementation,
So that test coverage gaps are identified early and quality is consistent across the team.

## Objective
Add a Gemini-powered review step that analyzes test plans for coverage completeness, edge cases, and alignment with acceptance criteria before implementation begins.

## Labels
`tooling`, `gen-ai`, `quality-gate`

## Effort Estimate
**T-shirt Size: M** (parser + API integration + testing)

## Budget & Model Selection
- **Model:** Gemini 1.5 Pro
- **Estimated Cost:** < $0.05 per review invocation
- **Monthly Cap:** $10/month maximum
- **Rationale:** Pro model provides sufficient reasoning for coverage analysis while remaining cost-effective

## Data Classification & Privacy Policy
- **Data Classification:** Test plans are classified as **Internal/Confidential** — they may contain business logic and implementation details
- **API Endpoint:** Standard Gemini 1.5 Pro API is approved for this use case per project policy
- **Data Retention:** Gemini API operates under Google's standard data handling terms; no customer data is used for training
- **IP Consideration:** Test plans describe internal logic; users are warned via `--dry-run` flag to inspect payloads before submission
- **Policy Reference:** Approved under internal AI tooling policy for non-PII, non-secret development artifacts

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
5. On API Failure: Workflow **Fails Closed** — blocks transition, logs error, alerts developer
6. State changes logged to governance audit trail

### Scenario 5: Gemini API Unavailable
1. Developer or workflow triggers test plan review
2. Gemini API returns 500 error, rate limit, or timeout
3. System retries up to 3 times with exponential backoff
4. On persistent failure: Returns ERROR verdict (not PASS or REVISE)
5. Workflow integration: **Fails Closed** — transition blocked, manual intervention required
6. Error logged with timestamp, error code, and retry count
7. Developer notified: "Review unavailable. Retry later or request manual review bypass."

### Scenario 6: Test Plan Exceeds Token Limits
1. Developer creates large test plan exceeding model context window
2. System detects token count exceeds limit during preprocessing
3. System truncates test plan with warning, preserving:
   - All acceptance criteria mappings
   - First N test cases (prioritized by section order)
4. Review proceeds with truncated content
5. Output includes warning: "Test plan truncated. Review covers first {N} test cases only."
6. Developer advised to split into multiple focused test plans

### Scenario 7: Dry Run - Payload Inspection
1. Developer runs `claude skill:test-plan-review --issue 123 --dry-run`
2. System performs all preprocessing (parsing, sanitization, secrets scan)
3. System outputs the exact prompt/payload that would be sent to Gemini API
4. No API call is made; no cost incurred
5. Developer inspects payload for sensitive content before actual submission
6. Developer runs without `--dry-run` flag to submit

### Scenario 8: Secrets Detected in Test Plan
1. Developer runs test plan review
2. Pre-flight secrets scan detects potential API key pattern in test plan
3. System blocks API submission and returns BLOCKED verdict
4. Output specifies: "Potential secret detected at line 42: `API_KEY=sk-...`"
5. Developer removes secret from test plan
6. Developer re-runs review successfully

## Requirements

### Pre-Flight Security Checks
1. Scan test plan content for secrets/credentials before API submission
2. Regex patterns for: API keys, passwords, tokens, private keys, connection strings
3. On detection: Block submission, return BLOCKED verdict with line reference
4. Provide `--skip-secrets-scan` flag for false positive override (requires explicit opt-in)
5. Log all blocked submissions with detected pattern type (not the secret itself)

### Review Analysis
1. Parse test plan markdown and identify test case sections
2. Sanitize markdown input: strip executable HTML, script tags, and potentially harmful content before processing
3. Extract acceptance criteria from linked GitHub issue
4. Map test cases to acceptance criteria (coverage matrix)
5. Identify edge cases and boundary conditions not covered
6. Check for test data requirements documentation
7. Flag security testing gaps for security-relevant features
8. Flag performance testing gaps when applicable

### Structured Output
1. Coverage matrix: AC → Test Cases mapping
2. Gap analysis with specific line references
3. Categorized feedback: Coverage, Edge Cases, Test Data, Security, Performance
4. Clear PASS/REVISE/ERROR/BLOCKED verdict
5. Confidence score for the review (0-100%)

### Fail-Safe Behavior
1. API errors: Retry 3x with exponential backoff (1s, 2s, 4s)
2. Persistent API failure: Return ERROR verdict, never auto-PASS
3. Workflow integration: **Fail Closed** — block state transitions on ERROR
4. Rate limiting: Queue requests, surface wait time to user
5. All failures logged with full context for debugging

### Token Limit Handling
1. Pre-check test plan token count before API submission
2. If exceeding limit: Truncate with preserved structure and clear warning
3. Truncation preserves: section headers, AC references, first N complete test cases
4. Warning included in output specifying what was truncated
5. Suggest splitting large test plans into focused sub-plans
6. Truncation limit N configurable via `TEST_PLAN_REVIEW_MAX_CASES` environment variable (default: 50)

### Audit Trail
1. Log test plan version (git hash or content hash)
2. Log review timestamp and verdict
3. Log Gemini model version used
4. Store full review output in reports directory
5. Track revision history across multiple reviews
6. Log any truncation applied due to token limits
7. Log API errors, retry attempts, and resolution
8. Log secrets scan blocks (pattern type only, not content)

### Prompt Management
1. Hard-coded review prompt following 0701c pattern
2. Prompt versioned with semantic versioning
3. Prompt stored in `prompts/test-plan-reviewer/v1.0.0.md`
4. Version included in audit trail

### Offline Development Support
1. Capture and store golden JSON response from Gemini 1.5 Pro as static fixture
2. Store fixture in `tests/fixtures/gemini-test-plan-response.json`
3. Enable mock mode via `TEST_PLAN_REVIEW_MOCK=true` environment variable
4. Mock mode uses fixture for parsing/reporting development without API costs

## Technical Approach
- **Skill Implementation:** New skill `test-plan-review` using existing skill infrastructure
- **Gemini Integration:** Use existing Gemini client pattern from `blog-review` skill; target Gemini 1.5 Pro
- **Issue Fetching:** GitHub CLI (`gh issue view`) to fetch acceptance criteria
- **Markdown Parsing:** Extract test cases using heading/list structure conventions
- **Markdown Sanitization:** Strip HTML tags, script elements, and executable content before processing using `isomorphic-dompurify` library (works in Node.js without jsdom dependency)
- **Secrets Scanning:** Pre-flight regex scan for common secret patterns before API submission
- **Token Management:** Pre-flight token count check with graceful truncation strategy; configurable limit
- **Error Handling:** Retry logic with exponential backoff; fail-closed for workflow integration
- **StateGraph Hook:** Optional integration point in governance workflow for auto-trigger
- **Checklist Output:** Structured markdown format for easy scanning
- **Offline Testing:** Golden fixture captured from production API response for cost-free TDD iteration
- **Dry Run Mode:** `--dry-run` flag outputs payload without API call for inspection

## Security Considerations
- Test plans may contain sensitive implementation details - review output stays local
- **Secrets Scanning:** Pre-flight scan blocks submission if API keys, passwords, or credentials detected
- **Dry Run:** `--dry-run` flag allows payload inspection before any API transmission
- GitHub token required for issue fetching (existing `gh` auth)
- No external data transmission beyond Gemini API call
- Audit logs stored in repo, subject to existing access controls
- Markdown input sanitized to prevent injection of executable content
- `isomorphic-dompurify` library used for sanitization (MIT license, verified compliant)

## Files to Create/Modify
- `skills/test-plan-review.md` — Skill definition and invocation
- `prompts/test-plan-reviewer/v1.0.0.md` — Hard-coded review prompt
- `src/skills/test-plan-review.ts` — Skill implementation
- `src/lib/test-plan-parser.ts` — Markdown parsing utilities with sanitization
- `src/lib/markdown-sanitizer.ts` — HTML/script stripping utility using `isomorphic-dompurify`
- `src/lib/secrets-scanner.ts` — Pre-flight secrets/credential detection
- `src/lib/acceptance-criteria-extractor.ts` — GitHub issue AC extraction
- `src/lib/token-counter.ts` — Token counting and truncation utilities
- `tests/fixtures/gemini-test-plan-response.json` — Golden API response fixture for offline development
- `docs/reports/{IssueID}/test-plan-review.md` — Review output template
- `workflows/governance.ts` — Add optional review state transition (if integrating)

## Dependencies
- Issue #62: Governance Workflow StateGraph (for workflow integration) — **Note:** Skill can be built in parallel; only workflow integration requires #62 completion
- Existing Gemini API integration (from blog-review skill)
- `isomorphic-dompurify` npm package for markdown sanitization (MIT license) — works in Node.js without jsdom

## Out of Scope (Future)
- Auto-generation of missing test cases — reviewer only identifies gaps
- Integration with test frameworks to verify test execution — separate concern
- Review of test implementation code — this reviews plans only
- Multi-model review (using multiple LLMs) — single Gemini reviewer for MVP
- Enterprise/Vertex AI endpoint — standard API approved for current use case

## Acceptance Criteria
- [ ] Test plans reviewed before implementation begins via skill invocation
- [ ] Reviewer provides structured feedback with specific line references
- [ ] Coverage matrix maps each acceptance criterion to test cases
- [ ] Supports unit test plans (function-level test cases)
- [ ] Supports integration test plans (flow-level test cases)
- [ ] Gemini 1.5 Pro review prompt hard-coded and versioned in `prompts/` directory
- [ ] Audit trail captures: test plan hash, review verdict, timestamp, prompt version
- [ ] PASS verdict requires 100% AC coverage and no critical gaps
- [ ] REVISE verdict includes actionable remediation guidance
- [ ] ERROR verdict returned on persistent API failures (never silent PASS)
- [ ] BLOCKED verdict returned when secrets detected in test plan
- [ ] Graceful handling of test plans exceeding token limits with truncation warning
- [ ] Markdown input sanitized before processing (no executable HTML/scripts)
- [ ] Pre-flight secrets scan blocks API submission when credentials detected
- [ ] API failures trigger retry with exponential backoff (3 attempts max)
- [ ] Workflow integration fails closed on ERROR verdict
- [ ] Optional StateGraph integration for automated triggering
- [ ] Golden fixture available for offline development and testing
- [ ] `--dry-run` flag outputs payload without API call for inspection

## Definition of Done

### Implementation
- [ ] Core skill implemented and callable via `claude skill:test-plan-review`
- [ ] Test plan parser handles common markdown structures
- [ ] Markdown sanitizer strips HTML/script tags before processing using `isomorphic-dompurify`
- [ ] Secrets scanner detects API keys, passwords, tokens before API submission
- [ ] Token counter with truncation logic implemented (configurable limit)
- [ ] Acceptance criteria extractor works with GitHub issue format
- [ ] Retry logic with exponential backoff for API errors
- [ ] `--dry-run` flag implemented for payload inspection
- [ ] Golden fixture captured and stored in `tests/fixtures/gemini-test-plan-response.json`
- [ ] Unit tests written and passing for parser, sanitizer, secrets scanner, and extractor
- [ ] Integration test with sample test plan and mock issue
- [ ] Error handling tests for API failure scenarios
- [ ] Secrets detection tests for common credential patterns
- [ ] Offline mock mode tests using golden fixture

### Tools
- [ ] Skill registered in skills directory
- [ ] Document skill usage in skill help text

### Documentation
- [ ] Update wiki with test plan review workflow
- [ ] Document expected test plan format for best results
- [ ] Document fail-safe behavior and ERROR verdict handling
- [ ] Document BLOCKED verdict and secrets scanning behavior
- [ ] Document `--dry-run` usage for payload inspection
- [ ] Document offline development workflow using golden fixture
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

### Dry Run Mode
```bash
# Inspect payload without API call
claude skill:test-plan-review --issue 62 --dry-run

# Review output, then submit for real
claude skill:test-plan-review --issue 62
```

### Offline Development Mode
```bash
# Enable mock mode to use golden fixture (no API calls)
export TEST_PLAN_REVIEW_MOCK=true
claude skill:test-plan-review --issue 62

# Configure truncation limit
export TEST_PLAN_REVIEW_MAX_CASES=25
```

### Forcing Error States
- Remove acceptance criteria section from test plan → should warn about missing structure
- Reference non-existent issue number → should error gracefully with helpful message
- Provide empty test plan → should return REVISE with "no test cases found"
- Disconnect network during API call → should retry 3x then return ERROR verdict
- Provide test plan with >100K tokens → should truncate with warning and proceed
- Include `<script>alert('xss')</script>` in test plan → should be stripped before processing
- Include `API_KEY=sk-1234567890abcdef` in test plan → should return BLOCKED verdict
- Include `password: "mysecret123"` in test plan → should return BLOCKED verdict

### Sample Prompt Structure
The review prompt should emphasize negative space:
- "What acceptance criteria have NO corresponding test cases?"
- "What boundary conditions are NOT tested?"
- "What failure modes are NOT covered?"
- "What test data setup is NOT documented?"

## Original Brief
# Test Plan Reviewer

## Problem

Test plans are created manually without automated review. Quality varies significantly:
- Some test plans miss edge cases
- Coverage of acceptance criteria is inconsistent
- Test data requirements are often undocumented
- No structured feedback loop before implementation

## Proposed Solution

Add a Gemini-powered review step for test plans that checks:
- Coverage of acceptance criteria from the source issue
- Edge case identification and boundary testing
- Test data requirements and setup needs
- Security testing considerations
- Performance testing requirements (if applicable)

The reviewer would:
1. Parse the test plan markdown
2. Cross-reference against the original issue's acceptance criteria
3. Generate structured feedback on gaps
4. Provide a PASS/REVISE verdict

## Acceptance Criteria

- [ ] Test plans reviewed before implementation begins
- [ ] Reviewer provides structured feedback with specific line references
- [ ] Integration with existing governance workflow
- [ ] Supports both unit test plans and integration test plans
- [ ] Gemini review prompt follows 0701c pattern (hard-coded, versioned)
- [ ] Audit trail captures test plan versions and review verdicts

## Technical Considerations

- Could extend existing issue workflow with new review step
- Or could be a separate workflow triggered manually
- Prompt should emphasize: "What scenarios are NOT covered?"
- Consider using checklist format for reviewer output

## Related

- Issue #62: Governance Workflow StateGraph
- Issue #101: Governance Workflow Monitoring & E2E Testing