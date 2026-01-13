# 0214 - ADR: Claude-Staging Pattern

**Status:** Implemented
**Date:** 2026-01-08
**Categories:** Process, Governance, Security

## 1. Context

Claude Code uses `.claude/` directory for configuration:
- `.claude/settings.json` - Hooks and tool configuration
- `.claude/settings.local.json` - Local permissions (gitignored)
- `.claude/agents/` - Custom agent definitions
- `.claude/hooks/` - Hook scripts

**Problem:** How do we develop and iterate on governance configuration without:
1. Breaking the live Claude Code environment mid-session
2. Requiring immediate deployment of untested hooks
3. Losing work if configuration causes errors

**Relationship to Other ADRs:**
- **ADR 0210 (Worktrees):** Code isolation pattern; claude-staging extends this to configuration
- **ADR 0213 (Adversarial Audit):** Hooks implement real-time audit enforcement

---

## 2. Decision

**We will use `claude-staging/` as a staging directory for Claude Code configuration changes.**

Structure:
```
Aletheia/
├── .claude/                    # LIVE - Active configuration (TRACKED in git)
│   ├── settings.json           # Hook configuration (tracked)
│   ├── settings.local.json     # Permissions (tracked per CLAUDE.md)
│   ├── hooks/                  # Executable scripts (tracked)
│   ├── agents/                 # Agent definitions (tracked)
│   └── commands/               # Skill definitions (tracked)
│
├── claude-staging/             # STAGING - Development area (GITIGNORED)
│   ├── settings.json           # Draft configuration
│   ├── hooks/                  # Draft scripts
│   ├── agents/                 # Draft agent definitions
│   └── README-DEPLOY.md        # Deployment instructions
```

**Critical Distinction:**
- `.claude/` = **TRACKED** - Live governance-as-code, version controlled
- `claude-staging/` = **GITIGNORED** - Development sandbox, disposable

**Workflow:**
1. Create/edit files in `claude-staging/`
2. Test manually (see deployment docs)
3. Copy to `.claude/` when ready
4. Optionally delete staging directory after deployment

---

## 3. Alternatives Considered

### Option A: Claude-Staging Directory — SELECTED

**Pros:**
- **Isolation:** Live environment unaffected during development
- **Visibility:** Changes are reviewable before deployment
- **Safety:** Can abandon staging without affecting production
- **Documentation:** README-DEPLOY.md captures deployment steps

**Cons:**
- Manual copy step required
- Two places to look for configuration

### Option B: Direct Edits to .claude/

**Pros:**
- Immediate effect
- Single source of truth

**Cons:**
- Broken hooks can disrupt active session
- No review before deployment
- Hard to rollback

### Option C: Branch-Based Configuration

**Pros:**
- Git-native workflow

**Cons:**
- `.claude/` is typically shared across branches
- Worktree switching doesn't isolate `.claude/`

---

## 4. Rationale

Configuration changes to Claude Code hooks have immediate effect. A syntax error in a hook script can block all file operations. A bad PreToolUse hook can prevent ANY edits. This is a high-risk area that warrants a staging pattern similar to how we use worktrees for code changes.

The `claude-staging/` pattern provides:
1. **Safe iteration** - Test before deploy
2. **Documentation** - README explains what each file does
3. **Reversibility** - Just delete staging if it doesn't work
4. **Visibility** - Changes are in a visible directory during development

**Why `.claude/` MUST be tracked:**
- Governance-as-code requires version control
- Hook changes affect all agents - need audit trail
- Rollback capability if hooks break
- Multi-agent environments need consistent configuration

---

## 5. Security Risk Analysis

**Risk Level:** Low

- **Attack Vector:** None - staging directory is local-only and gitignored
- **Data Exposure:** None - no secrets in hook scripts
- **Privilege Escalation:** None - hooks run with same permissions as Claude Code

**Positive Security Impact:**
- Enables testing of security hooks before deployment
- Reduces risk of broken security enforcement

---

## 6. Consequences

**Positive:**
- Can iterate on hooks without breaking active session
- Clear deployment path with documentation
- Supports governance-as-code philosophy

**Negative:**
- Manual copy step (no automation)
- Must remember to deploy after staging

---

## 7. Implementation

### 7.1 Directory Structure

```
claude-staging/
├── settings.json           # Hook configuration (copy to .claude/)
├── hooks/
│   ├── pre-edit-check.sh   # PreToolUse: Branch protection
│   └── post-edit-lint.sh   # PostToolUse: Active linting
├── agents/
│   └── security-reviewer.md # Opus-based security agent
└── README-DEPLOY.md         # Deployment instructions
```

### 7.2 Gitignore Entry

```gitignore
# Claude Code staging directory (local development, not deployed)
claude-staging/
```

### 7.3 Deployment Commands

```bash
# Create directories
mkdir -p .claude/hooks .claude/agents

# Copy files
cp claude-staging/settings.json .claude/settings.json
cp claude-staging/hooks/*.sh .claude/hooks/
cp claude-staging/agents/*.md .claude/agents/

# Make scripts executable
chmod +x .claude/hooks/*.sh
```

---

## 8. Related Documents

- `claude-staging/README-DEPLOY.md` - Deployment instructions
- `docs/0898-horizon-scanning-protocol.md` §4.3 - Triage analysis
- ADR 0210 - Git Worktree Isolation (parent pattern)
- ADR 0213 - Adversarial Audit Philosophy (motivation)
