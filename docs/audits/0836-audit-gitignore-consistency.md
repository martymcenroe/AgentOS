# 0836 - .gitignore Consistency Audit

**Status:** Active
**Created:** 2026-01-20
**Frequency:** Monthly or when new project created

---

## Purpose

Ensure all projects under AgentOS governance have consistent `.gitignore` patterns to prevent accidental commits of sensitive data, build artifacts, and environment-specific files.

---

## Required Patterns

Every `.gitignore` MUST include these patterns:

### Python Projects

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.venv/
venv/
ENV/
env/

# Poetry
poetry.lock  # Optional - some projects track this

# pytest
.pytest_cache/
.coverage
htmlcov/
```

### JavaScript/Node Projects

```gitignore
# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Build outputs
dist/
build/
*.tsbuildinfo

# Coverage
coverage/
.nyc_output/
```

### IDE and Editor

```gitignore
# IDE
.idea/
.vscode/
*.swp
*.swo
*~
.project
.classpath
.settings/

# OS
.DS_Store
Thumbs.db
```

### Security-Critical (MANDATORY)

```gitignore
# Secrets - NEVER COMMIT
.env
.env.*
*.pem
*.key
credentials.json
secrets.json
**/secrets/
**/.secrets/

# Local config
settings.local.json
*.local.json
*.local.yaml
```

### Project-Specific

```gitignore
# Logs (usually too large)
logs/
*.log

# Temp files
tmp/
temp/
*.tmp

# Test artifacts
test-results/
playwright-report/
```

---

## Audit Procedure

### Quick Check (2 minutes)

For each project, verify presence of security-critical patterns:

```bash
# Run from project root
grep -E "\.env|credentials|secrets|\.pem|\.key" .gitignore
```

Expected: At least 3-4 matches

### Full Audit (10 minutes)

1. **Compare against baseline:**
   ```bash
   # From AgentOS
   diff /c/Users/mcwiz/Projects/AgentOS/.gitignore /c/Users/mcwiz/Projects/{PROJECT}/.gitignore
   ```

2. **Check for exposed secrets:**
   ```bash
   git -C /c/Users/mcwiz/Projects/{PROJECT} ls-files | grep -iE "\.env|secret|credential|\.pem|\.key"
   ```
   Expected: Empty output (no matches)

3. **Verify no large files tracked:**
   ```bash
   git -C /c/Users/mcwiz/Projects/{PROJECT} ls-files | xargs -I {} stat --printf="%s %n\n" {} 2>/dev/null | sort -rn | head -10
   ```

---

## Remediation

If missing patterns found:

1. Add missing patterns to `.gitignore`
2. If sensitive files already tracked:
   ```bash
   git rm --cached {file}
   git commit -m "chore: remove {file} from tracking"
   ```
3. Consider git-crypt for files that must be in repo but encrypted

---

## Audit Record Template

```markdown
## .gitignore Audit - {PROJECT}

**Date:** YYYY-MM-DD
**Auditor:** {agent/human}

### Results

| Check | Status |
|-------|--------|
| Security patterns present | PASS/FAIL |
| No secrets in tracked files | PASS/FAIL |
| Python patterns (if applicable) | PASS/FAIL |
| Node patterns (if applicable) | PASS/FAIL |
| IDE patterns present | PASS/FAIL |

### Issues Found

(List any issues)

### Remediation

(List actions taken)
```

---

## Cross-Project Summary

Run this to audit all projects at once:

```bash
for proj in AgentOS Talos maintenance Aletheia Clio unleashed dispatch Iconoscope GlucoPulse Agora; do
  echo "=== $proj ==="
  grep -c "\.env" /c/Users/mcwiz/Projects/$proj/.gitignore 2>/dev/null || echo "NO .gitignore"
done
```
