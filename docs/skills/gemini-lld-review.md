# LLD Review Assignment

## Phase 1: Onboarding (Do This First)

1. Read `docs/0000-GUIDE.md` - understand the filing system and agent protocols
2. Execute the Identity Handshake Protocol from `GEMINI.md` - this is REQUIRED before proceeding
3. Read `IMMEDIATE-PLAN.md` - current project context
4. Read `docs/6000-open-issues.md` - open work items

**STOP and confirm:** If you cannot access any of these files, or if the Identity Handshake instructions are missing from GEMINI.md, report this FIRST. Do not proceed with the review until onboarding is complete.

## Phase 2: Context Loading

1. Read `docs/0102-TEMPLATE-feature-lld.md` - the LLD template (baseline for evaluation)
2. Read `docs/0108-lld-pre-implementation-review.md` - the review checklist
3. Read `docs/0005-testing-strategy-and-protocols.md` - testing requirements

## Phase 3: LLD Review

Read the target LLD: `docs/1{IssueID}-*.md`

Evaluate against the template and review checklist using the **Priority Tier System** below.

---

## Priority Tier System

**Review depth is proportional to priority. Tier 1 = exhaustive. Tier 3 = surface-level.**

### Tier 1: BLOCKING (Must Pass)

These issues STOP implementation. Be exhaustive.

| Category | Key Questions |
| --- | --- |
| **Security** | Input validation? Injection risks? Auth/AuthZ? Secrets management? OWASP Top 10? |
| **Privacy** | PII handling? Logging toxic content? Data minimization? GDPR/CCPA? |
| **Correctness** | Does implementation match requirements? Are interfaces correct? Edge cases handled? |
| **Control** | **(CRITICAL)** Does the test strategy rely on manual verification ("Vibes")? If yes, REJECT. Tests must be automated assertions. |
| **Fail-Safe** | **(CRITICAL)** Are timeout/failure paths explicitly defined? Is "Silent Failure" prevented? (e.g., Fail Open vs. Fail Closed). |

### Tier 2: HIGH PRIORITY (Should Pass)

These issues require fixes but don't block. Be thorough.

| Category | Key Questions |
| --- | --- |
| **Testing** | All scenarios covered? Willison Protocol (tests fail on revert)? Data hygiene (no real slurs in tests)? |
| **Mocking** | **(CRITICAL)** Can this be developed on an airplane? Is a "Mock Mode" defined for external dependencies (APIs/Auth)? |
| **Data Pipeline** | Where does data come from? How does it get there? Test fixtures defined? Deployment pipeline documented? |
| **Compliance** | Chrome Web Store policies? Extension permissions minimal? Legal requirements? |

### Tier 3: SUGGESTIONS (Nice to Have)

Note these but don't block on them. Surface-level review.

| Category | Key Questions |
| --- | --- |
| **Performance** | Latency budget? Memory budget? Cold start impact? Bottlenecks identified? |
| **Maintainability** | Code structure clear? Comments adequate? Future agents can understand? |
| **Documentation** | LLD complete per template? All sections filled (or marked N/A)? |

---

## Output Format

Structure your review as follows:

```markdown
# LLD Review: docs/1{IssueID}-{title}.md

## Identity Confirmation
{Your identity handshake response}

## Review Summary
{2-3 sentence overall assessment}

## Tier 1: BLOCKING Issues
{If none, write "No blocking issues found."}

### Security
- [ ] {Issue description + recommendation}

### Privacy
- [ ] {Issue description + recommendation}

### Correctness
- [ ] {Issue description + recommendation}

### Control & Fail-Safe
- [ ] {Issue description + recommendation}

## Tier 2: HIGH PRIORITY Issues
{If none, write "No high-priority issues found."}

### Testing & Mocking
- [ ] {Issue description + recommendation}

### Data Pipeline
- [ ] {Issue description + recommendation}

### Compliance
- [ ] {Issue description + recommendation}

## Tier 3: SUGGESTIONS
{Brief bullet points only}

- {Suggestion}
- {Suggestion}

## Questions for Orchestrator
{Decisions that require human judgment}

1. {Question}
2. {Question}

## Verdict

[ ] **APPROVED** - Ready for implementation
[ ] **REVISE** - Fix Tier 1/2 issues first (list which ones)
[ ] **DISCUSS** - Needs Orchestrator decision on questions above

```

---

## Review Checklist (from 0108)

Before signing off, verify these were checked:

### Data Source & Pipeline

* [ ] Data source documented (URL, API, database, etc.)
* [ ] Data refresh strategy defined (manual, scheduled, real-time)
* [ ] Pipeline from source → test → production documented
* [ ] Separate utility needed? Issue created if yes

### Test Fixtures & Data Hygiene

* [ ] Test data sources identified (mock, generated, downloaded)
* [ ] Sensitive data handling (no real slurs, PII in test files)
* [ ] Tests can run offline (mocked dependencies)
* [ ] Willison Protocol plan documented

### Environment Matrix

* [ ] Works locally without AWS
* [ ] Works in CI without credentials
* [ ] Production paths documented

### Dependency Chain

* [ ] Blocking issues identified
* [ ] Parallel work identified
* [ ] Blocked-by relationships documented

```

---

## Notes for Orchestrator

- Gemini's review should be passed to Opus for implementation
- Tier 1 issues must be resolved before coding begins
- Tier 2 issues should be addressed in the LLD before coding
- Tier 3 issues can be noted in the Implementation Report
- If Gemini requests clarification, provide it before Opus starts

```
