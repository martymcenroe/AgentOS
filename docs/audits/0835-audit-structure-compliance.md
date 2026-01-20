# 0835 - Project Structure Compliance Audit

**Status:** Active
**Created:** 2026-01-20
**Frequency:** Monthly or when project created
**Reference:** `docs/standards/0009-canonical-project-structure.md`

---

## Purpose

Verify all projects follow the canonical directory structure defined in standard 0009.

---

## Required Directories

### Documentation (`docs/`)

Every project MUST have:

```
docs/
├── adrs/                       # Architecture Decision Records
├── standards/                  # Project-specific standards
├── templates/                  # Document templates
├── lld/
│   ├── active/                 # In-progress LLDs
│   └── done/                   # Completed LLDs
├── reports/
│   ├── active/                 # In-progress reports
│   └── done/                   # Completed reports
├── runbooks/                   # Operational procedures
├── session-logs/               # Agent session context
└── audit-results/              # Historical audit outputs
```

### Tests (`tests/`)

Every project MUST have:

```
tests/
├── unit/
├── integration/
├── e2e/
├── contract/
├── visual/
├── benchmark/
├── security/
├── accessibility/
├── compliance/
├── fixtures/
└── harness/
```

### Claude Configuration (`.claude/`)

Every project MUST have:

```
.claude/
├── project.json
├── settings.json
├── hooks/
├── commands/
└── gemini-prompts/
```

### Root Files

Every project MUST have:
- `CLAUDE.md`
- `GEMINI.md`
- `README.md`
- `.gitignore`

---

## Audit Procedure

### Quick Check (2 minutes)

```bash
PROJECT=/c/Users/mcwiz/Projects/{NAME}

# Check docs structure
for dir in adrs standards templates lld/active lld/done reports/active reports/done runbooks session-logs audit-results; do
  [ -d "$PROJECT/docs/$dir" ] && echo "OK: docs/$dir" || echo "MISSING: docs/$dir"
done

# Check tests structure
for dir in unit integration e2e contract visual benchmark security accessibility compliance fixtures harness; do
  [ -d "$PROJECT/tests/$dir" ] && echo "OK: tests/$dir" || echo "MISSING: tests/$dir"
done

# Check root files
for file in CLAUDE.md GEMINI.md README.md .gitignore; do
  [ -f "$PROJECT/$file" ] && echo "OK: $file" || echo "MISSING: $file"
done
```

### Full Audit (10 minutes)

1. Run quick check
2. Verify `.claude/` structure
3. Check directory naming (plural, lowercase-hyphen)
4. Verify no deprecated structures (e.g., `test/` instead of `tests/`)
5. Check for orphaned files outside standard directories

---

## Automated Audit Script

```bash
#!/bin/bash
# Save as: audit-structure.sh

PROJECT=$1
if [ -z "$PROJECT" ]; then
  echo "Usage: audit-structure.sh /path/to/project"
  exit 1
fi

echo "=== Structure Audit: $(basename $PROJECT) ==="
echo ""

ERRORS=0

# Docs directories
DOCS_DIRS="adrs standards templates lld/active lld/done reports/active reports/done runbooks session-logs audit-results"
for dir in $DOCS_DIRS; do
  if [ ! -d "$PROJECT/docs/$dir" ]; then
    echo "FAIL: Missing docs/$dir"
    ((ERRORS++))
  fi
done

# Tests directories
TEST_DIRS="unit integration e2e contract visual benchmark security accessibility compliance fixtures harness"
for dir in $TEST_DIRS; do
  if [ ! -d "$PROJECT/tests/$dir" ]; then
    echo "FAIL: Missing tests/$dir"
    ((ERRORS++))
  fi
done

# Root files
ROOT_FILES="CLAUDE.md GEMINI.md README.md .gitignore"
for file in $ROOT_FILES; do
  if [ ! -f "$PROJECT/$file" ]; then
    echo "FAIL: Missing $file"
    ((ERRORS++))
  fi
done

# Check for deprecated singular directories
if [ -d "$PROJECT/test" ] && [ ! -d "$PROJECT/tests" ]; then
  echo "FAIL: Using 'test/' instead of 'tests/'"
  ((ERRORS++))
fi

if [ -d "$PROJECT/extension" ] && [ ! -d "$PROJECT/extensions" ]; then
  echo "FAIL: Using 'extension/' instead of 'extensions/'"
  ((ERRORS++))
fi

echo ""
if [ $ERRORS -eq 0 ]; then
  echo "PASS: All structure checks passed"
else
  echo "FAIL: $ERRORS issues found"
fi
```

---

## Remediation

To fix missing directories:

```bash
# Create all docs directories
mkdir -p docs/{adrs,standards,templates,lld/active,lld/done,reports/active,reports/done,runbooks,session-logs,audit-results}

# Create all tests directories
mkdir -p tests/{unit,integration,e2e,contract,visual,benchmark,security,accessibility,compliance,fixtures,harness}

# Add .gitkeep to empty directories
find docs tests -type d -empty -exec touch {}/.gitkeep \;
```

To rename deprecated directories:

```bash
# Rename singular to plural
git mv test tests
git mv extension extensions
```

---

## Audit Record Template

```markdown
## Structure Audit - {PROJECT}

**Date:** YYYY-MM-DD
**Auditor:** {agent/human}

### Documentation Structure

| Directory | Status |
|-----------|--------|
| docs/adrs/ | PASS/FAIL |
| docs/standards/ | PASS/FAIL |
| docs/templates/ | PASS/FAIL |
| docs/lld/active/ | PASS/FAIL |
| docs/lld/done/ | PASS/FAIL |
| docs/reports/active/ | PASS/FAIL |
| docs/reports/done/ | PASS/FAIL |
| docs/runbooks/ | PASS/FAIL |
| docs/session-logs/ | PASS/FAIL |
| docs/audit-results/ | PASS/FAIL |

### Test Structure

| Directory | Status |
|-----------|--------|
| tests/unit/ | PASS/FAIL |
| tests/integration/ | PASS/FAIL |
| tests/e2e/ | PASS/FAIL |
| tests/contract/ | PASS/FAIL |
| tests/visual/ | PASS/FAIL |
| tests/benchmark/ | PASS/FAIL |
| tests/security/ | PASS/FAIL |
| tests/accessibility/ | PASS/FAIL |
| tests/compliance/ | PASS/FAIL |
| tests/fixtures/ | PASS/FAIL |
| tests/harness/ | PASS/FAIL |

### Root Files

| File | Status |
|------|--------|
| CLAUDE.md | PASS/FAIL |
| GEMINI.md | PASS/FAIL |
| README.md | PASS/FAIL |
| .gitignore | PASS/FAIL |

### Issues Found

(List any issues)

### Remediation

(List actions taken)
```

---

## Cross-Project Summary

```bash
for proj in AgentOS Talos maintenance Aletheia Clio unleashed dispatch Iconoscope GlucoPulse Agora; do
  echo "=== $proj ==="
  bash audit-structure.sh /c/Users/mcwiz/Projects/$proj 2>/dev/null | tail -1
done
```
