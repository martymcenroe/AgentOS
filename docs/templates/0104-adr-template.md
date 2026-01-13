# 0104 - Template: Architecture Decision Record (ADR)

## Purpose
ADRs document significant architectural decisions with their context, alternatives, and rationale. They create a decision log that explains WHY the system is built the way it is.

## Best Practice Reference
This template follows the format popularized by Michael Nygard in [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) (2011), later adopted by Thoughtworks in their Technology Radar.

Additional resources:
- [ADR GitHub](https://adr.github.io/) - Community hub with templates and tools
- [Joel Parker Henderson's ADR examples](https://github.com/joelparkerhenderson/architecture-decision-record)

## When to Create an ADR
- Choosing between technologies (e.g., LangGraph vs Step Functions)
- Selecting architectural patterns (e.g., event-driven vs request-response)
- Making security/privacy trade-offs
- Decisions that are hard to reverse
- Decisions that team members frequently ask about

## ADR Numbering
- ADRs use the `02xx` namespace
- `0200-ADR-index.md` - Master index of all ADRs
- `0201-ADR-{topic}.md` through `029x-ADR-{topic}.md` - Individual decisions
- Numbers are never reused; superseded ADRs remain for history

## Status Values
| Status | Meaning |
|--------|---------|
| **Proposed** | Under discussion, not yet decided |
| **Implemented** | Decision made and in effect |
| **Deprecated** | No longer recommended, but not replaced |
| **Superseded** | Replaced by ADR-02XX (link to replacement) |

## Categories
Tag each ADR with one or more categories:
- **Security** - Authentication, authorization, encryption, vulnerabilities
- **Privacy** - Data handling, retention, user consent, compliance
- **Content Safety** - Filtering, moderation, age restrictions, hate speech
- **Infrastructure** - Cloud services, deployment, scaling, reliability
- **Data** - Storage, schemas, migrations, caching
- **Integration** - APIs, third-party services, protocols
- **Performance** - Latency, throughput, optimization
- **UX** - User experience trade-offs affecting architecture
- **Cost Optimization** - Budget-driven decisions (e.g., licensing, hosting)
- **Process** - Workflow and developer experience decisions
- **Compliance** - Legal, store policy, and regulatory requirements

## On Diagrams
Use diagrams when they clarify the decision better than prose. Good candidates:
- Comparing architectural options visually
- Showing data flow differences between alternatives
- Illustrating security boundaries or attack surfaces
- Before/after architecture comparisons

Use Mermaid syntax for consistency. Diagrams are optional but encouraged.

---

## Template

# 02XX - ADR: {Decision Title}

**Status:** Proposed | Implemented | Deprecated | Superseded by 02YY
**Date:** YYYY-MM-DD
**Categories:** {Security, Privacy, Content Safety, Infrastructure, Data, Integration, Performance, UX}

## 1. Context

{What is the issue motivating this decision? What forces are at play?}

{Include relevant constraints, requirements, or tensions.}

{Use diagrams if they help illustrate the problem space.}

## 2. Decision

**We will {do X}.**

{State the decision in a single, clear sentence. Use active voice.}

## 3. Alternatives Considered

### Option A: {Name} — SELECTED
**Description:** {Brief description}

**Pros:**
- {Pro 1}
- {Pro 2}

**Cons:**
- {Con 1}
- {Con 2}

### Option B: {Name} — Rejected
**Description:** {Brief description}

**Pros:**
- {Pro 1}

**Cons:**
- {Con 1}
- {Con 2} ← {Why this was the deciding factor}

### Option C: {Name} — Rejected
{Same format as above}

{Include a comparison diagram if it helps visualize the trade-offs.}

## 4. Rationale

{Why was Option A selected over the others?}

{What were the key deciding factors?}

{What trade-offs are we accepting?}

## 5. Security Risk Analysis

**Every ADR must address security implications.**

| Risk | Impact | Likelihood | Severity | Mitigation |
|------|--------|------------|----------|------------|
| {Risk 1} | High/Med/Low | High/Med/Low | {I × L} | {How addressed} |
| {Risk 2} | High/Med/Low | High/Med/Low | {I × L} | {How addressed} |

**Severity Formula:** Impact × Likelihood (High=3, Med=2, Low=1)
- **Critical (7-9):** Must address before implementation
- **Moderate (4-6):** Address during implementation
- **Low (1-3):** Accept or address later

**Residual Risk:** {What risk remains after mitigations?}

## 6. Consequences

### Positive
- {Benefit 1}
- {Benefit 2}

### Negative
- {Drawback 1 — and how we'll mitigate it}
- {Technical debt incurred}

### Neutral
- {Side effects that are neither good nor bad}

## 7. Implementation

- **Related Issues:** #XX, #YY
- **Related LLDs:** 10XX, 10YY
- **Status:** Not Started | In Progress | Complete

{Any guidance for implementing this decision}

## 8. References

- {Link to discussion thread, if any}
- {Link to external documentation or standards}
- {Link to prior art}

---

## Revision History

| Date | Author | Change |
|------|--------|--------|
| YYYY-MM-DD | {Name/Model} | Initial draft |
| YYYY-MM-DD | {Name/Model} | {What changed} |
