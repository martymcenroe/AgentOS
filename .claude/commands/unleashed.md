---
description: Unleashed version check and status
argument-hint: "[--help|--version|--check]"
---

# Unleashed

Manage and monitor the Unleashed auto-approval wrapper.

**If `$ARGUMENTS` contains `--help` or is empty:** Display Help section and STOP.

## Help

Usage: `/unleashed [--help|--version|--check]`

| Argument | Description |
|----------|-------------|
| `--help` | Show this help message |
| `--version` | Show current unleashed version (quick check) |
| `--check` | Check version status of all recent sessions (slower) |

## Execution

### `--version` Mode

Quick version check - just read and display the current version:

1. Use Grep to find `VERSION = ` in `C:\Users\mcwiz\Projects\AgentOS\tools\unleashed.py`
2. Display: `Unleashed v{version}`

**Example output:**
```
Unleashed v1.1.0
```

### `--check` Mode

Full session audit (takes longer):

1. **Get current version** from `C:\Users\mcwiz\Projects\AgentOS\tools\unleashed.py`

2. **Find recent event logs** in `C:\Users\mcwiz\Projects\AgentOS\logs\`:
   - Glob pattern: `unleashed_events_*.jsonl`
   - Filter to last 24 hours by filename

3. **Parse each log's START event**:
   - Read first line of each file
   - Extract `version` field (may be missing in older logs)
   - Extract project from context

4. **Build status report**:

| Session | Project | Version | Status |
|---------|---------|---------|--------|
| {session_id} | {project} | {version} | Current / Outdated / No version |

**Example output:**
```
Unleashed Version Check
=======================
Current version: 1.1.0

| Session | Project | Version | Status |
|---------|---------|---------|--------|
| 135029  | AgentOS | 1.1.0   | Current |
| 131517  | Aletheia | (none) | Restart needed |

Summary: 1 current, 1 need restart
```
