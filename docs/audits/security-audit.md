# Application Security Audit

Generic security audit framework based on OWASP and industry best practices.

## 1. Purpose

Application security audit covering web application and infrastructure security. Based on:
- OWASP Top 10 (2025)
- NIST Cybersecurity Framework
- CIS Controls

**Note:** AI-specific security (LLM safety, prompt injection) should be covered by a separate AI Safety audit.

---

## 2. OWASP Top 10 (2025) Checklist

| Risk | Category | Check |
|------|----------|-------|
| **A01** | Broken Access Control | Authentication enforced, authorization checks |
| **A02** | Security Misconfiguration | Minimal permissions, no debug endpoints |
| **A03** | Software Supply Chain | Dependencies audited, lock files committed |
| **A04** | Cryptographic Failures | HTTPS enforced, sensitive data encrypted |
| **A05** | Injection | Input validation, parameterized queries |
| **A06** | Insecure Design | Security requirements documented |
| **A07** | Auth Failures | Secure session management, MFA where applicable |
| **A08** | Data Integrity Failures | No untrusted deserialization |
| **A09** | Logging Failures | Security events logged, generic error messages |
| **A10** | Exceptional Conditions | Fail-closed design, graceful error handling |

### A03: Supply Chain Checklist

| Check | Requirement |
|-------|-------------|
| Dependency scanning | `npm audit`, `pip-audit`, or equivalent |
| Lock files committed | poetry.lock, package-lock.json, etc. |
| Dependabot configured | Automated security updates |
| No CDN dependencies | Assets bundled locally when possible |
| Build integrity | Trusted build tools only |

### A10: Exception Handling

| Check | Requirement |
|-------|-------------|
| Fail-closed design | Errors block, don't bypass |
| Generic error messages | No stack traces to clients |
| Rate limit handling | Graceful 429 responses |
| Timeout handling | Defined timeouts with graceful fallback |

---

## 3. Infrastructure Security

### Cloud Security (Generic)

| Check | Requirement |
|-------|-------------|
| IAM least privilege | Only required permissions |
| No hardcoded secrets | Environment variables or secrets manager |
| Encryption at rest | Default encryption enabled |
| Encryption in transit | HTTPS/TLS enforced |
| Logging enabled | Audit logs for security events |

### API Security

| Check | Requirement |
|-------|-------------|
| Authentication | All endpoints authenticated |
| Rate limiting | Abuse prevention enabled |
| Input validation | Size limits, format validation |
| CORS configured | Restrictive origin policy |

---

## 4. Agent Permission Security

**The agent's permission model is a security boundary.**

### Forbidden Patterns Check

Grep permission configuration for these patterns. If found in allow list, **FAIL the audit**:

| Pattern | Risk |
|---------|------|
| `eval:` | Arbitrary command execution |
| `exec:` | Process replacement |
| `env:` | Secret exposure |
| `printenv:` | Secret exposure |

### Verification

```bash
# These should return matches (in deny list)
grep -A50 '"deny"' .claude/settings.local.json | grep -E "eval|env|exec"

# This should return NO matches (not in allow list)
grep -B100 '"deny"' .claude/settings.local.json | grep -E '"Bash\(eval|"Bash\(env:|"Bash\(exec:'
```

---

## 5. Audit Procedure

### Prerequisites

1. Run dependency audit first (Dependabot, npm audit, etc.)
2. Ensure clean baseline (all tests pass)

### Execution

1. Run automated security tools
2. Review each section systematically
3. Mark status: ✅ Pass, ⚠️ Warning, ❌ Fail
4. Document findings
5. Create issues for failures
6. Re-audit after remediation

---

## 6. Output Format

```markdown
# Security Audit Report: {DATE}

## Summary
- Overall Status: PASS/FAIL
- Critical Findings: {count}
- Warnings: {count}

## OWASP Top 10 Status
| Risk | Status | Notes |
|------|--------|-------|
| A01 | ✅ | Access control verified |
| ... | ... | ... |

## Supply Chain Status
- npm audit: {result}
- Dependabot alerts: {count}
- Lock files: Committed/Missing

## Findings
| ID | Severity | Category | Finding | Status |
|----|----------|----------|---------|--------|
| F1 | Critical | A05 | SQL injection in... | Open/Fixed |

## Recommendations
1. ...
2. ...
```

---

## 7. References

### OWASP
- [OWASP Top 10:2025](https://owasp.org/Top10/)
- [OWASP ASVS](https://owasp.org/ASVS/) (Application Security Verification Standard)

### Other Frameworks
- NIST Cybersecurity Framework
- CIS Controls

---

*Source: AgentOS/docs/audits/security-audit.md*
*Project-specific security requirements extend this framework.*
