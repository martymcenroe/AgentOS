# 120 - Feature: Configure LangSmith Project for Tracing

<!-- Template Metadata
Last Updated: 2025-01-06
Updated By: LLD creation for Issue #120
Update Reason: Revision after Gemini Review #1 - Added automated verification scripts
-->

## 1. Context & Goal
* **Issue:** #120
* **Objective:** Create a dedicated "AgentOS" project in LangSmith and enable project-specific tracing for better trace organization and analysis.
* **Status:** Draft
* **Related Issues:** None

### Open Questions
*Questions that need clarification before or during implementation. Remove when resolved.*

- [x] ~~Is LangSmith already configured with API key in `~/.agentos/env`?~~ **RESOLVED: Yes.** Proceed with assumption that base environment exists.
- [x] ~~Should we add validation that traces are being sent correctly after configuration?~~ **RESOLVED: Yes.** Automated via LangSmith SDK verification script.

## 2. Proposed Changes

*This section is the **source of truth** for implementation. Describe exactly what will be built.*

### 2.1 Files Changed

| File | Change Type | Description |
|------|-------------|-------------|
| `~/.agentos/env` | Modify | Uncomment `LANGCHAIN_PROJECT` variable and set to "AgentOS" |
| `scripts/configure_tracing.py` | Add | Setup script to configure tracing and create LangSmith project |
| `tests/integration/test_tracing_config.py` | Add | Automated verification tests for tracing configuration |

### 2.2 Dependencies

*New packages, APIs, or services required.*

```toml
# pyproject.toml additions (if any)
# langsmith already installed as dependency of langchain
```

### 2.3 Data Structures

```python
# Pseudocode - NOT implementation
class TracingConfig(TypedDict):
    project_name: str  # LangSmith project name
    env_file_path: Path  # Path to env file
    configured: bool  # Whether configuration is complete
```

### 2.4 Function Signatures

```python
# scripts/configure_tracing.py
def ensure_langsmith_project(project_name: str) -> bool:
    """Create LangSmith project if it doesn't exist. Returns True if project exists/created."""
    ...

def update_env_file(env_path: Path, project_name: str) -> bool:
    """Update env file with LANGCHAIN_PROJECT variable. Returns True on success."""
    ...

def verify_configuration(project_name: str) -> bool:
    """Verify tracing is configured correctly. Returns True if valid."""
    ...

# tests/integration/test_tracing_config.py
def test_langsmith_project_exists() -> None:
    """T010: Verify AgentOS project exists in LangSmith."""
    ...

def test_env_variable_configured() -> None:
    """T020: Verify LANGCHAIN_PROJECT is set correctly in env file."""
    ...

def test_traces_route_to_project() -> None:
    """T030: Verify traces appear in AgentOS project."""
    ...
```

### 2.5 Logic Flow (Pseudocode)

```
1. Run configure_tracing.py script
   a. Check if LANGSMITH_API_KEY is set
      - IF not set THEN exit with error
   b. Use langsmith client to list projects
   c. IF "AgentOS" project not found THEN
      - Create project via langsmith API
   d. Read ~/.agentos/env file
   e. IF LANGCHAIN_PROJECT line exists commented THEN
      - Uncomment and set to "AgentOS"
   f. ELSE IF LANGCHAIN_PROJECT not present THEN
      - Append export LANGCHAIN_PROJECT="AgentOS"
   g. Write updated env file
   h. Print success message with verification instructions

2. Run automated verification (test_tracing_config.py)
   a. T010: Query LangSmith API for project list, assert "AgentOS" exists
   b. T020: Read env file, assert LANGCHAIN_PROJECT="AgentOS" present and uncommented
   c. T030: Execute dummy LangChain chain, query LangSmith for recent runs in AgentOS project
```

### 2.6 Technical Approach

* **Module:** `scripts/configure_tracing.py`, `tests/integration/test_tracing_config.py`
* **Pattern:** Setup script with automated verification
* **Key Decisions:** Using LangSmith SDK for both project creation and verification eliminates manual UI dependency

### 2.7 Architecture Decisions

*Document key architectural decisions that affect the design.*

| Decision | Options Considered | Choice | Rationale |
|----------|-------------------|--------|-----------|
| Project naming | "AgentOS", "agentos", "agent-os" | "AgentOS" | Matches official project name casing |
| Configuration method | Manual edit, Setup script | Setup script | Reduces user error, enables automation |
| Verification approach | Manual UI check, SDK-based automated tests | SDK-based automated tests | Eliminates manual verification; repeatable |
| Project creation | Manual UI, LangSmith SDK | LangSmith SDK | Enables full automation of setup |

**Architectural Constraints:**
- Must use existing `~/.agentos/env` file structure
- LangSmith SDK must be available (already installed via langchain dependency)
- LANGSMITH_API_KEY must be configured for automation to work

## 3. Requirements

*What must be true when this is done. These become acceptance criteria.*

1. AgentOS project exists in LangSmith dashboard
2. `LANGCHAIN_PROJECT="AgentOS"` is set and exported in `~/.agentos/env`
3. New workflow traces appear in the AgentOS project (not default project)

## 4. Alternatives Considered

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Setup script with SDK automation | Repeatable; testable; reduces user error | Requires langsmith SDK | **Selected** |
| Manual UI configuration | No code changes | Error-prone; not testable; requires manual verification | Rejected |
| Hardcode in application | No user action needed | Less flexible; requires code change | Rejected |
| Use `.env` in repo | Version controlled | User-specific config in repo; security concern | Rejected |

**Rationale:** Using a setup script with LangSmith SDK enables full automation of both configuration and verification, eliminating manual steps and enabling CI integration.

## 5. Data & Fixtures

*Per [0108-lld-pre-implementation-review.md](0108-lld-pre-implementation-review.md) - complete this section BEFORE implementation.*

### 5.1 Data Sources

| Attribute | Value |
|-----------|-------|
| Source | LangSmith SaaS platform API |
| Format | REST API / Python SDK |
| Size | N/A |
| Refresh | Real-time API calls |
| Copyright/License | N/A |

### 5.2 Data Pipeline

```
configure_tracing.py ──SDK──► LangSmith API (create project)
                     ──file──► ~/.agentos/env (update config)

test_tracing_config.py ──SDK──► LangSmith API (verify project, check runs)
                       ──file──► ~/.agentos/env (verify config)
```

### 5.3 Test Fixtures

| Fixture | Source | Notes |
|---------|--------|-------|
| Dummy LangChain chain | Generated in test | Simple chain for trace verification |
| Expected env file content | Hardcoded | Pattern match for LANGCHAIN_PROJECT |

### 5.4 Deployment Pipeline

Configuration is local to each user's environment. Script can be run manually or as part of onboarding.

**If data source is external:** LangSmith SDK handles API interaction; no separate utility needed.

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
| API key exposure | Script uses existing LANGSMITH_API_KEY from environment; no key in code | Addressed |
| Project access control | LangSmith handles project-level access; uses existing org permissions | Addressed |
| Env file permissions | Script preserves existing file permissions | Addressed |

### 7.2 Safety

*Safety concerns focus on preventing data loss, ensuring fail-safe behavior, and protecting system integrity.*

| Concern | Mitigation | Status |
|---------|------------|--------|
| Existing traces lost | Default project traces remain; this creates new project for future traces | Addressed |
| Env file corruption | Script creates backup before modification | Addressed |
| Missing API key | Script exits with clear error if LANGSMITH_API_KEY not set | Addressed |

**Fail Mode:** Fail Closed - Script exits with error if prerequisites not met; no partial configuration

**Recovery Strategy:** Backup of env file created before modification; can restore if needed

## 8. Performance & Cost Considerations

*This section addresses performance and cost concerns (6 patterns) from governance feedback.*

### 8.1 Performance

| Metric | Budget | Approach |
|--------|--------|----------|
| Script execution | < 10s | Single API call for project creation |
| Test execution | < 30s | Includes trace propagation wait time |
| Memory | < 50MB | Minimal SDK usage |

**Bottlenecks:** Trace propagation to LangSmith may take a few seconds; tests include appropriate wait

### 8.2 Cost Analysis

| Resource | Unit Cost | Estimated Usage | Monthly Cost |
|----------|-----------|-----------------|--------------|
| LangSmith | Existing plan | Same as current | No change |
| API calls | Included in plan | 2-3 for setup, 3-5 for tests | Negligible |

**Cost Controls:**
- [x] No additional cost - project organization is a free feature
- [x] Trace volume unchanged
- [x] Test runs minimal traces (1 per test run)

**Worst-Case Scenario:** N/A - one-time setup script with minimal ongoing cost

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

**Testing Philosophy:** All verification is automated via LangSmith SDK. Manual tests eliminated by using programmatic API access.

### 10.0 Test Plan (TDD - Complete Before Implementation)

**TDD Requirement:** Tests written before implementation begins.

| Test ID | Test Description | Expected Behavior | Status |
|---------|------------------|-------------------|--------|
| T010 | test_langsmith_project_exists | SDK query returns "AgentOS" in project list | RED |
| T020 | test_env_variable_configured | Env file contains uncommented LANGCHAIN_PROJECT="AgentOS" | RED |
| T030 | test_traces_route_to_project | After running dummy chain, trace appears in AgentOS project | RED |

**Coverage Target:** 100% for setup script; verification via integration tests

**TDD Checklist:**
- [ ] All tests written before implementation
- [ ] Tests currently RED (failing)
- [ ] Test IDs match scenario IDs in 10.1
- [ ] Test file created at: `tests/integration/test_tracing_config.py`

### 10.1 Test Scenarios

| ID | Scenario | Type | Input | Expected Output | Pass Criteria |
|----|----------|------|-------|-----------------|---------------|
| 010 | Project exists in LangSmith | Auto-Live | LangSmith API query | Project "AgentOS" in list | `"AgentOS" in client.list_projects()` |
| 020 | Env variable is set | Auto | Read ~/.agentos/env | LANGCHAIN_PROJECT="AgentOS" | Regex match passes, line uncommented |
| 030 | Traces route to project | Auto-Live | Run dummy chain | Trace in AgentOS project | Recent run found via API within 30s |
| 040 | Script handles missing API key | Auto | Unset LANGSMITH_API_KEY | Exit with error | Exit code != 0, error message displayed |
| 050 | Script creates backup | Auto | Run script | Backup file exists | ~/.agentos/env.backup exists |

*Note: Use 3-digit IDs with gaps of 10 (010, 020, 030...) to allow insertions.*

### 10.2 Test Commands

```bash
# Run all tracing configuration tests
poetry run pytest tests/integration/test_tracing_config.py -v

# Run only fast/mocked tests (env file checks only)
poetry run pytest tests/integration/test_tracing_config.py -v -m "not live"

# Run live integration tests (requires LangSmith API key)
poetry run pytest tests/integration/test_tracing_config.py -v -m live

# Run the setup script
poetry run python scripts/configure_tracing.py
```

### 10.3 Manual Tests (Only If Unavoidable)

**N/A - All scenarios automated.**

All verification previously marked as manual has been converted to automated tests using the LangSmith SDK:
- Project existence: Verified via `client.list_projects()`
- Env configuration: Verified via file read and regex
- Trace routing: Verified via `client.list_runs(project_name="AgentOS")`

## 11. Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| LangSmith project already exists with same name | Low | Low | Script checks existing projects before creating |
| Env file syntax error after edit | Med | Low | Script creates backup; validates syntax before write |
| Traces still going to default project | Low | Low | Automated test T030 verifies trace routing |
| LangSmith API unavailable | Med | Low | Script retries with exponential backoff; clear error message |
| LANGSMITH_API_KEY not set | Med | Med | Script validates prerequisite and exits with helpful error |

## 12. Definition of Done

### Code
- [ ] `scripts/configure_tracing.py` implemented and linted
- [ ] `tests/integration/test_tracing_config.py` implemented
- [ ] Code comments reference this LLD

### Tests
- [ ] T010 passes: Project exists in LangSmith
- [ ] T020 passes: Env variable configured correctly
- [ ] T030 passes: Traces route to AgentOS project
- [ ] T040 passes: Script handles missing API key
- [ ] T050 passes: Script creates backup

### Documentation
- [ ] LLD updated with any deviations
- [ ] Implementation Report (0103) completed

### Review
- [ ] Code review completed
- [ ] Automated tests passing
- [ ] User approval before closing issue

---

## Appendix: Review Log

*Track all review feedback with timestamps and implementation status.*

### Gemini Review #1 (REVISE)

**Reviewer:** Gemini 3 Pro
**Verdict:** REVISE

#### Comments

| ID | Comment | Implemented? |
|----|---------|--------------|
| G1.1 | "Manual 'Feature' vs. Automation: Convert from manual procedure to setup script" | YES - Added scripts/configure_tracing.py in Section 2.1, 2.4, 2.5 |
| G1.2 | "Section 10.0 TDD Test Plan: TDD is never N/A" | YES - Added full TDD plan with T010-T050 in Section 10.0 |
| G1.3 | "No Human Delegation: Replace manual verification with automated verification script" | YES - Added tests/integration/test_tracing_config.py; Section 10.3 now N/A |
| G1.4 | "Requirement Coverage: 0% Automated Coverage" | YES - All 3 requirements now have automated tests (T010, T020, T030) |
| G1.5 | "Setup Script suggestion" | YES - Added scripts/configure_tracing.py |

### Review Summary

| Review | Date | Verdict | Key Issue |
|--------|------|---------|-----------|
| Gemini #1 | 2025-01-06 | REVISE | Manual verification must be automated via LangSmith SDK |

**Final Status:** PENDING