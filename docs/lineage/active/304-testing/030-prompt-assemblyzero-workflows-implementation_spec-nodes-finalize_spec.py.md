# Implementation Request: assemblyzero/workflows/implementation_spec/nodes/finalize_spec.py

## Task

Write the complete contents of `assemblyzero/workflows/implementation_spec/nodes/finalize_spec.py`.

Change type: Add
Description: N6: Finalize and write spec

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

### assemblyzero/workflows/implementation_spec/nodes/validate_completeness.py (signatures)

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

def validate_completeness(state: ImplementationSpecState) -> dict[str, Any]:
    """N3: Check that spec meets mechanical completeness criteria.

Issue #304: Implementation Readiness Review Workflow"""
    ...

def check_modify_files_have_excerpts(
    spec: str, files: list[FileToModify]
) -> CompletenessCheck:
    """Every 'Modify' file must have current state excerpt.

Scans the spec for references to each Modify file and verifies that"""
    ...

def check_data_structures_have_examples(spec: str) -> CompletenessCheck:
    """Every data structure must have concrete JSON/YAML example.

Looks for data structure definitions (TypedDict, dataclass, dict schemas)"""
    ...

def check_functions_have_io_examples(spec: str) -> CompletenessCheck:
    """Every function must have input/output examples.

Scans the spec for function signatures and verifies each has at least"""
    ...

def check_change_instructions_specific(spec: str) -> CompletenessCheck:
    """Change instructions must be diff-level specific.

Verifies that the spec contains specific change instructions rather"""
    ...

def check_pattern_references_valid(
    spec: str,
    pattern_refs: list[PatternRef],
    repo_root_str: str = "",
) -> CompletenessCheck:
    """Verify referenced patterns exist at specified locations.

Checks that pattern references included in the spec (file:line"""
    ...

def _log_check(check: CompletenessCheck) -> None:
    """Log a single check result.

Args:"""
    ...

MIN_EXCERPT_CHARS = 50

MIN_EXAMPLE_CHARS = 20
```

### assemblyzero/workflows/implementation_spec/nodes/human_gate.py (signatures)

```python
"""N4: Human Gate node for Implementation Spec Workflow.

Issue #304: Implementation Readiness Review Workflow (LLD → Implementation Spec)

Optional human review checkpoint after mechanical validation (N3) passes.
When enabled (human_gate_enabled=True), presents the spec draft to the user
and prompts for a decision:
- [S] Send to Gemini review (proceed to N5)
- [R] Revise spec (return to N2 with optional feedback)
- [M] Manual handling (exit workflow)

When disabled (default), the graph routing in route_after_validation() skips
this node entirely and proceeds directly to N5.

This node populates:
- next_node: Routing decision ("N5_review_spec", "N2_generate_spec", or "END")
- review_feedback: User feedback if revision requested
- error_message: "" on success, error text on failure
"""

from typing import Any

from assemblyzero.workflows.implementation_spec.state import ImplementationSpecState

def _prompt_human_gate() -> str:
    """Prompt user for human gate decision.

Presents three options and loops until a valid choice is entered."""
    ...

def _display_spec_preview(spec_draft: str) -> None:
    """Display a truncated preview of the spec draft for human review.

Shows the first MAX_PREVIEW_LINES of the spec draft so the reviewer"""
    ...

def human_gate(state: ImplementationSpecState) -> dict[str, Any]:
    """N4: Optional human review checkpoint.

Issue #304: Implementation Readiness Review Workflow"""
    ...

MAX_PREVIEW_LINES = 80
```

### assemblyzero/workflows/implementation_spec/nodes/review_spec.py (full)

```python
"""N5: Review Spec node for Implementation Spec Workflow.

Issue #304: Implementation Readiness Review Workflow (LLD -> Implementation Spec)

Uses the configured reviewer LLM (Gemini) to perform an implementation
readiness review of the generated spec draft. This is a semantic review
that evaluates whether the spec contains enough concrete detail for
autonomous AI implementation.

This is distinct from N3 (mechanical validation): N3 checks for structural
completeness (excerpts, examples, etc.), while N5 evaluates whether the
spec is actually implementable (clear instructions, consistent patterns,
realistic examples, no ambiguity).

This node populates:
- review_verdict: "APPROVED", "REVISE", or "BLOCKED"
- review_feedback: Gemini's detailed review comments
- review_iteration: Current review round (unchanged; N2 increments on revision)
- error_message: "" on success, error text on failure
"""

import re
from pathlib import Path
from typing import Any

from assemblyzero.core.llm_provider import get_provider
from assemblyzero.workflows.requirements.audit import (
    next_file_number,
    save_audit_file,
)
from assemblyzero.workflows.implementation_spec.state import ImplementationSpecState


# =============================================================================
# Constants
# =============================================================================

# Default reviewer model spec
DEFAULT_REVIEWER = "gemini:3-pro-preview"

# Minimum spec size to be considered valid (bytes)
MIN_SPEC_SIZE = 100

# Maximum spec size to review (prevent prompt blow-up)
MAX_SPEC_SIZE = 200_000

# System prompt for Gemini readiness review
REVIEWER_SYSTEM_PROMPT = """\
You are a Senior Software Architect performing an Implementation Readiness Review.

Your role is to evaluate whether an Implementation Spec provides enough \
concrete detail for an autonomous AI agent to implement the changes with \
>80% first-try success rate.

CRITICAL INSTRUCTIONS:
1. You are reviewing an IMPLEMENTATION SPEC, not source code or a PR.
2. Your focus is EXECUTABILITY: Could an AI agent read this spec and produce \
correct code without asking questions?
3. You must provide a structured verdict: APPROVED, REVISE, or BLOCKED.
4. Be specific about what needs to change for REVISE/BLOCKED verdicts.

You are NOT reviewing:
- Code quality (there is no code yet)
- Test coverage (tests haven't been written yet)
- PR readiness (this is pre-implementation)

You ARE reviewing:
- Completeness: Are all files covered with specific instructions?
- Concreteness: Are there real code excerpts, not just descriptions?
- Specificity: Could someone write exact diffs from the instructions?
- Consistency: Do patterns, naming, and structure match the codebase?
- Feasibility: Are the instructions technically achievable?"""


# =============================================================================
# Main Node
# =============================================================================


async def review_spec(state: ImplementationSpecState) -> dict[str, Any]:
    """N5: Send spec to Gemini for implementation readiness review.

    Issue #304: Implementation Readiness Review Workflow

    Steps:
    1. Guard against empty/invalid spec drafts
    2. Build review prompt with spec and LLD context
    3. Call configured reviewer LLM (Gemini)
    4. Parse verdict from response
    5. Save verdict to audit trail
    6. Return state updates

    Args:
        state: Current workflow state. Requires:
            - spec_draft: Generated Implementation Spec markdown (from N2)
            - lld_content: Original LLD for reference
            - issue_number: GitHub issue number
            - assemblyzero_root: Path to AssemblyZero installation

    Returns:
        Dict with state field updates:
        - review_verdict: "APPROVED", "REVISE", or "BLOCKED"
        - review_feedback: Gemini's detailed review comments
        - error_message: "" on success, error text on failure
    """
    # Extract state
    spec_draft = state.get("spec_draft", "")
    lld_content = state.get("lld_content", "")
    issue_number = state.get("issue_number", 0)
    review_iteration = state.get("review_iteration", 0)
    max_iterations = state.get("max_iterations", 3)
    mock_mode = state.get("config_mock_mode", False)

    print(f"\n[N5] Reviewing Implementation Spec (iteration {review_iteration})...")

    # -------------------------------------------------------------------------
    # GUARD: Iteration bounds
    # -------------------------------------------------------------------------
    if review_iteration >= max_iterations:
        print(f"    [GUARD] Max iterations ({max_iterations}) reached")
        return {
            "review_verdict": "BLOCKED",
            "review_feedback": (
                f"Maximum review iterations ({max_iterations}) exceeded. "
                "Spec could not pass readiness review within allowed attempts."
            ),
            "error_message": "",
        }

    # -------------------------------------------------------------------------
    # GUARD: Pre-LLM content validation
    # -------------------------------------------------------------------------
    if not spec_draft or not spec_draft.strip():
        print("    [GUARD] BLOCKED: Spec draft is empty")
        return {
            "review_verdict": "BLOCKED",
            "review_feedback": "Spec draft is empty. Cannot perform readiness review.",
            "error_message": "GUARD: Spec draft is empty",
        }

    content_len = len(spec_draft)
    if content_len < MIN_SPEC_SIZE:
        print(f"    [GUARD] WARNING: Spec suspiciously short ({content_len} chars)")

    if content_len > MAX_SPEC_SIZE:
        print(f"    [GUARD] Truncating spec from {content_len} to {MAX_SPEC_SIZE} chars")
        spec_draft = spec_draft[:MAX_SPEC_SIZE] + "\n\n<!-- Truncated for review -->\n"

    # -------------------------------------------------------------------------
    # Build review content
    # -------------------------------------------------------------------------
    review_content = _build_review_content(
        spec_draft=spec_draft,
        lld_content=lld_content,
        issue_number=issue_number,
        review_iteration=review_iteration,
    )

    # -------------------------------------------------------------------------
    # Get reviewer provider
    # -------------------------------------------------------------------------
    if mock_mode:
        reviewer_spec = "mock:review"
    else:
        reviewer_spec = state.get("config_reviewer", DEFAULT_REVIEWER)

    try:
        reviewer = get_provider(reviewer_spec)
    except ValueError as e:
        print(f"    ERROR: Invalid reviewer: {e}")
        return {"error_message": f"Invalid reviewer: {e}"}

    print(f"    Reviewer: {reviewer_spec}")

    # -------------------------------------------------------------------------
    # Call reviewer LLM
    # -------------------------------------------------------------------------
    result = reviewer.invoke(
        system_prompt=REVIEWER_SYSTEM_PROMPT,
        content=review_content,
    )

    if not result.success:
        print(f"    ERROR: {result.error_message}")
        return {"error_message": f"Reviewer failed: {result.error_message}"}

    verdict_content = result.response or ""

    # -------------------------------------------------------------------------
    # Save verdict to audit trail
    # -------------------------------------------------------------------------
    audit_dir_str = state.get("audit_dir", "")
    audit_dir = Path(audit_dir_str) if audit_dir_str else None
    verdict_path = None

    if audit_dir and audit_dir.exists():
        file_num = next_file_number(audit_dir)
        verdict_path = save_audit_file(
            audit_dir, file_num, "readiness-verdict.md", verdict_content
        )

    # -------------------------------------------------------------------------
    # Parse verdict
    # -------------------------------------------------------------------------
    verdict_status, feedback = parse_review_verdict(verdict_content)

    # -------------------------------------------------------------------------
    # Report results
    # -------------------------------------------------------------------------
    verdict_lines = len(verdict_content.splitlines()) if verdict_content else 0
    print(f"    Verdict: {verdict_status} ({verdict_lines} lines)")
    if verdict_path:
        print(f"    Saved: {verdict_path.name}")

    if verdict_status == "REVISE" and feedback:
        # Show a preview of feedback
        feedback_preview = feedback[:200].replace("\n", " ")
        if len(feedback) > 200:
            feedback_preview += "..."
        print(f"    Feedback: {feedback_preview}")

    return {
        "review_verdict": verdict_status,
        "review_feedback": feedback,
        "error_message": "",
    }


# =============================================================================
# Review Content Builder
# =============================================================================


def _build_review_content(
    spec_draft: str,
    lld_content: str,
    issue_number: int,
    review_iteration: int,
) -> str:
    """Build the review content for the Gemini reviewer.

    Constructs a structured prompt containing the spec draft, the original
    LLD for reference, and review criteria.

    Args:
        spec_draft: Generated Implementation Spec markdown.
        lld_content: Original LLD markdown for cross-reference.
        issue_number: GitHub issue number.
        review_iteration: Current review iteration (0-based).

    Returns:
        Complete review prompt string.
    """
    sections: list[str] = []

    # Context header
    context = f"## Review Context\n\n"
    context += f"- **Issue:** #{issue_number}\n"
    context += f"- **Review Iteration:** {review_iteration}\n"
    if review_iteration > 0:
        context += (
            "- **Note:** This is a REVISED spec. Previous review(s) "
            "requested changes. Focus on whether the revisions address "
            "the prior feedback.\n"
        )
    sections.append(context)

    # Implementation Spec to review
    sections.append(
        f"## Implementation Spec to Review\n\n{spec_draft}"
    )

    # Original LLD for cross-reference (truncated if very large)
    if lld_content:
        lld_excerpt = lld_content
        if len(lld_excerpt) > 50_000:
            lld_excerpt = lld_excerpt[:50_000] + "\n\n<!-- LLD truncated for review -->\n"
        sections.append(
            f"## Original LLD (for cross-reference)\n\n{lld_excerpt}"
        )

    # Review criteria
    sections.append(_get_review_criteria())

    # Output format instructions
    sections.append(_get_output_format())

    return "\n\n".join(sections)


def _get_review_criteria() -> str:
    """Return the readiness review criteria.

    These criteria are distinct from the 0703c Implementation Review Prompt
    (which reviews actual code). This reviews the SPEC that will guide
    code generation.

    Returns:
        Review criteria as formatted markdown string.
    """
    return """\
## Readiness Review Criteria

Evaluate the Implementation Spec against these criteria:

### 1. File Coverage (BLOCKING)
- Does the spec address EVERY file listed in the LLD's Section 2.1?
- Does each "Modify" file include a current state excerpt?
- Does each "Add" file include the complete expected content or clear generation instructions?

### 2. Specificity (BLOCKING)
- Are change instructions specific enough to generate diffs?
- Do instructions include before/after code snippets where applicable?
- Are line-level references provided for modifications?
- Would an AI agent need to ask clarifying questions?

### 3. Concreteness (HIGH PRIORITY)
- Does every data structure have a concrete JSON/YAML example with realistic values?
- Does every function signature have input/output examples with actual values?
- Are there real code snippets (not pseudocode) for key implementations?

### 4. Pattern Consistency (HIGH PRIORITY)
- Do the patterns referenced actually exist in the codebase?
- Are naming conventions consistent with the existing codebase?
- Does the proposed implementation follow established project patterns?

### 5. Feasibility (HIGH PRIORITY)
- Are the proposed changes technically achievable?
- Are dependencies correctly identified?
- Are there any circular dependencies or ordering issues?
- Is the scope appropriate (not too large for a single implementation)?

### 6. Test Guidance (SUGGESTION)
- Does the spec include test file locations and patterns?
- Are test cases concrete enough to implement?"""


def _get_output_format() -> str:
    """Return the expected output format for the verdict.

    Returns:
        Output format instructions as formatted markdown string.
    """
    return """\
## Required Output Format

You MUST structure your review as follows:

```
## Readiness Review: Issue #{issue_number}

## Summary
{2-3 sentence overall assessment of the spec's readiness for implementation}

## File Coverage Assessment
{For each file in the LLD: covered/not covered, quality of instructions}

## Blocking Issues
{If none: "No blocking issues found."}
{If any: numbered list with specific file/section references}

## High Priority Issues
{If none: "No high-priority issues found."}
{If any: numbered list with specific recommendations}

## Suggestions
{Brief bullet points for improvements}

## Verdict
[ ] **APPROVED** - Spec is ready for implementation
[ ] **REVISE** - Fix blocking/high-priority issues first
[ ] **BLOCKED** - Fundamental issues prevent implementation
```

IMPORTANT:
- Mark EXACTLY ONE verdict checkbox with [X]
- If REVISE or BLOCKED, list SPECIFIC changes needed
- Reference specific sections/files from the spec in your feedback"""


# =============================================================================
# Verdict Parsing
# =============================================================================


def parse_review_verdict(response: str) -> tuple[str, str]:
    """Extract verdict and feedback from Gemini response.

    Parses the structured Gemini response to extract:
    1. The verdict (APPROVED, REVISE, or BLOCKED)
    2. The full feedback content for revision prompts

    The verdict is determined by checked checkboxes in the response:
    - [X] **APPROVED** -> "APPROVED"
    - [X] **REVISE** -> "REVISE"
    - [X] **BLOCKED** -> "BLOCKED"

    Falls back to keyword matching if no checkboxes found.

    Args:
        response: Raw Gemini response text.

    Returns:
        Tuple of (verdict_status, feedback_text).
        verdict_status: One of "APPROVED", "REVISE", "BLOCKED".
        feedback_text: The full response as feedback for revision prompts.
    """
    if not response or not response.strip():
        return "BLOCKED", "Empty review response received."

    response_upper = response.upper()

    # -------------------------------------------------------------------
    # Primary: Check for checked checkboxes (structured verdict)
    # -------------------------------------------------------------------
    if re.search(r"\[X\]\s*\**APPROVED\**", response_upper):
        verdict = "APPROVED"
    elif re.search(r"\[X\]\s*\**REVISE\**", response_upper):
        verdict = "REVISE"
    elif re.search(r"\[X\]\s*\**BLOCKED\**", response_upper):
        verdict = "BLOCKED"
    # -------------------------------------------------------------------
    # Secondary: Check for "Verdict: X" pattern
    # -------------------------------------------------------------------
    elif "VERDICT: APPROVED" in response_upper:
        verdict = "APPROVED"
    elif "VERDICT: REVISE" in response_upper:
        verdict = "REVISE"
    elif "VERDICT: BLOCKED" in response_upper:
        verdict = "BLOCKED"
    # -------------------------------------------------------------------
    # Tertiary: Check for DISCUSS (maps to BLOCKED)
    # -------------------------------------------------------------------
    elif re.search(r"\[X\]\s*\**DISCUSS\**", response_upper):
        verdict = "BLOCKED"
    # -------------------------------------------------------------------
    # Fallback: Default to BLOCKED (safe choice)
    # -------------------------------------------------------------------
    else:
        verdict = "BLOCKED"

    # -------------------------------------------------------------------
    # Extract feedback
    # -------------------------------------------------------------------
    # Use the full response as feedback for the revision prompt.
    # This ensures the drafter has full context when revising.
    feedback = _extract_feedback(response, verdict)

    return verdict, feedback


def _extract_feedback(response: str, verdict: str) -> str:
    """Extract actionable feedback from the review response.

    For APPROVED verdicts, extracts suggestions section if present.
    For REVISE/BLOCKED verdicts, extracts blocking issues, high priority
    issues, and suggestions as combined feedback.

    Args:
        response: Full Gemini review response.
        verdict: Parsed verdict status.

    Returns:
        Extracted feedback text for use in revision prompts.
    """
    if verdict == "APPROVED":
        # For APPROVED, only return suggestions (if any)
        suggestions = _extract_section(response, "Suggestions")
        if suggestions:
            return f"Approved with suggestions:\n{suggestions}"
        return "Approved. No changes needed."

    # For REVISE/BLOCKED, combine all actionable feedback
    feedback_parts: list[str] = []

    blocking = _extract_section(response, "Blocking Issues")
    if blocking:
        feedback_parts.append(f"## Blocking Issues\n{blocking}")

    high_priority = _extract_section(response, "High Priority Issues")
    if high_priority:
        feedback_parts.append(f"## High Priority Issues\n{high_priority}")

    file_coverage = _extract_section(response, "File Coverage Assessment")
    if file_coverage:
        feedback_parts.append(f"## File Coverage Assessment\n{file_coverage}")

    suggestions = _extract_section(response, "Suggestions")
    if suggestions:
        feedback_parts.append(f"## Suggestions\n{suggestions}")

    if feedback_parts:
        return "\n\n".join(feedback_parts)

    # Fallback: return the full response as feedback
    return response


def _extract_section(content: str, section_name: str) -> str:
    """Extract content from a named markdown section.

    Extracts text between a ## heading matching section_name and the
    next ## heading (or end of document).

    Args:
        content: Full markdown content.
        section_name: Name of the section to extract (without ## prefix).

    Returns:
        Section content (without the heading), or empty string if not found.
    """
    # Match section heading (## or ###)
    pattern = (
        rf"^##\s*#?\s*{re.escape(section_name)}\s*\n"
        rf"(.*?)"
        rf"(?=^##\s|\Z)"
    )
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""
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
