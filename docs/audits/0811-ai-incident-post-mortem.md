# 0823 - Audit: AI Incident Post-Mortem

## 1. Purpose

Structured process for analyzing AI system failures, near-misses, and unexpected behaviors. Captures lessons learned, identifies root causes, and drives systemic improvements. Based on NIST AI RMF GOVERN and MANAGE functions, adapted from SRE incident management practices.

**Aletheia Context:**
- AI-generated etymology errors
- Guardrail failures (false positives/negatives)
- Prompt injection attempts
- Claude Code workflow incidents
- Production outages affecting AI components

---

## 2. Incident Classification

### 2.1 Severity Levels

| Severity | Definition | Examples | Response Time |
|----------|------------|----------|---------------|
| **SEV-1** | Critical - safety or security breach | User data exposed, harmful content generated | Immediate |
| **SEV-2** | High - significant user impact | Service down, major feature broken | < 4 hours |
| **SEV-3** | Medium - degraded experience | Slow responses, minor errors | < 24 hours |
| **SEV-4** | Low - minor issues | Cosmetic bugs, edge cases | < 1 week |

### 2.1.1 Automatic Severity Indicators (MANDATORY)

**Agent classification is a SUGGESTION. Human confirms final severity.**

The following keywords/patterns trigger AUTOMATIC severity floors:

| Trigger | Auto-Minimum | Rationale |
|---------|--------------|-----------|
| "user data", "PII", "credentials", "password" | SEV-1 | Privacy breach |
| "security", "breach", "exploit", "injection" | SEV-1 | Security incident |
| "harmful", "offensive", "slur", "hate" | SEV-1 | Safety failure |
| "data loss", "corruption", "deleted" | SEV-1 | Data integrity |
| "service down", "outage", "unavailable" | SEV-2 | Availability |
| "bypass", "circumvent", "evade" | SEV-2 | Control failure |

**Classification Override Rules:**

1. Agent proposes severity based on assessment
2. If any auto-trigger keyword is present, severity CANNOT be lower than the trigger floor
3. Human can escalate (SEV-3 → SEV-1) but agent cannot downgrade below auto-floor
4. All severity classifications must be documented with rationale

**Example:**
- Incident: "Prompt injection bypassed guardrail"
- Keyword triggers: "injection" (SEV-1), "bypass" (SEV-2)
- Auto-floor: SEV-1 (highest trigger wins)
- Agent cannot classify this as SEV-3 or SEV-4

### 2.2 AI-Specific Incident Types

| Type | Description | Typical Severity |
|------|-------------|------------------|
| **Safety Failure** | Harmful content generated/passed | SEV-1 |
| **Privacy Breach** | User data exposed/logged | SEV-1 |
| **Model Error** | Incorrect/nonsensical output | SEV-3 |
| **Guardrail Bypass** | Content filter circumvented | SEV-2 |
| **Prompt Injection** | Malicious prompt succeeded | SEV-2 |
| **Availability** | AI service unavailable | SEV-2/3 |
| **Performance** | Slow or timeout responses | SEV-3 |
| **Agent Misbehavior** | Claude Code unexpected action | SEV-2/3 |

---

## 3. Incident Response Process

### 3.1 Detection

| Detection Source | Response |
|------------------|----------|
| User report (GitHub issue) | Triage immediately |
| CloudWatch alert | Investigate within SLA |
| Store review | Assess and respond |
| Self-discovery | Document and prioritize |
| Security scan | Escalate if needed |

### 3.2 Immediate Response

| Step | Action | Owner |
|------|--------|-------|
| 1 | Acknowledge incident | Developer |
| 2 | Assess severity | Developer |
| 3 | Mitigate if possible | Developer |
| 4 | Communicate status | Developer |
| 5 | Preserve evidence | Developer |

### 3.3 Evidence Preservation

| Evidence Type | How to Preserve |
|---------------|-----------------|
| User input | Screenshot, log excerpt |
| AI output | Screenshot, log excerpt |
| CloudWatch logs | Export relevant timeframe |
| Git state | Note commit hash |
| Configuration | Capture current settings |

---

## 4. Post-Mortem Template

### 4.1 Incident Summary

```markdown
## Incident: [Title]

**Date:** YYYY-MM-DD
**Severity:** SEV-X
**Duration:** X hours/minutes
**Impact:** [Who/what was affected]
**Status:** Resolved / Mitigated / Ongoing

### Timeline

| Time | Event |
|------|-------|
| HH:MM | [First indication] |
| HH:MM | [Detection] |
| HH:MM | [Response action] |
| HH:MM | [Resolution] |

### Summary

[2-3 sentence summary of what happened]
```

### 4.2 Root Cause Analysis

```markdown
## Root Cause Analysis

### What Happened
[Detailed technical description]

### Why It Happened
[Chain of causation - use 5 Whys if helpful]

### Contributing Factors
- [ ] Code defect
- [ ] Configuration error
- [ ] Model behavior
- [ ] Prompt engineering gap
- [ ] Edge case not handled
- [ ] External dependency
- [ ] Human error
- [ ] Process gap

### AI-Specific Factors
- [ ] Training data issue (Anthropic)
- [ ] Model version change
- [ ] Prompt injection
- [ ] Adversarial input
- [ ] Context window issue
- [ ] Guardrail gap
- [ ] Hallucination
```

### 4.3 Impact Assessment

```markdown
## Impact

### User Impact
- Users affected: [Number or percentage]
- User experience: [Description]
- Data impact: [None / Exposed / Corrupted]

### Business Impact
- Reputation: [None / Minor / Significant]
- Trust: [None / Minor / Significant]
- Store rating: [No impact / Risk]

### Technical Impact
- Systems affected: [List]
- Data integrity: [Intact / Compromised]
- Security: [No breach / Potential / Confirmed]
```

### 4.4 Action Items

```markdown
## Action Items

| ID | Action | Owner | Priority | Due | Status |
|----|--------|-------|----------|-----|--------|
| 1 | [Immediate fix] | | P1 | | |
| 2 | [Prevent recurrence] | | P2 | | |
| 3 | [Improve detection] | | P3 | | |
| 4 | [Update documentation] | | P3 | | |
| 5 | [Add test coverage] | | P2 | | |
```

### 4.5 Lessons Learned

```markdown
## Lessons Learned

### What Went Well
- [Detection, response, communication, etc.]

### What Could Be Improved
- [Gaps identified]

### Process Changes
- [New procedures, checks, audits]

### Documentation Updates
- [LLDs, audits, README, etc.]
```

---

## 5. AI-Specific Analysis

### 5.1 Model Behavior Analysis

| Question | Answer |
|----------|--------|
| Was model output as expected? | |
| Did prompt produce intended behavior? | |
| Was this a known model limitation? | |
| Could prompt engineering fix this? | |
| Is this a pattern or one-off? | |

### 5.2 Guardrail Effectiveness

| Guardrail | Triggered? | Correct? | Gap? |
|-----------|------------|----------|------|
| Selection check | | | |
| Denylist filter | | | |
| Semantic guardrail | | | |
| Output transform | | | |

### 5.3 Adversarial Analysis

| Question | Answer |
|----------|--------|
| Was this an attack? | |
| What technique was used? | |
| How did it bypass controls? | |
| What's the fix? | |

---

## 6. Incident Categories & Response Playbooks

### 6.1 Harmful Content Generated

**Immediate:**
1. Document exact input and output
2. Check if stored anywhere
3. Assess user exposure

**Analysis:**
- Which guardrail should have caught this?
- Why didn't it?
- Is this a pattern or edge case?

**Remediation:**
- Update denylist if term-based
- Update semantic guardrail if category-based
- Add specific test case
- Run 0809 Security Audit

### 6.2 Prompt Injection Succeeded

**Immediate:**
1. Document the injection payload
2. Assess what was exposed/affected
3. Block pattern if possible

**Analysis:**
- How did injection reach the model?
- What defenses were bypassed?
- What was the impact?

**Remediation:**
- Add to 0809 §3 test cases
- Update XML wrapping if needed
- Consider additional sanitization
- Update ASVS compliance

### 6.3 Service Unavailability

**Immediate:**
1. Check AWS status
2. Check Bedrock status
3. Review CloudWatch errors

**Analysis:**
- Lambda cold start?
- Bedrock throttling?
- Configuration issue?

**Remediation:**
- Improve error handling
- Add retry logic if missing
- Update monitoring/alerting

### 6.4 Claude Code Incident

**Immediate:**
1. Stop agent if running
2. Review session log
3. Assess damage (git diff)

**Analysis:**
- What unexpected action was taken?
- Was it within permissions?
- Why didn't escalation trigger?

**Remediation:**
- Update .claude/settings.local.json
- Update CLAUDE.md
- Run 0821 Agentic AI Governance Audit

---

## 7. Metrics & Trends

### 7.1 Incident Tracking

| Metric | Tracking | Target |
|--------|----------|--------|
| Incidents per month | Log | < 5 |
| Mean time to detect | Log | < 1 hour |
| Mean time to resolve | Log | < 4 hours |
| Repeat incidents | Track | 0 |
| Post-mortems completed | Track | 100% for SEV-1/2 |

### 7.2 Trend Analysis

| Period | SEV-1 | SEV-2 | SEV-3 | SEV-4 | Total |
|--------|-------|-------|-------|-------|-------|
| Q1 2026 | | | | | |
| Q2 2026 | | | | | |
| Q3 2026 | | | | | |
| Q4 2026 | | | | | |

### 7.3 Category Distribution

| Category | Count | Trend |
|----------|-------|-------|
| Safety failures | | |
| Model errors | | |
| Guardrail bypasses | | |
| Availability | | |
| Agent incidents | | |

---

## 8. Post-Mortem Quality Checklist

### 8.1 Completeness

| Check | Required For | Present? |
|-------|--------------|----------|
| Timeline | All | |
| Root cause identified | All | |
| Contributing factors | SEV-1/2 | |
| Impact assessment | All | |
| Action items | All | |
| Lessons learned | SEV-1/2 | |
| Owner assigned to actions | All | |

### 8.2 Quality

| Check | Requirement |
|-------|-------------|
| Blameless | Focus on systems, not individuals |
| Specific | Concrete details, not vague |
| Actionable | Clear next steps |
| Complete | All relevant factors covered |
| Shared | Documented in repo |

---

## 9. Integration with Other Audits

### 9.1 Audit Triggers

| Incident Type | Trigger Audit |
|---------------|---------------|
| Security incident | 0809 Security Audit |
| Privacy incident | 0810 Privacy Audit |
| Agent incident | 0821 Agentic AI Governance |
| Bias incident | 0822 Bias & Fairness |
| Supply chain issue | 0819 AI Supply Chain |

### 9.2 Feedback Loop

```
Incident
    ↓
Post-Mortem
    ↓
Action Items
    ↓
Audit Updates → Relevant 08xx audit
    ↓
0899 Meta-Audit (track coverage)
```

---

## 10. Incident Log

### 10.1 Active Incidents

| ID | Date | Title | Severity | Status | Post-Mortem |
|----|------|-------|----------|--------|-------------|
| | | | | | |

### 10.2 Resolved Incidents

| ID | Date | Title | Severity | Root Cause | Post-Mortem |
|----|------|-------|----------|------------|-------------|
| INC-001 | 2026-01-15 | OneDrive Mass Download via Unleashed | SEV-2 | Explore agents auto-approved `find` on user home, triggering 30GB OneDrive download | See below |

#### INC-001: OneDrive Mass Download via Unleashed

**Date:** 2026-01-15 08:50 AM CT
**Severity:** SEV-2 (High - significant system impact)
**Duration:** ~2 hours (system unresponsive)
**Status:** Resolved

**Summary:** Three Explore agents running with `unleashed` auto-approved `find` commands that traversed the entire user home directory (`C:\Users\mcwiz`), which includes a 30GB OneDrive folder with Files On-Demand enabled. This triggered massive file downloads, saturating disk I/O and making the system unresponsive.

**Root Cause:**
1. Explore agents issued broad `find "C:\Users\mcwiz" ...` commands
2. Unleashed v1.2.0 auto-approved these after 10-second countdown (no path validation)
3. OneDrive Files On-Demand triggered downloads for every file accessed
4. Multiple agents + OneDrive downloads = system freeze

**Contributing Factors:**
- [x] Configuration error (no OneDrive exclusion rules)
- [x] Process gap (no dangerous path detection for searches)
- [x] Edge case not handled (cloud-synced directories)

**Action Items Completed:**
1. Added DANGEROUS PATH CONSTRAINTS to CLAUDE.md
2. Added OneDrive exclusion to spawn agent prompts
3. Created `~/.agentos/excluded_paths.txt` config
4. Implemented dangerous path detection in unleashed v1.2.0
5. Implemented HARD BLOCK for destructive commands in unleashed v1.3.0
6. Created `~/.agentos/hard_block_commands.txt` and `safe_paths.txt`

**Lessons Learned:**
- Cloud-synced directories (OneDrive, Dropbox, iCloud) are hazardous for automated traversal
- Auto-approval tools need path-based safety gates, not just countdown timers
- Destructive commands need hard blocks, not just confirmation prompts
- User home directory should never be searched wholesale

---

## 11. Audit Procedure

### 11.1 This Audit's Purpose

This document serves dual purposes:
1. **Process definition** - How to handle AI incidents
2. **Incident registry** - Track what's happened

### 11.2 Quarterly Review

1. Review incident log completeness
2. Analyze trends
3. Verify action items completed
4. Assess process effectiveness
5. Update playbooks if needed

### 11.3 Post-Incident

After each SEV-1 or SEV-2:
1. Complete post-mortem within 1 week
2. Add to incident log
3. Create GitHub issues for actions
4. Trigger relevant audits
5. Update this document if process gaps found

---

## 12. References

### Frameworks
- [NIST AI RMF - MANAGE Function](https://www.nist.gov/itl/ai-risk-management-framework)
- [Google SRE - Postmortem Culture](https://sre.google/sre-book/postmortem-culture/)
- [Atlassian Incident Management](https://www.atlassian.com/incident-management)

### AI-Specific
- [Partnership on AI - Incident Database](https://incidentdatabase.ai/)
- [OECD AI Incidents Monitor](https://oecd.ai/en/incidents)

### Internal
- docs/0809-audit-security.md - Security testing
- docs/0821-audit-agentic-ai-governance.md - Agent incidents
- docs/0899-meta-audit.md - Audit coverage tracking

---

## 13. History

| Date | Change |
|------|--------|
| 2026-01-06 | Created. AI incident post-mortem process based on NIST AI RMF and SRE practices. |
