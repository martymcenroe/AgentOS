# Issue: Implement Governance Workflow StateGraph

## Summary

Build the compiled LangGraph StateGraph that connects existing governance nodes into a deterministic workflow, enabling "Claude, work on issue #47" to execute through state-machine-controlled gates.

## The Problem

We have built all the **components** but not the **orchestration**:

| Component | Status |
|-----------|--------|
| `AgentState` TypedDict | Done (#48) |
| `review_lld_node` | Done (#50) |
| `designer_node` | Done (#56) |
| `GeminiClient` with rotation | Done (#50) |
| `GovernanceAuditLog` | Done (#50) |
| Session-sharded logging | Done (#57) |
| **Compiled StateGraph** | Missing |

The `agentos/graphs/__init__.py` file is empty. Nodes exist but aren't connected.

## The Vision

```
User: "Claude, work on issue #47"

→ Graph checks state
→ Executes appropriate node
→ Transitions based on verdict
→ BLOCKS until gates pass (deterministic, not honor system)
→ State persisted via checkpointer
```

## Why This Matters

Current system (CLAUDE.md prompts):
- Probabilistic - Claude might skip steps
- No persistence - session ends, context lost
- Honor system - nothing actually blocks skipping gates

With StateGraph:
- **Deterministic** - state machine controls transitions
- **Persistent** - checkpoints survive session interruption
- **Enforced** - can't reach IMPLEMENT without APPROVED verdict

## Acceptance Criteria

- [ ] `governance_workflow` StateGraph compiles
- [ ] Deterministic transitions based on state values
- [ ] SQLite checkpointing for persistence
- [ ] CLI entry point with `--resume` flag
- [ ] Integration tests for workflow paths
