# Brief: The Watch - Regression Guardian Workflow

**Status:** Brief
**Priority:** High (prevents tech debt accumulation)
**Created:** 2026-02-01
**Inspiration:** Terry Pratchett's City Watch (Discworld)

---

## Problem Statement

Test failures accumulate silently. We just discovered 18 failing tests that had been broken for an unknown period. Without scheduled regression testing:

1. Refactoring breaks tests that nobody notices
2. Dependabot PRs can't be safely merged (no clean baseline)
3. "Works on my machine" becomes the standard
4. Tech debt compounds until a painful cleanup sprint

The Janitor (Issue #94) handles repository hygiene but doesn't run the test suite. We need a dedicated quality guardian.

---

## Proposed Solution: The Watch

A scheduled workflow that:
1. Runs the full test suite on a schedule (nightly, or on-demand)
2. Compares results against known baseline
3. Detects NEW failures (not pre-existing known issues)
4. Creates GitHub issues for regressions automatically
5. Blocks risky operations (like Dependabot merges) when baseline is unhealthy

*"We do not sleep. We are The Watch."*

---

## Key Concepts

### 1. Baseline Management

```python
# .watch/baseline.json
{
    "last_run": "2026-02-01T03:00:00Z",
    "total_tests": 547,
    "passed": 541,
    "failed": 5,
    "skipped": 1,
    "known_failures": [
        "tests/test_audit_sharding.py::TestTailMerges::test_merges_history_and_shards",
        "tests/test_gemini_client.py::TestCredentialLoading::test_loads_credentials_from_file",
        # ... etc
    ],
    "tracked_issues": {
        "tests/test_audit_sharding.py::TestTailMerges::test_merges_history_and_shards": 107,
        # maps test to GitHub issue
    }
}
```

### 2. Regression Detection

```
Current Run vs Baseline:
├── New failures? → Create issues, alert
├── Fixed tests? → Close issues, celebrate
├── Same failures? → No action (known issues)
└── Baseline healthy (0 unknown failures)? → Green light for Dependabot
```

### 3. Health Status API

```python
def get_health_status() -> HealthStatus:
    """Used by other workflows to check if it's safe to proceed."""
    return HealthStatus(
        healthy=len(unknown_failures) == 0,
        known_failures=5,
        unknown_failures=0,
        last_run="2026-02-01T03:00:00Z",
        dependabot_safe=True,
    )
```

---

## Integration Points

### With Dependabot Workflow
```python
# In dependabot workflow
health = watch.get_health_status()
if not health.dependabot_safe:
    print("ABORT: Test baseline unhealthy. Fix regressions first.")
    return 1
```

### With Janitor
The Watch could be a probe in the Janitor, OR a separate workflow that the Janitor queries. Separate workflow is cleaner - different concerns:
- Janitor: Repository hygiene (links, worktrees, drift)
- Watch: Code quality (tests, coverage, regressions)

### With CI/CD
- Can run as GitHub Action on schedule
- Can run as pre-merge check
- Provides clear "go/no-go" for releases

---

## Workflow Nodes

```
N0_collect_baseline
    ↓
N1_run_tests (poetry run pytest --tb=line -q)
    ↓
N2_compare_results
    ↓
    ├── New failures → N3_create_issues
    ├── Fixed tests → N4_close_issues
    └── No change → N5_update_baseline
    ↓
N6_report_status
```

---

## CLI Interface

```bash
# Run full watch check
python tools/run_watch.py

# Check health without running tests (uses cached baseline)
python tools/run_watch.py --status

# Update baseline (acknowledge current failures as "known")
python tools/run_watch.py --update-baseline

# Run but don't create issues (CI mode)
python tools/run_watch.py --no-issues

# JSON output for programmatic use
python tools/run_watch.py --json
```

---

## Output Example

```
================================================================================
                        THE WATCH - REGRESSION REPORT
              "We do not sleep. We are The Watch." - Ankh-Morpork
================================================================================
Last baseline: 2026-02-01T03:00:00Z
Current run:   2026-02-01T15:30:00Z

Tests:    547 total, 541 passed, 5 failed, 1 skipped

KNOWN FAILURES (5) - tracked in issues:
  ✓ #107: test_audit_sharding::test_merges_history_and_shards
  ✓ #108: test_gemini_client::test_loads_credentials_from_file
  ✓ #109: test_gemini_client::test_090_429_triggers_rotation
  ✓ #110: test_gemini_client::test_100_529_triggers_backoff
  ✓ #111: test_gemini_client::test_110_all_credentials_exhausted

NEW REGRESSIONS (0):
  None! 🎉

FIXED TESTS (0):
  None

STATUS: ✅ HEALTHY (all failures tracked)
DEPENDABOT: ✅ SAFE TO MERGE
================================================================================
```

---

## Acceptance Criteria

1. [ ] Runs full pytest suite and captures results
2. [ ] Compares against stored baseline
3. [ ] Creates GitHub issues for NEW failures only
4. [ ] Closes issues when tests are fixed
5. [ ] Provides health status API for other workflows
6. [ ] `--status` shows current health without running tests
7. [ ] `--update-baseline` acknowledges current state
8. [ ] JSON output for CI integration
9. [ ] Clear distinction: known failures vs unknown regressions

---

## The Ankh-Morpork Municipal Workflow Family

| Workflow | Role | Metaphor |
|----------|------|----------|
| **The Janitor** | Cleans up messes | Reactive maintenance |
| **The Watch** | Guards against regressions | Proactive defense |
| **The Historian** | Learns from past | Memory & context |
| **The Librarian** | Finds information | Knowledge retrieval (ook!) |
| **The Scout** | Reconnaissance | Early exploration |

The Watch stands guard. It doesn't fix problems—it detects them early and raises the alarm before they compound. Commander Vimes would approve.

---

## Dependencies

- pytest (already installed)
- GitHub CLI (`gh`) for issue management
- `.watch/` directory for baseline storage

---

## Future Enhancements

- Coverage tracking (alert on coverage drops)
- Performance regression detection (test duration trends)
- Flaky test detection (tests that pass/fail inconsistently)
- Slack/Discord notifications for regressions
- Dashboard showing test health over time

---

## References

- Issue #94: The Janitor (complementary workflow)
- Issue #107-111: Current known test failures
- `ideas/active/dependabot-workflow-automation.md` - needs Watch integration
