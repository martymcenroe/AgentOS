# Issue: Implement Governance Workflow StateGraph (v2)

## User Story

**As an** Orchestrator working in Claude Code with Opus 4.5,
**I want** a LangGraph state machine that enforces governance gates,
**So that** Opus cannot skip steps (LLD review, implementation review) even when it "forgets" or acts probabilistically.

---

## The Problem: Probabilistic Agents Don't Follow Rules

**Current Interaction Model:**

```
┌─────────────────────────────────────────────────────────────┐
│                      Claude Code                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    Opus 4.5                          │   │
│  │                                                      │   │
│  │  User: "Work on issue #47"                          │   │
│  │  Opus: [reads CLAUDE.md] "I should create LLD..."   │   │
│  │  Opus: [probabilistic] "Actually, let me just code" │   │
│  │  Opus: [skips gate] Creates PR without review       │   │
│  │                                                      │   │
│  │  ❌ CLAUDE.md is ADVISORY, not ENFORCED             │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

**The Reality:**
- I type instructions to Opus 4.5 in Claude Code
- Opus sometimes follows my instructions
- Opus often does NOT follow instructions (as demonstrated today)
- CLAUDE.md rules are suggestions, not constraints
- Gates can be skipped because nothing enforces them

---

## The Solution: LangGraph as Enforcement Layer

**Proposed Interaction Model:**

```
┌─────────────────────────────────────────────────────────────┐
│                      Claude Code                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    Opus 4.5                          │   │
│  │                                                      │   │
│  │  User: "Work on issue #47"                          │   │
│  │                                                      │   │
│  │  Opus: [MUST invoke workflow first]                 │   │
│  │        ↓                                            │   │
│  │  ┌──────────────────────────────────────────────┐  │   │
│  │  │  python tools/run_workflow.py --issue 47     │  │   │
│  │  │                                              │  │   │
│  │  │  LangGraph StateGraph:                       │  │   │
│  │  │  ├── Current state: LLD_PENDING              │  │   │
│  │  │  ├── Allowed action: Create LLD              │  │   │
│  │  │  └── BLOCKED: Cannot implement yet           │  │   │
│  │  └──────────────────────────────────────────────┘  │   │
│  │        ↓                                            │   │
│  │  Opus: "Issue #47 is at LLD_PENDING. I must        │   │
│  │         create an LLD before implementation."       │   │
│  │                                                      │   │
│  │  ✅ State machine ENFORCES the sequence             │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

**Key Insight:** Opus becomes a DISPATCHER, not the EXECUTOR.

- Opus invokes the workflow tool
- LangGraph does the actual gated work (Gemini calls, file creation)
- Opus reports results to user
- Opus CANNOT bypass because the workflow controls the actions

---

## How It Works

### Step 1: User Requests Work

```
User: "Claude, work on issue #47"
```

### Step 2: Opus Checks Workflow State

```python
# Opus MUST run this before any action
result = subprocess.run([
    "python", "tools/run_workflow.py",
    "--issue", "47",
    "--status"
])
```

Output:
```
Issue #47 Workflow State:
  Phase: LLD_PENDING
  LLD exists: No
  LLD approved: N/A
  Allowed actions: [create_lld]
  Blocked actions: [implement, create_pr]
```

### Step 3: Opus Takes Allowed Action

Opus can only do what the state machine allows:

```python
# If LLD_PENDING, Opus runs designer node via workflow
result = subprocess.run([
    "python", "tools/run_workflow.py",
    "--issue", "47",
    "--action", "create_lld"
])
```

### Step 4: Workflow Advances State

LangGraph creates the LLD and transitions:
```
LLD_PENDING → LLD_REVIEW_PENDING
```

### Step 5: Gemini Review (Automatic)

The workflow automatically submits to Gemini:
```python
# Inside LangGraph - NOT controlled by Opus
result = review_lld_node(state)
# Returns: APPROVED or BLOCKED
```

### Step 6: Gate Enforced

If BLOCKED:
```
Issue #47 Workflow State:
  Phase: LLD_REVISION_REQUIRED
  Gemini verdict: BLOCKED
  Reason: "Missing security section"
  Allowed actions: [revise_lld]
  Blocked actions: [implement, create_pr]
```

Opus CANNOT proceed to implementation. The state machine won't allow it.

---

## What LangGraph Controls

| Action | Controlled By | Opus Role |
|--------|---------------|-----------|
| Check workflow state | LangGraph | Invoke tool, report result |
| Create LLD draft | LangGraph (designer_node) | Invoke tool |
| Submit LLD to Gemini | LangGraph (review_lld_node) | Cannot bypass |
| Advance to implementation | LangGraph (conditional edge) | Cannot force |
| Submit code to Gemini | LangGraph (review_impl_node) | Cannot bypass |
| Create PR | LangGraph (only if APPROVED) | Cannot force |

---

## What Opus Still Does

- Interprets user intent ("work on issue #47")
- Invokes workflow tools
- Reports status to user
- Answers questions about the work
- Revises content when workflow is BLOCKED

Opus is the **interface**, LangGraph is the **enforcer**.

---

## Components Already Built

| Component | Status | Location |
|-----------|--------|----------|
| `AgentState` TypedDict | Done (#48) | `agentos/core/state.py` |
| `review_lld_node` | Done (#50) | `agentos/nodes/governance.py` |
| `designer_node` | Done (#56) | `agentos/nodes/designer.py` |
| `GeminiClient` with rotation | Done (#50) | `agentos/core/gemini_client.py` |
| `GovernanceAuditLog` | Done (#50) | `agentos/core/audit.py` |
| Session-sharded logging | Done (#57) | `agentos/core/audit.py` |

## What's Missing

| Component | Status | Location |
|-----------|--------|----------|
| **Compiled StateGraph** | Missing | `agentos/graphs/governance.py` |
| **CLI entry point** | Missing | `tools/run_workflow.py` |
| **State persistence** | Missing | SQLite checkpointer |

---

## Acceptance Criteria

- [ ] `governance_workflow` StateGraph compiles without errors
- [ ] `tools/run_workflow.py --issue N --status` shows current phase
- [ ] `tools/run_workflow.py --issue N --action X` advances workflow
- [ ] State persists across sessions (SQLite checkpoint)
- [ ] BLOCKED verdict prevents transition to implementation
- [ ] APPROVED verdict allows transition to implementation
- [ ] All transitions logged to audit trail

---

## Definition of Done

### Code
- [ ] `agentos/graphs/governance.py` - StateGraph definition
- [ ] `agentos/graphs/__init__.py` - exports `governance_workflow`
- [ ] `tools/run_workflow.py` - CLI entry point
- [ ] SQLite checkpointer configured

### Tests
- [ ] Unit tests for state transitions
- [ ] Integration test: fresh workflow reaches LLD_REVIEW
- [ ] Integration test: BLOCKED prevents implementation
- [ ] Integration test: resume from checkpoint
- [ ] mypy passes

### Documentation
- [ ] LLD reviewed by Gemini (this document, after approval)
- [ ] Implementation report
- [ ] Test report
- [ ] Usage examples added to wiki

### Review
- [ ] Implementation reviewed by Gemini
- [ ] PR approved and merged
