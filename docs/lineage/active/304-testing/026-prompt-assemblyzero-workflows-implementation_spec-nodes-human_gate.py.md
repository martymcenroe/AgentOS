# Implementation Request: assemblyzero/workflows/implementation_spec/nodes/human_gate.py

## Task

Write the complete contents of `assemblyzero/workflows/implementation_spec/nodes/human_gate.py`.

Change type: Add
Description: N4: Optional human review gate

## LLD Specification

# 304 - Feature: Implementation Readiness Review Workflow (LLD → Implementation Spec)

<!-- Template Metadata
Last Updated: 2026-02-16
Updated By: LLD Generation Workflow
Update Reason: Revision to fix path validation errors - directories don't exist
-->

## 1. Context & Goal
* **Issue:** #304
* **Objective:** Create a workflow that transforms approved LLDs into Implementation Specs with enough concrete detail for autonomous AI implementation
* **Status:** Approved (gemini-3-pro-preview, 2026-02-16)
* **Related Issues:** #139 (rename workflows/testing/ to workflows/implementation/)

### Open Questions

- [x] Should the Implementation Spec be a separate file or an appendix to the LLD? **Decision: Separate file in `docs/lld/drafts/` directory (using existing directory)**
- [x] What is the target success rate for first-try implementations? **Decision: >80% per issue requirements**
- [ ] Should there be a "lightweight" mode for simple changes that don't need full spec generation?

## 2. Proposed Changes

*This section is the **source of truth** for implementation. Describe exactly what will be built.*

### 2.1 Files Changed

| File | Change Type | Description |
|------|-------------|-------------|
| `assemblyzero/workflows/implementation_spec/` | Add (Directory) | New workflow package directory |
| `assemblyzero/workflows/implementation_spec/__init__.py` | Add | Package init with workflow exports |
| `assemblyzero/workflows/implementation_spec/graph.py` | Add | LangGraph workflow definition |
| `assemblyzero/workflows/implementation_spec/state.py` | Add | TypedDict state definitions |
| `assemblyzero/workflows/implementation_spec/nodes/` | Add (Directory) | Nodes subpackage directory |
| `assemblyzero/workflows/implementation_spec/nodes/__init__.py` | Add | Nodes package init |
| `assemblyzero/workflows/implementation_spec/nodes/load_lld.py` | Add | N0: Load approved LLD |
| `assemblyzero/workflows/implementation_spec/nodes/analyze_codebase.py` | Add | N1: Extract current state from files |
| `assemblyzero/workflows/implementation_spec/nodes/generate_spec.py` | Add | N2: Generate implementation spec draft |
| `assemblyzero/workflows/implementation_spec/nodes/validate_completeness.py` | Add | N3: Validate mechanical completeness |
| `assemblyzero/workflows/implementation_spec/nodes/human_gate.py` | Add | N4: Optional human review gate |
| `assemblyzero/workflows/implementation_spec/nodes/review_spec.py` | Add | N5: Gemini readiness review |
| `assemblyzero/workflows/implementation_spec/nodes/finalize_spec.py` | Add | N6: Finalize and write spec |
| `docs/standards/0701-implementation-spec-template.md` | Add | Template for Implementation Specs |
| `docs/standards/0702-implementation-readiness-review.md` | Add | Review criteria and process documentation |
| `docs/prompts/` | Add (Directory) | New prompts directory under docs |
| `docs/prompts/implementation_spec/` | Add (Directory) | Prompts for this workflow |
| `docs/prompts/implementation_spec/drafter_system.md` | Add | Claude system prompt for spec generation |
| `docs/prompts/implementation_spec/drafter_user.md` | Add | Claude user prompt template |
| `docs/prompts/implementation_spec/reviewer_system.md` | Add | Gemini system prompt for readiness review |
| `docs/prompts/implementation_spec/reviewer_user.md` | Add | Gemini user prompt template |
| `tools/run_implementation_spec_workflow.py` | Add | CLI tool to run the workflow |
| `tests/unit/test_implementation_spec_workflow.py` | Add | Unit tests for workflow |
| `tests/unit/test_implementation_spec_nodes.py` | Add | Unit tests for individual nodes |

### 2.1.1 Path Validation (Mechanical - Auto-Checked)

*Issue #277: Before human or Gemini review, paths are verified programmatically.*

Mechanical validation automatically checks:
- All "Modify" files must exist in repository
- All "Delete" files must exist in repository
- All "Add" files must have existing parent directories
- No placeholder prefixes (`src/`, `lib/`, `app/`) unless directory exists

**Parent directories to verify exist:**
- `assemblyzero/workflows/` ✓ (exists, see repo structure)
- `docs/standards/` ✓ (exists, see repo structure)
- `docs/` ✓ (exists, for new `docs/prompts/` directory)
- `tools/` ✓ (exists, see repo structure)
- `tests/unit/` ✓ (exists, see repo structure)

**New directories being created:**
- `assemblyzero/workflows/implementation_spec/` - Parent `assemblyzero/workflows/` exists ✓
- `assemblyzero/workflows/implementation_spec/nodes/` - Created after parent ✓
- `docs/prompts/` - Parent `docs/` exists ✓
- `docs/prompts/implementation_spec/` - Created after parent ✓

**If validation fails, the LLD is BLOCKED before reaching review.**

### 2.2 Dependencies

*New packages, APIs, or services required.*

```toml
# pyproject.toml additions (if any)
# No new dependencies required - uses existing:
# - langgraph (workflow orchestration)
# - anthropic (Claude for drafting)
# - google-generativeai (Gemini for review)
```

### 2.3 Data Structures

```python
# State for the Implementation Spec workflow
class ImplementationSpecState(TypedDict):
    # Input
    issue_number: int                    # GitHub issue being implemented
    lld_path: str                        # Path to approved LLD file
    
    # Loaded content
    lld_content: str                     # Raw LLD markdown
    files_to_modify: list[FileToModify]  # Parsed from LLD section 2.1
    
    # Codebase analysis
    current_state_snapshots: dict[str, str]  # file_path -> code excerpt
    pattern_references: list[PatternRef]      # Similar patterns found
    
    # Generated spec
    spec_draft: str                      # Generated Implementation Spec
    spec_path: str                       # Output path for spec
    
    # Validation
    completeness_issues: list[str]       # Issues found in N3
    validation_passed: bool              # N3 result
    
    # Review
    review_verdict: Literal["APPROVED", "REVISE", "BLOCKED"]
    review_feedback: str                 # Gemini review comments
    review_iteration: int                # Current review round
    
    # Workflow control
    max_iterations: int                  # Default 3
    human_gate_enabled: bool             # Whether N4 is active
    
class FileToModify(TypedDict):
    path: str                # File path from LLD
    change_type: Literal["Add", "Modify", "Delete"]
    description: str         # From LLD
    current_content: str | None  # Loaded in N1 for Modify/Delete
    
class PatternRef(TypedDict):
    file_path: str           # Where pattern exists
    start_line: int          # Line range
    end_line: int
    pattern_type: str        # e.g., "node implementation", "state definition"
    relevance: str           # Why this pattern is relevant

class CompletenessCheck(TypedDict):
    check_name: str          # e.g., "modify_files_have_excerpts"
    passed: bool
    details: str             # Explanation if failed
```

### 2.4 Function Signatures

```python
# graph.py
def create_implementation_spec_graph() -> CompiledStateGraph:
    """Create the LangGraph workflow for Implementation Spec generation."""
    ...

def route_after_validation(state: ImplementationSpecState) -> str:
    """Route after N3: to N4/N5 if passed, back to N2 if blocked."""
    ...

def route_after_review(state: ImplementationSpecState) -> str:
    """Route after N5: to N6 if approved, back to N2 if revise."""
    ...

# nodes/load_lld.py
def load_lld(state: ImplementationSpecState) -> dict:
    """N0: Load and parse the approved LLD file."""
    ...

def parse_files_to_modify(lld_content: str) -> list[FileToModify]:
    """Extract files from LLD Section 2.1 table."""
    ...

# nodes/analyze_codebase.py
def analyze_codebase(state: ImplementationSpecState) -> dict:
    """N1: Read files and extract current state snapshots."""
    ...

def extract_relevant_excerpt(file_path: str, lld_context: str) -> str:
    """Extract the portion of file relevant to the change."""
    ...

def find_pattern_references(
    files_to_modify: list[FileToModify],
    repo_root: Path
) -> list[PatternRef]:
    """Find similar implementation patterns in the codebase."""
    ...

# nodes/generate_spec.py
async def generate_spec(state: ImplementationSpecState) -> dict:
    """N2: Generate Implementation Spec draft using Claude."""
    ...

def build_drafter_prompt(
    lld_content: str,
    current_state: dict[str, str],
    patterns: list[PatternRef]
) -> str:
    """Build the prompt for Claude spec generation."""
    ...

# nodes/validate_completeness.py
def validate_completeness(state: ImplementationSpecState) -> dict:
    """N3: Check that spec meets mechanical completeness criteria."""
    ...

def check_modify_files_have_excerpts(spec: str, files: list[FileToModify]) -> CompletenessCheck:
    """Every 'Modify' file must have current state excerpt."""
    ...

def check_data_structures_have_examples(spec: str) -> CompletenessCheck:
    """Every data structure must have concrete JSON/YAML example."""
    ...

def check_functions_have_io_examples(spec: str) -> CompletenessCheck:
    """Every function must have input/output examples."""
    ...

def check_change_instructions_specific(spec: str) -> CompletenessCheck:
    """Change instructions must be diff-level specific."""
    ...

def check_pattern_references_valid(
    spec: str, 
    pattern_refs: list[PatternRef]
) -> CompletenessCheck:
    """Verify referenced patterns exist at specified locations."""
    ...

# nodes/human_gate.py
def human_gate(state: ImplementationSpecState) -> dict:
    """N4: Optional human review checkpoint."""
    ...

# nodes/review_spec.py
async def review_spec(state: ImplementationSpecState) -> dict:
    """N5: Send spec to Gemini for implementation readiness review."""
    ...

def parse_review_verdict(response: str) -> tuple[str, str]:
    """Extract verdict and feedback from Gemini response."""
    ...

# nodes/finalize_spec.py
def finalize_spec(state: ImplementationSpecState) -> dict:
    """N6: Write final spec to docs/lld/drafts/ directory."""
    ...

def generate_spec_filename(issue_number: int) -> str:
    """Generate filename like 'spec-0304-implementation-readiness.md'."""
    ...
```

### 2.5 Logic Flow (Pseudocode)

```
1. N0: Load LLD
   - Read approved LLD file from docs/lld/active/{issue}.md or docs/lld/done/{issue}.md
   - Parse Section 2.1 to extract files to modify
   - Validate LLD has "APPROVED" status
   - IF not approved THEN abort with error
   
2. N1: Analyze Codebase
   - FOR each file in files_to_modify:
     - IF change_type is "Modify" or "Delete":
       - Read file content
       - Extract relevant excerpt (functions/classes mentioned in LLD)
     - Store in current_state_snapshots
   - Scan repo for similar patterns (existing workflows, nodes)
   - Store pattern references with file:line locations
   
3. N2: Generate Spec
   - Build prompt with:
     - Full LLD content
     - Current state snapshots for each file
     - Pattern references with code excerpts
     - Implementation Spec template
   - Call Claude API with drafter prompts
   - Parse response as Implementation Spec draft
   
4. N3: Validate Completeness
   - Run mechanical checks:
     - Every "Modify" file has current state excerpt
     - Every data structure has concrete example
     - Every function has I/O examples
     - Change instructions are specific (contains line refs or diff notation)
     - Pattern references point to existing code
   - IF any check fails:
     - validation_passed = False
     - Store issues in completeness_issues
   - ELSE:
     - validation_passed = True
   
5. Route after N3:
   - IF validation_passed AND review_iteration < max_iterations:
     - IF human_gate_enabled: goto N4
     - ELSE: goto N5
   - ELSE IF NOT validation_passed:
     - IF review_iteration < max_iterations: goto N2 (regenerate)
     - ELSE: abort with "Max iterations exceeded"
   
6. N4: Human Gate (optional)
   - Display spec draft for human review
   - Prompt for approval/feedback
   - IF approved: continue to N5
   - IF feedback provided: goto N2 with feedback
   
7. N5: Review Spec
   - Build Gemini prompt with:
     - Implementation Spec draft
     - Readiness review criteria
   - Call Gemini API
   - Parse verdict: APPROVED / REVISE / BLOCKED
   - Store feedback
   
8. Route after N5:
   - IF verdict == "APPROVED": goto N6
   - IF verdict == "REVISE" AND iteration < max:
     - Increment review_iteration
     - goto N2 with feedback
   - IF verdict == "BLOCKED" OR iteration >= max:
     - Abort with review feedback
   
9. N6: Finalize Spec
   - Add review log to spec
   - Write to docs/lld/drafts/spec-{issue_number}.md
   - Return success with spec path
```

### 2.6 Technical Approach

* **Module:** `assemblyzero/workflows/implementation_spec/`
* **Pattern:** LangGraph state machine with conditional routing
* **Key Decisions:** 
  - Reuse existing workflow patterns from `workflows/requirements/`
  - Separate mechanical validation (N3) from semantic review (N5)
  - Make human gate optional (default: disabled for automation)

### 2.7 Architecture Decisions

| Decision | Options Considered | Choice | Rationale |
|----------|-------------------|--------|-----------|
| Spec storage location | Append to LLD, Separate file, In-memory only | Separate file in `docs/lld/drafts/` | Clean separation of concerns; LLD is design, Spec is execution; uses existing directory |
| Drafter model | Claude, Gemini, GPT-4 | Claude (via SDK) | Consistent with existing workflows; better at structured generation |
| Reviewer model | Claude, Gemini | Gemini | Different perspective from drafter; Gemini good at checklist validation |
| Validation timing | Before review only, After generation only, Both | Before review (N3) | Catch mechanical issues early, save API costs |
| Pattern matching approach | AST parsing, Regex, Embedding search | Regex + file scanning | Simple, fast, sufficient for finding similar node implementations |
| Prompts location | `prompts/` (root), `docs/prompts/`, inline | `docs/prompts/` | Root `prompts/` doesn't exist; `docs/` has existing structure |

**Architectural Constraints:**
- Must integrate with existing `run_requirements_workflow.py` pattern
- Must use existing Gemini/Claude credential paths
- Cannot introduce new external dependencies beyond existing stack
- Must follow existing node structure (single file per node, state in/dict out)

## 3. Requirements

*What must be true when this is done. These become acceptance criteria.*

1. **R1:** Workflow transforms approved LLDs into Implementation Specs with concrete details
2. **R2:** Every "Modify" file in the spec includes current state excerpt from the actual codebase
3. **R3:** Every data structure has at least one concrete JSON/YAML example (not just TypedDict)
4. **R4:** Every function signature has input/output examples with actual values
5. **R5:** Change instructions are specific enough to generate diffs (line-level guidance)
6. **R6:** Pattern references include file:line and are verified to exist
7. **R7:** Gemini review uses different criteria than LLD review (executability focus)
8. **R8:** Workflow achieves >80% first-try implementation success rate
9. **R9:** CLI tool follows existing pattern (`run_implementation_spec_workflow.py`)
10. **R10:** Human gate is optional and defaults to disabled

## 4. Alternatives Considered

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Extend LLD template instead of separate spec | Single document, less complexity | LLD becomes too large, mixes design with execution | **Rejected** |
| Use Claude for both drafting and review | Consistent model, simpler | No independent perspective, may miss issues drafter would miss | **Rejected** |
| Skip mechanical validation (N3) | Faster workflow | Wastes API calls on incomplete specs | **Rejected** |
| Make human gate mandatory | Catches more issues | Blocks automation, defeats purpose | **Rejected** |
| Generate specs as part of implementation workflow | Single workflow, less overhead | Harder to debug, can't pre-verify spec quality | **Rejected** |
| Store prompts in root `prompts/` directory | Matches some patterns | Directory doesn't exist; would need to create | **Rejected** |

**Rationale:** Separate spec file with mechanical validation before Gemini review provides the best balance of automation and quality control. Using `docs/prompts/` leverages existing `docs/` directory structure.

## 5. Data & Fixtures

### 5.1 Data Sources

| Attribute | Value |
|-----------|-------|
| Source | Approved LLD files in `docs/lld/`, codebase files |
| Format | Markdown (LLD), Python (codebase) |
| Size | LLDs: 5-30KB, Codebase files: 1-50KB each |
| Refresh | On-demand per workflow run |
| Copyright/License | MIT (AssemblyZero project) |

### 5.2 Data Pipeline

```
docs/lld/{issue}.md ──parse──► FileToModify list ──read──► Current state snapshots
                                                              │
                                                              ▼
                                              Pattern references ──build──► Claude prompt
                                                                              │
                                                                              ▼
                                              Implementation Spec draft ──validate──► N3
                                                                              │
                                                                              ▼
                                              Gemini review ──finalize──► docs/lld/drafts/spec-{issue}.md
```

### 5.3 Test Fixtures

| Fixture | Source | Notes |
|---------|--------|-------|
| `tests/fixtures/lld_approved_simple.md` | Generated | Simple LLD with 2 files to modify |
| `tests/fixtures/lld_approved_complex.md` | Generated | Complex LLD with 10+ files, patterns |
| `tests/fixtures/lld_not_approved.md` | Generated | LLD without APPROVED status |
| `tests/fixtures/mock_codebase/` | Generated | Minimal codebase structure for testing |
| `tests/fixtures/spec_complete.md` | Generated | Example of complete Implementation Spec |
| `tests/fixtures/spec_incomplete.md` | Generated | Spec failing completeness checks |

### 5.4 Deployment Pipeline

N/A - CLI tool runs locally. Specs are committed to repository like LLDs.

## 6. Diagram

### 6.1 Mermaid Quality Gate

Before finalizing any diagram, verify in [Mermaid Live Editor](https://mermaid.live) or GitHub preview:

- [x] **Simplicity:** Similar components collapsed (per 0006 §8.1)
- [x] **No touching:** All elements have visual separation (per 0006 §8.2)
- [x] **No hidden lines:** All arrows fully visible (per 0006 §8.3)
- [x] **Readable:** Labels not truncated, flow direction clear
- [ ] **Auto-inspected:** Agent rendered via mermaid.ink and viewed (per 0006 §8.5)

**Auto-Inspection Results:**
```
- Touching elements: [ ] None / [ ] Found: ___
- Hidden lines: [ ] None / [ ] Found: ___
- Label readability: [ ] Pass / [ ] Issue: ___
- Flow clarity: [ ] Clear / [ ] Issue: ___
```

*Reference: [0006-mermaid-diagrams.md](0006-mermaid-diagrams.md)*

### 6.2 Diagram

```mermaid
flowchart TD
    subgraph Input
        LLD[Approved LLD]
        CODE[Codebase Files]
    end

    subgraph Workflow["Implementation Spec Workflow"]
        N0[N0: Load LLD]
        N1[N1: Analyze Codebase]
        N2[N2: Generate Spec<br/>Claude]
        N3{N3: Validate<br/>Completeness}
        N4[N4: Human Gate<br/>Optional]
        N5{N5: Review Spec<br/>Gemini}
        N6[N6: Finalize]
    end

    subgraph Output
        SPEC[Implementation Spec]
    end

    LLD --> N0
    N0 --> N1
    CODE --> N1
    N1 --> N2
    N2 --> N3
    
    N3 -->|PASSED| N4
    N3 -->|BLOCKED| N2
    
    N4 --> N5
    
    N5 -->|APPROVED| N6
    N5 -->|REVISE| N2
    
    N6 --> SPEC
```

## 7. Security & Safety Considerations

### 7.1 Security

| Concern | Mitigation | Status |
|---------|------------|--------|
| API key exposure in logs | Use existing credential handling; no keys in state | Addressed |
| Arbitrary file read | Limit file reads to files listed in LLD Section 2.1 | Addressed |
| Prompt injection via LLD | LLD is internal document, not user input | N/A |

### 7.2 Safety

| Concern | Mitigation | Status |
|---------|------------|--------|
| Infinite retry loops | Max 3 iterations (configurable) | Addressed |
| Large file loading | Excerpt extraction limits content size; use `summarize_file_for_context()` | Addressed |
| API timeout | Use existing `compute_dynamic_timeout()` from #373 | Addressed |
| Partial spec written on failure | Atomic write: generate to temp, move on success | Addressed |

**Fail Mode:** Fail Closed - If validation or review fails after max iterations, workflow aborts without writing spec

**Recovery Strategy:** Re-run workflow from beginning; no partial state persisted between runs

## 8. Performance & Cost Considerations

### 8.1 Performance

| Metric | Budget | Approach |
|--------|--------|----------|
| Total workflow time | < 5 minutes | Parallel file reads in N1; single API call per node |
| Memory | < 256MB | Stream file reads; don't load entire codebase |
| API calls per run | 2-6 (1 Claude + 1-3 Gemini) | Mechanical validation reduces unnecessary reviews |

**Bottlenecks:** 
- Claude spec generation (30-60s per call)
- Gemini review (15-30s per call)
- Large codebases may slow N1 file scanning

### 8.2 Cost Analysis

| Resource | Unit Cost | Estimated Usage | Monthly Cost |
|----------|-----------|-----------------|--------------|
| Claude Sonnet (spec gen) | ~$0.003/1K tokens | ~20K tokens/run, 30 runs/month | ~$1.80 |
| Gemini Pro (review) | ~$0.00025/1K tokens | ~15K tokens/run, 45 runs/month | ~$0.17 |
| Total | | | ~$2.00 |

**Cost Controls:**
- [x] Mechanical validation (N3) prevents unnecessary Gemini calls
- [x] Max iteration limit prevents runaway retries
- [x] Excerpt extraction limits prompt size

**Worst-Case Scenario:** If every run hits 3 iterations, costs ~$6/month - acceptable

## 9. Legal & Compliance

| Concern | Applies? | Mitigation |
|---------|----------|------------|
| PII/Personal Data | No | Workflow processes code and docs only |
| Third-Party Licenses | No | Uses existing licensed dependencies |
| Terms of Service | Yes | Claude and Gemini API usage within ToS |
| Data Retention | No | Specs stored in git, follows project policy |
| Export Controls | No | No restricted algorithms |

**Data Classification:** Internal (design documents)

**Compliance Checklist:**
- [x] No PII stored without consent
- [x] All third-party licenses compatible with project license
- [x] External API usage compliant with provider ToS
- [x] Data retention policy documented (git history)

## 10. Verification & Testing

### 10.0 Test Plan (TDD - Complete Before Implementation)

**TDD Requirement:** Tests MUST be written and failing BEFORE implementation begins.

| Test ID | Test Description | Expected Behavior | Status |
|---------|------------------|-------------------|--------|
| T010 | Load approved LLD | Parses LLD and extracts files list | RED |
| T020 | Reject unapproved LLD | Raises error for PENDING status | RED |
| T030 | Analyze codebase extracts excerpts | Returns dict of file→excerpt | RED |
| T040 | Generate spec includes all sections | Spec has concrete examples | RED |
| T050 | Validate completeness catches missing excerpts | Returns BLOCKED | RED |
| T060 | Validate completeness passes complete spec | Returns PASSED | RED |
| T070 | Review spec routing on APPROVED | Routes to N6 | RED |
| T080 | Review spec routing on REVISE | Routes to N2, increments iteration | RED |
| T090 | Finalize writes spec file | File exists at expected path | RED |
| T100 | CLI runs full workflow | Produces spec file | RED |

**Coverage Target:** ≥95% for all new code

**TDD Checklist:**
- [ ] All tests written before implementation
- [ ] Tests currently RED (failing)
- [ ] Test IDs match scenario IDs in 10.1
- [ ] Test file created at: `tests/unit/test_implementation_spec_workflow.py`

### 10.1 Test Scenarios

| ID | Scenario | Type | Input | Expected Output | Pass Criteria |
|----|----------|------|-------|-----------------|---------------|
| 010 | Happy path - simple LLD | Auto | `tests/fixtures/lld_approved_simple.md` | Spec at `docs/lld/drafts/spec-999.md` | File exists, contains excerpts |
| 020 | Complex LLD with many files | Auto | `tests/fixtures/lld_approved_complex.md` | Complete spec | All 10+ files have excerpts |
| 030 | Unapproved LLD rejection | Auto | `tests/fixtures/lld_not_approved.md` | Error raised | Workflow aborts before N1 |
| 040 | File not found in codebase | Auto | LLD with non-existent file | Graceful error | Clear message about missing file |
| 050 | Incomplete spec regeneration | Auto | Mock Claude returns incomplete | N3 → N2 retry | Second attempt improves |
| 060 | Max iterations exceeded | Auto | Mock always returns incomplete | Workflow aborts | Error after 3 iterations |
| 070 | Gemini REVISE verdict | Auto | Mock Gemini returns REVISE | Regenerate with feedback | Feedback in next N2 prompt |
| 080 | Pattern reference validation | Auto | Spec references existing pattern | Check passes | Pattern at file:line exists |
| 090 | Invalid pattern reference | Auto | Spec references non-existent line | Check fails | Completeness blocked |
| 100 | CLI end-to-end | Auto | Valid issue number | Spec file created | Exit code 0 |

### 10.2 Test Commands

```bash
# Run all automated tests
poetry run pytest tests/unit/test_implementation_spec_workflow.py tests/unit/test_implementation_spec_nodes.py -v

# Run only fast/mocked tests (exclude live)
poetry run pytest tests/unit/test_implementation_spec_*.py -v -m "not live"

# Run live integration tests (hits real APIs)
poetry run pytest tests/unit/test_implementation_spec_*.py -v -m live
```

### 10.3 Manual Tests (Only If Unavoidable)

N/A - All scenarios automated.

## 11. Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Claude generates inconsistent spec format | Med | Med | Strict template in prompt; mechanical validation |
| Gemini review criteria too strict | Med | Low | Tunable criteria; start lenient, tighten over time |
| Large codebases slow workflow | Low | Med | Excerpt extraction limits; parallel file reads |
| Pattern matching misses relevant code | Low | Med | Fallback to keyword search; human gate option |
| Implementation success rate below 80% | High | Med | Iterate on prompt engineering; add more examples |

## 12. Definition of Done

### Code
- [ ] Implementation complete and linted
- [ ] Code comments reference this LLD

### Tests
- [ ] All test scenarios pass
- [ ] Test coverage meets threshold (≥95%)

### Documentation
- [ ] LLD updated with any deviations
- [ ] Implementation Report (0103) completed
- [ ] 0701-implementation-spec-template.md created
- [ ] 0702-implementation-readiness-review.md created

### Review
- [ ] Code review completed
- [ ] User approval before closing issue

### 12.1 Traceability (Mechanical - Auto-Checked)

*Issue #277: Cross-references are verified programmatically.*

Files mentioned in Definition of Done:
- `assemblyzero/workflows/implementation_spec/` - Listed in 2.1 ✓
- `docs/standards/0701-implementation-spec-template.md` - Listed in 2.1 ✓
- `docs/standards/0702-implementation-readiness-review.md` - Listed in 2.1 ✓
- `tests/unit/test_implementation_spec_workflow.py` - Listed in 2.1 ✓

Risk mitigations traceability:
- "mechanical validation" → `validate_completeness()` in 2.4 ✓
- "excerpt extraction" → `extract_relevant_excerpt()` in 2.4 ✓

**If files are missing from Section 2.1, the LLD is BLOCKED.**

---

## Reviewer Suggestions

*Non-blocking recommendations from the reviewer.*

- **Performance:** Ensure `nodes/analyze_codebase.py` implements a reasonable timeout or file size limit when extracting excerpts to prevent hanging on accidentally large files.
- **Maintainability:** Consider versioning the `docs/standards/0701-implementation-spec-template.md` (e.g., adding a version header) so the workflow can detect if it's generating an outdated spec format in the future.

## Appendix: Review Log

*Track all review feedback with timestamps and implementation status.*

### Review Summary

| Review | Date | Verdict | Key Issue |
|--------|------|---------|-----------|
| 1 | 2026-02-16 | APPROVED | `gemini-3-pro-preview` |
| | | | |

**Final Status:** APPROVED

## Required File Paths (from LLD - do not deviate)

The following paths are specified in the LLD. Write ONLY to these paths:

- `assemblyzero/workflows/implementation_spec`
- `assemblyzero/workflows/implementation_spec/__init__.py`
- `assemblyzero/workflows/implementation_spec/graph.py`
- `assemblyzero/workflows/implementation_spec/nodes`
- `assemblyzero/workflows/implementation_spec/nodes/__init__.py`
- `assemblyzero/workflows/implementation_spec/nodes/analyze_codebase.py`
- `assemblyzero/workflows/implementation_spec/nodes/finalize_spec.py`
- `assemblyzero/workflows/implementation_spec/nodes/generate_spec.py`
- `assemblyzero/workflows/implementation_spec/nodes/human_gate.py`
- `assemblyzero/workflows/implementation_spec/nodes/load_lld.py`
- `assemblyzero/workflows/implementation_spec/nodes/review_spec.py`
- `assemblyzero/workflows/implementation_spec/nodes/validate_completeness.py`
- `assemblyzero/workflows/implementation_spec/state.py`
- `docs/prompts`
- `docs/prompts/implementation_spec`
- `docs/prompts/implementation_spec/drafter_system.md`
- `docs/prompts/implementation_spec/drafter_user.md`
- `docs/prompts/implementation_spec/reviewer_system.md`
- `docs/prompts/implementation_spec/reviewer_user.md`
- `docs/standards/0701-implementation-spec-template.md`
- `docs/standards/0702-implementation-readiness-review.md`
- `tools/run_implementation_spec_workflow.py`
- `tests/unit/test_implementation_spec_nodes.py`
- `tests/unit/test_implementation_spec_workflow.py`

Any files written to other paths will be rejected.

## Tests That Must Pass

```python
# From C:\Users\mcwiz\Projects\AssemblyZero-304\tests\test_issue_304.py
"""Test file for Issue #304.

Generated by AssemblyZero TDD Testing Workflow.
Tests will fail with ImportError until implementation exists (TDD RED phase).
"""

import pytest

# TDD: This import fails until implementation exists (RED phase)
# Once implemented, tests can run (GREEN phase)
from assemblyzero.workflows.implementation_spec.graph import *  # noqa: F401, F403


# Fixtures for mocking
@pytest.fixture
def mock_external_service():
    """Mock external service for isolation."""
    # TODO: Implement mock
    yield None


# Integration/E2E fixtures
@pytest.fixture
def test_client():
    """Test client for API calls."""
    # TODO: Implement test client
    yield None


# Unit Tests
# -----------

def test_id():
    """
    Test Description | Expected Behavior | Status
    """
    # TDD: Arrange
    # Set up test data

    # TDD: Act
    # Call the function under test

    # TDD: Assert
    # Verify test_id works correctly
    assert False, 'TDD RED: test_id not implemented'


def test_t010():
    """
    Load approved LLD | Parses LLD and extracts files list | RED
    """
    # TDD: Arrange
    # Set up test data

    # TDD: Act
    # Call the function under test

    # TDD: Assert
    # Verify test_t010 works correctly
    assert False, 'TDD RED: test_t010 not implemented'


def test_t020():
    """
    Reject unapproved LLD | Raises error for PENDING status | RED
    """
    # TDD: Arrange
    # Set up test data

    # TDD: Act
    # Call the function under test

    # TDD: Assert
    # Verify test_t020 works correctly
    assert False, 'TDD RED: test_t020 not implemented'


def test_t030():
    """
    Analyze codebase extracts excerpts | Returns dict of file→excerpt |
    RED
    """
    # TDD: Arrange
    # Set up test data

    # TDD: Act
    # Call the function under test

    # TDD: Assert
    # Verify test_t030 works correctly
    assert False, 'TDD RED: test_t030 not implemented'


def test_t040():
    """
    Generate spec includes all sections | Spec has concrete examples |
    RED
    """
    # TDD: Arrange
    # Set up test data

    # TDD: Act
    # Call the function under test

    # TDD: Assert
    # Verify test_t040 works correctly
    assert False, 'TDD RED: test_t040 not implemented'


def test_t050():
    """
    Validate completeness catches missing excerpts | Returns BLOCKED |
    RED
    """
    # TDD: Arrange
    # Set up test data

    # TDD: Act
    # Call the function under test

    # TDD: Assert
    # Verify test_t050 works correctly
    assert False, 'TDD RED: test_t050 not implemented'


def test_t060():
    """
    Validate completeness passes complete spec | Returns PASSED | RED
    """
    # TDD: Arrange
    # Set up test data

    # TDD: Act
    # Call the function under test

    # TDD: Assert
    # Verify test_t060 works correctly
    assert False, 'TDD RED: test_t060 not implemented'


def test_t070():
    """
    Review spec routing on APPROVED | Routes to N6 | RED
    """
    # TDD: Arrange
    # Set up test data

    # TDD: Act
    # Call the function under test

    # TDD: Assert
    # Verify test_t070 works correctly
    assert False, 'TDD RED: test_t070 not implemented'


def test_t080():
    """
    Review spec routing on REVISE | Routes to N2, increments iteration |
    RED
    """
    # TDD: Arrange
    # Set up test data

    # TDD: Act
    # Call the function under test

    # TDD: Assert
    # Verify test_t080 works correctly
    assert False, 'TDD RED: test_t080 not implemented'


def test_t090():
    """
    Finalize writes spec file | File exists at expected path | RED
    """
    # TDD: Arrange
    # Set up test data

    # TDD: Act
    # Call the function under test

    # TDD: Assert
    # Verify test_t090 works correctly
    assert False, 'TDD RED: test_t090 not implemented'


def test_t100():
    """
    CLI runs full workflow | Produces spec file | RED
    """
    # TDD: Arrange
    # Set up test data

    # TDD: Act
    # Call the function under test

    # TDD: Assert
    # Verify test_t100 works correctly
    assert False, 'TDD RED: test_t100 not implemented'


def test_010():
    """
    Happy path - simple LLD | Auto |
    `tests/fixtures/lld_approved_simple.md` | Spec at
    `docs/lld/drafts/spec-999.md` | File exists, contains excerpts
    """
    # TDD: Arrange
    # Set up test data

    # TDD: Act
    # Call the function under test

    # TDD: Assert
    # Verify test_010 works correctly
    assert False, 'TDD RED: test_010 not implemented'


def test_020():
    """
    Complex LLD with many files | Auto |
    `tests/fixtures/lld_approved_complex.md` | Complete spec | All 10+
    files have excerpts
    """
    # TDD: Arrange
    # Set up test data

    # TDD: Act
    # Call the function under test

    # TDD: Assert
    # Verify test_020 works correctly
    assert False, 'TDD RED: test_020 not implemented'


def test_030():
    """
    Unapproved LLD rejection | Auto |
    `tests/fixtures/lld_not_approved.md` | Error raised | Workflow aborts
    before N1
    """
    # TDD: Arrange
    # Set up test data

    # TDD: Act
    # Call the function under test

    # TDD: Assert
    # Verify test_030 works correctly
    assert False, 'TDD RED: test_030 not implemented'


def test_040():
    """
    File not found in codebase | Auto | LLD with non-existent file |
    Graceful error | Clear message about missing file
    """
    # TDD: Arrange
    # Set up test data

    # TDD: Act
    # Call the function under test

    # TDD: Assert
    # Verify test_040 works correctly
    assert False, 'TDD RED: test_040 not implemented'


def test_050(mock_external_service):
    """
    Incomplete spec regeneration | Auto | Mock Claude returns incomplete
    | N3 → N2 retry | Second attempt improves
    """
    # TDD: Arrange
    # Set up test data

    # TDD: Act
    # Call the function under test

    # TDD: Assert
    # Verify test_050 works correctly
    assert False, 'TDD RED: test_050 not implemented'


def test_060(mock_external_service):
    """
    Max iterations exceeded | Auto | Mock always returns incomplete |
    Workflow aborts | Error after 3 iterations
    """
    # TDD: Arrange
    # Set up test data

    # TDD: Act
    # Call the function under test

    # TDD: Assert
    # Verify test_060 works correctly
    assert False, 'TDD RED: test_060 not implemented'


def test_070(mock_external_service):
    """
    Gemini REVISE verdict | Auto | Mock Gemini returns REVISE |
    Regenerate with feedback | Feedback in next N2 prompt
    """
    # TDD: Arrange
    # Set up test data

    # TDD: Act
    # Call the function under test

    # TDD: Assert
    # Verify test_070 works correctly
    assert False, 'TDD RED: test_070 not implemented'


def test_080():
    """
    Pattern reference validation | Auto | Spec references existing
    pattern | Check passes | Pattern at file:line exists
    """
    # TDD: Arrange
    # Set up test data

    # TDD: Act
    # Call the function under test

    # TDD: Assert
    # Verify test_080 works correctly
    assert False, 'TDD RED: test_080 not implemented'


def test_090():
    """
    Invalid pattern reference | Auto | Spec references non-existent line
    | Check fails | Completeness blocked
    """
    # TDD: Arrange
    # Set up test data

    # TDD: Act
    # Call the function under test

    # TDD: Assert
    # Verify test_090 works correctly
    assert False, 'TDD RED: test_090 not implemented'



# E2E Tests
# ---------

@pytest.mark.e2e
def test_100(test_client):
    """
    CLI end-to-end | Auto | Valid issue number | Spec file created | Exit
    code 0
    """
    # TDD: Arrange
    # Set up test data

    # TDD: Act
    # Call the function under test

    # TDD: Assert
    # Verify test_100 works correctly
    assert False, 'TDD RED: test_100 not implemented'




```

## Previously Implemented Files

These files have already been implemented. Use them for imports and references:

### assemblyzero/workflows/implementation_spec/__init__.py (signatures)

```python
"""Implementation Spec Workflow package.

Issue #304: Implementation Readiness Review Workflow (LLD → Implementation Spec)

This package provides a workflow that transforms approved LLDs into
Implementation Specs with enough concrete detail for autonomous AI
implementation.

Key components:
- state: ImplementationSpecState TypedDict and supporting types
- graph: LangGraph workflow definition with conditional routing
- nodes/: Individual node implementations (N0-N6)

Workflow steps:
1. N0: Load approved LLD and parse files list
2. N1: Analyze codebase, extract current state excerpts
3. N2: Generate Implementation Spec draft (Claude)
4. N3: Validate mechanical completeness
5. N4: Optional human review gate
6. N5: Gemini readiness review
7. N6: Finalize and write spec to docs/lld/drafts/
"""

from assemblyzero.workflows.implementation_spec.graph import (
    create_implementation_spec_graph,
    route_after_review,
    route_after_validation,
)

from assemblyzero.workflows.implementation_spec.state import (
    CompletenessCheck,
    FileToModify,
    ImplementationSpecState,
    PatternRef,
)
```

### assemblyzero/workflows/implementation_spec/graph.py (signatures)

```python
"""LangGraph workflow definition for Implementation Spec generation.

Issue #304: Implementation Readiness Review Workflow (LLD → Implementation Spec)

Creates a LangGraph StateGraph that connects:
- N0: load_lld (load and parse approved LLD)
- N1: analyze_codebase (extract current state from files)
- N2: generate_spec (generate Implementation Spec draft via Claude)
- N3: validate_completeness (mechanical completeness checks)
- N4: human_gate (optional human review checkpoint)
- N5: review_spec (Gemini readiness review)
- N6: finalize_spec (write final spec to docs/lld/drafts/)

Graph structure:
    START -> N0 -> N1 -> N2 -> N3 -> N4 -> N5 -> N6 -> END
                          ^         |              |
                          |         v              |
                          +---------+--------------+

Routing is controlled by:
- validation_passed: N3 result determines if spec meets completeness criteria
- review_verdict: N5 Gemini verdict (APPROVED / REVISE / BLOCKED)
- review_iteration: Current iteration count vs max_iterations
- human_gate_enabled: Whether N4 is active (default: disabled)
"""

from typing import Literal

from langgraph.graph import END, START, StateGraph

from langgraph.graph.state import CompiledStateGraph

from assemblyzero.workflows.implementation_spec.nodes.analyze_codebase import (
    analyze_codebase,
)

from assemblyzero.workflows.implementation_spec.nodes.finalize_spec import (
    finalize_spec,
)

from assemblyzero.workflows.implementation_spec.nodes.generate_spec import (
    generate_spec,
)

from assemblyzero.workflows.implementation_spec.nodes.human_gate import human_gate

from assemblyzero.workflows.implementation_spec.nodes.load_lld import load_lld

from assemblyzero.workflows.implementation_spec.nodes.review_spec import review_spec

from assemblyzero.workflows.implementation_spec.nodes.validate_completeness import (
    validate_completeness,
)

from assemblyzero.workflows.implementation_spec.state import ImplementationSpecState

def route_after_load(
    state: ImplementationSpecState,
) -> Literal["N1_analyze_codebase", "END"]:
    """Route after N0: load_lld.

Routes to:"""
    ...

def route_after_analyze(
    state: ImplementationSpecState,
) -> Literal["N2_generate_spec", "END"]:
    """Route after N1: analyze_codebase.

Routes to:"""
    ...

def route_after_validation(
    state: ImplementationSpecState,
) -> Literal["N4_human_gate", "N5_review_spec", "N2_generate_spec", "END"]:
    """Route after N3: validate_completeness.

Routes to:"""
    ...

def route_after_human_gate(
    state: ImplementationSpecState,
) -> Literal["N5_review_spec", "N2_generate_spec", "END"]:
    """Route after N4: human_gate.

Routes based on human decision:"""
    ...

def route_after_review(
    state: ImplementationSpecState,
) -> Literal["N6_finalize_spec", "N2_generate_spec", "END"]:
    """Route after N5: review_spec.

Routes to:"""
    ...

def create_implementation_spec_graph() -> CompiledStateGraph:
    """Create the LangGraph workflow for Implementation Spec generation.

Graph structure:"""
    ...

N0_LOAD_LLD = "N0_load_lld"

N1_ANALYZE_CODEBASE = "N1_analyze_codebase"

N2_GENERATE_SPEC = "N2_generate_spec"

N3_VALIDATE_COMPLETENESS = "N3_validate_completeness"

N4_HUMAN_GATE = "N4_human_gate"

N5_REVIEW_SPEC = "N5_review_spec"

N6_FINALIZE_SPEC = "N6_finalize_spec"
```

### assemblyzero/workflows/implementation_spec/state.py (signatures)

```python
"""TypedDict state definitions for Implementation Spec workflow.

Issue #304: Implementation Readiness Review Workflow (LLD → Implementation Spec)

Defines the state schema used by the LangGraph workflow:
- ImplementationSpecState: Main workflow state
- FileToModify: Parsed file entry from LLD Section 2.1
- PatternRef: Reference to similar implementation patterns
- CompletenessCheck: Result of a mechanical completeness check
"""

from __future__ import annotations

from typing import Literal, TypedDict

class FileToModify(TypedDict):

    """A file entry parsed from LLD Section 2.1.

Attributes:"""

class PatternRef(TypedDict):

    """Reference to a similar implementation pattern in the codebase.

Used by N1 (analyze_codebase) to find existing patterns that inform"""

class CompletenessCheck(TypedDict):

    """Result of a single mechanical completeness check in N3.

Attributes:"""

class ImplementationSpecState(TypedDict, total=False):

    """Main workflow state for the Implementation Spec generation workflow.

This TypedDict defines all state fields used across nodes N0-N6."""
```

### assemblyzero/workflows/implementation_spec/nodes/__init__.py (signatures)

```python
"""Nodes package for Implementation Spec workflow.

Issue #304: Implementation Readiness Review Workflow (LLD → Implementation Spec)

Individual node implementations for the LangGraph workflow:
- N0: load_lld - Load and parse approved LLD
- N1: analyze_codebase - Extract current state from codebase files
- N2: generate_spec - Generate Implementation Spec draft (Claude)
- N3: validate_completeness - Mechanical completeness checks
- N4: human_gate - Optional human review checkpoint
- N5: review_spec - Gemini readiness review
- N6: finalize_spec - Write final spec to docs/lld/drafts/
"""

from assemblyzero.workflows.implementation_spec.nodes.analyze_codebase import (
    analyze_codebase,
    extract_relevant_excerpt,
    find_pattern_references,
)

from assemblyzero.workflows.implementation_spec.nodes.finalize_spec import (
    finalize_spec,
    generate_spec_filename,
)

from assemblyzero.workflows.implementation_spec.nodes.generate_spec import (
    build_drafter_prompt,
    generate_spec,
)

from assemblyzero.workflows.implementation_spec.nodes.human_gate import human_gate

from assemblyzero.workflows.implementation_spec.nodes.load_lld import (
    load_lld,
    parse_files_to_modify,
)

from assemblyzero.workflows.implementation_spec.nodes.review_spec import (
    parse_review_verdict,
    review_spec,
)

from assemblyzero.workflows.implementation_spec.nodes.validate_completeness import (
    check_change_instructions_specific,
    check_data_structures_have_examples,
    check_functions_have_io_examples,
    check_modify_files_have_excerpts,
    check_pattern_references_valid,
    validate_completeness,
)
```

### assemblyzero/workflows/implementation_spec/nodes/load_lld.py (signatures)

```python
"""N0: Load LLD node for Implementation Spec Workflow.

Issue #304: Implementation Readiness Review Workflow (LLD → Implementation Spec)

Reads the approved LLD file and extracts:
- Full LLD content (raw markdown)
- Files to modify from Section 2.1 table
- Validates LLD has APPROVED status

This node populates:
- lld_content: Raw LLD markdown
- files_to_modify: List[FileToModify] parsed from Section 2.1
- error_message: "" on success, error text on failure
"""

import re

from pathlib import Path

from typing import Any

from assemblyzero.workflows.implementation_spec.state import (
    FileToModify,
    ImplementationSpecState,
)

def find_lld_path(issue_number: int, repo_root: Path) -> Path | None:
    """Find the LLD file for an issue number.

Searches docs/lld/active/ and docs/lld/done/ with multiple naming"""
    ...

def parse_files_to_modify(lld_content: str) -> list[FileToModify]:
    """Extract files from LLD Section 2.1 table.

Parses the "Files Changed" table to extract file paths, change types,"""
    ...

def _normalize_change_type(raw: str) -> str:
    """Normalize a change type string to Add, Modify, or Delete.

Handles variations like "Add (Directory)", "Modify", "modify", etc."""
    ...

def _check_approved_status(lld_content: str) -> bool:
    """Check if the LLD has an APPROVED status marker.

Looks for approval markers in common locations:"""
    ...

def load_lld(state: ImplementationSpecState) -> dict[str, Any]:
    """N0: Load and parse the approved LLD file.

Issue #304: Implementation Readiness Review Workflow"""
    ...

LLD_ACTIVE_DIR = Path("docs/lld/active")

LLD_DONE_DIR = Path("docs/lld/done")

LLD_DRAFTS_DIR = Path("docs/lld/drafts")
```

### assemblyzero/workflows/implementation_spec/nodes/analyze_codebase.py (signatures)

```python
"""N1: Analyze Codebase node for Implementation Spec Workflow.

Issue #304: Implementation Readiness Review Workflow (LLD → Implementation Spec)

Reads files listed in the LLD and extracts current state:
- For "Modify" and "Delete" files: reads content and extracts relevant excerpts
- For "Add" files: verifies parent directories exist
- Finds similar implementation patterns in the codebase (existing nodes,
  state definitions, graph constructions) to guide spec generation

This node populates:
- current_state_snapshots: dict[str, str] - file_path → code excerpt
- pattern_references: list[PatternRef] - similar patterns found
- files_to_modify: Updated with current_content for Modify/Delete files
- error_message: "" on success, error text on failure
"""

import ast

import re

from pathlib import Path

from typing import Any

from assemblyzero.workflows.implementation_spec.state import (
    FileToModify,
    ImplementationSpecState,
    PatternRef,
)

def analyze_codebase(state: ImplementationSpecState) -> dict[str, Any]:
    """N1: Read files and extract current state snapshots.

Issue #304: Implementation Readiness Review Workflow"""
    ...

def extract_relevant_excerpt(
    file_path: str, content: str, lld_context: str
) -> str:
    """Extract the portion of a file relevant to the change.

For Python files, uses AST-based summarization to extract imports,"""
    ...

def _summarize_python_file(content: str) -> str:
    """Extract imports and signatures from a Python file for compact context.

Issue #373 pattern: Instead of embedding full file bodies (~20KB+),"""
    ...

def _summarize_function(
    node: ast.FunctionDef | ast.AsyncFunctionDef, source: str
) -> str:
    """Extract function signature and docstring.

Args:"""
    ...

def _summarize_class(node: ast.ClassDef, source: str) -> str:
    """Extract class signature, docstring, and method signatures.

Args:"""
    ...

def _truncate_content(content: str, max_chars: int) -> str:
    """Truncate content to a maximum number of characters.

Truncates at a line boundary to avoid partial lines."""
    ...

def find_pattern_references(
    files_to_modify: list[FileToModify],
    repo_root: Path,
) -> list[PatternRef]:
    """Find similar implementation patterns in the codebase.

Scans the repository for existing implementations that are similar"""
    ...

def _find_node_patterns(
    target_path: str,
    workflows_dir: Path,
    repo_root: Path,
    seen: set[str],
) -> list[PatternRef]:
    """Find existing node implementations as patterns.

Looks for node files in other workflow packages to serve as"""
    ...

def _find_state_patterns(
    workflows_dir: Path,
    repo_root: Path,
    seen: set[str],
) -> list[PatternRef]:
    """Find existing state.py definitions as patterns.

Args:"""
    ...

def _find_graph_patterns(
    workflows_dir: Path,
    repo_root: Path,
    seen: set[str],
) -> list[PatternRef]:
    """Find existing graph.py definitions as patterns.

Args:"""
    ...

def _find_test_patterns(
    target_path: str,
    repo_root: Path,
    seen: set[str],
) -> list[PatternRef]:
    """Find similar test files as patterns.

Args:"""
    ...

def _find_tool_patterns(
    repo_root: Path,
    seen: set[str],
) -> list[PatternRef]:
    """Find existing CLI tool scripts as patterns.

Args:"""
    ...

def _names_similar(name_a: str, name_b: str) -> bool:
    """Check if two identifier names are similar.

Uses a simple heuristic: checks if the names share significant"""
    ...

MAX_FILE_SIZE_BYTES = 1_000_000

MAX_EXCERPT_CHARS = 15_000

MAX_PATTERN_REFS = 10

PYTHON_EXTENSIONS = {".py"}

SKIP_DIRS = {
    "__pycache__",
    ".git",
    ".tox",
    ".mypy_cache",
    ".pytest_cache",
    "node_modules",
    ".venv",
    "venv",
    "done",
}
```

### assemblyzero/workflows/implementation_spec/nodes/generate_spec.py (signatures)

```python
"""N2: Generate Implementation Spec node for Implementation Spec Workflow.

Issue #304: Implementation Readiness Review Workflow (LLD → Implementation Spec)

Uses the configured drafter LLM (Claude) to generate an Implementation Spec
from the approved LLD, codebase analysis results (current state snapshots
and pattern references), and the Implementation Spec template.

Supports revision mode when N3 (validate_completeness) or N5 (review_spec)
routes back with feedback. Revision prompts include cumulative feedback
history to prevent regression.

This node populates:
- spec_draft: Generated Implementation Spec markdown
- spec_path: Path where the draft was saved in the audit trail
- review_iteration: Incremented on revision cycles
- error_message: "" on success, error text on failure
"""

import re

from pathlib import Path

from typing import Any

from assemblyzero.core.llm_provider import get_provider

from assemblyzero.workflows.requirements.audit import (
    get_repo_structure,
    load_template,
    next_file_number,
    save_audit_file,
)

from assemblyzero.workflows.implementation_spec.state import (
    ImplementationSpecState,
    PatternRef,
)

async def generate_spec(state: ImplementationSpecState) -> dict[str, Any]:
    """N2: Generate Implementation Spec draft using Claude.

Issue #304: Implementation Readiness Review Workflow"""
    ...

def build_drafter_prompt(
    lld_content: str,
    current_state: dict[str, str],
    patterns: list[PatternRef],
    template: str = "",
    issue_number: int = 0,
    existing_draft: str = "",
    review_feedback: str = "",
    completeness_issues: list[str] | None = None,
    repo_root: str = "",
    """Build the prompt for Claude spec generation.

Constructs either an initial draft prompt or a revision prompt"""
    ...

def _build_initial_prompt(
    lld_content: str,
    current_state: dict[str, str],
    patterns: list[PatternRef],
    template: str,
    issue_number: int,
    files_to_modify: list,
) -> str:
    """Build prompt for initial spec generation.

Args:"""
    ...

def _build_revision_prompt(
    lld_content: str,
    current_state: dict[str, str],
    patterns: list[PatternRef],
    template: str,
    issue_number: int,
    existing_draft: str,
    review_feedback: str,
    completeness_issues: list[str],
    repo_root: str,
    """Build prompt for spec revision based on feedback.

Args:"""
    ...

def _format_current_state_section(
    current_state: dict[str, str],
    files_to_modify: list,
) -> str:
    """Format current state snapshots into a prompt section.

Args:"""
    ...

def _format_patterns_section(patterns: list[PatternRef]) -> str:
    """Format pattern references into a prompt section.

Args:"""
    ...

def _strip_preamble(content: str) -> str:
    """Strip any preamble text before the first # heading.

Claude sometimes adds explanatory text before the actual spec content"""
    ...

def _truncate_prompt(prompt: str) -> str:
    """Truncate prompt to stay within token limits.

Preserves the beginning (instructions, feedback) and end (template,"""
    ...

SPEC_TEMPLATE_PATH = Path("docs/standards/0701-implementation-spec-template.md")

DEFAULT_DRAFTER = "claude:opus-4.5"

MAX_PATTERN_EXCERPT_CHARS = 3_000

MAX_SNAPSHOT_CHARS = 10_000

MAX_TOTAL_PROMPT_CHARS = 120_000
```

### assemblyzero/workflows/implementation_spec/nodes/validate_completeness.py (full)

```python
"""N3: Validate Completeness node for Implementation Spec Workflow.

Issue #304: Implementation Readiness Review Workflow (LLD -> Implementation Spec)

Runs mechanical completeness checks on the generated Implementation Spec
draft to catch issues before expensive Gemini review (N5). Each check
verifies one aspect of spec quality:

- Every "Modify" file must have a current state excerpt
- Every data structure must have a concrete JSON/YAML example
- Every function must have input/output examples
- Change instructions must be specific (diff-level guidance)
- Pattern references must point to existing code locations

This node populates:
- completeness_issues: List of issue descriptions from failed checks
- validation_passed: Whether all checks passed
- error_message: "" on success, error text on failure
"""

import re
from pathlib import Path
from typing import Any

from assemblyzero.workflows.implementation_spec.state import (
    CompletenessCheck,
    FileToModify,
    ImplementationSpecState,
    PatternRef,
)


# =============================================================================
# Constants
# =============================================================================

# Minimum number of characters for a meaningful excerpt
MIN_EXCERPT_CHARS = 50

# Minimum number of characters for an example to be considered concrete
MIN_EXAMPLE_CHARS = 20

# Patterns that indicate diff-level specificity in change instructions
SPECIFICITY_INDICATORS = [
    r"```",                           # Code blocks (before/after snippets)
    r"line\s+\d+",                    # Line number references
    r"lines?\s+\d+\s*[-–]\s*\d+",    # Line range references
    r"before:.*after:",               # Before/after pattern
    r"replace\s+.*\s+with",          # Replace X with Y
    r"add\s+(after|before|above|below)",  # Positional add instructions
    r"delete\s+(line|function|class|method|block)",  # Delete targets
    r"import\s+",                     # Import statements (specific)
    r"def\s+\w+",                     # Function definitions
    r"class\s+\w+",                   # Class definitions
]


# =============================================================================
# Main Node
# =============================================================================


def validate_completeness(state: ImplementationSpecState) -> dict[str, Any]:
    """N3: Check that spec meets mechanical completeness criteria.

    Issue #304: Implementation Readiness Review Workflow

    Runs a series of mechanical checks on the generated spec draft to
    verify it has sufficient detail for autonomous implementation. Failed
    checks produce actionable error messages that guide N2 revision.

    Steps:
    1. Verify spec_draft exists and is non-trivial
    2. Run each completeness check independently
    3. Collect results and determine pass/fail
    4. Return state updates with check results

    Args:
        state: Current workflow state. Requires:
            - spec_draft: Generated Implementation Spec markdown (from N2)
            - files_to_modify: List[FileToModify] from N0
            - pattern_references: List[PatternRef] from N1
            - repo_root: Repository root path (for pattern validation)

    Returns:
        Dict with state field updates:
        - completeness_issues: List of issue descriptions (empty if all passed)
        - validation_passed: True if all checks passed
        - error_message: "" on success, error text on failure
    """
    print("\n[N3] Validating mechanical completeness...")

    spec_draft = state.get("spec_draft", "")
    files_to_modify = state.get("files_to_modify", [])
    pattern_references = state.get("pattern_references", [])
    repo_root_str = state.get("repo_root", "")

    # --------------------------------------------------------------------------
    # GUARD: Must have a spec draft to validate
    # --------------------------------------------------------------------------
    if not spec_draft or len(spec_draft.strip()) < 100:
        print("    [GUARD] BLOCKED: Spec draft is empty or too short")
        return {
            "completeness_issues": [
                "Spec draft is empty or too short (< 100 chars). "
                "N2 must generate a substantive Implementation Spec."
            ],
            "validation_passed": False,
            "error_message": "",
        }
    # --------------------------------------------------------------------------

    # Run all checks
    checks: list[CompletenessCheck] = []

    # Check 1: Every "Modify" file must have current state excerpt
    check_excerpts = check_modify_files_have_excerpts(spec_draft, files_to_modify)
    checks.append(check_excerpts)
    _log_check(check_excerpts)

    # Check 2: Data structures should have concrete examples
    check_data = check_data_structures_have_examples(spec_draft)
    checks.append(check_data)
    _log_check(check_data)

    # Check 3: Functions should have I/O examples
    check_functions = check_functions_have_io_examples(spec_draft)
    checks.append(check_functions)
    _log_check(check_functions)

    # Check 4: Change instructions should be specific
    check_instructions = check_change_instructions_specific(spec_draft)
    checks.append(check_instructions)
    _log_check(check_instructions)

    # Check 5: Pattern references should be valid
    check_patterns = check_pattern_references_valid(
        spec_draft, pattern_references, repo_root_str
    )
    checks.append(check_patterns)
    _log_check(check_patterns)

    # Collect issues from failed checks
    completeness_issues = [
        check["details"] for check in checks if not check["passed"]
    ]

    validation_passed = len(completeness_issues) == 0

    # Report summary
    passed_count = sum(1 for c in checks if c["passed"])
    total_count = len(checks)
    print(
        f"\n    Results: {passed_count}/{total_count} checks passed"
    )

    if validation_passed:
        print("    PASSED: All completeness checks passed")
    else:
        print(f"    BLOCKED: {len(completeness_issues)} check(s) failed")
        for issue in completeness_issues:
            print(f"      - {issue[:120]}...")

    return {
        "completeness_issues": completeness_issues,
        "validation_passed": validation_passed,
        "error_message": "",
    }


# =============================================================================
# Individual Checks
# =============================================================================


def check_modify_files_have_excerpts(
    spec: str, files: list[FileToModify]
) -> CompletenessCheck:
    """Every 'Modify' file must have current state excerpt.

    Scans the spec for references to each Modify file and verifies that
    there is a code block or excerpt showing the current state of the code
    that will be changed.

    Args:
        spec: Implementation Spec markdown content.
        files: List of FileToModify from the LLD.

    Returns:
        CompletenessCheck with pass/fail result and details.
    """
    modify_files = [
        f for f in files if f.get("change_type") == "Modify"
    ]

    if not modify_files:
        return CompletenessCheck(
            check_name="modify_files_have_excerpts",
            passed=True,
            details="No Modify files in LLD — check not applicable.",
        )

    missing: list[str] = []

    for file_spec in modify_files:
        file_path = file_spec.get("path", "")
        if not file_path:
            continue

        # Look for the file path referenced in the spec
        # Accept both full path and basename references
        basename = Path(file_path).name
        file_mentioned = (
            file_path in spec or basename in spec
        )

        if not file_mentioned:
            missing.append(file_path)
            continue

        # Check for a code block near the file reference
        # Find the position of the file reference and look for a code block
        # within ~2000 chars after it
        pos = spec.find(file_path)
        if pos == -1:
            pos = spec.find(basename)
        if pos == -1:
            missing.append(file_path)
            continue

        # Look for a code block (``` ... ```) within a reasonable range
        search_region = spec[pos : pos + 3000]
        has_code_block = "```" in search_region

        if not has_code_block:
            missing.append(file_path)

    if missing:
        file_list = ", ".join(f"`{f}`" for f in missing[:5])
        suffix = f" (and {len(missing) - 5} more)" if len(missing) > 5 else ""
        return CompletenessCheck(
            check_name="modify_files_have_excerpts",
            passed=False,
            details=(
                f"Missing current state excerpts for Modify files: "
                f"{file_list}{suffix}. Each Modify file MUST include a "
                f"code block showing the current code that will be changed."
            ),
        )

    return CompletenessCheck(
        check_name="modify_files_have_excerpts",
        passed=True,
        details=f"All {len(modify_files)} Modify files have current state excerpts.",
    )


def check_data_structures_have_examples(spec: str) -> CompletenessCheck:
    """Every data structure must have concrete JSON/YAML example.

    Looks for data structure definitions (TypedDict, dataclass, dict schemas)
    in the spec and verifies each has at least one concrete example with
    realistic values, not just the type definition.

    Args:
        spec: Implementation Spec markdown content.

    Returns:
        CompletenessCheck with pass/fail result and details.
    """
    # Find data structure definitions in the spec
    # Look for TypedDict, dataclass, dict, Pydantic model patterns
    structure_patterns = [
        r"(?:class\s+\w+\s*\(.*?TypedDict.*?\))",
        r"(?:class\s+\w+\s*\(.*?BaseModel.*?\))",
        r"(?:@dataclass[^\n]*\n\s*class\s+\w+)",
    ]

    structures_found: list[str] = []
    for pattern in structure_patterns:
        matches = re.findall(pattern, spec, re.IGNORECASE)
        for match in matches:
            # Extract name from "class FooBar(...)"
            name_match = re.search(r"class\s+(\w+)", match)
            if name_match:
                structures_found.append(name_match.group(1))

    if not structures_found:
        # No data structures found — check passes (nothing to validate)
        return CompletenessCheck(
            check_name="data_structures_have_examples",
            passed=True,
            details="No data structure definitions found in spec — check not applicable.",
        )

    # For each structure, look for a concrete example
    # Examples can be JSON blocks, YAML blocks, or Python dict literals
    missing_examples: list[str] = []

    for struct_name in structures_found:
        # Find where this structure is defined/discussed in the spec
        pos = spec.find(struct_name)
        if pos == -1:
            continue

        # Look in a reasonable region after the structure reference
        search_region = spec[pos : pos + 5000]

        # Check for concrete examples: JSON, YAML, or Python dict/instance
        has_json = bool(re.search(r"\{[^}]*[\"'][\w]+[\"']\s*:", search_region))
        has_yaml = bool(re.search(r"^\s+\w+:\s+\S+", search_region, re.MULTILINE))
        has_python_dict = bool(
            re.search(r"\{[^}]*[\"']\w+[\"']\s*:", search_region)
        )
        has_instance = bool(
            re.search(
                rf"{struct_name}\s*\(", search_region
            )
        )
        has_code_example = bool(
            re.search(r"```(?:json|yaml|python|py)?\s*\n.{20,}", search_region)
        )

        if not any([has_json, has_yaml, has_python_dict, has_instance, has_code_example]):
            missing_examples.append(struct_name)

    if missing_examples:
        struct_list = ", ".join(f"`{s}`" for s in missing_examples[:5])
        suffix = (
            f" (and {len(missing_examples) - 5} more)"
            if len(missing_examples) > 5
            else ""
        )
        return CompletenessCheck(
            check_name="data_structures_have_examples",
            passed=False,
            details=(
                f"Data structures missing concrete examples: "
                f"{struct_list}{suffix}. Each data structure MUST have at "
                f"least one JSON/YAML/Python example with realistic values."
            ),
        )

    return CompletenessCheck(
        check_name="data_structures_have_examples",
        passed=True,
        details=(
            f"All {len(structures_found)} data structures have concrete examples."
        ),
    )


def check_functions_have_io_examples(spec: str) -> CompletenessCheck:
    """Every function must have input/output examples.

    Scans the spec for function signatures and verifies each has at least
    one concrete input/output example showing actual values.

    Args:
        spec: Implementation Spec markdown content.

    Returns:
        CompletenessCheck with pass/fail result and details.
    """
    # Find function signatures in the spec (within code blocks or inline)
    # Match "def function_name(" patterns
    func_pattern = re.compile(r"(?:async\s+)?def\s+(\w+)\s*\(")
    all_functions = func_pattern.findall(spec)

    # Deduplicate and filter private/dunder methods
    public_functions = sorted(set(
        f for f in all_functions
        if not f.startswith("_") and f not in ("__init__", "__str__", "__repr__")
    ))

    if not public_functions:
        return CompletenessCheck(
            check_name="functions_have_io_examples",
            passed=True,
            details="No public function signatures found in spec — check not applicable.",
        )

    missing_examples: list[str] = []

    for func_name in public_functions:
        # Find where this function is discussed in the spec
        # Look for the function name outside of code block definitions
        positions = [m.start() for m in re.finditer(re.escape(func_name), spec)]

        if not positions:
            continue

        # Check if ANY occurrence has a nearby I/O example
        has_example = False

        for pos in positions:
            search_region = spec[pos : pos + 4000]

            # Check for I/O example indicators
            has_input_output = bool(
                re.search(
                    r"(?:input|output|returns?|result|example|usage|call)",
                    search_region,
                    re.IGNORECASE,
                )
            )
            has_code_block = "```" in search_region
            has_arrow = bool(
                re.search(r"(?:->|=>|→|returns?\s*:)", search_region)
            )
            has_concrete_values = bool(
                re.search(
                    r'(?:\d+|"[^"]+"|True|False|None|\[.*\]|\{.*\})',
                    search_region,
                )
            )

            # Must have at least a code block with concrete values,
            # or an input/output section with values
            if has_code_block and has_concrete_values:
                has_example = True
                break
            if has_input_output and has_concrete_values:
                has_example = True
                break

        if not has_example:
            missing_examples.append(func_name)

    if missing_examples:
        func_list = ", ".join(f"`{f}()`" for f in missing_examples[:5])
        suffix = (
            f" (and {len(missing_examples) - 5} more)"
            if len(missing_examples) > 5
            else ""
        )
        return CompletenessCheck(
            check_name="functions_have_io_examples",
            passed=False,
            details=(
                f"Functions missing input/output examples: "
                f"{func_list}{suffix}. Each function MUST have at least one "
                f"example with concrete input values and expected output."
            ),
        )

    return CompletenessCheck(
        check_name="functions_have_io_examples",
        passed=True,
        details=(
            f"All {len(public_functions)} public functions have I/O examples."
        ),
    )


def check_change_instructions_specific(spec: str) -> CompletenessCheck:
    """Change instructions must be diff-level specific.

    Verifies that the spec contains specific change instructions rather
    than vague directives. Looks for indicators of specificity such as
    code blocks, line references, before/after snippets, and precise
    modification instructions.

    Args:
        spec: Implementation Spec markdown content.

    Returns:
        CompletenessCheck with pass/fail result and details.
    """
    # Count specificity indicators in the spec
    indicator_counts: dict[str, int] = {}
    total_indicators = 0

    for pattern in SPECIFICITY_INDICATORS:
        matches = re.findall(pattern, spec, re.IGNORECASE)
        count = len(matches)
        if count > 0:
            indicator_counts[pattern] = count
            total_indicators += count

    # Count code blocks specifically (strong indicator)
    code_blocks = re.findall(r"```[\s\S]*?```", spec)
    code_block_count = len(code_blocks)

    # The spec should have substantial code blocks for specificity
    # Minimum thresholds based on spec size
    spec_lines = len(spec.splitlines())

    # At least 1 code block per 50 lines of spec, minimum 3
    min_code_blocks = max(3, spec_lines // 50)

    if code_block_count < min_code_blocks:
        return CompletenessCheck(
            check_name="change_instructions_specific",
            passed=False,
            details=(
                f"Insufficient code blocks for specificity: found "
                f"{code_block_count}, expected at least {min_code_blocks} "
                f"for a {spec_lines}-line spec. Change instructions MUST "
                f"include before/after code snippets, line references, or "
                f"diff-level guidance."
            ),
        )

    # Also check for minimum total specificity indicators
    min_indicators = max(5, spec_lines // 30)

    if total_indicators < min_indicators:
        return CompletenessCheck(
            check_name="change_instructions_specific",
            passed=False,
            details=(
                f"Change instructions lack specificity: found "
                f"{total_indicators} specificity indicators, expected at "
                f"least {min_indicators}. Include line references, "
                f"before/after snippets, and precise modification targets."
            ),
        )

    return CompletenessCheck(
        check_name="change_instructions_specific",
        passed=True,
        details=(
            f"Change instructions have adequate specificity: "
            f"{code_block_count} code blocks, "
            f"{total_indicators} specificity indicators."
        ),
    )


def check_pattern_references_valid(
    spec: str,
    pattern_refs: list[PatternRef],
    repo_root_str: str = "",
) -> CompletenessCheck:
    """Verify referenced patterns exist at specified locations.

    Checks that pattern references included in the spec (file:line
    locations) point to real code in the repository. This prevents
    the implementation agent from following stale or incorrect references.

    Args:
        spec: Implementation Spec markdown content.
        pattern_refs: List of PatternRef from N1 (codebase analysis).
        repo_root_str: Repository root path string.

    Returns:
        CompletenessCheck with pass/fail result and details.
    """
    if not pattern_refs:
        return CompletenessCheck(
            check_name="pattern_references_valid",
            passed=True,
            details="No pattern references provided — check not applicable.",
        )

    if not repo_root_str:
        # Can't validate without repo root — pass with warning
        return CompletenessCheck(
            check_name="pattern_references_valid",
            passed=True,
            details=(
                "No repo_root available for pattern validation — "
                "skipping file existence checks."
            ),
        )

    repo_root = Path(repo_root_str)
    invalid_refs: list[str] = []

    for ref in pattern_refs:
        file_path = ref.get("file_path", "")
        start_line = ref.get("start_line", 0)
        end_line = ref.get("end_line", 0)

        if not file_path:
            continue

        # Check if this pattern is actually referenced in the spec
        if file_path not in spec:
            # Pattern from N1 not used in spec — skip validation
            continue

        # Verify the file exists
        full_path = repo_root / file_path
        if not full_path.exists():
            invalid_refs.append(
                f"`{file_path}` — file does not exist"
            )
            continue

        # Verify the line range is valid
        if start_line > 0 or end_line > 0:
            try:
                content = full_path.read_text(encoding="utf-8")
                total_lines = len(content.splitlines())

                if start_line > total_lines:
                    invalid_refs.append(
                        f"`{file_path}:{start_line}` — line {start_line} "
                        f"exceeds file length ({total_lines} lines)"
                    )
                elif end_line > total_lines:
                    invalid_refs.append(
                        f"`{file_path}:{start_line}-{end_line}` — "
                        f"end line {end_line} exceeds file length "
                        f"({total_lines} lines)"
                    )
            except (OSError, UnicodeDecodeError) as e:
                invalid_refs.append(
                    f"`{file_path}` — cannot read file: {e}"
                )

    if invalid_refs:
        ref_list = "; ".join(invalid_refs[:5])
        suffix = (
            f" (and {len(invalid_refs) - 5} more)"
            if len(invalid_refs) > 5
            else ""
        )
        return CompletenessCheck(
            check_name="pattern_references_valid",
            passed=False,
            details=(
                f"Invalid pattern references in spec: {ref_list}{suffix}. "
                f"Pattern references MUST point to existing files at valid "
                f"line ranges."
            ),
        )

    return CompletenessCheck(
        check_name="pattern_references_valid",
        passed=True,
        details=(
            f"All pattern references validated "
            f"({len(pattern_refs)} references checked)."
        ),
    )


# =============================================================================
# Utility
# =============================================================================


def _log_check(check: CompletenessCheck) -> None:
    """Log a single check result.

    Args:
        check: CompletenessCheck to log.
    """
    status = "PASS" if check["passed"] else "FAIL"
    name = check["check_name"]
    print(f"    [{status}] {name}")
```

## Output Format

Output ONLY the file contents. No explanations, no markdown headers, just the code.

```python
# Your implementation here
```

IMPORTANT:
- Output the COMPLETE file contents
- Do NOT output a summary or description
- Do NOT say "I've implemented..."
- Just output the code in a single code block
