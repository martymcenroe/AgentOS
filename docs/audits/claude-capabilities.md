# 0815 - Audit: Claude Code Capabilities

## 1. Purpose

Track new Claude Code capabilities and evaluate alignment with AgentOS philosophy. Given rapid Anthropic evolution, run **weekly**.

**AgentOS Philosophy:**
- Agents work autonomously within guardrails
- Documentation before code
- Explicit permission model
- Lessons learned captured
- Workflow standardization

---

## 2. Current Capability Inventory

### Active Features

| Feature | Using? | AgentOS Alignment | Notes |
|---------|--------|-------------------|-------|
| **File Operations** | ✅ | ✅ Aligned | Read/Write/Edit |
| **Bash Commands** | ✅ | ✅ Aligned | With deny list (eval, env, python denied) |
| **Web Search** | ✅ | ✅ Aligned | Research |
| **Web Fetch** | ✅ | ✅ Aligned | Documentation |
| **TodoWrite** | ✅ | ✅ Aligned | Task tracking |
| **Git Operations** | ✅ | ✅ Aligned | With guardrails |
| **GitHub CLI** | ✅ | ✅ Aligned | Issue/PR management |
| **Multi-tool Calls** | ✅ | ✅ Aligned | Parallel execution |
| **Custom Slash Commands** | ✅ | ✅ Aligned | `/closeout`, `/full-cleanup` enforce 0009 protocols |
| **Skills** | ✅ | ✅ Aligned | Managed skills for closeout/cleanup |
| **Background Tasks** | ⚪ | ? | Evaluate |
| **MCP Servers** | ⚪ | ✅ Aligned | Evaluate for CloudWatch Log Inspector |
| **Hooks** | ⚪ | ? | Evaluate |
| **Browser Integration** | ⚪ | ✅ Aligned | Evaluate for extension UI testing |

### Underutilized Features

| Feature | Current Use | Potential Use | Priority |
|---------|-------------|---------------|----------|
| Task (subagents) | Rare | Parallel research | Medium |
| LSP | Never | Code navigation | Low |
| NotebookEdit | Never | N/A (no notebooks) | N/A |
| EnterPlanMode | Never | Complex features | Medium |

---

## 3. New Capability Detection

### Check Sources

1. **Claude Code Changelog:** Check for updates
2. **System Prompt:** Review available tools
3. **Anthropic Blog:** New announcements
4. **GitHub Issues:** Feature requests/releases

### Weekly Review Questions

| Question | Answer | Date Checked |
|----------|--------|--------------|
| New tools available? | Browser Integration (`--chrome`), MCP Servers | 2026-01-05 |
| Existing tools enhanced? | Custom Slash Commands now in use | 2026-01-05 |
| New permission patterns? | Hardened: eval, env, python moved to deny | 2026-01-05 |
| New best practices? | Skills for protocol enforcement | 2026-01-05 |
| Deprecations announced? | None | 2026-01-05 |
| New tools available? | Subagents (Task tool), Named Sessions, Status Line, Thinking Mode | 2026-01-06 |
| Existing tools enhanced? | Task tool now has specialized agent types (Explore, Plan, general-purpose) | 2026-01-06 |
| New permission patterns? | Path Format Rules (Windows vs Unix) added to CLAUDE.md | 2026-01-06 |
| New best practices? | Subagents for parallel research, /friction for permission analysis | 2026-01-06 |

### 2026-01-06 Audit Findings (Issue #182)

**New Features Identified via Deep Mode Web Search:**

| Feature | Description | AgentOS Relevance | Priority |
|---------|-------------|-------------------|----------|
| **Subagents** | Specialized agents via Task tool (`Explore`, `Plan`, `general-purpose`) | High - could automate research phases | Medium |
| **Named Sessions** | `/rename`, `/resume` for session continuity | Medium - multi-day tasks | Low |
| **Status Line** | `/statusline` configuration | Low - UI preference | Low |
| **Thinking Mode** | Enabled by default for Opus 4.5 | Already active | N/A |
| **Skills System** | Dynamic instruction loading (we already use: `/audit`, `/onboard`, `/cleanup`, `/friction`) | High - already adopted | ✅ Adopted |

**2026 Preview (Demo Stage):**
- Long-running tasks
- Swarm capabilities (multi-agent coordination)

**Recommendation:** Subagents (`Task` tool with `Explore` type) should be evaluated for codebase research tasks. Already seeing benefits in audit execution.

---

## 4. AgentOS Alignment Evaluation

### Evaluation Criteria

For each new capability, assess:

| Criterion | Weight | Score (1-5) |
|-----------|--------|-------------|
| Reduces manual orchestration | High | |
| Improves autonomy within guardrails | High | |
| Enhances documentation workflow | Medium | |
| Supports permission model | High | |
| Captures lessons learned | Medium | |
| Integrates with existing tools | Low | |

### Adoption Decision Matrix

| Score | Decision |
|-------|----------|
| 20+ | Adopt immediately |
| 15-19 | Plan adoption |
| 10-14 | Evaluate further |
| < 10 | Skip for now |

---

## 5. Experimentation Backlog

### Features to Try

| Feature | Hypothesis | Experiment | Status |
|---------|------------|------------|--------|
| Browser Integration (`--chrome`) | Could debug extension UI faster than Playwright | Attempt to load extension in `claude --chrome` session | Backlog |
| MCP (CloudWatch) | Safer/faster than `aws logs tail` text parsing | Connect AWS MCP server for Log Inspector (#69) | Backlog |
| Hooks | Could enforce workflow rules | Pre-commit integration | Backlog |
| Task (Explore) | Could speed up codebase research | Try on next research task | Backlog |
| Background Tasks | Could parallelize slow operations | Test with long-running tests | Backlog |

### Completed Experiments

| Feature | Result | Adopted? | Notes |
|---------|--------|----------|-------|
| | | | |

---

## 6. Permission Model Review

### Current Permissions

Review `.claude/settings.local.json`:

| Category | Permissions | Appropriate? |
|----------|-------------|--------------|
| File ops | Read/Write/Edit Aletheia/** | ✅ |
| Bash | Comprehensive allow list | ✅ |
| Deny | git reset, force push, pip, **eval, env, python** | ✅ (hardened 0809) |
| Web | Search, Fetch | ✅ |
| Tools | `./tools/*` binned scripts | ✅ AgentOS aligned |

### Permission Gaps

| Scenario | Missing Permission | Should Add? |
|----------|-------------------|-------------|
| Browser testing | `--chrome` flag | Evaluate in experiment |
| CloudWatch logs | MCP server | Evaluate in experiment |

---

## 7. Audit Procedure

**Frequency:** Weekly (Mondays)

1. Check Anthropic announcements for new capabilities
2. Review system prompt for new tools
3. Evaluate each new capability against §4 criteria
4. Update §2 capability inventory
5. Add promising features to §5 experimentation backlog
6. Review permission model (§6)
7. Document findings

---

## 8. Audit Record

| Date | Auditor | New Capabilities Found | Experiments Started |
|------|---------|------------------------|---------------------|
| 2026-01-05 | Gemini 3.0 Pro | Custom Slash Commands (active), Browser Integration, MCP CloudWatch | Browser/MCP added to backlog |
| 2026-01-06 | Claude Opus 4.5 | Subagents (Explore, Plan), Named Sessions, Status Line, Thinking Mode | Subagent research evaluation (active in this session) |
| 2026-01-12 | Claude Opus 4.5 | **Claude Code 2.1.0/2.1.1** - Hooks for agents/skills, Hot reload skills, Haiku 4.5, Auto-background bash, Prompt suggestions, Claude in Chrome Beta | Skills/Hooks to evaluate |

---

## 9. References

- [Claude Code Documentation](https://docs.anthropic.com/claude-code)
- [Anthropic Blog](https://www.anthropic.com/news)
- docs/0004-orchestration-protocol.md (AgentOS)
- docs/0015-agent-prohibited-actions.md
- .claude/settings.local.json
