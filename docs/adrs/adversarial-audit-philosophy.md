# 0213 - ADR: Adversarial Audit Philosophy

**Status:** Proposed
**Date:** 2026-01-08
**Categories:** Process, Security, Compliance

## 1. Context

Our current audit procedures suffer from several weaknesses:

1. **Reactive posture** - Audits verify compliance rather than actively seeking violations
2. **Rubber-stamp tendency** - "Pass with exceptions" becomes the norm without accountability
3. **Ad-hoc exceptions** - Deviations are noted but not formally tracked or justified
4. **Confirmation bias** - Auditors look for evidence that supports passing, not evidence of failure
5. **Stale audits** - Audits that consistently pass may have become too weak to catch real issues

The core problem: **audits are designed to confirm compliance rather than discover violations.**

This is backwards. A rigorous audit should be adversarial—actively trying to disprove claims, find gaps, and surface risks. The goal is not to pass; the goal is to find problems before production does.

### The Exception Problem

Currently, an audit can "pass with exceptions" based on verbal justification:
- "We know about this XSS vector but it's low risk"
- "This permission is broader than needed but we'll fix it later"
- "The test coverage is low but the code is simple"

These exceptions accumulate without bounds, are never revisited, and become permanent technical debt that compounds risk.

## 2. Decision

**We will adopt an adversarial audit philosophy where the auditor's primary objective is to find violations, not confirm compliance.**

Core principles:
1. **Default-FAIL** - Everything fails until proven passing
2. **Disprove, don't confirm** - Seek evidence against claims, not for them
3. **No ad-hoc exceptions** - All exceptions require ADR documentation
4. **Evidence-based assertions** - Every PASS needs concrete proof
5. **Decay detection** - Consistently-passing audits trigger rigor review

## 3. Alternatives Considered

### Option A: Adversarial Audit Philosophy — SELECTED
**Description:** Transform audits from compliance verification to violation discovery. Require ADR documentation for all exceptions. Implement decay detection for stale audits.

**Pros:**
- Catches real issues before production
- Creates accountability for exceptions
- Forces honest assessment of risk
- Prevents audit theater
- Aligns with security industry best practices (red teaming)

**Cons:**
- Higher initial audit cost (more thorough)
- May surface uncomfortable truths
- Requires cultural shift in how audits are perceived

### Option B: Status Quo (Compliance Verification) — Rejected
**Description:** Continue with current approach of verifying documented requirements are met.

**Pros:**
- Familiar process
- Lower friction
- Faster audit completion

**Cons:**
- Misses real vulnerabilities
- Creates false sense of security
- Exceptions accumulate without accountability ← **Deciding factor**
- Audits become checkbox exercises

### Option C: Fully Automated Audits Only — Rejected
**Description:** Only audit what can be automated; skip manual judgment calls.

**Pros:**
- Consistent, reproducible
- No human bias
- Fast

**Cons:**
- Can't assess architectural decisions
- Misses context-dependent issues
- Many security issues require human judgment ← **Deciding factor**

## 4. Rationale

Option A was selected because:

1. **Security industry consensus** - Red teaming and adversarial testing are standard practice precisely because compliance-focused audits miss real issues
2. **Exception accountability** - ADR requirement forces explicit cost-benefit analysis and creates audit trail
3. **Sustainable rigor** - Decay detection prevents audits from becoming stale
4. **Honest risk assessment** - Better to know about problems than to assume compliance

The key insight: **an audit that always passes is either very good or very weak.** We need mechanisms to distinguish between these states.

## 5. Security Risk Analysis

| Risk | Impact | Likelihood | Severity | Mitigation |
|------|--------|------------|----------|------------|
| Audit finds critical issue late | High | Med | 6 | Adversarial approach catches issues earlier |
| Exception accumulation creates compound risk | High | High | 9 | ADR requirement with exception budget |
| Auditors confirm rather than disprove | Med | High | 6 | Explicit adversarial training and checklists |
| Stale audits miss new attack vectors | High | Med | 6 | Decay detection triggers rigor review |
| Over-aggressive audits block valid work | Med | Low | 2 | Exception ADR provides release valve |

**Residual Risk:** Adversarial audits may still miss issues that require domain expertise beyond the auditor's knowledge. Mitigated by periodic external review and framework updates.

## 6. Consequences

### Positive
- Higher confidence in audit results
- Reduced risk of production incidents
- Clear accountability for known issues
- Audit findings become actionable
- Technical debt is explicitly tracked

### Negative
- Initial audits take longer (20-50% increase)
- More findings to triage and prioritize
- Requires updating all 08xx audit procedures

### Neutral
- Shift in audit culture from "verify" to "challenge"
- More ADRs created for exceptions (increases documentation)

## 7. Implementation

### 7.1 Audit Procedure Updates

All 08xx audits must be updated to include:

**Adversarial Stance Declaration:**
```markdown
## Audit Stance

This audit operates under the Adversarial Audit Philosophy (ADR 0213).

**Objective:** Find violations, not confirm compliance.
**Default:** FAIL until proven passing.
**Evidence:** Every PASS requires concrete proof (file:line or command output).
**Exceptions:** Require ADR documentation (see Exception Registry below).
```

**Exception Registry Section:**
```markdown
## Exception Registry

| Exception | ADR | Justification | Review Date | Status |
|-----------|-----|---------------|-------------|--------|
| {what} | 02XX | {brief why} | YYYY-MM-DD | Active/Expired |

**Exception Budget:** {N} (exceeding budget = automatic FAIL)
```

**Evidence Requirements:**
```markdown
## Evidence Standards

| Finding | Required Evidence |
|---------|-------------------|
| PASS | File path + line number, or command output |
| FAIL | Reproduction steps |
| EXCEPTION | ADR number + review date |
```

### 7.2 Decay Detection

Add to 0899 Meta-Audit:

```markdown
## Decay Detection

| Audit | Consecutive Clean Runs | Last Finding | Action |
|-------|------------------------|--------------|--------|
| 0809 Security | 3 | 2025-12-01 | Review rigor |
| 0810 Privacy | 2 | 2025-12-15 | OK |

**Trigger:** 3+ consecutive runs with 0 findings → Mandatory rigor review
**Review:** Is the audit too weak, or is compliance genuinely strong?
```

### 7.3 Adversarial Techniques

Add to each security-related audit (0809, 0810, 0821):

```markdown
## Adversarial Test Cases

Actively attempt these attacks during audit:

1. **Injection:** Submit `<script>alert('xss')</script>` in all text inputs
2. **Auth bypass:** Access endpoints without authentication
3. **Data leakage:** Request another user's data
4. **Rate limit evasion:** Exceed documented limits
5. **Privilege escalation:** Attempt admin actions as regular user

**Document:** What was attempted, what succeeded, what was blocked.
```

### 7.4 Implementation Order

1. Create exception ADR template (new 0105)
2. Update 0800-audit-index.md with adversarial philosophy reference
3. Update 0899-meta-audit.md with decay detection
4. Update 0809-audit-security.md as reference implementation
5. Roll out to remaining 08xx audits

- **Related Issues:** (none yet - create after approval)
- **Related LLDs:** N/A (process change, not feature)
- **Status:** Not Started

## 8. References

- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/) - Adversarial testing methodology
- [Red Team Handbook](https://www.mitre.org/publications/technical-papers/red-team-handbook) - MITRE adversarial operations
- [Google's Bug Hunters](https://bughunters.google.com/) - Vulnerability reward program philosophy
- [ADR 0210](0210-ADR-git-worktree-isolation.md) - Example of process ADR

---

## Revision History

| Date | Author | Change |
|------|--------|--------|
| 2026-01-08 | Claude Opus 4.5 | Initial draft |
