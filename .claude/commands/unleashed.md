---
description: Unleashed version check and status
argument-hint: "[--check]"
---

# Unleashed

Manage and monitor the Unleashed auto-approval wrapper.

## Help

Usage: `/unleashed [--check]`

| Argument | Description |
|----------|-------------|
| `--check` | Check version status of all recent unleashed sessions |

## Execution

### `--check` Mode

**Steps:**

1. **Get current version** from `C:\Users\mcwiz\Projects\AgentOS\tools\unleashed.py`:
   - Use Grep to find `VERSION = ` line
   - Extract the version string

2. **Find all recent event logs** in `C:\Users\mcwiz\Projects\AgentOS\logs\`:
   - Use Glob pattern: `unleashed_events_*.jsonl`
   - Filter to last 24 hours by filename (YYYYMMDD pattern)

3. **Parse each log's START event**:
   - Read first line of each file
   - Extract `version` field (may be missing in older logs)
   - Extract working directory from context of first AUTO_APPROVED event

4. **Build status report**:

| Session | Project | Version | Status |
|---------|---------|---------|--------|
| {session_id} | {project} | {version} | Current / Outdated / No version |

**Status logic:**
- `Current`: Version matches current VERSION
- `Outdated`: Version exists but doesn't match
- `No version`: Pre-versioning log (missing version field)

**Example output:**

```
Unleashed Version Check
=======================
Current version: 1.1.0

| Session         | Project  | Version | Status    |
|-----------------|----------|---------|-----------|
| 20260114_192308 | AgentOS  | 1.1.0   | Current   |
| 20260114_131517 | Aletheia | (none)  | No version - restart needed |
| 20260114_124833 | Talos    | (none)  | No version - restart needed |

Summary: 1 current, 2 need restart
```

### No Arguments

If no arguments provided, show help message.
