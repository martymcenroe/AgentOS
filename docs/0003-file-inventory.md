# AgentOS - File Inventory & Status Map

**Document:** 0003
**Version:** 1.0
**Last Updated:** 2026-01-13

## 1. Status Taxonomy

| Status | Meaning |
|--------|---------|
| **Stable** | Verified, documented, production-ready |
| **Beta** | Functional but lacks full test coverage or documentation |
| **In-Progress** | Active development; expect instability |
| **Placeholder** | Skeleton or empty file; do not run |
| **Legacy** | Deprecated/archived (reference only) |

---

## 2. Documentation Inventory (47 files)

### Standards (00xx) - 7 files

| File | Status | Description |
|------|--------|-------------|
| `0001-orchestration-protocol.md` | Stable | Multi-agent coordination rules |
| `0002-coding-standards.md` | Stable | Code style and practices |
| `0003-agent-prohibited-actions.md` | Stable | Forbidden agent actions |
| `0004-mermaid-diagrams.md` | Stable | Diagram conventions |
| `0005-session-closeout-protocol.md` | Stable | End-of-session procedures |
| `0006-standard-labels.md` | Stable | GitHub labels |
| `0007-testing-strategy.md` | Stable | Test-first philosophy |

### Templates (01xx) - 10 files

| File | Status | Description |
|------|--------|-------------|
| `0100-template-guide.md` | Stable | How to use templates |
| `0101-issue-template.md` | Stable | GitHub issue format |
| `0102-feature-lld-template.md` | Stable | Low-level design |
| `0103-implementation-report-template.md` | Stable | Post-impl docs |
| `0104-adr-template.md` | Stable | ADR format |
| `0105-implementation-plan-template.md` | Stable | Pre-impl planning |
| `0106-lld-pre-impl-review.md` | Stable | Review checklist |
| `0107-test-script-template.md` | Stable | Test case format |
| `0108-test-report-template.md` | Stable | Test results format |
| `0109-runbook-template.md` | Stable | Operational procedures |

### ADRs (02xx) - 5 files

| File | Status | Description |
|------|--------|-------------|
| `0201-adversarial-audit-philosophy.md` | Stable | Security mindset |
| `0202-claude-staging-pattern.md` | Stable | Safe deployment |
| `0203-git-worktree-isolation.md` | Stable | Multi-agent safety |
| `0204-single-identity-orchestration.md` | Stable | Agent identity |
| `0205-test-first-philosophy.md` | Stable | Quality approach |

### Skills (06xx) - 4 files

| File | Status | Description |
|------|--------|-------------|
| `0600-command-reference.md` | Stable | All 8 commands documented |
| `0601-gemini-dual-review.md` | Stable | AI-to-AI review |
| `0602-gemini-lld-review.md` | Stable | Design review |
| `0699-skill-instructions-index.md` | Stable | Skill index |

### Audits (08xx) - 19 files

| File | Status | Description |
|------|--------|-------------|
| `0800-audit-index.md` | Stable | Master audit list |
| `0801-security-audit.md` | Stable | OWASP security |
| `0802-privacy-audit.md` | Stable | IAPP privacy |
| `0803-code-quality-audit.md` | Stable | Maintainability |
| `0804-accessibility-audit.md` | Stable | WCAG compliance |
| `0805-license-compliance.md` | Stable | OSS licenses |
| `0806-bias-fairness.md` | Stable | AI fairness |
| `0807-explainability.md` | Stable | AI transparency |
| `0808-ai-safety-audit.md` | Stable | Safety measures |
| `0809-agentic-ai-governance.md` | Stable | Agent oversight |
| `0810-ai-management-system.md` | Stable | ISO 42001 |
| `0811-ai-incident-post-mortem.md` | Stable | Failure analysis |
| `0812-ai-supply-chain.md` | Stable | Dependencies |
| `0813-claude-capabilities.md` | Stable | Model features |
| `0814-horizon-scanning-protocol.md` | Stable | Threat monitoring |
| `0815-permission-friction.md` | Stable | Approval overhead |
| `0816-permission-permissiveness.md` | Stable | Access control |
| `0817-agentos-audit.md` | Stable | Self-audit |
| `0899-meta-audit.md` | Stable | Audit the audits |

### Runbooks (09xx) - 3 files

| File | Status | Description |
|------|--------|-------------|
| `0900-runbook-index.md` | Stable | All runbooks |
| `0901-new-project-setup.md` | Stable | Project init |
| `0902-nightly-agentos-audit.md` | Stable | Scheduled audit |

---

## 3. Tools Inventory

| File | Status | Description |
|------|--------|-------------|
| `tools/agentos-generate.py` | Stable | Config generator |
| `tools/agentos-permissions.py` | Stable | Permission manager |
| `tools/zugzwang.py` | Stable | Friction logger |
| `tools/append_session_log.py` | Stable | Session tracking |
| `tools/bash-gate.sh` | Stable | Pre-execution blocking |
| `tools/claude-usage-scraper.py` | Stable | Quota visibility |

---

## 4. Configuration Inventory

| File | Status | Description |
|------|--------|-------------|
| `CLAUDE.md` | Stable | Core agent rules |
| `.claude/project.json.example` | Stable | Project config template |
| `.claude/commands/*.md` | Stable | 8 canonical skills |
| `.claude/templates/*.template` | Stable | Config templates |

---

## 5. Summary Statistics

| Category | Count | Status |
|----------|-------|--------|
| Documentation | 47 | All numbered |
| Tools | 6 | All stable |
| Commands | 8 | All stable |
| Templates | 7 | All stable |
| **Total** | **68** | |

---

## 6. Maintenance Notes

- Review this inventory during `/cleanup --full`
- Update when adding new files
- Run numbering audit if files added without numbers

---

*Last audit: 2026-01-13*
