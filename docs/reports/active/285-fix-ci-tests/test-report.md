# Test Report - Fix CI and Skip Integration Tests (#285)

## Test Command Executed
`poetry run pytest tests/unit/ -v --tb=short`

## Full Test Output Summary
```
========================================== test session starts ==========================================
platform win32 -- Python 3.14.0, pytest-9.0.2, pluggy-1.6.0 -- C:\Users\mcwiz\AppData\Local\pypoetry\Cache\virtualenvs\unleashed-Zukdy2xA-py3.14\Scripts\python.exe
cachedir: .pytest_cache
benchmark: 5.2.3 (defaults: timer=time.perf_counter disable_gc=False min_rounds=5 min_time=0.000005 max_time=1.0 calibration_precision=10 warmup=False warmup_iterations=100000)
rootdir: C:\Users\mcwiz\Projects\AssemblyZero
configfile: pyproject.toml
plugins: anyio-4.12.1, langsmith-0.6.9, benchmark-5.2.3, cov-7.0.0
collected 1054 items / 3 deselected / 1051 selected                                                      

... (1050 tests passed) ...

====================== 1050 passed, 1 skipped, 3 deselected, 2 warnings in 11.36s ======================= 
```

## Skipped/Deselected Test Audit
- **3 deselected**: These correspond to tests marked with `@pytest.mark.integration` which are now correctly skipped by default due to `addopts` in `pyproject.toml`.
- **1 skipped**: `tests/unit/test_verdict_analyzer_scanner.py::TestScanDirectory::test_detects_symlink_loops` (Standard skip for OS compatibility).

## Status
VERIFIED: Unit tests pass and integration tests are correctly skipped by default.
