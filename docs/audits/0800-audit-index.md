# 0800 - Audit Index

## 1. Purpose

Master index of all AgentOS audits. Provides navigation, categorization, and quick reference for the audit suite.

---

## 2. Audit Philosophy

> "Don't trust metadata—verify reality."

Audits exist because:
1. **Docs drift from code** - Architecture changes, docs don't update
2. **Issues drift from reality** - Issues marked open are actually complete (or vice versa)
3. **Process steps get skipped** - Reports not created, inventory not updated
4. **Terminology evolves** - Old names persist in forgotten corners
5. **The system itself decays** - Cross-references break, templates diverge

### 2.1 Evidence over Inference (CRITICAL)

**Do not assume compliance based on file names or documentation claims. Grep the code/config for the specific setting.**

| Bad Practice | Good Practice |
|--------------|---------------|
| "0810 says in-memory only" | `grep put_item src/lambda_function.py` |
| "CLAUDE.md says eval is forbidden" | `grep eval .claude/settings.local.json` |
| "Package says MIT license" | Compare LICENSE, package.json, pyproject.toml |

**The code is the truth. The docs are a claim about the truth.**

### 2.2 N/A Verification Policy (MANDATORY)

**"N/A" is not a free pass.** Items marked Not Applicable require verification each audit:

| Wrong | Right |
|-------|-------|
| "Data Poisoning: N/A (no fine-tuning)" | "Data Poisoning: ⬜ VERIFY no fine-tuning → ✅ VERIFIED: No training jobs, no custom models" |
| Check box without evidence | Grep/inspect to prove claim still true |

**Every N/A claim requires:**
1. **Architectural verification** - Confirm the reason still holds (check code/config)
2. **Documentation** - Note in audit record: "Verified [item] N/A: [evidence]"
3. **Re-evaluation** - If architecture changed, audit the item fully

**Rationale:** Architecture evolves. What was N/A last quarter (e.g., "no fine-tuning") may not be N/A now. Blind N/A checkboxes become security debt.

### 2.3 Fix-First Mandate (NON-NEGOTIABLE)

> "An audit that finds the same error twice is a broken audit."

**Audits MUST fix errors, not just document them.**

| Wrong | Right |
|-------|-------|
| "Finding: stale artifact. Noted as exception." | "Finding: stale artifact. Auto-fixed via `build_release.py`." |
| "Finding: missing permission. Added to issues." | "Finding: missing permission. Auto-added to `settings.local.json`." |
| "npm audit found 3 vulns. Documented." | "npm audit found 3 vulns. Ran `npm audit fix`. Now 0." |

**Fix-First Hierarchy:**

1. **Auto-fix immediately** - If the fix is mechanical (add entry, update file, run command), do it
2. **Auto-fix with rebuild** - If fix requires a build/test cycle, run it (e.g., `build_release.py`)
3. **Create GitHub issue** - Only if fix requires human judgment, design discussion, or code changes
4. **Exception** - Only if fix is impossible (external dependency, third-party bug)

**The goal:** The next audit run should find ZERO of the same errors.

**Audit Record Requirement:**

```markdown
### Auto-Fixed
- [x] Rebuilt stale Chrome artifact
- [x] Added `Bash(new-tool:*)` to allowlist

### Requires Human Decision
- [ ] Version bump: 1.0 → 1.1? (needs product decision)

### Exceptions (Truly Unfixable)
- [ ] Claude Code permission bug #17637 (upstream)
```

---

## 3. Audit Suite Overview

### 3.1 At a Glance (Frequency-Based)

| Tier | Frequency | Count | Focus |
|------|-----------|-------|-------|
| **Continuous** | Per-PR, on-change | 3 | Code quality, gitignore |
| **Weekly** | Hygiene checks | 9 | Permissions, worktree, issues, reports |
| **Monthly** | Governance checks | 11 | AI governance, structure, wiki, cost |
| **Quarterly** | Deep audits | 12 | Security, privacy, compliance, fairness |
| **On-Demand** | Event-triggered | 4 | Incidents, friction, terminology |
| **Ultimate** | Expensive/rare | 4 | Security, privacy, ISO 42001, encryption |
| **Under Development** | Not yet automated | 6 | Documentation health stubs |
| **Meta** | System governance | 1 | Audit validation |
| **Total** | | **40** | |

*Note: Ultimate tier audits also appear in Quarterly but only run with `--ultimate` flag.*
*Note: Audits 0826-0831 are infrastructure audits for child projects (Aletheia).*

### 3.2 Quick Reference

**All Audits (41 total):**

| Audit | One-Line Description | Tier | Auto-Fix |
|-------|----------------------|------|----------|
| 0801 | Security (OWASP, ASVS) | Ultimate | No |
| 0802 | Privacy (GDPR-aware, data handling) | Ultimate | No |
| 0803 | Code Quality | Continuous | CI |
| 0804 | Accessibility (WCAG) | Monthly | No |
| 0805 | License Compliance | Quarterly | No |
| 0806 | Bias & Fairness | Quarterly | No |
| 0807 | Explainability (XAI) | Quarterly | No |
| 0808 | AI Safety (LLM, NIST AI RMF) | Quarterly | No |
| 0809 | Agentic AI Governance (OWASP Agentic) | Monthly | No |
| 0810 | AI Management System (ISO 42001) | Ultimate | No |
| 0811 | AI Incident Post-Mortem | On-Demand | No |
| 0812 | AI Supply Chain (OWASP LLM03, AIBOM) | Quarterly | No |
| 0813 | Claude Code Capabilities | Quarterly | No |
| 0814 | Horizon Scanning Protocol | Quarterly | No |
| 0815 | Permission Friction | On-Demand | **Yes** |
| 0816 | Permission Permissiveness | Weekly | **Yes** |
| 0817 | AgentOS Self-Audit | Monthly | **Yes** |
| 0826 | Cross-Browser Testing | Monthly | No |
| 0827 | Infrastructure Integration (AWS) | Monthly | No |
| 0828 | Build Artifact Freshness | Weekly | No |
| 0829 | Lambda Failure Remediation | On-Demand | Partial |
| 0831 | Web Assets | Monthly | No |
| 0832 | Cost Optimization | Monthly | Partial |
| 0833 | Gitignore Encryption Review | Ultimate | No |
| 0834 | Worktree Hygiene | Weekly | No |
| 0835 | Structure Compliance | Monthly | No |
| 0836 | Gitignore Consistency | Continuous | No |
| 0837 | README Compliance | Continuous | No |
| 0838 | Broken References | Weekly | No |
| 0839 | Wiki Alignment | Monthly | No |
| 0840 | Cross-Project Harvest | Monthly | No |
| 0848 | Code Quality Procedure | Monthly | No |
| 0899 | Meta-Audit | Quarterly | No |

**Under Development (design complete, automation pending):**

| Audit | One-Line Description | Target Tier | Auto-Fix |
|-------|----------------------|-------------|----------|
| 0841 | Open Issues Currency (stale/complete issues) | Weekly | No |
| 0842 | Reports Completeness (closed issues have reports) | Weekly | **Yes** |
| 0843 | LLD-to-Code Alignment | On-Demand | No |
| 0844 | File Inventory Drift | Weekly | **Yes** |
| 0845 | Terminology Consistency | On-Demand | **Yes** |
| 0846 | Architecture Drift (code vs docs) | Monthly | **Yes** |

**Implemented (fully operational):**

| Audit | One-Line Description | Tier | Auto-Fix |
|-------|----------------------|------|----------|
| 0847 | Implementation Completeness (stubs, fake tests) | Monthly | No |

---

## 4. Audit Categories (Frequency-Based)

### 4.1 Continuous Tier (Per-PR, On-Change)

Fast audits that run automatically on code changes.

| Number | Name | Trigger | Auto-Fix |
|--------|------|---------|----------|
| 0803 | Code Quality | Per PR (CI) | CI |
| 0836 | Gitignore Consistency | On .gitignore change | No |
| 0837 | README Compliance | On README change | No |

### 4.2 Weekly Tier

Hygiene checks for ongoing project health.

| Number | Name | Focus | Auto-Fix |
|--------|------|-------|----------|
| 0816 | Permission Permissiveness | Access control review | **Yes** |
| 0828 | Build Artifact Freshness | Stale build detection | No |
| 0834 | Worktree Hygiene | Branch cleanup | No |
| 0838 | Broken References | Link validation | No |
| 0841 | Open Issues Currency | Stale issue detection | No |
| 0842 | Reports Completeness | Missing report detection | **Yes** |
| 0844 | File Inventory Drift | Inventory sync | **Yes** |

*Note: 0841, 0842, 0844 are under development.*

### 4.3 Monthly Tier

Regular governance and structure checks.

| Number | Name | Focus | Auto-Fix |
|--------|------|-------|----------|
| 0804 | Accessibility (WCAG) | UI compliance | No |
| 0809 | Agentic AI Governance | OWASP Agentic | No |
| 0817 | AgentOS Self-Audit | Framework health | **Yes** |
| 0826 | Cross-Browser Testing | Extension parity | No |
| 0827 | Infrastructure Integration | AWS verification | No |
| 0831 | Web Assets | UI quality | No |
| 0832 | Cost Optimization | Token efficiency | Partial |
| 0835 | Structure Compliance | Directory conventions | No |
| 0839 | Wiki Alignment | Wiki/code sync | No |
| 0840 | Cross-Project Harvest | Pattern extraction | No |
| 0846 | Architecture Drift | Code/docs alignment | **Yes** |
| 0847 | Implementation Completeness | Stub detection | No |
| 0848 | Code Quality Procedure | Systematic review | No |

*Note: 0826, 0827, 0831, 0846 are under development.*

### 4.4 Quarterly Tier

Deep compliance and governance audits.

| Number | Name | Framework | Auto-Fix |
|--------|------|-----------|----------|
| 0805 | License Compliance | OSS licenses | No |
| 0806 | Bias & Fairness | ISO 24027, NIST | No |
| 0807 | Explainability | XAI, EU AI Act | No |
| 0808 | AI Safety | OWASP LLM, NIST AI RMF | No |
| 0812 | AI Supply Chain | OWASP LLM03, SPDX 3.0 | No |
| 0813 | Claude Code Capabilities | Model features | No |
| 0814 | Horizon Scanning | Threat monitoring | No |
| 0899 | Meta-Audit | Audit validation | No |

### 4.5 On-Demand Tier

Event-triggered audits that run when needed.

| Number | Name | Trigger | Auto-Fix |
|--------|------|---------|----------|
| 0811 | AI Incident Post-Mortem | On incident | No |
| 0815 | Permission Friction | On friction event | **Yes** |
| 0829 | Lambda Failure Remediation | On CloudWatch alert | Partial |
| 0843 | LLD-to-Code Alignment | Post-implementation | No |
| 0845 | Terminology Consistency | On rename | **Yes** |

*Note: 0829, 0843, 0845 are under development.*

### 4.6 Ultimate Tier

Expensive, Opus-heavy audits that only run on explicit request.

| Number | Name | Why Ultimate | Auto-Fix |
|--------|------|--------------|----------|
| 0801 | Security (OWASP, ASVS) | Complex security reasoning | No |
| 0802 | Privacy (GDPR) | Privacy impact analysis | No |
| 0810 | AI Management System (ISO 42001) | Comprehensive framework | No |
| 0833 | Gitignore Encryption Review | Sensitive file analysis | No |

**Trigger conditions:**
- `/audit 0801` - Direct invocation of specific ultimate audit
- `/audit --ultimate` - Runs all standard + ultimate audits

**NOT triggered by:**
- `/audit` (standard run)
- `/audit --full` (all standard, excludes ultimate)

**Cost rationale:** These audits require Opus-level reasoning and typically cost $2-5+ per run. They cover critical areas but don't need frequent execution.

### 4.7 Under Development

Audits with design complete but automation pending.

| Number | Name | Target Tier | Status |
|--------|------|-------------|--------|
| 0826 | Cross-Browser Testing | Monthly | Stub - needs test scripts |
| 0827 | Infrastructure Integration | Monthly | Stub - needs AWS CLI scripts |
| 0828 | Build Artifact Freshness | Weekly | Stub - needs timestamp checker |
| 0829 | Lambda Failure Remediation | On-Demand | Stub - needs CloudWatch integration |
| 0831 | Web Assets | Monthly | Stub - needs Lighthouse integration |
| 0841 | Open Issues Currency | Weekly | Designed - needs gh CLI automation |
| 0842 | Reports Completeness | Weekly | Designed - needs report generator |
| 0843 | LLD-to-Code Alignment | On-Demand | Designed - needs AST parser |
| 0844 | File Inventory Drift | Weekly | Designed - needs inventory tool |
| 0845 | Terminology Consistency | On-Demand | Designed - needs grep automation |
| 0846 | Architecture Drift | Monthly | Designed - needs structure comparator |

### 4.8 Meta Audits

Audits that govern the audit system itself.

| Number | Name | Frequency | Purpose |
|--------|------|-----------|---------|
| 0899 | Meta-Audit | Quarterly | Validate audit execution |

---

## 5. Frequency Matrix

*Note: Section 4 now contains the primary frequency-based organization. This section provides a condensed reference.*

### 5.1 By Frequency

| Frequency | Audits |
|-----------|--------|
| **Continuous** | 0803, 0836, 0837 |
| **Weekly** | 0816, 0828, 0834, 0838, 0841*, 0842*, 0844* |
| **Monthly** | 0804, 0809, 0817, 0826*, 0827*, 0831*, 0832, 0835, 0839, 0840, 0846*, 0847, 0848 |
| **Quarterly** | 0805, 0806, 0807, 0808, 0812, 0813, 0814, 0899 |
| **On-Demand** | 0811, 0815, 0829*, 0843*, 0845* |
| **Ultimate** | 0801, 0802, 0810, 0833 |

*\* = Under development*

---

## 6. Standards Coverage Map

### 6.1 By Standard

| Standard | Primary Audit | Supporting Audits |
|----------|---------------|-------------------|
| **OWASP LLM Top 10 (2025)** | 0808 | 0809, 0812 |
| **OWASP Agentic Top 10 (2026)** | 0809 | 0808, 0815 |
| **ISO/IEC 42001:2023** | 0810 | 0809, 0806 |
| **EU AI Act** | 0807 | 0809, 0810 |
| **NIST AI RMF** | 0808 | 0811 |
| **ASVS 4.0.3** | 0801 §4 | |
| **CWE Top 25** | 0801 §2 | |
| **SPDX 3.0 AI Profile** | 0812 | |

### 6.2 Coverage Gaps

See **0814 Horizon Scanning Protocol** for ongoing gap discovery.

---

## 7. Audit Dependencies

### 7.1 Dependency Graph

```
0899 Meta-Audit
  └── validates all 08xx audits

0814 Horizon Scanning
  └── discovers gaps for all 08xx

0809 Agentic AI Governance
  ├── depends on: 0808, 0815
  └── informs: 0811

0812 AI Supply Chain
  └── depends on: 0805

0801 Security
  └── informs: 0809, 0811

0811 AI Incident Post-Mortem
  └── triggers: 0801, 0809, 0806 (as needed)
```

### 7.2 Run Order (when running multiple)

1. Code quality audit first (0803)
2. Permission audit (0816)
3. Security/Privacy (0801, 0802)
4. AI Governance (0806-0812)
5. Agent audits (0808, 0809, 0815)
6. Meta audits last (0814, 0899)

---

## 8. Record-Keeping Requirements (MANDATORY)

### 8.1 Auditor Identity

**Every audit record entry MUST include auditor identity.** No anonymous audits.

| Field | Requirement | Example |
|-------|-------------|---------|
| **Auditor** | Model name + version | "Claude Opus 4.5", "Gemini 3.0 Pro" |
| **Date** | ISO 8601 format | 2026-01-10 |
| **Findings** | Explicit PASS/FAIL with issue refs | "PASS", "FAIL: See #234" |

**Accountability Rule:** The auditor recorded in the audit record MUST match the git commit author. If Claude runs the audit, the commit must be by Claude. This creates traceability.

### 8.2 Audit Record Format

Standard format for all audits:

```markdown
| Date | Auditor | Findings Summary | Issues Created |
|------|---------|------------------|----------------|
| YYYY-MM-DD | [Model Name] | [PASS/FAIL summary] | #NNN, #NNN |
```

**Forbidden entries:**
- ❌ Empty auditor field
- ❌ "TBD" or "TODO" as auditor
- ❌ Generic "Agent" without model name
- ❌ Findings without PASS/FAIL classification

### 8.3 Audit Failure → GitHub Issue (MANDATORY)

**Every audit failure MUST create a GitHub issue.** No internal-only findings.

| Finding | Action | Issue Label |
|---------|--------|-------------|
| **FAIL** | Create issue immediately | `audit`, `high-priority` |
| **WARN** | Create issue | `audit`, `low-priority` |
| **PASS** | No issue needed | - |

**Audit Record Entry Format for Failures:**

```markdown
| Date | Auditor | Findings Summary | Issues Created |
|------|---------|------------------|----------------|
| 2026-01-10 | Claude Opus 4.5 | FAIL: XSS in overlay | #NNN |
```

**Forbidden:**
- ❌ `FAIL` without issue reference
- ❌ `FAIL: See internal notes`
- ❌ Findings buried in prose without issue

**Rationale:** GitHub issues are visible, trackable, and cannot be quietly dismissed. Internal audit records can be edited or forgotten.

---

## 9. Audit Ownership

### 9.1 By Role

| Role | Audits Owned |
|------|--------------|
| **Developer** | All (solo project) |
| **CI/CD** | 0813 |
| **Dependabot** | 0816 (triggers) |

### 9.2 Accountability

| Audit | Accountable | Responsible | Consulted |
|-------|-------------|-------------|-----------|
| 0801 Security | Developer | Developer | - |
| 0809 Agentic | Developer | Claude Code | Developer |
| 0811 Incident | Developer | Developer | - |

---

## 10. Quick Links

### 10.1 By Number

**Core Audits (0801-0817)**
- [0801 - Security](0801-security-audit.md) 🔒
- [0802 - Privacy](0802-privacy-audit.md) 🔒
- [0803 - Code Quality](0803-code-quality-audit.md)
- [0804 - Accessibility](0804-accessibility-audit.md)
- [0805 - License Compliance](0805-license-compliance.md)
- [0806 - Bias & Fairness](0806-bias-fairness.md)
- [0807 - Explainability](0807-explainability.md)
- [0808 - AI Safety](0808-ai-safety-audit.md)
- [0809 - Agentic AI Governance](0809-agentic-ai-governance.md)
- [0810 - AI Management System](0810-ai-management-system.md) 🔒
- [0811 - AI Incident Post-Mortem](0811-ai-incident-post-mortem.md)
- [0812 - AI Supply Chain](0812-ai-supply-chain.md)
- [0813 - Claude Capabilities](0813-claude-capabilities.md)
- [0814 - Horizon Scanning](0814-horizon-scanning-protocol.md)
- [0815 - Permission Friction](0815-permission-friction.md) ✨
- [0816 - Permission Permissiveness](0816-permission-permissiveness.md) ✨
- [0817 - AgentOS Self-Audit](0817-agentos-audit.md) ✨

**Infrastructure Audits (0826-0831) - For Child Projects**
- [0826 - Cross-Browser Testing](0826-audit-cross-browser-testing.md) 📝
- [0827 - Infrastructure Integration](0827-audit-infrastructure-integration.md) 📝
- [0828 - Build Artifact Freshness](0828-audit-build-artifact-freshness.md) 📝
- [0829 - Lambda Failure Remediation](0829-audit-lambda-failure-remediation.md) 📝
- [0831 - Web Assets](0831-audit-web-assets.md) 📝

**Extended Audits (0832-0848)**
- [0832 - Cost Optimization](0832-audit-cost-optimization.md) ✨
- [0833 - Gitignore Encryption Review](0833-audit-gitignore-encryption.md) 🔒
- [0834 - Worktree Hygiene](0834-audit-worktree-hygiene.md)
- [0835 - Structure Compliance](0835-audit-structure-compliance.md)
- [0836 - Gitignore Consistency](0836-audit-gitignore-consistency.md)
- [0837 - README Compliance](0837-audit-readme-compliance.md)
- [0838 - Broken References](0838-audit-broken-references.md)
- [0839 - Wiki Alignment](0839-audit-wiki-alignment.md)
- [0840 - Cross-Project Harvest](0840-cross-project-harvest.md)
- [0848 - Code Quality Procedure](0848-audit-code-quality-procedure.md)

**Documentation Health (0841-0847)**
- [0841 - Open Issues Currency](0841-audit-open-issues.md) 📝
- [0842 - Reports Completeness](0842-audit-reports-completeness.md) ✨📝
- [0843 - LLD-to-Code Alignment](0843-audit-lld-code-alignment.md) 📝
- [0844 - File Inventory Drift](0844-audit-file-inventory.md) ✨📝
- [0845 - Terminology Consistency](0845-audit-terminology.md) ✨📝
- [0846 - Architecture Drift](0846-audit-architecture-drift.md) ✨📝
- [0847 - Implementation Completeness](0847-audit-implementation-completeness.md) 🔨

**Meta (0899)**
- [0899 - Meta-Audit](0899-meta-audit.md)

✨ = Auto-fix capability
🔒 = Ultimate tier (only runs with `--ultimate` flag)
📝 = Under development (design complete, automation pending)
🔨 = Anti-laziness audit (forces thorough work)

### 10.2 By Topic

| Topic | Relevant Audits |
|-------|-----------------|
| Agent behavior | 0808, 0809, 0815 |
| AI safety | 0808, 0809, 0806 |
| Accessibility | 0804, 0831 |
| AWS/Infrastructure | 0827, 0829 |
| Browser extensions | 0826, 0831 |
| Build/CI | 0803, 0828 |
| Code quality | 0803, 0847, 0848 |
| Compliance | 0806, 0807, 0810 |
| Cost | 0832 |
| Dependencies | 0805, 0812 |
| Documentation | 0838, 0839, 0841-0846 |
| Incidents | 0811 |
| License | 0805 |
| Permissions | 0815, 0816 |
| Privacy | 0802 |
| Security | 0801, 0833 |
| Structure | 0835, 0836, 0837, 0844 |

---

## 11. Model Recommendations

Cost optimization: use the cheapest model that can reliably execute each audit.

### 11.1 By Model Tier

| Model | Cost | Audits | Rationale |
|-------|------|--------|-----------|
| **Haiku** | $ | 0803, 0805, 0812, 0814, 0816, 0817, 0827, 0828, 0834, 0836, 0837, 0838, 0899 | Simple checklist, grep patterns, file parsing |
| **Sonnet** | $$ | 0804, 0806, 0807, 0813, 0815, 0826, 0831, 0832, 0839, 0840, 0847, 0848 | Moderate reasoning, framework analysis |
| **Opus** | $$$ | 0801, 0802, 0808, 0809, 0810, 0811, 0829 | Complex reasoning, security/privacy analysis |

### 11.2 Detailed Rationale

| Audit | Recommended | Why |
|-------|-------------|-----|
| 0801 Security | **Opus** | OWASP/ASVS requires nuanced security reasoning |
| 0802 Privacy | **Opus** | GDPR/privacy analysis requires contextual judgment |
| 0803 Code Quality | Haiku | Linting output parsing |
| 0804 Accessibility | Sonnet | WCAG checklist with moderate reasoning |
| 0805 License Compliance | Haiku | SPDX string matching |
| 0806 Bias & Fairness | Sonnet | Structured bias evaluation |
| 0807 Explainability | Sonnet | XAI evaluation with framework guidance |
| 0808 AI Safety | **Opus** | LLM safety requires nuanced reasoning |
| 0809 Agentic AI Governance | **Opus** | Complex agent behavior analysis |
| 0810 AI Management System | **Opus** | ISO 42001 requires comprehensive analysis |
| 0811 AI Incident Post-Mortem | **Opus** | Root cause analysis requires deep reasoning |
| 0812 AI Supply Chain | Haiku | Dependency scanning, manifest parsing |
| 0813 Claude Capabilities | Sonnet | Web research for new features |
| 0814 Horizon Scanning | Haiku | Framework registry parsing |
| 0815 Permission Friction | Sonnet | Session log analysis, pattern recognition |
| 0816 Permission Permissiveness | Haiku | Settings file parsing |
| 0817 AgentOS Self-Audit | Haiku | Text diff comparison |
| 0826 Cross-Browser Testing | Sonnet | Browser compatibility analysis |
| 0827 Infrastructure Integration | Haiku | AWS CLI parsing, config verification |
| 0828 Build Artifact Freshness | Haiku | Timestamp comparison |
| 0829 Lambda Failure Remediation | **Opus** | Root cause analysis, code fixes |
| 0831 Web Assets | Sonnet | Visual design evaluation |
| 0832 Cost Optimization | Sonnet | Token analysis, optimization suggestions |
| 0834 Worktree Hygiene | Haiku | Git command parsing |
| 0836 Gitignore Consistency | Haiku | Pattern matching |
| 0837 README Compliance | Haiku | Template matching |
| 0838 Broken References | Haiku | Link validation |
| 0839 Wiki Alignment | Sonnet | Content comparison |
| 0840 Cross-Project Harvest | Sonnet | Pattern extraction |
| 0847 Implementation Completeness | Sonnet | Stub/mock detection |
| 0848 Code Quality Procedure | Sonnet | Systematic review |
| 0899 Meta-Audit | Haiku | Execution tracking |

### 11.3 Estimated Savings

By using appropriate models instead of Opus for all audits:
- **Haiku audits (13):** ~66% savings per audit
- **Sonnet audits (12):** ~25% savings per audit
- **Opus audits (7):** No change (required for complexity)

---

## 12. Getting Started

### 12.1 For New Contributors

1. Read this index to understand the audit landscape
2. Review 0815 for Claude Code workflow rules
3. Code quality audit (0813) runs automatically on PRs
4. Security (0809) and Privacy (0810) are the most comprehensive

### 12.2 For Audit Execution

1. Check 0899 for audit schedule and status
2. Run audit per its documented procedure
3. Record findings in audit's Audit Record section
4. Create GitHub issues for failures
5. Update 0899 with execution date

### 12.3 For Gap Discovery

1. Review 0814 Horizon Scanning Protocol
2. Check Framework Registry for updates
3. Triage new frameworks per 0814 §4
4. Propose new audits if gaps found

---

## 13. History

| Date | Change |
|------|--------|
| 2026-02-05 | **Issue #19: Major frequency-based reorganization.** Reorganized all audits by frequency tier (Continuous, Weekly, Monthly, Quarterly, On-Demand, Ultimate). Fixed 0837 collision (renamed code-quality-procedure to 0848). Created 5 infrastructure audit stubs (0826-0831) for child projects (Aletheia). Removed 15 phantom audit references (082x range) that were documented but never created. Expanded Ultimate tier: added 0801, 0802, 0810 to join 0833. Corrected file count: 40 audits (29 implemented + 11 under development). Updated Model Recommendations with correct audit numbers. |
| 2026-01-21 | **Major index reconciliation.** Fixed numbering collision: index described conceptual audits (0801-0807 Documentation Health) that conflicted with actual files (0801-security, 0802-privacy, etc.). Solution: Renumbered Documentation Health audits to 0841-0846 (stubs created). Fixed duplicates: 0817→0839 (wiki alignment), 0832→0840 (cross-project harvest). Updated all Quick Links to point to actual files. Total audits: 33 (27 implemented + 6 stubs). |
| 2026-01-16 | Created 0833 (Gitignore Encryption Review) for encrypt vs ignore recommendations. Added Ultimate tier for expensive/rare audits (--ultimate flag). Part of Issue #18 (git-crypt ideas folder). Total audits: 34. |
| 2026-01-12 | Added auto-fix capability to 9 audits (0802, 0804, 0805, 0806, 0807, 0808, 0824, 0828, 0830). Added Documentation Health category (0801-0807) to index. Total audits: 32. |
| 2026-01-11 | Renumbered 0827-audit-web-assets.md to 0831 (resolved duplicate with 0827-infrastructure-integration). Total audits: 25. |
| 2026-01-11 | Created 0830 (Architecture Freshness) for documentation completeness and currency. Part of Architectural Depth Model (#308). Total audits: 24. |
| 2026-01-10 | Created 0829 (Lambda Failure Remediation) for proactive CloudWatch error detection and fix-or-draft workflow. Total audits: 23. |
| 2026-01-10 | Created 0827 (Infrastructure Integration) for Lambda, DynamoDB, API Gateway verification. Total audits: 22. |
| 2026-01-09 | Created 0826 (Cross-Browser Testing) after Firefox incident. Enforces file parity and mock fidelity. Total audits: 21. |
| 2026-01-08 | Split 0809 per ADR 0213. Created 0825 (AI Safety) with LLM, Agentic, NIST AI RMF sections. 0809 now focused on app security. Total audits: 20. |
| 2026-01-08 | Index consistency audit. Fixed broken links (0811-0814, 0815, 0817). Corrected audit names/descriptions to match actual files. Added 0817 Wiki Alignment. Total audits: 19. |
| 2026-01-06 | Major update. Added AI Governance audits (0818-0823), split meta-audit into 0898 (horizon scanning) and 0899 (validation). Merged 0800-common-audits.md into this file (preserved Audit Philosophy section). Total audits: 17. |
| 2026-01-14 | Created 0832 (Cost Optimization) for skill/command token efficiency analysis. Total audits: 33. |
