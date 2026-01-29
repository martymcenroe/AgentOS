# LLD Creation & Governance Review Workflow

## User Story
As a **developer creating Low Level Designs**,
I want **an automated workflow that enforces draft → human edit → governance review cycles**,
So that **all LLDs meet quality standards before implementation begins, with full audit trails**.

## Objective
Implement a LangGraph workflow that orchestrates LLD creation from GitHub issues, enforces human review gates, and loops until Gemini 3 Pro governance approval.

## UX Flow

### Scenario 1: Happy Path (First-Pass Approval)
1. Developer runs `python tools/run_lld_workflow.py --issue 42`
2. System fetches issue #42 content from GitHub
3. System generates LLD draft via `designer.py` node
4. System opens draft in VS Code and pauses for human edits
5. Developer refines the LLD, saves, and confirms continuation
6. System submits LLD to `governance.py` for Gemini 3 Pro review
7. Governance returns `[x] **APPROVED**`
8. System saves final LLD to `docs/LLDs/active/LLD-042.md`
9. Result: Workflow completes successfully with approved LLD

### Scenario 2: Governance Rejection Loop
1. Developer runs workflow for issue #42
2. System generates draft, human edits, submits for review
3. Governance returns `[x] **BLOCK**` with critique: "Missing error handling section"
4. System displays critique and routes back to human edit step
5. Developer addresses feedback in VS Code
6. System resubmits to governance
7. Governance returns `[x] **APPROVED**`
8. Result: Workflow completes after 2 iterations

### Scenario 3: Workflow Resume After Interruption
1. Developer starts workflow, completes draft step
2. Developer closes terminal mid-edit (machine restart, etc.)
3. Developer runs `python tools/run_lld_workflow.py --issue 42 --resume`
4. System loads checkpoint from SQLite, resumes at human edit step
5. Result: Workflow continues from last checkpoint without data loss

### Scenario 4: Issue Not Found
1. Developer runs workflow for non-existent issue #9999
2. System queries GitHub API
3. System exits with error: "Issue #9999 not found in repository"
4. Result: Clean failure with actionable message

## Requirements

### Workflow Graph
1. Create `agentos/workflows/lld/graph.py` with LangGraph StateGraph
2. Implement three nodes: `N0_design`, `N1_human_edit`, `N2_review`
3. Implement conditional edge from `N2_review` based on governance verdict
4. Use `SqliteSaver` checkpointer for workflow persistence
5. Support maximum 5 revision iterations before forcing manual intervention

### State Management
1. Create `agentos/workflows/lld/state.py` with TypedDict state schema
2. Track: `issue_id`, `lld_draft_path`, `lld_content`, `governance_verdict`, `governance_critique`, `iteration_count`
3. Persist state between node executions for checkpoint/resume capability

### Node Integration
1. `N0_design` must reuse existing `agentos/nodes/designer.py` without modification
2. `N2_review` must reuse existing `agentos/nodes/governance.py` without modification
3. Nodes receive state dict and return state updates (LangGraph convention)

### Human Gate Implementation
1. `N1_human_edit` must write draft to filesystem at predictable path
2. Open file in VS Code via `code --wait` for blocking edit experience
3. Display governance critique (if any) before edit session
4. Read file contents back into state after human confirms

### CLI Runner
1. Create `tools/run_lld_workflow.py` with argparse interface
2. Required argument: `--issue` (integer)
3. Optional argument: `--resume` (continue from checkpoint)
4. Optional argument: `--max-iterations` (default: 5)
5. Exit code 0 on approval, non-zero on failure

## Technical Approach
- **LangGraph StateGraph:** Orchestrates node execution with conditional routing and checkpointing
- **SqliteSaver:** Enables pause/resume at human edit gate via `.checkpoints.db`
- **Subprocess for VS Code:** `code --wait {filepath}` blocks until user closes editor
- **Existing Nodes:** Import and wrap `designer.py` and `governance.py` functions without modification

## Security Considerations
- GitHub token required for issue fetch (uses existing `GITHUB_TOKEN` env var)
- Gemini API key required for governance review (uses existing `GEMINI_API_KEY`)
- SQLite checkpoint DB stored locally, no sensitive data transmitted
- LLD drafts may contain proprietary design info—files stay local until explicit commit

## Files to Create/Modify
- `agentos/workflows/lld/__init__.py` — Package init
- `agentos/workflows/lld/state.py` — TypedDict state schema
- `agentos/workflows/lld/graph.py` — LangGraph StateGraph definition
- `agentos/workflows/lld/nodes.py` — Node wrapper functions for designer/governance
- `tools/run_lld_workflow.py` — CLI entry point
- `docs/LLDs/active/.gitkeep` — Ensure output directory exists

## Dependencies
- Issue #62 (Issue Creation Workflow) should be completed first for pattern reference
- Existing `agentos/nodes/designer.py` must be functional
- Existing `agentos/nodes/governance.py` must be functional
- `docs/skills/0702c-LLD-Review-Prompt.md` must exist for governance criteria

## Out of Scope (Future)
- **Auto-commit approved LLDs** — deferred; user manually commits for now
- **Slack/Discord notifications** — nice-to-have for team workflows
- **Parallel multi-issue processing** — current scope is single-issue
- **Web UI for human edit gate** — VS Code integration is MVP

## Acceptance Criteria
- [ ] `python tools/run_lld_workflow.py --issue 42` executes full workflow
- [ ] Workflow pauses at human edit step until user closes VS Code
- [ ] Governance rejection routes back to human edit with critique displayed
- [ ] Workflow refuses to complete until `[x] **APPROVED**` received
- [ ] Final LLD saved to `docs/LLDs/active/LLD-{issue_id}.md`
- [ ] `--resume` flag successfully continues interrupted workflow
- [ ] Existing `designer.py` and `governance.py` are imported, not copied/rewritten
- [ ] Maximum 5 iterations enforced before workflow exits with guidance

## Definition of Done

### Implementation
- [ ] Core workflow graph implemented with all three nodes
- [ ] State management with TypedDict schema
- [ ] CLI runner with argument parsing
- [ ] SqliteSaver checkpointing functional
- [ ] Unit tests for state transitions
- [ ] Integration test for full happy path

### Tools
- [ ] `tools/run_lld_workflow.py` created and executable
- [ ] Help text via `--help` documents all arguments
- [ ] Tool added to `tools/README.md` inventory

### Documentation
- [ ] Update wiki with LLD workflow usage guide
- [ ] Add architecture diagram to `docs/workflows/`
- [ ] Document checkpoint/resume behavior
- [ ] Add new files to `docs/0003-file-inventory.md`

### Reports (Pre-Merge Gate)
- [ ] `docs/reports/063/implementation-report.md` created
- [ ] `docs/reports/063/test-report.md` created

### Verification
- [ ] Run 0809 Security Audit - PASS
- [ ] Run 0817 Wiki Alignment Audit - PASS

## Testing Notes

### Manual Testing
1. Create a test issue with design requirements
2. Run workflow: `python tools/run_lld_workflow.py --issue {test_issue}`
3. Verify VS Code opens with draft
4. Make intentional error, save, close VS Code
5. Verify governance rejects and loops back
6. Fix error, save, close VS Code
7. Verify approval and file output

### Force Rejection
- Edit draft to remove "## Error Handling" section before review
- Governance should reject with specific critique about missing section

### Checkpoint Testing
- Start workflow, complete draft step
- Kill process with Ctrl+C during human edit
- Run with `--resume`, verify continuation from edit step