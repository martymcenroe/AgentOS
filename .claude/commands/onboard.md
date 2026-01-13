---
description: Agent onboarding (quick/full mode)
argument-hint: "[--help] [--quick | --full]"
---

# Agent Onboarding

**If `$ARGUMENTS` contains `--help`:** Display the Help section below and STOP. Do not execute onboarding.

Onboard yourself to the current project by reading and understanding the documentation.

## Help

```
/onboard - Agent onboarding for current project

Usage: `/onboard [--help] [--quick | --full]`

Options:
| Flag | Effect |
|------|--------|
| `--help` | Show this help message and exit |
| `--quick` | Read digest only, report age (~$0.02, 30s) - for simple tasks |
| `--full` | Full onboarding (~$0.35, 2min) - for complex work (default) |

Examples:
- `/onboard --help` - show this help
- `/onboard --quick` - quick onboard for status check
- `/onboard --full` - full onboard for feature work
- `/onboard` - same as --full
```

## Project Detection

Detect the current project from working directory:
- Extract project name from path (e.g., `/c/Users/mcwiz/Projects/Aletheia` → `Aletheia`)
- Project root: `C:\Users\mcwiz\Projects\{PROJECT}`

## Modes

| Mode | Cost | Time | Use Case |
|------|------|------|----------|
| `--quick` | ~$0.02 | ~30s | Simple tasks, status checks |
| `--full` (default) | ~$0.35 | ~2min | Complex features, audits |

## Quick Mode (`--quick`)

**Model hint:** Quick mode can use **Haiku** (~66% cost savings) since it only reads existing docs.

Read only the essential files:
1. Read `CLAUDE.md` in the project root
2. Read `docs/0000-GUIDE.md` or equivalent guide (if exists)
3. Glob `docs/session-logs/*.md` and read the most recent entry
4. Report readiness

**Use when:** Task is simple, context is clear, or you're resuming recent work.

## Full Mode (`--full` or no argument)

Complete onboarding:

### Step 1: Core Documentation (parallel reads)
Read these files simultaneously:
- `CLAUDE.md` - Project rules
- `docs/0000-GUIDE.md` or `docs/README.md` - System philosophy
- `docs/0001-*.md` or `docs/architecture.md` - Architecture (if exists)

### Step 2: Current State
- Check for `docs/0000a-IMMEDIATE-PLAN.md` or similar sprint focus doc
- Glob `docs/session-logs/*.md` and read the most recent session log (last 3 entries only)
- Check open issues: `gh issue list --state open --limit 10`

### Step 3: Project-Specific Setup
If the project has special setup:
- Check for `tools/generate_onboard_digest.py` and run it if exists
- Check for `docs/0000b-ONBOARD-DIGEST.md` and read it

### Step 4: Acknowledge

Report:
1. Project name and type
2. Current focus (from sprint doc or recent session)
3. Top 3 priority issues (if any)
4. Last session's state on exit
5. Ready for command

## Rules
- Use absolute paths and `git -C` patterns (no cd && chaining)
- Use `--repo {owner}/{repo}` for all gh commands
- Never use forbidden commands (git reset, git push --force, pip install, etc.)
- All code changes require worktrees - NEVER commit directly to main

## Efficiency Notes

To minimize cost:
1. **Parallel reads** - Read independent files simultaneously
2. **Scan, don't deep-read** - For issue lists, scan titles/labels, skip bodies unless relevant
3. **Recent entries only** - For session logs, read last 3 entries, not the entire file

## Fallback for Unknown Projects

If the project doesn't have standard AgentOS documentation:
1. Read CLAUDE.md (if exists)
2. Read README.md
3. List top-level directories to understand structure
4. Report: "Project {NAME} - minimal onboarding complete. No AgentOS docs found."
