# AI Safety Audit

Generic AI safety audit framework for LLM-integrated applications.

## 1. Purpose

AI safety audit covering LLM security, agentic AI risks, and AI governance. Based on:
- OWASP Top 10 for LLM Applications
- OWASP Top 10 for Agentic AI
- NIST AI Risk Management Framework

**Scope:** AI-specific security concerns. General application security covered by security-audit.md.

---

## 2. OWASP Top 10 for LLM Applications

| Risk | Category | Check |
|------|----------|-------|
| **LLM01** | Prompt Injection | User input isolated from system prompts |
| **LLM02** | Insecure Output Handling | LLM output sanitized before use |
| **LLM03** | Training Data Poisoning | N/A for managed models (Bedrock, OpenAI) |
| **LLM04** | Model Denial of Service | Rate limiting, input size limits |
| **LLM05** | Supply Chain | Model provenance verified |
| **LLM06** | Sensitive Information Disclosure | No PII in prompts, responses filtered |
| **LLM07** | Insecure Plugin Design | N/A if no plugins used |
| **LLM08** | Excessive Agency | Agent actions scoped and approved |
| **LLM09** | Overreliance | Human verification for critical decisions |
| **LLM10** | Model Theft | N/A for managed models |

### LLM01: Prompt Injection Defenses

| Defense | Implementation |
|---------|----------------|
| Input isolation | User text wrapped in XML/delimiters |
| System prompt protection | Not exposed to user |
| Input validation | Size limits, format validation |

### LLM06: Information Disclosure Defenses

| Defense | Implementation |
|---------|----------------|
| No PII in prompts | Minimize user data in requests |
| Response filtering | Guardrails on output |
| Generic errors | No model internals exposed |

---

## 3. OWASP Top 10 for Agentic AI

For AI agents with tool access and autonomy:

| Risk | Category | Check |
|------|----------|-------|
| **AGT01** | Insufficient Agent Oversight | Actions reviewed before execution |
| **AGT02** | Excessive Agent Autonomy | Scope limited to necessary actions |
| **AGT03** | Insecure Tool Binding | Tools validated, permissions scoped |
| **AGT04** | Unintended Agent Actions | Actions match user intent |
| **AGT05** | Poor Communication | Clear feedback on agent actions |
| **AGT06** | Compromised Memory | Session data isolated and protected |
| **AGT07** | Insufficient Error Recovery | Graceful failure, no undefined states |
| **AGT08** | Deceptive Agent Behavior | Agent cannot hide or lie about actions |
| **AGT09** | Improper Resource Management | Rate limits, resource caps |
| **AGT10** | Inadequate Audit Trails | All actions logged |

### AGT02: Autonomy Controls

| Control | Implementation |
|---------|----------------|
| Action allowlist | Defined set of permitted operations |
| Confirmation for destructive | Human approval for irreversible |
| Scope boundaries | Cannot access outside project |

---

## 4. NIST AI Risk Management Framework

### Governance

| Check | Requirement |
|-------|-------------|
| AI policy documented | Clear usage guidelines |
| Roles defined | Who manages AI components |
| Incident response | Plan for AI failures |

### Map

| Check | Requirement |
|-------|-------------|
| AI components inventoried | All AI usage documented |
| Risk assessment completed | Risks identified and rated |

### Measure

| Check | Requirement |
|-------|-------------|
| Performance metrics | Accuracy, latency tracked |
| Bias metrics | Fairness monitoring |
| Safety metrics | Harm prevention tracked |

### Manage

| Check | Requirement |
|-------|-------------|
| Monitoring in place | Runtime performance |
| Update process | Model updates controlled |
| Rollback capability | Can revert to previous |

---

## 5. Guardrail Configuration

### Input Guardrails

| Guardrail | Purpose | Status |
|-----------|---------|--------|
| Size limits | Prevent DoS | |
| Format validation | Expected input types | |
| Denylist check | Block prohibited content | |

### Output Guardrails

| Guardrail | Purpose | Status |
|-----------|---------|--------|
| Content filtering | Remove harmful output | |
| PII detection | Prevent leakage | |
| Response validation | Structured output check | |

---

## 6. Audit Procedure

1. Inventory AI components
2. Review LLM Top 10 checklist
3. Review Agentic Top 10 (if applicable)
4. Check NIST RMF alignment
5. Verify guardrails configuration
6. Document findings
7. Create remediation plan

---

## 7. Output Format

```markdown
# AI Safety Audit Report: {DATE}

## Summary
- LLM Components: {count}
- Agent Components: {count}
- Critical Findings: {count}

## LLM Top 10 Status
| Risk | Status | Notes |
|------|--------|-------|
| LLM01 | ✅ | Input isolated |
| ... | ... | ... |

## Agentic Top 10 Status (if applicable)
| Risk | Status | Notes |
|------|--------|-------|
| AGT01 | ✅ | Oversight in place |
| ... | ... | ... |

## Guardrail Status
| Type | Guardrail | Status |
|------|-----------|--------|
| Input | Size limit | ✅ |
| Output | Content filter | ⚠️ |

## Findings
| ID | Severity | Category | Finding | Remediation |
|----|----------|----------|---------|-------------|
| AI1 | High | LLM01 | Possible injection via... | Add XML wrapping |

## Recommendations
1. ...
2. ...
```

---

## 8. References

- [OWASP Top 10 for LLM](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [OWASP Top 10 for Agentic AI](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework)

---

*Source: AgentOS/docs/audits/ai-safety-audit.md*
*Project-specific AI requirements extend this framework.*
