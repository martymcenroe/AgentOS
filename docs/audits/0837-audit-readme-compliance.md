# 0837 - README Compliance Audit

**Status:** Active
**Created:** 2026-01-20
**Frequency:** Monthly or when project created/updated

---

## Purpose

Ensure all project READMEs follow the AgentOS template and present a professional, consistent appearance to external reviewers.

---

## Required Sections

Every README.md MUST include:

### Mandatory Sections

1. **Title** - Project name as H1
2. **One-liner** - Brief description (blockquote or subtitle)
3. **Overview** - 2-3 sentences explaining purpose
4. **Status** - Table showing development/docs/test status
5. **Quick Start** - Installation and run commands
6. **Project Structure** - Directory tree overview
7. **Documentation** - Links to key docs
8. **Development** - Reference to AgentOS conventions
9. **License** - License specification

### Optional Sections

- **Features** - If project has distinct features
- **Architecture** - If complex system
- **API** - If exposes API
- **Contributing** - If accepting contributions
- **Acknowledgments** - If applicable

---

## Audit Procedure

### Quick Check (1 minute)

Verify required sections exist:

```bash
# Run from project root
grep -E "^#|^##" README.md | head -15
```

Expected output should show most of:
- `# ProjectName`
- `## Overview`
- `## Status`
- `## Quick Start`
- `## Project Structure`
- `## Documentation`
- `## Development`
- `## License`

### Full Audit (5 minutes)

For each README, check:

| Check | How to Verify |
|-------|---------------|
| Has title | First line is `# ProjectName` |
| Has one-liner | Line 3-5 has `>` blockquote or subtitle |
| Has overview | `## Overview` section exists |
| Has status table | Contains `\| Aspect \| Status \|` |
| Has quick start | `## Quick Start` with code block |
| Has structure | Directory tree in code block |
| Has docs links | Links to `docs/` files |
| Has AgentOS reference | Mentions AgentOS governance |
| Has license | `## License` section exists |

---

## Template Reference

See: `AgentOS/.claude/templates/README.md.template`

---

## Remediation

If README is non-compliant:

1. Copy template from AgentOS
2. Fill in project-specific values
3. Preserve any existing content that fits template sections
4. Remove duplicate or orphaned sections

---

## Audit Record Template

```markdown
## README Audit - {PROJECT}

**Date:** YYYY-MM-DD
**Auditor:** {agent/human}

### Checklist

| Section | Present | Compliant |
|---------|---------|-----------|
| Title | YES/NO | YES/NO |
| One-liner | YES/NO | YES/NO |
| Overview | YES/NO | YES/NO |
| Status table | YES/NO | YES/NO |
| Quick Start | YES/NO | YES/NO |
| Project Structure | YES/NO | YES/NO |
| Documentation links | YES/NO | YES/NO |
| AgentOS reference | YES/NO | YES/NO |
| License | YES/NO | YES/NO |

### Issues Found

(List any missing or non-compliant sections)

### Remediation

(List actions taken)
```

---

## Cross-Project Summary

Run this to audit all projects at once:

```bash
for proj in AgentOS Talos maintenance Aletheia Clio unleashed dispatch Iconoscope GlucoPulse Agora; do
  echo "=== $proj ==="
  grep -c "^## " /c/Users/mcwiz/Projects/$proj/README.md 2>/dev/null || echo "NO README"
done
```

---

## Professional Appearance Checklist

Beyond structural compliance, verify:

- [ ] No spelling errors in first paragraph
- [ ] Code blocks have language specified (```bash, ```python)
- [ ] Links are not broken
- [ ] No TODO/FIXME in visible sections
- [ ] Status table is current (not outdated)
- [ ] Quick start commands actually work
