# The Historian: Automated History Check for Issue Workflow

## User Story
As an AgentOS user starting a new issue,
I want the system to automatically check for similar past work,
So that I don't waste time solving problems we've already solved or re-litigating settled decisions.

## Objective
Implement an automated history check node ("The Historian") that queries past completed work before drafting new issues, preventing duplicate effort and preserving institutional knowledge.

## UX Flow

### Scenario 1: No Similar Past Work (Happy Path)
1. User runs issue workflow with a new brief
2. System embeds the brief and queries the vector store for similar history
3. No matches found above threshold (< 0.5 similarity)
4. Workflow proceeds automatically to sandbox/draft phase
5. Result: User experiences no interruption

### Scenario 2: High Similarity Match Found (Duplicate Alert)
1. User runs issue workflow with brief "Optimize Docker build times"
2. System finds "Issue #12: Docker Build Optimization" with 0.91 similarity
3. Workflow pauses with warning: "⚠️ Similar past work detected"
4. User sees: Issue #12 title, summary, and similarity score
5. User chooses option:
   - **Abort**: Workflow terminates ("This appears to be a duplicate")
   - **Link**: Past work summary injected into brief as context, workflow continues
   - **Ignore**: Workflow continues without modification
6. Result: User makes informed decision about proceeding

### Scenario 3: Related Context Found (Silent Enhancement)
1. User runs issue workflow with brief "Add structured logging to API"
2. System finds "Issue #57: Distributed Logging Fix" with 0.67 similarity
3. Related work summary automatically appended to brief as "Related Past Work" section
4. Workflow proceeds automatically (no pause)
5. Result: Agent has historical context without user interruption

### Scenario 4: Rejected Decision in History
1. User runs issue workflow with brief "Implement multi-stage Docker builds"
2. System finds "Issue #25: Docker Build Strategy" noting multi-stage was rejected
3. High similarity triggers pause with context showing the rejection reason
4. User can proceed with knowledge of why this was previously rejected
5. Result: Prevents re-litigating settled architectural decisions

## Requirements

### Vector Infrastructure
1. Expand `rebuild_knowledge_base.py` to index `docs/audit/done/*/001-issue.md`
2. Expand indexing to include `docs/LLDs/done/*.md`
3. Tag indexed history documents with metadata `type: history`
4. Distinguish from existing `type: standard` documents (architectural standards)
5. Extract and store issue number, title, and summary as retrievable metadata

### Historian Node
1. Create `agentos/nodes/historian.py` implementing the history check
2. Accept `brief_content` as input state
3. Embed brief content using same embedding model as Librarian
4. Query vector store with filter `type == history`, retrieve `k=3` results
5. Apply threshold logic:
   - `> 0.85`: High similarity → Duplicate Alert (pause workflow)
   - `0.5 - 0.85`: Related context → Silent enhancement (append to brief)
   - `< 0.5`: No match → Proceed unchanged
6. Output `history_check_result` with status and any matched documents

### Workflow Integration
1. Insert Historian node after "Load Brief" in `agentos/workflows/issue/graph.py`
2. Implement conditional gate based on `history_check_result`
3. Use `human_node` pattern for user interaction on Duplicate Alert
4. Support three user response options: Abort, Link, Ignore
5. Pass enriched brief (with linked context) to downstream nodes

### User Interface
1. Display matched issue number, title, and excerpt on Duplicate Alert
2. Show similarity score for transparency
3. Provide clear option labels with keyboard shortcuts
4. Log user's decision for analytics

## Technical Approach
- **Vector Store:** Extend existing Librarian infrastructure with history corpus and `type` metadata filtering
- **Embedding:** Reuse embedding pipeline from `tools/rebuild_knowledge_base.py`
- **Node Pattern:** Follow existing LangGraph node conventions in `agentos/nodes/`
- **Conditional Routing:** Use LangGraph's conditional edge pattern for gate logic
- **Human Interaction:** Leverage `human_node` interrupt pattern already in codebase

## Security Considerations
- History documents are local project files, no external data exposure
- Vector store queries are read-only during workflow execution
- User retains full control via Abort/Link/Ignore decision
- No automatic actions taken on high-similarity matches without user consent

## Files to Create/Modify
- `agentos/nodes/historian.py` — New node implementing history check logic
- `tools/rebuild_knowledge_base.py` — Extend to index `done/` directories with history metadata
- `agentos/workflows/issue/graph.py` — Insert Historian node and conditional gate
- `agentos/workflows/issue/state.py` — Add `history_check_result` to workflow state
- `docs/wiki/architecture/historian.md` — Document the Historian subsystem

## Dependencies
- Issue #DN-002 (The Librarian) should be completed first to establish vector store infrastructure
- Requires `docs/audit/done/` and `docs/LLDs/done/` directory structure to exist

## Out of Scope (Future)
- **Cross-repository history search** — Querying other projects' history, deferred
- **Automatic issue linking in GitHub** — Creating formal issue references, future enhancement
- **History analytics dashboard** — Visualizing what topics we've covered, separate feature
- **Configurable thresholds** — Hardcoded for MVP, config file support later
- **Incremental indexing** — Full rebuild for now, delta updates in future

## Acceptance Criteria
- [ ] `rebuild_knowledge_base.py` indexes `docs/audit/done/*/001-issue.md` without error
- [ ] `rebuild_knowledge_base.py` indexes `docs/LLDs/done/*.md` without error
- [ ] Indexed history documents have `type: history` metadata
- [ ] Brief "Fix the logging bug" triggers warning when similar logging issue exists in `done/`
- [ ] User can select "Abort" to terminate workflow on duplicate detection
- [ ] User can select "Link" to inject past work summary into brief
- [ ] User can select "Ignore" to proceed without modification
- [ ] Similarity scores 0.5-0.85 silently append context (no user prompt)
- [ ] Similarity scores < 0.5 proceed with no modification or interruption
- [ ] Zero false positives blocking workflow (only > 0.85 triggers pause)

## Definition of Done

### Implementation
- [ ] Core Historian node implemented with threshold logic
- [ ] Workflow graph updated with new node and conditional routing
- [ ] Knowledge base rebuild script extended for history indexing
- [ ] Unit tests for historian node threshold behavior
- [ ] Integration test for full workflow with history check

### Tools
- [ ] Update `rebuild_knowledge_base.py` with `--include-history` flag
- [ ] Document rebuild command with history indexing

### Documentation
- [ ] Create `docs/wiki/architecture/historian.md`
- [ ] Update workflow documentation with Historian node
- [ ] Add ADR for history similarity thresholds (0.5/0.85)
- [ ] Add new files to `docs/0003-file-inventory.md`

### Reports (Pre-Merge Gate)
- [ ] `docs/reports/{IssueID}/implementation-report.md` created
- [ ] `docs/reports/{IssueID}/test-report.md` created

### Verification
- [ ] Run 0809 Security Audit - PASS
- [ ] Run 0817 Wiki Alignment Audit - PASS

## Testing Notes

**To test Duplicate Alert flow:**
1. Ensure a completed issue exists in `docs/audit/done/` (e.g., "Docker optimization")
2. Run `rebuild_knowledge_base.py` to index history
3. Create a brief with very similar content to the completed issue
4. Start issue workflow and verify pause/warning appears
5. Test all three options: Abort, Link, Ignore

**To test Silent Context flow:**
1. Create a brief with moderately related content (target 0.6-0.7 similarity)
2. Verify workflow proceeds without pause
3. Check that "Related Past Work" section appears in enriched brief

**To test No Match flow:**
1. Create a brief for entirely novel work
2. Verify workflow proceeds without any modification or delay

**To force specific similarity scores for testing:**
- Use exact text from past issues for > 0.9
- Use related keywords/concepts for 0.5-0.85
- Use completely unrelated domain terms for < 0.5