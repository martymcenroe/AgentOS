# 0814 - Audit: License Compliance

## 1. Purpose

Ensure all dependencies use licenses compatible with Aletheia's MIT license and distribution model.

**Aletheia License:** MIT (permissive, commercial-friendly)

### License Consistency Check (CRITICAL)

**These three files must declare the same license.** If they don't match, FAIL the audit:

```bash
🤖 grep -i "license" LICENSE | head -1
🤖 grep -i "license" package.json
🤖 grep -i "license" pyproject.toml
```

| File | Expected | Actual | Match? |
|------|----------|--------|--------|
| `LICENSE` (root) | MIT | | |
| `package.json` (`"license":`) | MIT | | |
| `pyproject.toml` (`tool.poetry.license`) | MIT | | |

**Note:** pyproject.toml may not have an explicit license field (Poetry doesn't require it). If absent, verify LICENSE file is authoritative.

---

## 2. License Compatibility Matrix

### Compatible Licenses (Green)

| License | Compatible? | Notes |
|---------|-------------|-------|
| MIT | ✅ Yes | Same as ours |
| BSD-2-Clause | ✅ Yes | Permissive |
| BSD-3-Clause | ✅ Yes | Permissive |
| Apache-2.0 | ✅ Yes | Permissive (attribution required) |
| ISC | ✅ Yes | Permissive |
| CC0 | ✅ Yes | Public domain |
| Unlicense | ✅ Yes | Public domain |

### Conditional Licenses (Yellow)

| License | Compatible? | Notes |
|---------|-------------|-------|
| LGPL-2.1 | ⚠️ Conditional | OK if dynamically linked |
| LGPL-3.0 | ⚠️ Conditional | OK if dynamically linked |
| MPL-2.0 | ⚠️ Conditional | File-level copyleft |

### Incompatible Licenses (Red)

| License | Compatible? | Notes |
|---------|-------------|-------|
| GPL-2.0 | ❌ No | Strong copyleft |
| GPL-3.0 | ❌ No | Strong copyleft |
| AGPL-3.0 | ❌ No | Network copyleft |
| SSPL | ❌ No | Not OSI approved |
| Proprietary | ❌ No | Requires separate license |

---

## 3. Python Dependencies Audit

### Command

```bash
poetry show --tree | head -50
pip-licenses --format=markdown  # if installed
```

### Dependency Check

| Package | License | Status |
|---------|---------|--------|
| boto3 | Apache-2.0 | ✅ Compatible |
| botocore | Apache-2.0 | ✅ Compatible |
| requests | Apache-2.0 | ✅ Compatible |
| beautifulsoup4 | MIT | ✅ Compatible |
| colorama | BSD-3-Clause | ✅ Compatible |
| tzdata | Apache-2.0 | ✅ Compatible |
| pillow | HPND | ✅ Compatible |
| pytest | MIT | ✅ Compatible |
| ruff | MIT | ✅ Compatible |
| mypy | MIT | ✅ Compatible |
| types-requests | Apache-2.0 | ✅ Compatible |
| types-colorama | Apache-2.0 | ✅ Compatible |

---

## 4. JavaScript Dependencies Audit

### Command

```bash
npx license-checker --summary
npx license-checker --onlyAllow "MIT;Apache-2.0;BSD-2-Clause;BSD-3-Clause;ISC"
```

### Dependency Check

| Package | License | Status |
|---------|---------|--------|
| @playwright/test | Apache-2.0 | ✅ Compatible (devDep) |
| eslint | MIT | ✅ Compatible (devDep) |
| serve | MIT | ✅ Compatible (devDep) |

**Note:** All JS dependencies are `devDependencies` only. No runtime dependencies are bundled in the extension artifact, simplifying license compliance.

---

## 5. Attribution Requirements

### Licenses Requiring Attribution

| License | Requirement | Location |
|---------|-------------|----------|
| Apache-2.0 | NOTICE file | LICENSE or NOTICE |
| BSD-3-Clause | Copyright in docs | LICENSE |

### Current Attribution

- [x] LICENSE file includes MIT license text
- [x] Third-party licenses documented (this file)
- [x] NOTICE file exists for Apache-2.0 dependencies

---

## 6. Audit Procedure

1. List all Python dependencies: `poetry show`
2. Check each license against §2 matrix
3. List all JS dependencies: `npm ls --all`
4. Check each license against §2 matrix
5. Verify attribution requirements met
6. Document any issues

---

## 7. Audit Record

| Date | Auditor | Findings Summary | Issues Created |
|------|---------|------------------|----------------|
| 2026-01-05 | Gemini 3.0 Pro | CRITICAL: package.json had ISC (fixed to MIT), MEDIUM: missing deps in inventory (added), LOW: NOTICE file missing (created) | None (all fixed inline) |

---

## 8. References

- [SPDX License List](https://spdx.org/licenses/)
- [Choose a License](https://choosealicense.com/)
- [OSI Approved Licenses](https://opensource.org/licenses)
