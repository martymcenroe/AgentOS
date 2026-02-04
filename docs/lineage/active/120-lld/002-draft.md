# 120 - Feature: Configure LangSmith Project for Tracing

<!-- Template Metadata
Last Updated: 2025-01-06
Updated By: LLD creation for Issue #120
Update Reason: Initial LLD creation for LangSmith project configuration
-->

## 1. Context & Goal
* **Issue:** #120
* **Objective:** Create a dedicated "AgentOS" project in LangSmith and enable project-specific tracing for better trace organization and analysis.
* **Status:** Draft
* **Related Issues:** None

### Open Questions
*Questions that need clarification before or during implementation. Remove when resolved.*

- [ ] Is LangSmith already configured with API key in `~/.agentos/env`? (Assumed yes based on "currently using default project")
- [ ] Should we add validation that traces are being sent correctly after configuration?

## 2. Proposed Changes

*This section is the **source of truth** for implementation. Describe exactly what will be built.*

### 2.1 Files Changed

| File | Change Type | Description |
|------|-------------|-------------|
| `~/.agentos/env` | Modify | Uncomment `LANGCHAIN_PROJECT` variable and set to "AgentOS" |

### 2.2 Dependencies

*New packages, APIs, or services required.*

```toml
# pyproject.toml additions (if any)
# None - LangSmith integration already exists
```

### 2.3 Data Structures

```python
# N/A - Configuration change only, no new data structures
```

### 2.4 Function Signatures

```python
# N/A - Configuration change only, no new functions
```

### 2.5 Logic Flow (Pseudocode)

```
1. Create "AgentOS" project in LangSmith UI
   - Navigate to https://smith.langchain.com
   - Go to Projects → New Project
   - Enter name: "AgentOS"
   - Save project
2. Update environment configuration
   - Open ~/.agentos/env
   - Find commented LANGCHAIN_PROJECT line
   - Uncomment and set to: export LANGCHAIN_PROJECT="AgentOS"
   - Save file
3. Verify configuration
   - Source the env file or start new terminal
   - Run an AgentOS workflow
   - Check LangSmith AgentOS project for new traces
```

### 2.6 Technical Approach

* **Module:** N/A (configuration only)
* **Pattern:** Environment variable configuration
* **Key Decisions:** Using environment file approach maintains consistency with existing AgentOS configuration patterns

### 2.7 Architecture Decisions

*Document key architectural decisions that affect the design.*

| Decision | Options Considered | Choice | Rationale |
|----------|-------------------|--------|-----------|
| Project naming | "AgentOS", "agentos", "agent-os" | "AgentOS" | Matches official project name casing |
| Configuration location | `~/.agentos/env`, `.env` in repo, hardcoded | `~/.agentos/env` | Issue specifies this location; keeps user-specific config separate from repo |

**Architectural Constraints:**
- Must use existing `~/.agentos/env` file structure
- Cannot require code changes to AgentOS application

## 3. Requirements

*What must be true when this is done. These become acceptance criteria.*

1. AgentOS project exists in LangSmith dashboard
2. `LANGCHAIN_PROJECT="AgentOS"` is set and exported in `~/.agentos/env`
3. New workflow traces appear in the AgentOS project (not default project)

## 4. Alternatives Considered

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Environment file configuration | Consistent with existing setup; user-specific | Manual edit required | **Selected** |
| Hardcode in application | No user action needed | Less flexible; requires code change | Rejected |
| Use `.env` in repo | Version controlled | User-specific config in repo; security concern | Rejected |

**Rationale:** Using `~/.agentos/env` maintains the existing configuration pattern and keeps user-specific settings (like project names) separate from the codebase.

## 5. Data & Fixtures

*Per [0108-lld-pre-implementation-review.md](0108-lld-pre-implementation-review.md) - complete this section BEFORE implementation.*

### 5.1 Data Sources

| Attribute | Value |
|-----------|-------|
| Source | LangSmith SaaS platform |
| Format | Environment variable (string) |
| Size | N/A |
| Refresh | Static configuration |
| Copyright/License | N/A |

### 5.2 Data Pipeline

```
~/.agentos/env ──sourced──► Shell Environment ──LANGCHAIN_PROJECT──► LangChain SDK ──traces──► LangSmith API
```

### 5.3 Test Fixtures

| Fixture | Source | Notes |
|---------|--------|-------|
| N/A | N/A | Configuration change; verification via live traces |

### 5.4 Deployment Pipeline

Configuration is local to each user's environment. No deployment pipeline required.

**If data source is external:** N/A - LangSmith project creation is a one-time manual operation.

## 6. Diagram
*N/A - Simple configuration change does not warrant an architecture diagram.*

### 6.1 Mermaid Quality Gate

N/A - No diagram required for this configuration task.

### 6.2 Diagram

N/A

## 7. Security & Safety Considerations

*This section addresses security (10 patterns) and safety (9 patterns) concerns from governance feedback.*

### 7.1 Security

| Concern | Mitigation | Status |
|---------|------------|--------|
| API key exposure | API key already managed in env file; no changes to key handling | Addressed |
| Project access control | LangSmith handles project-level access; uses existing org permissions | Addressed |

### 7.2 Safety

*Safety concerns focus on preventing data loss, ensuring fail-safe behavior, and protecting system integrity.*

| Concern | Mitigation | Status |
|---------|------------|--------|
| Existing traces lost | Default project traces remain; this creates new project for future traces | Addressed |
| Misconfigured variable | If LANGCHAIN_PROJECT is invalid, LangSmith SDK falls back gracefully | Addressed |

**Fail Mode:** Fail Open - If project name is invalid, traces go to default project (no data loss)

**Recovery Strategy:** If traces don't appear in AgentOS project, verify env variable is exported and restart terminal session

## 8. Performance & Cost Considerations

*This section addresses performance and cost concerns (6 patterns) from governance feedback.*

### 8.1 Performance

| Metric | Budget | Approach |
|--------|--------|----------|
| Latency | No change | Configuration only; no runtime impact |
| Memory | No change | Single environment variable |
| API Calls | No change | Same traces, different project routing |

**Bottlenecks:** None - this is a configuration change only

### 8.2 Cost Analysis

| Resource | Unit Cost | Estimated Usage | Monthly Cost |
|----------|-----------|-----------------|--------------|
| LangSmith | Existing plan | Same as current | No change |

**Cost Controls:**
- [x] No additional cost - project organization is a free feature
- [x] Trace volume unchanged

**Worst-Case Scenario:** N/A - configuration change only

## 9. Legal & Compliance

*This section addresses legal concerns (8 patterns) from governance feedback.*

| Concern | Applies? | Mitigation |
|---------|----------|------------|
| PII/Personal Data | No | Tracing content unchanged |
| Third-Party Licenses | N/A | Using existing LangSmith service |
| Terms of Service | Yes | Within normal LangSmith usage patterns |
| Data Retention | N/A | Governed by existing LangSmith configuration |
| Export Controls | N/A | No changes to data being sent |

**Data Classification:** Internal (traces contain workflow execution data)

**Compliance Checklist:**
- [x] No PII stored without consent
- [x] All third-party licenses compatible with project license
- [x] External API usage compliant with provider ToS
- [x] Data retention policy documented (via LangSmith settings)

## 10. Verification & Testing

*Ref: [0005-testing-strategy-and-protocols.md](0005-testing-strategy-and-protocols.md)*

**Testing Philosophy:** This is a configuration task; verification is manual by necessity (requires UI interaction and live service).

### 10.0 Test Plan (TDD - Complete Before Implementation)

**TDD Requirement:** N/A - Configuration task, not code implementation.

| Test ID | Test Description | Expected Behavior | Status |
|---------|------------------|-------------------|--------|
| T010 | Verify env file contains LANGCHAIN_PROJECT | Variable is uncommented and set to "AgentOS" | N/A |
| T020 | Verify traces appear in LangSmith | New traces visible in AgentOS project | N/A |

**Coverage Target:** N/A - Manual verification

**TDD Checklist:**
- [x] N/A - Configuration task, verification is inherently manual

### 10.1 Test Scenarios

| ID | Scenario | Type | Input | Expected Output | Pass Criteria |
|----|----------|------|-------|-----------------|---------------|
| 010 | Project exists in LangSmith | Manual | Navigate to LangSmith | AgentOS project visible | Project listed in Projects view |
| 020 | Env variable is set | Manual | `cat ~/.agentos/env \| grep LANGCHAIN_PROJECT` | `export LANGCHAIN_PROJECT="AgentOS"` | Line is uncommented and correct |
| 030 | Traces route to project | Auto-Live | Run any AgentOS workflow | Trace appears in AgentOS project | Trace visible within 30 seconds |

*Note: Use 3-digit IDs with gaps of 10 (010, 020, 030...) to allow insertions.*

### 10.2 Test Commands

```bash
# Verify environment variable is set
grep -v "^#" ~/.agentos/env | grep LANGCHAIN_PROJECT

# Verify variable is exported in current shell
echo $LANGCHAIN_PROJECT

# Run a workflow to generate a trace (example)
cd ~/agentos && poetry run python -c "from agentos import workflow; workflow.run_test()"
```

### 10.3 Manual Tests (Only If Unavoidable)

**Justification:** LangSmith project creation requires browser-based UI interaction; verification requires viewing external dashboard.

| ID | Scenario | Why Not Automated | Steps |
|----|----------|-------------------|-------|
| 010 | Create LangSmith project | Requires authenticated browser session and UI interaction | 1. Go to smith.langchain.com 2. Login 3. Navigate to Projects 4. Click New Project 5. Enter "AgentOS" 6. Save |
| 030 | Verify trace appears | Requires visual confirmation in LangSmith UI | 1. Run workflow 2. Open LangSmith 3. Navigate to AgentOS project 4. Verify trace entry exists |

*Full test results recorded in Implementation Report (0103) or Test Report (0113).*

## 11. Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| LangSmith project already exists with same name | Low | Low | Check existing projects before creating |
| Env file syntax error after edit | Med | Low | Verify shell sources file correctly after edit |
| Traces still going to default project | Low | Low | Verify env variable is exported, not just set |

## 12. Definition of Done

### Code
- [x] No code changes required
- [x] N/A - Configuration only

### Tests
- [ ] LangSmith project "AgentOS" exists
- [ ] `~/.agentos/env` contains uncommented `LANGCHAIN_PROJECT="AgentOS"`
- [ ] At least one trace appears in AgentOS project after workflow run

### Documentation
- [ ] LLD updated with any deviations
- [ ] Implementation Report (0103) completed

### Review
- [ ] Configuration verified by user
- [ ] User approval before closing issue

---

## Appendix: Review Log

*Track all review feedback with timestamps and implementation status.*

### Review Summary

| Review | Date | Verdict | Key Issue |
|--------|------|---------|-----------|
| - | - | - | Awaiting review |

**Final Status:** PENDING