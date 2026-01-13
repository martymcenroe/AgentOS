# 0210 - ADR: Git Worktree Isolation

**Status:** Implemented
**Date:** 2025-12-29
**Categories:** Process, Infrastructure, UX

## 1. Context
Switching branches in a single directory (`git checkout`) disrupts local development state:
* Destroys uncommitted temp files.
* Changes dependencies (poetry environment).
* Restarts watching servers/logs.
* **Risk:** "Parallel Universe" confusion (editing file in wrong branch).

## 2. Decision
**We will use `git worktree` to maintain isolated directories for active feature branches.**

Structure:
- `Aletheia/` (Main - Do not touch)
- `Aletheia-80-wire/` (Feature 80)
- `Aletheia-95-sec/` (Feature 95)

## 3. Alternatives Considered

### Option A: Git Worktrees — SELECTED
**Pros:**
- **Isolation:** Dependencies and logs stay intact per feature.
- **Parallelism:** Can run two versions of the app simultaneously.
- **Safety:** Impossible to accidentally commit to wrong branch if folders are named correctly.

**Cons:**
- Disk space usage (full copy of files).
- "Main is already checked out" error (requires `git merge origin/main` workflow).

### Option B: Single Folder Switching
**Pros:**
- Simple standard git usage.

**Cons:**
- Context switching cost is high.
- High risk of cross-contamination.

## 4. Rationale
The cognitive load of managing state across branch switches is too high. Disk space is cheap; attention is expensive.

## 5. Security Risk Analysis
Low risk. Local dev environment only.

## 6. Consequences
- **Positive:** Clean context switching, persistent logs.
- **Negative:** Must learn `git worktree` commands; cannot checkout `main` in feature folders.
