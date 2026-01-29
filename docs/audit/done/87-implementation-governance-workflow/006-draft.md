# Implementation Workflow: TDD Enforcement & Context-Aware Code Generation

## User Story
As an **AgentOS developer**,
I want an **implementation workflow that enforces Test-Driven Development and injects architectural context**,
So that **LLM agents write code grounded in reality, use existing utilities, and cannot hallucinate test results**.

## Objective
Create a LangGraph-based implementation workflow that acts as an arbiter—running real pytest commands, enforcing test-first development, and safely managing git operations outside of LLM control.

## Budget Estimate
- **Estimated tokens per run:** ~50k input tokens / ~4k output tokens
- **Max cost per feature implementation:** ~$0.50-$1.00 (depending on retry count)
- **Retry loop impact:** Each retry adds ~20k input tokens (test output injection)
- **Maximum tokens (3 retries + escalation):** ~130k input / ~16k output

## Data Handling Policy
- **Code context transmission:** Code files provided via `--context` are transmitted to the configured Model Provider (e.g., Anthropic Claude)
- **User responsibility:** Ensure `--context` does not include files containing:
  - Personally Identifiable Information (PII)
  - Hardcoded secrets, API keys, or credentials
  - Proprietary code not licensed for LLM transmission
- **Local processing:** Pytest execution and git operations remain local; only code context and agent prompts are transmitted

## UX Flow

### Scenario 1: Happy Path - Successful TDD Cycle
1. Developer runs `python tools/run_implementation_workflow.py --issue 42 --lld docs/LLDs/active/42-feature.md --context docs/standards/0002-coding.md`
2. Workflow loads LLD and context files, builds master prompt
3. Agent scaffolds failing test files based on LLD spec
4. Workflow runs pytest → confirms tests FAIL with **exit code 1** (Red phase - assertion failures)
5. Agent writes implementation code using injected context (knows about `GovernanceAuditLog`, etc.)
6. Workflow runs pytest → tests PASS (Green phase)
7. Workflow runs lint/audit checks
8. Human reviews in VS Code, approves
9. Workflow commits, merges, safely cleans up worktree
10. Result: Feature implemented with verified tests, no hallucination

### Scenario 2: Test Retry Loop (Agent Struggles)
1. Agent writes implementation code
2. Workflow runs pytest → FAIL (exit code 1 - assertion failure)
3. Workflow injects actual pytest stderr/stdout into agent context
4. Agent rewrites code (retry 1)
5. Workflow runs pytest → FAIL again (exit code 1)
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

### Scenario 5: Test Scaffold Has Syntax Error
1. Agent scaffolds test file with Python syntax error
2. N2_TestGate_Fail runs pytest → exit code 4 (Usage Error / collection failure)
3. Workflow detects non-assertion failure: "Test file has syntax or collection error. Rescaffolding."
4. Agent returns to N1_Scaffold (not N3_Coder)
5. Result: Broken test files don't proceed to implementation phase

## Requirements

### TDD Enforcement
1. Tests MUST be written before implementation code (Red-Green-Refactor)
2. N2_TestGate_Fail node MUST verify pytest fails with **exit code 1 specifically** (assertion failures only)
3. N2_TestGate_Fail MUST route back to N1_Scaffold if exit code is 2, 3, 4, or 5 (non-assertion failures indicate broken test scaffolding)
4. N4_TestGate_Pass node MUST verify pytest passes (exit code == 0)
5. Real subprocess execution—never ask LLM "did tests pass?"
6. Maximum 3 retry attempts before human escalation
7. Pytest subprocess calls MUST include a 300-second (5 minute) timeout to prevent hanging tests from freezing the agent

### Pytest Exit Code Handling
1. **Exit Code 0:** Tests passed - proceed to next phase
2. **Exit Code 1:** Tests failed (assertion errors) - valid TDD "Red" state, proceed to implementation
3. **Exit Code 2:** Interrupted - escalate to human review
4. **Exit Code 3:** Internal error - escalate to human review
5. **Exit Code 4:** Usage/collection error (syntax errors, import failures) - retry N1_Scaffold
6. **Exit Code 5:** No tests collected - retry N1_Scaffold

### Context Injection
1. Accept `--context` flag with list of file paths
2. Load and concatenate context files into master prompt
3. Context persists through N1_Scaffold and N3_Coder nodes
4. Support both `.py` and `.md` files as context

### Path Security
1. All paths provided via `--context` MUST be validated to resolve within the current working directory
2. Reject paths containing `../` traversal sequences
3. Reject absolute paths outside project root
4. Reject symbolic links pointing outside project root
5. Log rejected paths to `GovernanceAuditLog` with reason
6. Basic secret file rejection: Reject files matching patterns `*.env`, `.env*`, `*credentials*`, `*secret*`, `*.pem`, `*.key` (case-insensitive)

### State Management
1. Track `test_exit_code` from real pytest runs
2. Track `test_output` (stdout/stderr) for debugging
3. Track `retry_count` to prevent infinite loops
4. Track `changed_files` for safe cleanup
5. Track `scaffold_retry_count` separately for N1 retries (syntax/collection errors)

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
- **State Schema (`agentos/workflows/implementation/state.py`):** TypedDict with `issue_id`, `lld_content`, `context_content`, `test_output`, `test_exit_code`, `retry_count`, `scaffold_retry_count`, `changed_files`.
- **Test Arbiter:** Python `subprocess.run(['pytest', '-v', '--tb=short'], timeout=300)` captures real output. No LLM interpretation of pass/fail. Timeout prevents hanging tests. Exit code 1 specifically required for valid "Red" state.
- **Exit Code Router:** Dedicated routing function that maps pytest exit codes to appropriate next nodes (see Pytest Exit Code Handling requirements).
- **Context Loader:** Reads files after path validation, builds structured prompt with clear sections: `## LLD Specification`, `## Project Context`, `## Coding Standards`.
- **Path Validator:** Resolves all paths via `pathlib.Path.resolve()`, verifies they start with `cwd`, rejects traversal attempts. Includes basic secret file pattern matching.
- **CLI Runner (`tools/run_implementation_workflow.py`):** Argparse interface, initializes state, invokes graph, handles cleanup on interrupt.
- **Mock LLM Mode:** Environment variable `AGENTOS_MOCK_LLM=1` enables deterministic mock responses for testing graph routing logic without API calls. Static fixtures in `tests/fixtures/implementation/` provide canned responses for each node.

## Security Considerations

- **Subprocess Isolation:** Pytest runs in subprocess with timeout, not eval'd code
- **Path Validation:** Context files must exist, be within project root, and not use `../` traversal. Implementation uses `pathlib.Path.resolve()` and validates `resolved_path.is_relative_to(project_root)`
- **Secret File Rejection:** Basic pattern matching rejects common secret file patterns (`.env`, `*.key`, etc.) before transmission
- **Privileged Cleanup:** Only N7_Safe_Merge node can execute destructive git commands
- **No Shell=True:** All subprocess calls use explicit argument lists
- **Audit Trail:** All node transitions logged via `GovernanceAuditLog`
- **Symlink Protection:** Symbolic links are resolved before validation to prevent indirect traversal

## Files to Create/Modify

- `agentos/workflows/implementation/__init__.py` — Package init
- `agentos/workflows/implementation/graph.py` — Main StateGraph definition with all nodes
- `agentos/workflows/implementation/state.py` — ImplementationState TypedDict
- `agentos/workflows/implementation/nodes/context_loader.py` — N0 node implementation with path validation
- `agentos/workflows/implementation/nodes/scaffold.py` — N1 test scaffolding node
- `agentos/workflows/implementation/nodes/test_gates.py` — N2 (must fail with exit code 1) and N4 (must pass) nodes with timeout and exit code routing
- `agentos/workflows/implementation/nodes/coder.py` — N3 implementation writing node
- `agentos/workflows/implementation/nodes/lint_audit.py` — N5 static analysis node
- `agentos/workflows/implementation/nodes/human_review.py` — N6 VS Code integration
- `agentos/workflows/implementation/nodes/safe_merge.py` — N7 privileged git operations
- `agentos/workflows/implementation/path_validator.py` — Centralized path security validation with secret file rejection
- `agentos/workflows/implementation/exit_code_router.py` — Pytest exit code to node routing logic
- `agentos/workflows/implementation/mock_llm.py` — Mock LLM responses for offline testing
- `tools/run_implementation_workflow.py` — CLI entry point
- `tests/workflows/implementation/test_graph.py` — Graph routing tests (uses mock mode)
- `tests/workflows/implementation/test_nodes.py` — Individual node unit tests
- `tests/workflows/implementation/test_path_validator.py` — Path traversal security tests
- `tests/workflows/implementation/test_exit_code_router.py` — Exit code routing logic tests
- `tests/fixtures/implementation/` — Static fixtures for mock LLM mode

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
- **Advanced Secret Scanning** — full AST-based secret detection deferred; basic pattern matching only for MVP
- **Gitignore-Aware Directory Context** — `--context` accepts files only; directory support with gitignore deferred

## Acceptance Criteria

- [ ] Running `python tools/run_implementation_workflow.py --issue 42 --lld path/to/lld.md` executes the full graph
- [ ] Tests are created BEFORE implementation code (N1 → N2 order enforced)
- [ ] N2_TestGate_Fail accepts ONLY exit code 1 as valid "Red" state
- [ ] N2_TestGate_Fail routes to N1_Scaffold on exit codes 4 or 5 (syntax/collection errors)
- [ ] N2_TestGate_Fail routes to N6_Human_Review on exit codes 2 or 3 (interrupts/internal errors)
- [ ] N2_TestGate_Fail rejects if pytest passes (tests must fail first)
- [ ] N4_TestGate_Pass routes to N3_Coder on pytest failure (retry loop)
- [ ] Retry count increments and caps at 3 before human escalation
- [ ] `--context` files appear in agent prompts during N1 and N3
- [ ] Real pytest stdout/stderr captured in `state['test_output']`
- [ ] Worktree cleanup only executes after successful N7_Safe_Merge
- [ ] `GovernanceAuditLog` records all node transitions
- [ ] CLI exits with appropriate codes (0/1/2)
- [ ] Paths with `../` traversal are rejected with clear error message
- [ ] Files matching secret patterns (`.env`, `*.key`, etc.) are rejected
- [ ] Pytest subprocess times out after 300 seconds
- [ ] `AGENTOS_MOCK_LLM=1` enables offline graph testing

## Definition of Done

### Implementation
- [ ] All nodes implemented and wired in graph
- [ ] Conditional routing logic tested (including all pytest exit codes)
- [ ] CLI argument parsing complete
- [ ] Error handling for missing files, invalid paths
- [ ] Path validation rejects traversal attempts
- [ ] Secret file pattern rejection implemented
- [ ] Mock LLM mode functional for offline development
- [ ] Exit code router correctly maps all pytest exit codes

### Tools
- [ ] `tools/run_implementation_workflow.py` documented with `--help`
- [ ] Example usage in tool docstring

### Documentation
- [ ] Update `docs/wiki/workflows.md` with Implementation Workflow section
- [ ] Add architecture diagram showing node flow
- [ ] Document retry behavior and human escalation
- [ ] Document pytest exit code handling logic
- [ ] Add new files to `docs/0003-file-inventory.md`
- [ ] Document data transmission policy in wiki

### Reports (Pre-Merge Gate)
- [ ] `docs/reports/004/implementation-report.md` created
- [ ] `docs/reports/004/test-report.md` created

### Verification
- [ ] Run 0809 Security Audit - PASS (subprocess handling, path validation)
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

**To test path validation security:**
```bash
# Attempt traversal attack
python tools/run_implementation_workflow.py --issue 42 --lld docs/lld.md --context ../../../etc/passwd
# Expected: "Error: Path '../../../etc/passwd' resolves outside project root"

# Attempt absolute path outside project
python tools/run_implementation_workflow.py --issue 42 --lld docs/lld.md --context /etc/passwd
# Expected: "Error: Absolute paths outside project root not allowed"
```

**To test secret file rejection:**
```bash
# Attempt to include .env file
python tools/run_implementation_workflow.py --issue 42 --lld docs/lld.md --context .env
# Expected: "Error: File '.env' matches secret file pattern and cannot be transmitted"

# Attempt to include key file
python tools/run_implementation_workflow.py --issue 42 --lld docs/lld.md --context config/server.key
# Expected: "Error: File 'server.key' matches secret file pattern and cannot be transmitted"
```

**To test mock LLM mode (offline development):**
```bash
# Run graph routing tests without API calls
AGENTOS_MOCK_LLM=1 pytest tests/workflows/implementation/test_graph.py -v

# Force specific mock responses to test error paths
AGENTOS_MOCK_LLM=1 MOCK_FORCE_FAIL=N3 python tools/run_implementation_workflow.py --issue 42 --lld docs/lld.md
```

**To test pytest timeout:**
```bash
# Create a test that hangs indefinitely
# Verify workflow times out after 300 seconds and escalates
```

**To test pytest exit code routing:**
```bash
# Test syntax error handling (exit code 4)
# Create test file with syntax error, verify routes to N1_Scaffold
AGENTOS_MOCK_LLM=1 MOCK_PYTEST_EXIT=4 pytest tests/workflows/implementation/test_exit_code_router.py -v

# Test no tests collected (exit code 5)
# Create empty test file, verify routes to N1_Scaffold
AGENTOS_MOCK_LLM=1 MOCK_PYTEST_EXIT=5 pytest tests/workflows/implementation/test_exit_code_router.py -v

# Test internal error (exit code 3)
# Verify routes to N6_Human_Review
AGENTOS_MOCK_LLM=1 MOCK_PYTEST_EXIT=3 pytest tests/workflows/implementation/test_exit_code_router.py -v
```

## Labels
`workflow`, `core-infrastructure`, `python`

## Effort Estimate
**Large (L)** — Complex state management, subprocess handling, security validation, exit code routing, and mock infrastructure

## Original Brief
# Governance Workflow: Implementation & TDD Enforcement

**Context:** We have firmly established the "Governance-as-Code" pattern with the Issue and LLD workflows. Now we face the most critical challenge: the **Implementation Phase**. This is where LLMs historically fail by hallucinating test results, deleting the wrong files, or writing code that ignores project standards.

## Problem

1. **The "Trust Me" Trap:** Claude/LLMs often claim "I ran the tests and they passed," when they simply imagined a passing result.
2. **Infinite Loops:** Without a strict "Arbiter," an agent can get stuck in a loop of writing broken code, seeing an error, and rewriting the same broken code until the token limit is hit.
3. **Context Amnesia:** The coder doesn't know about `agentos/core/audit.py` or our logging standards unless manually told, leading to duplicate utility functions.
4. **Dangerous Cleanup:** Agents executing `git worktree remove` or `rm -rf` as tool calls are unsafe; these must be privileged **Nodes** in the graph.

## Goal

Create `tools/run_implementation_workflow.py` that enforces a **Test-Driven Development (TDD)** cycle and supports **Context Injection** to ground the LLM in reality.

**Core Philosophy:** The Graph is the Arbiter. The LLM submits code; the Graph runs `pytest`. If `pytest` fails, the Graph rejects the submission.

## Proposed Architecture

### 1. The State Graph (`agentos/workflows/implementation/graph.py`)

* **Input:** `issue_id`, `lld_path` (Approved Design), `context_files` (List[str]).
* **Nodes:**
    * **N0_ContextLoader:** Reads `lld_path` + `context_files`. Builds the "Master Prompt".
    * **N1_Scaffold:** Creates **ONLY** the test files (`tests/test_feature.py`) based on the LLD.
    * **N2_TestGate_Fail:** Runs `pytest`. **MUST FAIL**. (Verifies tests are testing new functionality).
    * **N3_Coder:** Writes/Edits implementation code (`src/feature.py`) to satisfy the tests.
    * **N4_TestGate_Pass:** Runs `pytest`. **MUST PASS**.
        * *Routing:* If Fail -> Return to `N3_Coder` (Max 3 retries).
        * *Routing:* If Pass -> Proceed to `N5`.
    * **N5_Lint_Audit:** Runs static analysis / security checks.
    * **N6_Human_Review:** Final human check in VS Code.
    * **N7_Safe_Merge:** Automated commit, squash (optional), and safe worktree cleanup.

### 2. State Management (`agentos/workflows/implementation/state.py`)

```python
class ImplementationState(TypedDict):
    issue_id: int
    lld_content: str
    context_content: str      # Injected architecture/standards
    test_output: str          # Real stdout/stderr from pytest
    test_exit_code: int       # 0 = Pass, 1 = Fail
    retry_count: int          # To prevent infinite loops
    changed_files: List[str]  # Tracked for cleanup
```

### 3. The TDD Arbiter Logic

We do not ask the LLM "Did the tests pass?" We run `subprocess.run(['pytest', ...])` in a Python function.

* **The Loop:**
```python
def route_after_test(state):
    if state['test_exit_code'] == 0:
        return "N5_Lint_Audit"
    if state['retry_count'] > 3:
        return "N6_Human_Review" # "I'm stuck, human help me"
    return "N3_Coder" # Try again with error logs
```

### 4. The CLI Runner (`tools/run_implementation_workflow.py`)

* **Usage:**
```bash
python tools/run_implementation_workflow.py \
  --issue 42 \
  --lld docs/LLDs/active/42-feature.md \
  --context docs/standards/0002-coding.md agentos/core/audit.py
```

* **Behavior:**
    * Injects the LLD and Context Files into `N1` and `N3`.
    * Manages the Git Worktree isolation (setup/teardown) safely outside the LLM's control.

## Success Criteria

* [ ] **Test-First Enforcement:** The workflow *requires* a failing test before implementation code is accepted.
* [ ] **Context Awareness:** The agent uses existing utilities (e.g., `GovernanceAuditLog`) because `agentos/core/audit.py` was passed via `--context`.
* [ ] **Reality Check:** The workflow loops back automatically when real `pytest` execution fails.
* [ ] **Safety:** Cleanup (worktree removal) happens only after successful merge/commit.