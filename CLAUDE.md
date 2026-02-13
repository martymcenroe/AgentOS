# CLAUDE.md - AssemblyZero Universal Rules

These rules apply to ALL projects under this user's workspace.

---

## Bash Command Constraints

```
BANNED:     &&    |    ;    cd X && command
REQUIRED:   One command per Bash call, absolute paths only
```

| WRONG | CORRECT |
|-------|---------|
| `cd /path && git status` | `git -C /path status` |
| `cat file.txt` | Use `Read` tool |
| `grep pattern file` | Use `Grep` tool |
| `cmd1 && cmd2 && cmd3` | 3 parallel Bash calls |

**If you are about to type `&&` in a Bash command, STOP and rewrite.**

AWS CLI on Windows: ALWAYS prefix with `MSYS_NO_PATHCONV=1`

## Path Format Constraints

| Tool | Format | Example |
|------|--------|---------|
| Bash | Unix `/c/...` | `/c/Users/mcwiz/Projects/...` |
| Read/Write/Edit/Glob | Windows `C:\...` | `C:\Users\mcwiz\Projects\...` |

NEVER use `~` - Windows doesn't expand it.

## Dangerous Path Constraints (I/O Safety)

**NEVER search or traverse these paths:**

| Path | Risk | Why |
|------|------|-----|
| `C:\Users\<user>\OneDrive\` | CRITICAL | Files On-Demand triggers massive downloads |
| `C:\Users\<user>\` (root) | HIGH | Contains OneDrive, AppData, 100K+ files |
| `C:\Users\<user>\AppData\` | HIGH | Hundreds of thousands of small files |

2026-01-15 Incident: `find` on user home triggered 30GB OneDrive download.

Safe alternative: scope to `C:\Users\mcwiz\Projects\` or narrower.

## Destructive Command Constraints

Destructive commands ONLY allowed within `C:\Users\mcwiz\Projects\`.
Catastrophic commands (dd, mkfs, shred, format) are ALWAYS blocked.
Git destructive (reset --hard, push --force, clean -fd, branch -D) require explicit user approval.

## Spawning Agents

When spawning to other models (Sonnet, Haiku), include in the prompt:

> **NEVER search these paths (I/O disaster):**
> - `C:\Users\mcwiz\OneDrive\` - triggers massive cloud downloads
> - `C:\Users\mcwiz\` (root) - contains OneDrive, AppData
> - `C:\Users\mcwiz\AppData\` - hundreds of thousands of files
> - Always scope searches to `C:\Users\mcwiz\Projects\` or narrower

## Python Dependencies

- Use `poetry run python` for all execution - never bare `python`
- Use `poetry add <package>` for dependencies - never `pip install`

## Communication

- Ask clarifying questions before assuming
- After completing a task, ask "What do you want to work on next?" - never offer numbered options
- If blocked, stop and report

## Source of Truth

AssemblyZero is the canonical source for core rules and tools.
Fix things in AssemblyZero, not in local project copies.
Tools execute from `AssemblyZero/tools/`, not copied locally.

## Project Rules

If the current directory has its own `CLAUDE.md`, read it - those rules ADD TO these.
If the project uses the full AssemblyZero workflow, also read `WORKFLOW.md`.
