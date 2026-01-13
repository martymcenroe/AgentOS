# 0898 - Horizon Scanning Protocol

## 1. Purpose

Systematic discovery of emerging AI governance frameworks, standards, and threats that should be reflected in the AgentOS audit suite. Transforms the audit system from reactive (validating existing audits) to proactive (surfacing what's missing).

**Core Question:** "What should we be auditing that we're not?"

**Relationship to Other Audits:**
- **0898 (this):** Discovers gaps, tracks frameworks, triggers new audit creation
- **0899:** Validates existing audits are executed correctly
- **0800:** Index of all audits

---

## 2. Framework Version Tracking

### 2.1 Active Framework Registry

Track current versions of frameworks that inform our audit suite:

| Framework | Current Version | Last Checked | Our Coverage | Status |
|-----------|-----------------|--------------|--------------|--------|
| **OWASP Top 10** | 2025 | 2026-01-09 | 0809 §2 | ✅ Updated |
| **OWASP LLM Top 10** | 2025 | 2026-01-09 | 0809 §3 | ✅ Current |
| **OWASP Agentic Top 10** | 2026 (Dec 2025 release) | 2026-01-09 | 0821 Agentic | ✅ Current |
| **ISO/IEC 42001** | 2023 | 2026-01-09 | 0818 AIMS | ✅ Current |
| **EU AI Act** | 2024 (GPAI: Aug 2025 ✅, High-risk: Aug 2026†) | 2026-01-09 | 0809, 0820 | ⚠️ Monitor |
| **NIST AI RMF** | 1.0 (2023, revision in progress) | 2026-01-09 | 0818, 0823 | ✅ Current |
| **NIST Cyber AI Profile** | IR 8596 Draft (Dec 2025) | 2026-01-09 | None | 📋 Triage |
| **ASVS** | 4.0.3 | 2026-01-09 | 0809 §4 | ✅ Current |
| **CWE Top 25** | 2024 | 2026-01-09 | 0809 §2 | ✅ Current |
| **SPDX AI Profile** | 3.0 | 2026-01-09 | 0819 AIBOM | 📋 Evaluate |

† EU "Digital Omnibus on AI" (Nov 2025) proposes delaying high-risk to Dec 2027 (Annex III) / Aug 2028 (embedded)

### 2.1.1 Framework Triage Queue

**NIST Cyber AI Profile (IR 8596)**
- **Published:** Dec 2025 (Draft)
- **Comment Period Closes:** Jan 30, 2026
- **Workshop:** Jan 14, 2026
- **Relevance:** High (browser extension + AI system)
- **Action:** Monitor for final release, evaluate for 0809/0818 integration

**SPDX 3.0 AI Profile**
- **Status:** Released
- **Relevance:** Medium (for AIBOM in 0819)
- **Action:** Evaluate for formal AIBOM generation in supply chain audit

### 2.2 Version Check Procedure

**Quarterly (or on trigger):**

```bash
# Check OWASP updates
🤖 Search: "OWASP LLM Top 10" site:owasp.org
🤖 Search: "OWASP Agentic" site:genai.owasp.org

# Check ISO updates
🤖 Search: "ISO 42001" updates site:iso.org

# Check NIST updates
🤖 Search: "NIST AI RMF" updates site:nist.gov

# Check EU AI Act implementation
🤖 Search: "EU AI Act" implementation guidance
```

### 2.3 Version Change Response

| Change Type | Response |
|-------------|----------|
| Minor update (clarification) | Note in registry, review relevant audit |
| Major update (new controls) | Gap analysis, update audit or create new |
| New framework published | Triage per §4 |
| Framework deprecated | Review for replacement |

---

## 3. Quarterly Research Protocol

### 3.1 Research Questions

Every quarter, systematically investigate:

| Category | Questions |
|----------|-----------|
| **Standards Bodies** | What new ISO/IEC AI standards published? What's in draft? |
| **OWASP** | Any updates to LLM Top 10? New guidance documents? |
| **Regulatory** | EU AI Act implementation updates? US state AI laws? |
| **Big 4 / Analysts** | What are Deloitte, KPMG, Gartner publishing on AI governance? |
| **Academic** | Major AI safety/security papers with practical implications? |
| **Industry** | What are Microsoft, Google, AWS publishing on responsible AI? |
| **Incidents** | Notable AI incidents that reveal new risk categories? |

### 3.2 Research Sources

| Source | URL | Focus |
|--------|-----|-------|
| OWASP GenAI | genai.owasp.org | LLM/Agentic security |
| ISO | iso.org/ics/35.020 | AI standards |
| NIST AI | nist.gov/artificial-intelligence | US framework |
| EU AI Act | artificialintelligenceact.eu | Regulation |
| Partnership on AI | partnershiponai.org | Industry practices |
| AI Incident Database | incidentdatabase.ai | Failure patterns |
| CSA | cloudsecurityalliance.org | Cloud AI security |
| ISACA | isaca.org | Audit guidance |
| IEEE | ieee.org | Technical standards |

### 3.3 Research Log

| Date | Researcher | Findings | Action Taken |
|------|------------|----------|--------------|
| 2026-01-06 | Claude Opus 4.5 | OWASP Top 10:2025 released (A03 Supply Chain, A10 Exceptions) | Updated 0809 §2 (Issue #180) |
| 2026-01-06 | Claude Opus 4.5 | NIST Cyber AI Profile (IR 8596) draft released Dec 2025 | Added to triage queue |
| 2026-01-06 | Claude Opus 4.5 | EU AI Act GPAI obligations effective Aug 2025 | Updated regulatory triggers |
| 2026-01-06 | Claude Opus 4.5 | Chrome extension security incidents (ShadyPanda, 4.3M users) | Noted in 0809; Aletheia not affected |
| 2026-01-08 | Claude Opus 4.5 | ChrisWiles/claude-code-showcase: Active Hooks architecture | ADOPT - See §4.3 |
| 2026-01-09 | Claude Opus 4.5 | OWASP Agentic Top 10 released Dec 10, 2025 (100+ experts) | Verified 0821 coverage |
| 2026-01-09 | Claude Opus 4.5 | OWASP GenAI promoted to Flagship status (March 2025) | No action required |
| 2026-01-09 | Claude Opus 4.5 | NIST AI RMF revision in progress per AI Action Plan | Monitor for updates |
| 2026-01-09 | Claude Opus 4.5 | EU Digital Omnibus on AI (Nov 2025) may delay high-risk dates | Updated registry note |
| 2026-01-09 | Claude Opus 4.5 | AI Incident Database: 1116+ incidents, 140+ new in 2025 | Monitored; no new risk categories |
| 2026-01-09 | Claude Opus 4.5 | ISO 42001: 76% organizations planning adoption (CSA 2025) | No version change; adoption growing |
| 2026-01-09 | Claude Opus 4.5 | anthropics/claude-code official plugins: code-review, security-guidance, pr-review-toolkit | ADOPT - See §4.3 |

---

## 4. New Framework Triage

### 4.1 Triage Template

When a new framework, standard, or guidance is identified:

```markdown
## Framework Triage: [Name]

**Source:** [Organization]
**Published:** [Date]
**URL:** [Link]

### Relevance Assessment (1-5)

| Factor | Score | Notes |
|--------|-------|-------|
| Applies to our tech stack | | |
| Applies to our risk profile | | |
| Industry adoption momentum | | |
| Regulatory weight | | |
| **Total** | /20 | |

### Gap Analysis

| Framework Requirement | Current Coverage | Gap? |
|-----------------------|------------------|------|
| [Requirement 1] | [Audit 08xx §X] | |
| [Requirement 2] | None | Yes |

### Decision

- [ ] **Adopt** - Create/update audit to incorporate
- [ ] **Monitor** - Track for future adoption
- [ ] **Ignore** - Not relevant to AgentOS

### If Adopting

- Target audit: 08xx
- Effort estimate: [hours]
- Priority: P1/P2/P3
- Issue created: #xxx
```

### 4.2 Triage Criteria

| Score | Interpretation |
|-------|----------------|
| 16-20 | High relevance - prioritize adoption |
| 11-15 | Medium relevance - plan adoption |
| 6-10 | Low relevance - monitor only |
| 1-5 | Not relevant - document decision and ignore |

### 4.3 Completed Triages

#### [2026-01-08] ChrisWiles/claude-code-showcase - Active Hooks Architecture

**Source:** https://github.com/ChrisWiles/claude-code-showcase
**Topic:** Automated Audit & Governance-as-Code
**Researcher:** Claude Opus 4.5

##### Relevance Assessment

| Factor | Score | Notes |
|--------|-------|-------|
| Applies to our tech stack | 5 | Direct `claude-code` integration |
| Applies to our risk profile | 5 | Addresses ADR 0210 (worktree isolation), ADR 0213 (adversarial audit) |
| Industry adoption momentum | 3 | Emerging pattern, limited public examples |
| Regulatory weight | 4 | Supports audit trail requirements |
| **Total** | 17/20 | High relevance |

##### Key Findings

The repository demonstrates a "Shift Left" approach to AI safety using `claude-code` native features:

1. **PostToolUse Hooks**: Run linters immediately after `Edit`/`Write` operations
   - Catches security issues (innerHTML, missing sender.id) before AI moves to next file
   - Tight feedback loop vs pre-commit hooks (fail after 1 file, not 5)

2. **PreToolUse Hooks**: Block operations before they happen
   - Enforce branch protection (ADR 0210) at edit-time, not commit-time
   - Environment variable `$CLAUDE_TOOL_INPUT_FILE_PATH` provides context

3. **Role-Based Agents**: Structured `.claude/agents/` definitions
   - Explicit checklists vs generic "review this" prompts
   - Model-specific assignments (Opus for security review)

##### Gap Analysis

| Framework Requirement | Current Coverage | Gap? |
|-----------------------|------------------|------|
| Real-time lint feedback | Pre-commit only | Yes |
| Branch protection at edit-time | Manual enforcement | Yes |
| Structured security reviewer | Ad-hoc prompts | Yes |
| Agent specialization | None | Yes |

##### Decision

**ADOPT** (Score: 17/20 - High relevance)

##### Implementation

Created staging files in `claude-staging/` for manual deployment:
- `settings.json` - Hook configuration
- `hooks/pre-edit-check.sh` - Branch protection (ADR 0210)
- `hooks/post-edit-lint.sh` - Active ESLint/Ruff integration
- `agents/security-reviewer.md` - Opus-based security reviewer

See `claude-staging/README-DEPLOY.md` for deployment instructions.

#### [2026-01-09] anthropics/claude-code - Official Plugin Architecture

**Source:** https://github.com/anthropics/claude-code/blob/main/plugins/README.md
**Topic:** Official Claude Code Plugin Patterns (code-review, security-guidance, pr-review-toolkit)
**Researcher:** Claude Opus 4.5

##### Relevance Assessment

| Factor | Score | Notes |
|--------|-------|-------|
| Applies to our tech stack | 5 | Official `claude-code` integration patterns |
| Applies to our risk profile | 5 | Security-guidance, code-review address audit gaps |
| Industry adoption momentum | 5 | Official Anthropic patterns, 13 plugins |
| Regulatory weight | 4 | Supports security audit trail, compliance |
| **Total** | 19/20 | High relevance |

##### Key Findings

The official Claude Code repository contains 13 plugins demonstrating production patterns:

1. **code-review Plugin**: Multi-agent parallel PR review
   - 5 parallel Sonnet agents (CLAUDE.md compliance, bugs, history, PR context, comments)
   - Confidence-based scoring to filter false positives
   - Reduces review time from ~5min sequential to ~1min parallel

2. **security-guidance Plugin**: Real-time security warning hook
   - PreToolUse hook monitoring 9+ OWASP patterns
   - Warns before editing files with: eval(), innerHTML, pickle, os.system, etc.
   - Non-blocking (warns but doesn't stop work)

3. **pr-review-toolkit Plugin**: Specialized review agents
   - 6 focused agents: comment-analyzer, test-analyzer, silent-failure-hunter, type-design, code-reviewer, code-simplifier
   - `--focus` flags for targeted reviews

4. **Plugin Architecture Pattern**:
   ```
   plugin-name/
   ├── .claude-plugin/plugin.json
   ├── commands/
   ├── agents/
   ├── skills/
   ├── hooks/
   └── README.md
   ```

##### Gap Analysis

| Plugin Feature | Current Coverage | Gap? |
|----------------|------------------|------|
| Real-time security warnings (PreToolUse) | Post-edit lint only | Yes |
| Multi-agent parallel PR review | Single security-reviewer | Yes |
| Confidence-based filtering | None | Yes |
| Plugin structure standard | Ad-hoc | Minor |

##### Decision

**ADOPT** (Score: 19/20 - High relevance)

##### Implementation

Extended `claude-staging/` with official patterns:

1. **pre-edit-security-warn.sh** - PreToolUse hook scanning 15+ OWASP patterns
   - JS/TS: innerHTML, outerHTML, eval(), new Function(), onMessage without sender.id
   - Python: eval(), exec(), os.system(), subprocess shell=True, pickle.load()
   - Shell: eval, nested command substitution
   - HTML: inline scripts, event handlers (CSP violations)

2. **/code-review command** - Multi-agent parallel review
   - 5 agents: security (Opus), CLAUDE.md compliance, bug detector, code quality, test coverage (Sonnet)
   - Confidence-based filtering (excludes <0.5 findings)
   - Focus modes: `--focus security`, `--focus quality`, `--focus all`

See `claude-staging/README-DEPLOY.md` for deployment instructions.

---

## 5. Trigger Pattern Library

### 5.1 External Triggers

Events that should trigger immediate horizon scanning:

| Trigger | Response | Owner |
|---------|----------|-------|
| OWASP publishes new guidance | Run §3 research protocol for OWASP | Developer |
| ISO publishes AI standard | Triage per §4 | Developer |
| Major AI incident reported | Check if new risk category | Developer |
| EU AI Act deadline approaching | Compliance review | Developer |
| Anthropic policy change | Review Claude Code governance | Developer |
| AWS Bedrock update | Review supply chain, security | Developer |

### 5.2 Internal Triggers

Patterns in our own system that suggest audit gaps:

| Pattern | Indicates | Response |
|---------|-----------|----------|
| Same issue found repeatedly | Audit not preventing | Strengthen audit |
| Issue found in production, not audit | Detection gap | Add test case |
| Agent asks permission too often | Over-restriction | Run 0808 |
| Agent does unexpected action | Under-restriction | Run 0821 |
| User reports false positive | Guardrail tuning needed | Run 0822 |
| User reports harmful content | Safety gap | Run 0809, 0823 |

### 5.3 Regulatory Triggers

| Trigger | Date | Response |
|---------|------|----------|
| EU AI Act - Prohibited practices | Feb 2025 | ✅ Review complete |
| EU AI Act - GPAI obligations | Aug 2, 2025 | ✅ Review complete (Aletheia not GPAI) |
| NIST Cyber AI Profile - Comment period | Jan 30, 2026 | ⚠️ Optional: Submit comments |
| EU AI Act - High-risk obligations | Aug 2, 2026 | ⏳ Plan compliance review Q2 2026 |
| EU AI Act - Legacy systems | Aug 2, 2027 | Monitor |

---

## 6. Emerging Risk Radar

### 6.1 Risk Categories Under Watch

Risks not yet fully addressed in current audits:

| Risk Category | Relevance | Current Coverage | Watch Priority |
|---------------|-----------|------------------|----------------|
| **Model collapse** (training on AI output) | Low (use Bedrock) | None | Low |
| **Agentic swarms** | Low (single agent) | None | Monitor |
| **AI-generated malware** | Medium | 0809 | Monitor |
| **Deepfake integration** | Low | None | Low |
| **Autonomous goal-seeking** | Medium | 0821 | Active |
| **Supply chain poisoning** | Medium | 0819 | Active |
| **Regulatory fragmentation** | Medium | Multiple | Active |

### 6.2 Technology Watch

| Technology | Status | Implication for Audits |
|------------|--------|------------------------|
| Claude 4 / GPT-5 | Expected 2026 | Model upgrade procedures |
| Multi-agent frameworks | Emerging | 0821 expansion needed |
| AI agents in browsers | Emerging | Extension security |
| On-device LLMs | Emerging | Architecture change |
| Federated AI | Research | Privacy implications |

---

## 7. Audit Suite Gap Analysis

### 7.1 Current Coverage Map

| Domain | Audit(s) | Coverage Level |
|--------|----------|----------------|
| Security | 0809 | High |
| Privacy | 0810 | High |
| Code quality | 0811, 0812, 0813, 0814 | High |
| Dependencies | 0816 | Medium |
| Agent governance | 0808, 0815, 0821 | High |
| AI management | 0818 | Medium (new) |
| Supply chain | 0819 | Medium (new) |
| Explainability | 0820 | Low (new) |
| Bias/fairness | 0822 | Low (new) |
| Incident response | 0823 | Medium (new) |
| Meta/discovery | 0898, 0899 | High |

### 7.2 Identified Gaps

| Gap | Severity | Proposed Solution | Status |
|-----|----------|-------------------|--------|
| Continuous compliance automation | Medium | Add to 0899 | Planned |
| Audit effectiveness metrics | Medium | Add to 0899 | Planned |
| Multi-agent governance | Low | Future 0821 update | Monitor |
| Real-time monitoring | Low | Future consideration | Monitor |

---

## 8. Continuous Compliance Integration

### 8.1 Compliance as Code Vision

Long-term goal: audits generate from CI/CD artifacts, not manual checklists.

| Audit | Automation Potential | Current State | Target State |
|-------|----------------------|---------------|--------------|
| 0809 Security | High | Manual | CI security scans |
| 0811 Linting | High | Automated | ✅ Complete |
| 0812 Type checking | High | Automated | ✅ Complete |
| 0813 Test coverage | High | Automated | ✅ Complete |
| 0816 Dependencies | High | Semi-auto | Dependabot + alerts |
| 0819 Supply chain | Medium | Manual | SBOM generation |
| 0821 Agent governance | Low | Manual | Manual (complex) |

### 8.2 Automation Roadmap

| Phase | Target | Audits |
|-------|--------|--------|
| Current | Manual with CLI verification | Most |
| Near-term | CI generates evidence | 0811-0814, 0816 |
| Mid-term | Automated SBOM/AIBOM | 0819 |
| Long-term | Policy-as-code | 0809, 0821 |

---

## 9. Execution Schedule

### 9.1 Quarterly Cycle

| Month | Activity |
|-------|----------|
| **Q Start** | Full horizon scan (§3) |
| **Q Start + 2w** | Triage new frameworks (§4) |
| **Q Mid** | Update Framework Registry (§2) |
| **Q End** | Gap analysis review (§7) |

### 9.2 Event-Driven

| Event | Immediate Action |
|-------|------------------|
| Major framework release | Triage within 1 week |
| Security incident (industry) | Review within 48 hours |
| Regulatory deadline < 6 months | Compliance review |

---

## 10. Audit Record

| Date | Activity | Findings | Actions |
|------|----------|----------|---------|
| 2026-01-06 | Initial creation | 6 new audits identified | Created 0818-0823 |
| 2026-01-06 | Deep mode scan | OWASP 2025, NIST Cyber AI Profile, EU AI Act dates | Updated 0809 §2, added to triage queue |
| 2026-01-09 | Quarterly scan | All frameworks current; OWASP Agentic Top 10 released Dec 10, 2025; EU Digital Omnibus may delay high-risk; AIID at 1116+ incidents | Updated registry, research log |

---

## 11. References

### Horizon Scanning
- [UK Government Horizon Scanning](https://www.gov.uk/government/groups/horizon-scanning-programme-team)
- [OECD AI Policy Observatory](https://oecd.ai/)

### Framework Sources
- [OWASP GenAI](https://genai.owasp.org/)
- [ISO AI Standards](https://www.iso.org/committee/6794475/x/catalogue/)
- [NIST AI](https://www.nist.gov/artificial-intelligence)
- [EU AI Act](https://artificialintelligenceact.eu/)

### Internal
- docs/0899-meta-audit.md - Audit validation
- docs/0800-audit-index.md - Audit suite index

---

## 12. History

| Date | Change |
|------|--------|
| 2026-01-06 | Created. Extracted discovery/horizon scanning from 0899 into dedicated protocol. |
