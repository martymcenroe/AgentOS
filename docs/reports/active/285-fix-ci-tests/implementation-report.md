# Implementation Report - Fix CI and Skip Integration Tests (#285)

## Issue Reference
[#285: bug: integration tests run by default, making real API calls](https://github.com/martymcenroe/AssemblyZero/issues/285)

## Files Changed
- `.github/workflows/ci.yml`: Updated `poetry install` to include `--with dev`.
- `pyproject.toml`: Added `[tool.pytest.ini_options]` to skip `integration` and `e2e` tests by default.

## Design Decisions
1. **CI Fix**: Poetry 2.0+ does not install `[dependency-groups]` by default. Added `--with dev` to ensure `pytest` and other tools are available in CI.
2. **Pytest Markers**: Added `integration`, `e2e`, and `expensive` markers.
3. **Default Deselection**: Configured `addopts = "-m 'not integration and not e2e'"` to protect API quota during accidental local runs and in CI.

## Known Limitations
- Developers must explicitly run `poetry run pytest -m integration` to execute integration tests.
