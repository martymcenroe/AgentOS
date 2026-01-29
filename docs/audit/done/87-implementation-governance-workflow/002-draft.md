# Implementation Workflow: TDD Enforcement & Context-Aware Code Generation

## User Story
As an **AgentOS developer**,
I want an **implementation workflow that enforces Test-Driven Development and injects architectural context**,
So that **LLM agents write code grounded in reality, use existing utilities, and cannot hallucinate test results**.

## Objective
Create a LangGraph-based implementation workflow that acts as an arbiter—running real pytest commands, enforcing test-first development, and safely managing git operations outside of LLM control.

## UX Flow

### Scenario 1: Happy Path - Successful TDD Cycle
1. Developer runs `python tools/run_implementation_workflow.py --issue 42 --lld docs/LLDs/active/42-feature.md --context docs/standards/0002-coding.md`
2. Workflow loads LLD and context files, builds master prompt
3. Agent scaffolds failing test files based on LLD spec
4. Workflow runs pytest → confirms tests FAIL (Red phase)
5. Agent writes implementation code using injected context (knows about `GovernanceAuditLog`, etc.)
6. Workflow runs pytest → tests PASS (Green phase)
7. Workflow runs lint/audit checks
8. Human reviews in VS Code, approves
9. Workflow commits, merges, safely cleans up worktree
10. Result: Feature implemented with verified tests, no hallucination

### Scenario 2: Test Retry Loop (Agent Struggles)
1. Agent writes implementation code
2. Workflow runs pytest → FAIL (exit code 1)
3. Workflow injects actual pytest stderr/stdout into agent context
4. Agent rewrites code (retry 1)
5. Workflow runs pytest → FAIL again
6. Loop continues up to 3 retries
7. On retry 4: Workflow escalates to Human Review node with full error history
8. Result: Human intervenes before infinite loop burns tokens

### Scenario 3: Test-First Violation Detected
1. Agent attempts to write implementation before tests
2. N2_TestGate_Fail runs pytest → tests PASS (nothing to test yet)
3. Workflow rejects: "Tests must fail before implementation. Write meaningful tests first."
4. Agent returns to N1_Scaffold
5. Result: TDD discipline enforced by graph structure

### Scenario 4: Context Injection Prevents Duplication
1. Developer passes `--context agentos/core/audit.py agentos/core/config.py`
2. Agent sees existing `GovernanceAuditLog` class in context
3. Agent imports and uses existing utility instead of recreating it
4. Result: No duplicate `AuditLogger` class, consistent codebase

## Requirements

### TDD Enforcement
1. Tests MUST be written before implementation code (Red-Green-Refactor)
2. N2_TestGate_Fail node MUST verify pytest fails (exit code != 0)
3. N4_TestGate_Pass node MUST verify pytest passes (exit code == 0)
4. Real subprocess execution—never ask LLM "did tests pass?"
5. Maximum 3 retry attempts before human escalation

### Context Injection
1. Accept `--context` flag with list of file paths
2. Load and concatenate context files into master prompt
3. Context persists through N1_Scaffold and N3_Coder nodes
4. Support both `.py` and `.md` files as context

### State Management
1. Track `test_exit_code` from real pytest runs
2. Track `test_output` (stdout/stderr) for debugging
3. Track `retry_count` to prevent infinite loops
4. Track `changed_files` for safe cleanup

### Safe Operations
1. Git worktree setup/teardown managed by Graph nodes, not LLM
2. `rm -rf` and `git worktree remove` are privileged Node operations only
3. Cleanup happens ONLY after successful merge/commit
4. Rollback capability if merge fails

### CLI Interface
1. Required flags: `--issue`, `--lld`
2. Optional flags: `--context` (multiple files), `--max-retries` (default 3)
3. Clear progress output showing current node
4. Exit codes: 0 (success), 1 (tests failed after retries), 2 (human intervention required)

## Technical Approach

- **State Graph (`agentos/workflows/implementation/graph.py`):** LangGraph StateGraph with conditional routing based on pytest exit codes. Nodes are pure functions, routing is deterministic based on state.
- **State Schema (`agentos/workflows/implementation/state.py`):** TypedDict with `issue_id`, `lld_content`, `context_content`, `test_output`, `test_exit_code`, `retry_count`, `changed_files`.
- **Test Arbiter:** Python `subprocess.run(['pytest', '-v', '--tb=short'])` captures real output. No LLM interpretation of pass/fail.
- **Context Loader:** Reads files, builds structured prompt with clear sections: `## LLD Specification`, `## Project Context`, `## Coding Standards`.
- **CLI Runner (`tools/run_implementation_workflow.py`):** Argparse interface, initializes state, invokes graph, handles cleanup on interrupt.

## Security Considerations

- **Subprocess Isolation:** Pytest runs in subprocess, not eval'd code
- **Path Validation:** Context files must exist and be within project root
- **Privileged Cleanup:** Only N7_Safe_Merge node can execute destructive git commands
- **No Shell=True:** All subprocess calls use explicit argument lists
- **Audit Trail:** All node transitions logged via `GovernanceAuditLog`

## Files to Create/Modify

- `agentos/workflows/implementation/__init__.py` — Package init
- `agentos/workflows/implementation/graph.py` — Main StateGraph definition with all nodes
- `agentos/workflows/implementation/state.py` — ImplementationState TypedDict
- `agentos/workflows/implementation/nodes/context_loader.py` — N0 node implementation
- `agentos/workflows/implementation/nodes/scaffold.py` — N1 test scaffolding node
- `agentos/workflows/implementation/nodes/test_gates.py` — N2 (must fail) and N4 (must pass) nodes
- `agentos/workflows/implementation/nodes/coder.py` — N3 implementation writing node
- `agentos/workflows/implementation/nodes/lint_audit.py` — N5 static analysis node
- `agentos/workflows/implementation/nodes/human_review.py` — N6 VS Code integration
- `agentos/workflows/implementation/nodes/safe_merge.py` — N7 privileged git operations
- `tools/run_implementation_workflow.py` — CLI entry point
- `tests/workflows/implementation/test_graph.py` — Graph routing tests
- `tests/workflows/implementation/test_nodes.py` — Individual node unit tests

## Dependencies

- Issue #003 (LLD Workflow) should be completed first for `lld_path` integration
- Requires `langgraph` package (already in dependencies)
- Requires `pytest` available in environment

## Out of Scope (Future)

- **Parallel Test Execution** — pytest-xdist optimization deferred
- **Multi-Agent Review** — single agent implementation first
- **Auto-Refactor Node** — manual refactor in N3 for now
- **PR Creation** — separate workflow, this ends at local merge
- **Coverage Enforcement** — future enhancement to N5

## Acceptance Criteria

- [ ] Running `python tools/run_implementation_workflow.py --issue 42 --lld path/to/lld.md` executes the full graph
- [ ] Tests are created BEFORE implementation code (N1 → N2 order enforced)
- [ ] N2_TestGate_Fail rejects if pytest passes (tests must fail first)
- [ ] N4_TestGate_Pass routes to N3_Coder on pytest failure (retry loop)
- [ ] Retry count increments and caps at 3 before human escalation
- [ ] `--context` files appear in agent prompts during N1 and N3
- [ ] Real pytest stdout/stderr captured in `state['test_output']`
- [ ] Worktree cleanup only executes after successful N7_Safe_Merge
- [ ] `GovernanceAuditLog` records all node transitions
- [ ] CLI exits with appropriate codes (0/1/2)

## Definition of Done

### Implementation
- [ ] All nodes implemented and wired in graph
- [ ] Conditional routing logic tested
- [ ] CLI argument parsing complete
- [ ] Error handling for missing files, invalid paths

### Tools
- [ ] `tools/run_implementation_workflow.py` documented with `--help`
- [ ] Example usage in tool docstring

### Documentation
- [ ] Update `docs/wiki/workflows.md` with Implementation Workflow section
- [ ] Add architecture diagram showing node flow
- [ ] Document retry behavior and human escalation
- [ ] Add new files to `docs/0003-file-inventory.md`

### Reports (Pre-Merge Gate)
- [ ] `docs/reports/004/implementation-report.md` created
- [ ] `docs/reports/004/test-report.md` created

### Verification
- [ ] Run 0809 Security Audit - PASS (subprocess handling)
- [ ] Run 0817 Wiki Alignment Audit - PASS

## Testing Notes

**To test the retry loop:**
```bash
# Create an LLD that specifies impossible requirements
# Watch agent fail 3 times then escalate
```

**To test context injection:**
```bash
# Pass --context with a file containing a utility class
# Verify agent imports it instead of recreating
grep "from agentos.core.audit import" generated_code.py
```

**To force N2 rejection (tests must fail first):**
```bash
# Manually create passing tests before running workflow
# N2 should reject with "Tests must fail before implementation"
```

**To verify real pytest execution:**
```bash
# Intentionally break a test assertion
# Verify state['test_output'] contains actual pytest traceback
```