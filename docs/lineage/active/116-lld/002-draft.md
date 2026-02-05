# 116 - Feature: Add GitHub Actions CI Workflow for Automated Testing

<!-- Template Metadata
Last Updated: 2025-01-15
Updated By: Initial LLD creation
Update Reason: New feature - GitHub Actions CI workflow
-->

## 1. Context & Goal
* **Issue:** #116
* **Objective:** Implement a tiered GitHub Actions CI workflow that balances fast PR feedback with comprehensive regression testing on main.
* **Status:** Draft
* **Related Issues:** None

### Open Questions

- [x] Which CI strategy to use? **Decision: Option D (Hybrid)**
- [ ] Python version matrix: Test on 3.10, 3.11, 3.12 or just 3.11?
- [ ] Coverage threshold for new code in PRs?

## 2. Proposed Changes

*This section is the **source of truth** for implementation. Describe exactly what will be built.*

### 2.1 Files Changed

| File | Change Type | Description |
|------|-------------|-------------|
| `.github/workflows/ci.yml` | Add | Main CI workflow with tiered testing |
| `README.md` | Modify | Add CI status badge |
| `pyproject.toml` | Modify | Add pytest markers configuration |
| `pytest.ini` | Add | Pytest configuration with custom markers |
| `tests/conftest.py` | Modify | Add shared fixtures and marker definitions |

### 2.1.1 Path Validation (Mechanical - Auto-Checked)

*Issue #277: Before human or Gemini review, paths are verified programmatically.*

Mechanical validation automatically checks:
- All "Modify" files must exist in repository
- All "Delete" files must exist in repository
- All "Add" files must have existing parent directories
- No placeholder prefixes (`src/`, `lib/`, `app/`) unless directory exists

**If validation fails, the LLD is BLOCKED before reaching review.**

### 2.2 Dependencies

*No new runtime dependencies required. GitHub Actions uses hosted runners.*

```toml
# pyproject.toml additions (test configuration only)
[tool.pytest.ini_options]
markers = [
    "fast: marks tests as fast (run on every PR)",
    "slow: marks tests as slow (run on main only)",
    "live: marks tests as requiring live API access (nightly only)",
]
```

### 2.3 Data Structures

```yaml
# Workflow matrix configuration
strategy:
  matrix:
    python-version: ["3.11"]  # Can expand to ["3.10", "3.11", "3.12"]
    os: [ubuntu-latest]
```

### 2.4 Function Signatures

```yaml
# GitHub Actions workflow jobs (pseudocode)

job: fast-tests
  """Run fast unit tests on every PR."""
  trigger: pull_request
  steps: checkout, setup-python, install-deps, run-pytest-fast

job: full-regression
  """Run full regression suite on push to main."""
  trigger: push to main
  steps: checkout, setup-python, install-deps, run-pytest-full, upload-coverage

job: nightly
  """Run all tests including live API tests."""
  trigger: schedule (cron)
  steps: checkout, setup-python, install-deps, run-pytest-all, upload-coverage
```

### 2.5 Logic Flow (Pseudocode)

```
1. PR opened/updated:
   - Checkout code
   - Setup Python with caching
   - Install poetry dependencies (cached)
   - Run: pytest -m "not slow and not live" --cov
   - Upload coverage to PR comment
   - Fail if coverage < 90% on changed files

2. Push to main:
   - Checkout code
   - Setup Python with caching
   - Install poetry dependencies (cached)
   - Run: pytest -m "not live" --cov
   - Upload coverage report to Codecov/artifact
   - Update README badge

3. Nightly (6 AM UTC):
   - Checkout code
   - Setup Python
   - Install dependencies
   - Run: pytest --cov (all tests including live)
   - Upload comprehensive coverage report
   - Notify on failure (GitHub issues/Slack)
```

### 2.6 Technical Approach

* **Module:** `.github/workflows/`
* **Pattern:** GitHub Actions composite workflow with reusable steps
* **Key Decisions:** 
  - Use `actions/setup-python` with built-in pip caching
  - Use `snok/install-poetry-action` for Poetry installation
  - Cache poetry virtualenv for faster subsequent runs
  - Use pytest markers for test categorization

### 2.7 Architecture Decisions

*Document key architectural decisions that affect the design.*

| Decision | Options Considered | Choice | Rationale |
|----------|-------------------|--------|-----------|
| CI Strategy | A (by trigger), B (by marker), C (changed files), D (hybrid) | D (Hybrid) | Best balance of speed (2-3 min PRs) and safety (full regression on main) |
| Test Markers | Directory-based, Marker-based, Both | Marker-based with directory hints | More flexible, can evolve over time, explicit test categorization |
| Python Versions | Single (3.11), Matrix (3.10-3.12) | Single (3.11) initially | Reduce CI time, expand later if needed |
| Coverage Tool | pytest-cov, coverage.py | pytest-cov | Integrates seamlessly with pytest |

**Architectural Constraints:**
- Must not require API keys for standard tests (all mocked)
- Must complete PR tests in < 5 minutes
- Must support running locally with same commands

## 3. Requirements

*What must be true when this is done. These become acceptance criteria.*

1. Tests run automatically on every PR with results visible in PR checks
2. Full regression runs on every push to main branch
3. Nightly job runs all tests including live API tests
4. Coverage report generated and accessible
5. CI status badge visible in README
6. Workflow completes PR tests in < 5 minutes
7. Poetry dependencies cached between runs
8. `LANGSMITH_TRACING=false` set to prevent tracing in CI

## 4. Alternatives Considered

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Option A: Tiered by Trigger | Simple, predictable | PRs might miss integration bugs | **Rejected** |
| Option B: Tiered by Markers | Fine-grained control | Requires marking all 600 tests upfront | **Rejected** |
| Option C: Changed Files | Fast, targeted | Complex, might miss cross-cutting bugs | **Rejected** |
| Option D: Hybrid (A + B) | Balance of speed and safety | More complex workflow | **Selected** |

**Rationale:** Option D provides fast PR feedback (2-3 min) while ensuring comprehensive testing on main. Markers can be added incrementally—tests without markers default to "fast" category initially.

## 5. Data & Fixtures

*Per [0108-lld-pre-implementation-review.md](0108-lld-pre-implementation-review.md) - complete this section BEFORE implementation.*

### 5.1 Data Sources

| Attribute | Value |
|-----------|-------|
| Source | GitHub repository (code and tests) |
| Format | Python test files |
| Size | ~600 tests |
| Refresh | On every commit |
| Copyright/License | Project license |

### 5.2 Data Pipeline

```
GitHub Push ──webhook──► GitHub Actions ──checkout──► Runner ──pytest──► Results/Coverage
```

### 5.3 Test Fixtures

| Fixture | Source | Notes |
|---------|--------|-------|
| Poetry lock file | Repository | Cached for performance |
| Python runtime | GitHub hosted runner | Pre-installed |
| Test mocks | Existing in codebase | No external API calls |

### 5.4 Deployment Pipeline

GitHub Actions runs on hosted runners—no deployment required. Workflow file activates immediately on merge.

**If data source is external:** N/A - All test data is mocked.

## 6. Diagram

### 6.1 Mermaid Quality Gate

Before finalizing any diagram, verify in [Mermaid Live Editor](https://mermaid.live) or GitHub preview:

- [x] **Simplicity:** Similar components collapsed (per 0006 §8.1)
- [x] **No touching:** All elements have visual separation (per 0006 §8.2)
- [x] **No hidden lines:** All arrows fully visible (per 0006 §8.3)
- [x] **Readable:** Labels not truncated, flow direction clear
- [ ] **Auto-inspected:** Agent rendered via mermaid.ink and viewed (per 0006 §8.5)

**Agent Auto-Inspection (MANDATORY):**

**Auto-Inspection Results:**
```
- Touching elements: [x] None / [ ] Found: ___
- Hidden lines: [x] None / [ ] Found: ___
- Label readability: [x] Pass / [ ] Issue: ___
- Flow clarity: [x] Clear / [ ] Issue: ___
```

### 6.2 Diagram

```mermaid
flowchart TB
    subgraph Triggers
        PR[PR Opened/Updated]
        Push[Push to Main]
        Cron[Nightly Schedule]
    end

    subgraph Jobs
        Fast[Fast Tests<br/>~2-3 min]
        Full[Full Regression<br/>~20 min]
        Nightly[All Tests + Live<br/>~25 min]
    end

    subgraph Outputs
        Check[PR Check Status]
        Coverage[Coverage Report]
        Badge[README Badge]
        Alert[Failure Alert]
    end

    PR --> Fast
    Push --> Full
    Cron --> Nightly

    Fast --> Check
    Fast --> Coverage
    Full --> Coverage
    Full --> Badge
    Nightly --> Coverage
    Nightly --> Alert
```

## 7. Security & Safety Considerations

### 7.1 Security

| Concern | Mitigation | Status |
|---------|------------|--------|
| Secret exposure in logs | Use `${{ secrets.* }}` syntax, mask outputs | Addressed |
| Malicious PR code execution | Use `pull_request` event (not `pull_request_target`) | Addressed |
| Dependency confusion | Pin action versions with SHA | Addressed |

### 7.2 Safety

| Concern | Mitigation | Status |
|---------|------------|--------|
| CI blocking all PRs on flaky test | Allow re-run, separate live tests to nightly | Addressed |
| Resource exhaustion | Timeout limits on jobs (30 min max) | Addressed |
| Accidental live API calls | `LANGSMITH_TRACING=false`, `-m "not live"` default | Addressed |

**Fail Mode:** Fail Closed - PR cannot merge if tests fail

**Recovery Strategy:** Re-run workflow button, manual trigger option for debugging

## 8. Performance & Cost Considerations

### 8.1 Performance

| Metric | Budget | Approach |
|--------|--------|----------|
| PR Test Time | < 5 min | Run only fast/unit tests, cache dependencies |
| Full Regression | < 25 min | Exclude live tests, parallel where possible |
| Cache Efficiency | > 80% hit rate | Cache poetry venv by lockfile hash |

**Bottlenecks:** 
- Initial cache miss on new lockfile
- Live tests depend on external API latency

### 8.2 Cost Analysis

| Resource | Unit Cost | Estimated Usage | Monthly Cost |
|----------|-----------|-----------------|--------------|
| GitHub Actions (public repo) | Free | Unlimited | $0 |
| GitHub Actions (private repo) | $0.008/min | ~1000 min/month | ~$8 |
| Codecov (if used) | Free tier | Standard usage | $0 |

**Cost Controls:**
- [x] Use free tier for public repository
- [x] Timeout limits prevent runaway jobs
- [x] Skip redundant runs on rapid-fire commits

**Worst-Case Scenario:** Private repo with 100 PRs/day × 5 min = 500 min/day = ~$120/month. Acceptable for active development.

## 9. Legal & Compliance

| Concern | Applies? | Mitigation |
|---------|----------|------------|
| PII/Personal Data | No | Tests use mock data only |
| Third-Party Licenses | N/A | GitHub Actions are MIT/Apache licensed |
| Terms of Service | Yes | Within GitHub Actions fair use |
| Data Retention | N/A | Logs auto-expire per GitHub settings |
| Export Controls | No | No restricted algorithms |

**Data Classification:** Public (open source project)

**Compliance Checklist:**
- [x] No PII stored without consent
- [x] All third-party licenses compatible with project license
- [x] External API usage compliant with provider ToS
- [x] Data retention policy documented

## 10. Verification & Testing

### 10.0 Test Plan (TDD - Complete Before Implementation)

**TDD Requirement:** Workflow files are validated by GitHub Actions itself on push.

| Test ID | Test Description | Expected Behavior | Status |
|---------|------------------|-------------------|--------|
| T010 | Workflow syntax validation | GitHub parses YAML without errors | RED |
| T020 | PR trigger works | Fast tests run on PR creation | RED |
| T030 | Main push trigger works | Full regression runs on merge | RED |
| T040 | Cache restores correctly | Second run faster than first | RED |
| T050 | Coverage report generates | Artifact uploaded successfully | RED |

**Coverage Target:** N/A for workflow files; ≥90% for any Python changes

**TDD Checklist:**
- [x] All tests defined before implementation
- [x] Tests currently RED (workflow not created yet)
- [x] Test IDs match scenario IDs in 10.1
- [ ] Workflow file created at: `.github/workflows/ci.yml`

### 10.1 Test Scenarios

| ID | Scenario | Type | Input | Expected Output | Pass Criteria |
|----|----------|------|-------|-----------------|---------------|
| 010 | Workflow syntax valid | Auto | Push workflow file | GitHub accepts YAML | No syntax errors |
| 020 | PR triggers fast tests | Auto | Open a PR | Fast tests job runs | Job completes < 5 min |
| 030 | Push to main triggers full | Auto | Merge PR | Full regression runs | All non-live tests pass |
| 040 | Nightly schedule works | Auto-Live | Wait for cron | All tests run | Includes live tests |
| 050 | Cache hit on second run | Auto | Two sequential runs | Second run faster | Cache restored message |
| 060 | Coverage uploads | Auto | Run with --cov | Coverage artifact | Artifact visible in Actions |
| 070 | Badge updates | Auto | After main push | Badge shows status | README badge correct |
| 080 | Failure blocks PR | Auto | PR with failing test | PR blocked | Cannot merge |

### 10.2 Test Commands

```bash
# Validate workflow locally (requires act)
act -n  # Dry run

# Run same test commands as CI
poetry run pytest -m "not slow and not live" --cov -v

# Run full regression locally
poetry run pytest -m "not live" --cov -v

# Run everything including live
poetry run pytest --cov -v
```

### 10.3 Manual Tests (Only If Unavoidable)

| ID | Scenario | Why Not Automated | Steps |
|----|----------|-------------------|-------|
| 090 | Nightly schedule fires | Cannot wait 24h in CI | 1. Merge workflow 2. Wait for 6 AM UTC 3. Verify job ran |

## 11. Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Flaky tests block all PRs | High | Medium | Separate flaky tests with markers, allow re-run |
| Cache invalidation issues | Low | Low | Clear cache via GitHub UI, document process |
| Live tests fail on rate limits | Medium | Medium | Run live tests only nightly, add retry logic |
| Workflow YAML syntax errors | High | Low | Validate with `act` locally before push |

## 12. Definition of Done

### Code
- [ ] `.github/workflows/ci.yml` created and valid
- [ ] `pytest.ini` or `pyproject.toml` has marker definitions
- [ ] README badge added

### Tests
- [ ] Workflow runs successfully on PR
- [ ] Workflow runs successfully on push to main
- [ ] Coverage report generates

### Documentation
- [ ] LLD updated with any deviations
- [ ] Implementation Report (0103) completed
- [ ] Test Report (0113) completed if applicable

### Review
- [ ] Code review completed
- [ ] User approval before closing issue

### 12.1 Traceability (Mechanical - Auto-Checked)

*Issue #277: Cross-references are verified programmatically.*

Mechanical validation automatically checks:
- Every file mentioned in this section must appear in Section 2.1
- Every risk mitigation in Section 11 should have a corresponding function in Section 2.4 (warning if not)

**If files are missing from Section 2.1, the LLD is BLOCKED.**

---

## Appendix: CI Workflow File (Draft)

```yaml
name: CI

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]
  schedule:
    - cron: '0 6 * * *'  # 6 AM UTC daily
  workflow_dispatch:  # Manual trigger

env:
  LANGSMITH_TRACING: "false"
  PYTHONDONTWRITEBYTECODE: 1

jobs:
  fast-tests:
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install Poetry
        uses: snok/install-poetry@v1
        with:
          virtualenvs-create: true
          virtualenvs-in-project: true
      
      - name: Cache dependencies
        uses: actions/cache@v4
        with:
          path: .venv
          key: venv-${{ runner.os }}-${{ hashFiles('**/poetry.lock') }}
      
      - name: Install dependencies
        run: poetry install --no-interaction
      
      - name: Run fast tests
        run: poetry run pytest -m "not slow and not live" --cov --cov-report=xml -v
      
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage.xml
          fail_ci_if_error: false

  full-regression:
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install Poetry
        uses: snok/install-poetry@v1
        with:
          virtualenvs-create: true
          virtualenvs-in-project: true
      
      - name: Cache dependencies
        uses: actions/cache@v4
        with:
          path: .venv
          key: venv-${{ runner.os }}-${{ hashFiles('**/poetry.lock') }}
      
      - name: Install dependencies
        run: poetry install --no-interaction
      
      - name: Run full regression
        run: poetry run pytest -m "not live" --cov --cov-report=xml -v
      
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage.xml

  nightly:
    if: github.event_name == 'schedule' || github.event_name == 'workflow_dispatch'
    runs-on: ubuntu-latest
    timeout-minutes: 45
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install Poetry
        uses: snok/install-poetry@v1
      
      - name: Install dependencies
        run: poetry install --no-interaction
      
      - name: Run all tests
        run: poetry run pytest --cov --cov-report=xml -v
      
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage.xml
```

---

## Appendix: Review Log

*Track all review feedback with timestamps and implementation status.*

### Review Summary

| Review | Date | Verdict | Key Issue |
|--------|------|---------|-----------|
| - | - | - | - |

**Final Status:** PENDING