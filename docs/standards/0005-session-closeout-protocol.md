# 0009 - Session Cleanup Protocol

A streamlined checklist for ending sessions cleanly. Three modes available based on scope.

## How to Invoke

```
/cleanup           # Normal mode (default)
/cleanup --quick   # Quick mode
/cleanup --full    # Full mode
```

| Mode | Time | Use Case |
|------|------|----------|
| **Quick** | ~2 min | End of chat, minimal changes made |
| **Normal** | ~5 min | Standard session end (default) |
| **Full** | ~12 min | Feature complete, before breaks, environment feels messy |

## Philosophy

> "Leave the campsite cleaner than you found it."

A proper cleanup takes 2-12 minutes but saves 30+ minutes of confusion in the next session.

### Core Principles

1. **Parallel Execution** - Run independent commands simultaneously
2. **Single Commit** - ONE commit at the end, not per-step
3. **Progressive Enhancement** - Quick ⊂ Normal ⊂ Full
4. **Fast-Fail** - Check critical state early (Lambda, branches)

---

## Execution Model

The `/cleanup` command delegates to **Sonnet** for cost efficiency (~80% cheaper than Opus). Results return to your main session.

```
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 1: PARALLEL INFORMATION GATHERING                        │
│ (All read-only, run simultaneously)                            │
├─────────────────────────────────────────────────────────────────┤
│ Quick:   status, branch --list, gh pr list                     │
│ Normal:  + stash list, fetch --prune, gh issue list            │
│ Full:    + worktree list, branch -vv, branch -r                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 2: CONDITIONAL FIXES (Sequential, only if needed)        │
├─────────────────────────────────────────────────────────────────┤
│ Normal:  Regenerate 6000-open-issues.md                        │
│ Full:    + stale branch/worktree cleanup                       │
│          + Inventory audit, Wiki check                         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 3: SESSION LOG                                           │
│ Append entry via tools/append_session_log.py                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 4: SINGLE COMMIT & PUSH                                  │
│ git add → git commit → git push (ONE commit total)             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 5: PARALLEL VERIFICATION                                 │
│ Confirm clean state                                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Mode Details

### Quick Mode (~2 min)

**When to use:** End of chat with minimal or no file changes.

**Phase 1 - Parallel Reads (3 calls):**
```bash
git -C /c/Users/mcwiz/Projects/Aletheia status
git -C /c/Users/mcwiz/Projects/Aletheia branch --list
gh pr list --state open --repo martymcenroe/Aletheia
```

**Phase 3 - Session Log:**
```bash
poetry run python /c/Users/mcwiz/Projects/Aletheia/tools/append_session_log.py \
    --model "Claude Sonnet 4" \
    --summary "Quick cleanup" \
    --created "None" \
    --closed "None" \
    --next "Per user direction"
```

**Note:** Session log is written to file but NOT committed. Session logs should be committed by the agent doing actual work, not by cleanup agents. This prevents commit spam when multiple agents run cleanup simultaneously.

**Phase 4 - Verify:**
```bash
git -C /c/Users/mcwiz/Projects/Aletheia status
gh pr list --state open --repo martymcenroe/Aletheia
```

---

### Normal Mode (~5 min) - DEFAULT

**When to use:** Standard session ending.

**Phase 1 - Parallel Reads (6 calls):**
```bash
git -C /c/Users/mcwiz/Projects/Aletheia status
git -C /c/Users/mcwiz/Projects/Aletheia branch --list
git -C /c/Users/mcwiz/Projects/Aletheia stash list
git -C /c/Users/mcwiz/Projects/Aletheia fetch --prune
gh pr list --state open --repo martymcenroe/Aletheia
gh issue list --state open --repo martymcenroe/Aletheia
```

**Phase 2 - Doc Sync:**
```bash
poetry run python /c/Users/mcwiz/Projects/Aletheia/tools/print/print_most_recent_open_issues.py --no-print
```

**Phase 3 - Session Log:**
```bash
poetry run python /c/Users/mcwiz/Projects/Aletheia/tools/append_session_log.py \
    --model "Claude Sonnet 4" \
    --summary "Session summary here" \
    --created "None" \
    --closed "None" \
    --next "Per user direction"
```

**Note:** Doc sync and session log are written to files but NOT committed. This prevents race conditions when multiple agents run cleanup simultaneously. Session logs should be committed by the agent doing actual work.

**Phase 4 - Verify:**
```bash
git -C /c/Users/mcwiz/Projects/Aletheia status
gh pr list --state open --repo martymcenroe/Aletheia
```

---

### Full Mode (~12 min)

**When to use:** Feature complete, before breaks, environment feels messy.

**Phase 1 - Parallel Reads (9 calls):**
```bash
git -C /c/Users/mcwiz/Projects/Aletheia status
git -C /c/Users/mcwiz/Projects/Aletheia branch --list
git -C /c/Users/mcwiz/Projects/Aletheia stash list
git -C /c/Users/mcwiz/Projects/Aletheia fetch --prune
git -C /c/Users/mcwiz/Projects/Aletheia worktree list
git -C /c/Users/mcwiz/Projects/Aletheia branch -vv
git -C /c/Users/mcwiz/Projects/Aletheia branch -r
gh pr list --state open --repo martymcenroe/Aletheia
gh issue list --state open --repo martymcenroe/Aletheia
```

**Phase 2 - Analysis & Fixes:**

1. **Branch Check** - Flag any branch other than main
2. **Worktree Check** - Remove stale worktrees
3. **Stash Check** - Document any stash entries
4. **Doc Sync** - Regenerate 6000-open-issues.md
5. **Inventory Audit** - Glob check against 0003-file-inventory.md
6. **Index Consistency Check** - Verify index files match reality (see § Index Consistency Verification)
7. **Plan Check** - Validate IMMEDIATE-PLAN issue references (see § IMMEDIATE-PLAN Staleness Detection)
8. **Wiki Check** - If user-facing changes, check wiki alignment (0817)

**Phase 3 - Session Log:**
```bash
poetry run python /c/Users/mcwiz/Projects/Aletheia/tools/append_session_log.py \
    --model "Claude Sonnet 4" \
    --summary "Full cleanup - detailed summary" \
    --created "#XX" \
    --closed "#YY" \
    --next "Next steps"
```

**Phase 4 - Commit & Push (if needed):**

**Note:** Session logs are NOT committed (prevents race conditions). Only commit files that full cleanup legitimately modifies (inventory updates, IMMEDIATE-PLAN corrections, stale worktree removals).

```bash
# Check if there are actual changes to commit (excluding session logs)
git -C /c/Users/mcwiz/Projects/Aletheia status --short

# If changes exist (inventory, IMMEDIATE-PLAN, etc.), commit them:
git -C /c/Users/mcwiz/Projects/Aletheia add docs/6000-open-issues.md
git -C /c/Users/mcwiz/Projects/Aletheia add docs/0003-file-inventory.md
git -C /c/Users/mcwiz/Projects/Aletheia add docs/0000a-IMMEDIATE-PLAN.md
git -C /c/Users/mcwiz/Projects/Aletheia add docs/9000-lessons-learned.md
git -C /c/Users/mcwiz/Projects/Aletheia commit -m "docs: full cleanup YYYY-MM-DD"
git -C /c/Users/mcwiz/Projects/Aletheia push

# If no changes, skip commit
```

**Phase 5 - Gemini Auth Restore:**

If Gemini API key mode was used during this session, restore OAuth mode:
```bash
bash ~/.gemini/use-oauth.sh
```

This ensures the next session starts with OAuth (global default) and doesn't leave credentials in a project-specific state.

**Phase 6 - Verify:**
```bash
git -C /c/Users/mcwiz/Projects/Aletheia status
git -C /c/Users/mcwiz/Projects/Aletheia worktree list
git -C /c/Users/mcwiz/Projects/Aletheia branch -r
gh pr list --state open --repo martymcenroe/Aletheia
```

**Human Reminder:**
- Chrome: `chrome://extensions/` → Reload extension
- Firefox: `about:debugging` → Reload extension

---

## Expected Output

The cleanup returns a summary table:

| Check | Status |
|-------|--------|
| Git Status | ✅ Clean / ⚠️ {details} |
| Open PRs | ✅ 0 / ⚠️ {count} open |
| Open Issues | {count} |
| Branches | ✅ Only main / ⚠️ {list} |
| Worktrees | ✅ Only main / ⚠️ {list} |
| Stashes | ✅ None / ⚠️ {count} |
| Session Log | ✅ Written (not committed) |
| Doc Sync | ✅ Regenerated (not committed in quick/normal) |

---

## Unexpected Conditions

Report to human if any of these occur:

| Condition | Message |
|-----------|---------|
| Branch exists without worktree | `⚠️ UNEXPECTED: Branch {name} exists` |
| Issue should be closed but isn't | `⚠️ UNEXPECTED: Issue #{N} appears done` |
| Uncommitted work in worktree | `⚠️ UNEXPECTED: Uncommitted changes` |
| File not in inventory | `⚠️ DRIFT: File {path} not in 0003` |
| Closed issue in IMMEDIATE-PLAN | `⚠️ STALE: Issue #N is CLOSED but referenced in IMMEDIATE-PLAN` |

---

## IMMEDIATE-PLAN Staleness Detection

**Problem:** `docs/0000a-IMMEDIATE-PLAN.md` references issues (e.g., "#147 is BLOCKED BY #116") that can become stale when issues are closed. Without validation, these stale references persist and mislead future agents.

**Trigger:** Full mode cleanup, OR when any issue is closed during the session.

### Detection Procedure

**Step 1: Extract issue references from IMMEDIATE-PLAN**

Use Grep to find all `#NNN` patterns:
```bash
grep -oE '#[0-9]+' /c/Users/mcwiz/Projects/Aletheia/docs/0000a-IMMEDIATE-PLAN.md
```

**Step 2: Check each unique issue's state**

For each issue number found, query GitHub:
```bash
gh issue view NNN --repo martymcenroe/Aletheia --json state,title
```

**Step 3: Identify stale references**

An issue reference is **stale** if:
- The issue is CLOSED, AND
- IMMEDIATE-PLAN describes it as current work, blocking, or pending

**Step 4: Report findings**

| Condition | Action |
|-----------|--------|
| All referenced issues are OPEN | ✅ No action needed |
| Closed issue in "Critical Path" section | ⚠️ Update section to mark step complete |
| Closed issue in "BLOCKED BY" relationship | ⚠️ Remove blocking constraint, update dependent issue |
| Closed issue in "V2 Features" table | ⚠️ Update status column |

### Remediation

When stale references are found:

1. **Read the full IMMEDIATE-PLAN** to understand context
2. **Check the closed issue** for resolution details: `gh issue view NNN --repo martymcenroe/Aletheia`
3. **Update IMMEDIATE-PLAN** to reflect current reality:
   - Mark completed steps as ✅ COMPLETE
   - Remove or update blocking relationships
   - Update status indicators
4. **Stage the change**: `git -C /c/Users/mcwiz/Projects/Aletheia add docs/0000a-IMMEDIATE-PLAN.md`

### Example

**Before (stale):**
```markdown
| #116 | LinkedIn OAuth (auth gate) | **HIGH** - enables user identification |
| #147 | GDPR data erasure | ⛔ **BLOCKED BY #116** |
```

**After (current):**
```markdown
| #116 | LinkedIn OAuth (auth gate) | ✅ COMPLETE (PR #XXX) |
| #147 | GDPR data erasure | **HIGH** - auth gate complete, ready to implement |
```

---

## Index Consistency Verification

**Problem:** Index files (`0003`, `0200`, `0800`) can drift from reality when files are added/removed without updating the corresponding index.

**Trigger:** Full mode cleanup.

### Index Files to Verify

| Index | Purpose | Verification |
|-------|---------|--------------|
| `0003-file-inventory.md` | All project files | Compare against `git ls-files` |
| `0200-ADR-index.md` | ADR registry | Compare against `docs/02*-ADR-*.md` glob |
| `0800-audit-index.md` | Audit registry | Compare against `docs/08*-audit-*.md` glob |

### Verification Procedure

**Step 1: ADR Index Check**

```bash
# List actual ADR files (excluding index)
ls /c/Users/mcwiz/Projects/Aletheia/docs/02*-ADR-*.md
```

Compare output against entries in `0200-ADR-index.md`. Flag:
- ADR files not in index
- Index entries pointing to non-existent files

**Step 2: Audit Index Check**

```bash
# List actual audit files (excluding index)
ls /c/Users/mcwiz/Projects/Aletheia/docs/08*-audit-*.md
```

Compare output against entries in `0800-audit-index.md` §9.1. Flag:
- Audit files not in index
- Index entries pointing to non-existent files

**Step 3: Template Registry Check**

```bash
# List template files
ls /c/Users/mcwiz/Projects/Aletheia/docs/01*-TEMPLATE-*.md
```

Verify all templates are referenced in `0100-TEMPLATE-GUIDE.md`.

### Remediation

| Condition | Action |
|-----------|--------|
| File exists, not in index | Add entry to index |
| Index entry, file missing | Remove from index OR locate moved file |
| Numbering gap | Note in drift report (gaps are OK) |

### Example Output

```
⚠️ INDEX DRIFT DETECTED:

ADR Index (0200):
  - MISSING: 0212-ADR-unified-v3-secure-dom.md not in index table
  - OK: 10 files, 10 entries

Audit Index (0800):
  - OK: 17 files, 17 entries
```

---

## Anti-Patterns

| Don't | Do Instead |
|:------|:-----------|
| **Commit after each step** | **Stage with `git add`, ONE commit at end** |
| **Run commands sequentially** | **Run independent commands in parallel** |
| Close laptop mid-conversation | Complete the turn, write session-log |
| Leave feature branch checked out | Return to main |
| Skip session-log "just this once" | It's 2 minutes, do it |
| Leave stash entries unexplained | Document or drop them |

---

## Rules

- Use absolute paths and `git -C` patterns (no cd && chaining)
- Use `--repo martymcenroe/Aletheia` for all gh commands
- Never modify `.claude/settings.local.json` during cleanup
- Never use forbidden commands (git reset, git push --force, etc.)
