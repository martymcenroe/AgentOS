# Privacy Audit

Generic privacy audit framework based on IAPP, GDPR, and privacy-by-design principles.

## 1. Purpose

Privacy audit covering data collection, processing, storage, and user rights. Based on:
- IAPP Privacy Framework
- GDPR Principles
- IEEE Privacy Standards
- Privacy by Design (PbD)

---

## 2. Data Inventory

### What Data is Collected?

| Data Type | Collected? | Purpose | Retention |
|-----------|------------|---------|-----------|
| User Identifiers | | | |
| User Content | | | |
| Usage Analytics | | | |
| Error Logs | | | |
| Session Data | | | |

### Data Classification

| Category | Examples | Sensitivity |
|----------|----------|-------------|
| PII | Name, email, IP | High |
| User Content | Submitted text, uploads | Medium-High |
| Analytics | Page views, clicks | Low-Medium |
| System | Logs, errors | Low |

---

## 3. GDPR Principles Checklist

| Principle | Requirement | Status |
|-----------|-------------|--------|
| **Lawfulness** | Valid legal basis for processing | |
| **Purpose Limitation** | Clear, specific purposes | |
| **Data Minimization** | Only necessary data collected | |
| **Accuracy** | Data kept accurate, up-to-date | |
| **Storage Limitation** | Retention periods defined | |
| **Integrity & Confidentiality** | Security measures in place | |
| **Accountability** | Can demonstrate compliance | |

---

## 4. Privacy by Design Checklist

| Principle | Check |
|-----------|-------|
| Proactive not Reactive | Privacy considered in design phase |
| Privacy as Default | No action needed from user |
| Embedded into Design | Part of architecture, not add-on |
| Positive-Sum | Privacy AND functionality |
| End-to-End Security | Full lifecycle protection |
| Visibility & Transparency | Open operations |
| User-Centric | Respect user privacy |

---

## 5. Data Subject Rights

### Rights Checklist

| Right | Implemented? | Mechanism |
|-------|--------------|-----------|
| Access | | User can view their data |
| Rectification | | User can correct data |
| Erasure | | User can delete data |
| Portability | | User can export data |
| Objection | | User can opt out |
| Restrict Processing | | User can limit use |

### Erasure Process

1. User requests deletion
2. Identify all data stores
3. Execute deletion
4. Verify deletion
5. Confirm to user

---

## 6. Technical Controls

### Data at Rest

| Control | Requirement |
|---------|-------------|
| Encryption | AES-256 or equivalent |
| Access Control | Role-based, least privilege |
| Backup Security | Encrypted backups |

### Data in Transit

| Control | Requirement |
|---------|-------------|
| TLS Version | 1.2 or higher |
| Certificate | Valid, trusted CA |
| Perfect Forward Secrecy | Enabled |

### Data Retention

| Data Type | Retention Period | Deletion Method |
|-----------|------------------|-----------------|
| Session Data | 24 hours | Automatic TTL |
| Logs | 30-90 days | Automatic rotation |
| User Content | Per policy | On request |

---

## 7. Third-Party Data Sharing

| Third Party | Data Shared | Purpose | Controls |
|-------------|-------------|---------|----------|
| | | | |

### Third-Party Requirements

- [ ] Data Processing Agreement (DPA)
- [ ] Adequate security measures
- [ ] Purpose limitation
- [ ] Sub-processor notification

---

## 8. Audit Procedure

1. Complete data inventory
2. Review each checklist item
3. Document current state
4. Identify gaps
5. Create remediation plan
6. Re-audit after changes

---

## 9. Output Format

```markdown
# Privacy Audit Report: {DATE}

## Summary
- Data Types: {count}
- GDPR Compliance: {%}
- PbD Score: {X}/7

## Data Inventory
| Type | Collected | Sensitivity | Retention |
|------|-----------|-------------|-----------|
| ... | | | |

## Findings
| ID | Severity | Category | Finding | Remediation |
|----|----------|----------|---------|-------------|
| P1 | High | Retention | No TTL on... | Add 24h TTL |

## Recommendations
1. ...
2. ...
```

---

## 10. References

- IAPP (International Association of Privacy Professionals)
- GDPR (General Data Protection Regulation)
- IEEE Standards on Privacy
- NIST Privacy Framework

---

*Source: AgentOS/docs/audits/privacy-audit.md*
*Project-specific privacy requirements extend this framework.*
