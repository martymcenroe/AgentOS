---
repo: martymcenroe/AssemblyZero
issue: 401
url: https://github.com/martymcenroe/AssemblyZero/issues/401
fetched: 2026-02-19T03:17:50.607905Z
---

# Issue #401: Requirements workflow drafter has no codebase context — hallucinates design

## Problem

The requirements workflow (`run_reqts_workflow.py`) drafts LLDs with zero knowledge of the target codebase. The `claude -p` call receives:

1. The issue text
2. A template
3. The repo directory listing (added in #389)

That's it. Claude runs with `--tools ""` and `--setting-sources user` — no file access, no MCP, no project CLAUDE.md. It cannot read a single line of code from the target repo.

This was masked on AssemblyZero because issues are extremely detailed and the author knows the codebase intimately. On other projects with terser issues, the drafter completely hallucinated the design — invented file paths, imagined architectures, fabricated conventions.

## Root Cause

The implementation spec workflow has an explicit codebase analysis step (N1: `analyze_codebase`) that reads files, finds patterns, and injects excerpts into the drafter prompt. The requirements workflow has no equivalent. It skips straight from "read the issue" to "generate the LLD."

## Proposed Fix

Add a codebase analysis node to the requirements workflow, similar to the implementation spec's N1. Before drafting, the workflow should:

1. **Read key files**: `CLAUDE.md`, `README.md`, `pyproject.toml` / `package.json`, existing architecture docs
2. **Scan existing patterns**: look at module structure, naming conventions, existing similar features
3. **Identify dependencies**: what frameworks, libraries, and tools are already in use
4. **Find related code**: if the issue mentions "authentication" or "testing", find existing auth/test code
5. **Inject context into drafter prompt**: "Here is the existing codebase context. Your LLD must be consistent with these patterns."

The directory listing from #389 is a start but wildly insufficient. A directory tree tells you file names, not architecture.

## Impact

Every LLD generated for a project other than AssemblyZero is potentially hallucinated. This undermines the entire pipeline — bad LLD → bad spec → bad tests → bad code.

## Acceptance Criteria

- [ ] Requirements workflow reads key project files before drafting
- [ ] Existing code patterns are injected into the drafter prompt
- [ ] LLDs for unfamiliar projects reference real file paths and real patterns
- [ ] Works cross-repo (the `--repo` flag already points to the target)