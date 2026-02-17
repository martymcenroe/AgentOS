# Implementation Readiness Review

<!-- Standard: 0702 -->
<!-- Version: 1.0 -->
<!-- Last Updated: 2026-02-16 -->
<!-- Issue: #304 -->

> **Purpose:** This document defines the review criteria and process for evaluating Implementation Specs before they are used for autonomous AI implementation. The readiness review ensures specs contain enough concrete detail for >80% first-try implementation success.

---

## 1. Overview

The Implementation Readiness Review is performed by Gemini (N5 node) after mechanical completeness validation (N3) passes. It evaluates whether an Implementation Spec is **actually implementable** — not just structurally complete, but semantically clear, consistent, and unambiguous.

### 1.1 Distinction from Mechanical Validation (N3)

| Aspect | N3: Mechanical Validation | N5: Readiness Review |
|--------|--------------------------|---------------------|
| **What** | Structural completeness checks | Semantic implementability assessment |
| **How** | Regex/pattern matching | LLM-based evaluation (Gemini) |
| **Checks** | Excerpts exist, examples present, diffs included | Instructions are clear, examples are realistic, no ambiguity |
| **Speed** | Milliseconds | 15-30 seconds |
| **Cost** | Free (local) | ~$0.004 per review |
| **Verdict** | PASSED / BLOCKED | APPROVED / REVISE / BLOCKED |

### 1.2 Workflow Position

```
N0 → N1 → N2 → N3 (mechanical) → N4 (human, optional) → N5 (readiness) → N6
                ^                                          |
                |                                          |
                +------------------------------------------+
                          (REVISE loops back to N2)
```

---

## 2. Review Criteria

The readiness review evaluates the Implementation Spec against six criteria categories. Each category contains specific checkpoints that the reviewer must assess.

### 2.1 Criterion 1: Current State Accuracy

**Question:** Are the current state excerpts accurate and sufficient for implementation?

| Checkpoint | Pass Criteria |
|------------|---------------|
| Excerpts match actual codebase | Code excerpts are real, not fabricated or outdated |
| Line numbers are plausible | Referenced line ranges exist in files of that size |
| Relevant code is included | The excerpt covers the area being modified, not unrelated code |
| Context is sufficient | Enough surrounding code to understand where changes fit |

**Failure examples:**
- Excerpt shows a function that doesn't exist in the file
- Line numbers reference beyond the end of the file
- Excerpt shows imports but the modification is to a class 200 lines later

### 2.2 Criterion 2: Data Structure Clarity

**Question:** Can an AI agent create these data structures from the spec alone?

| Checkpoint | Pass Criteria |
|------------|---------------|
| Type definitions are complete | All fields have types, no `Any` without justification |
| Examples use realistic values | Values resemble actual data, not placeholders like "foo" or "test" |
| Examples match type definitions | JSON/YAML examples are consistent with TypedDict/dataclass fields |
| Edge cases are noted | Optional fields, empty collections, None values are addressed |

**Failure examples:**
- TypedDict has `items: list[str]` but example shows `"items": [1, 2, 3]`
- Example uses `"name": "example"` instead of a realistic value like `"name": "load_lld"`
- Missing fields in the example that are required in the type definition

### 2.3 Criterion 3: Function Implementability

**Question:** Can an AI agent implement each function from the spec alone?

| Checkpoint | Pass Criteria |
|------------|---------------|
| Input examples are realistic | Inputs resemble actual workflow data, not toy examples |
| Output examples match return types | Returned dict keys match what callers expect |
| Edge cases are actionable | Each edge case describes input condition AND expected behavior |
| Error handling is specified | How errors propagate (exceptions vs. error_message field) |
| Dependencies are clear | All imports and external calls are documented |

**Failure examples:**
- Function returns `dict[str, Any]` but no example shows which keys are returned
- Edge case says "handles invalid input" without specifying what "invalid" means
- Function calls `get_provider()` but this import isn't listed in Dependencies section

### 2.4 Criterion 4: Change Instruction Precision

**Question:** Can an AI agent generate correct diffs from these instructions?

| Checkpoint | Pass Criteria |
|------------|---------------|
| Add files have complete contents | New files show the entire file, not just snippets |
| Modify files use diff notation | Changes shown as `+`/`-` lines with context |
| Line references are specific | "Add at line 15" not "add somewhere in the file" |
| Multiple changes are ordered | When a file has multiple changes, they're in line order |
| Delete files verify no dependents | Confirmation that no other files import from deleted file |

**Failure examples:**
- "Add error handling to the function" without showing the actual code
- Diff context doesn't match current state excerpt from Section 3
- New file shows only the key function, missing imports and module docstring

### 2.5 Criterion 5: Pattern Consistency

**Question:** Does the spec follow patterns from the existing codebase?

| Checkpoint | Pass Criteria |
|------------|---------------|
| Pattern references are relevant | Referenced patterns are genuinely similar to the implementation |
| New code follows referenced patterns | Proposed code structure matches the cited pattern |
| Naming conventions are consistent | New names follow the project's naming style |
| Error handling matches project style | Same error propagation approach as existing code |
| Import organization matches | Import grouping (stdlib, third-party, local) follows convention |

**Failure examples:**
- References a pattern from `workflows/requirements/` but implements differently
- Existing nodes use `error_message` field but new code raises exceptions
- Existing graph uses `N0_load_lld` naming but new code uses `step_1_load`

### 2.6 Criterion 6: Test Coverage Mapping

**Question:** Do the tests adequately verify the implementation?

| Checkpoint | Pass Criteria |
|------------|---------------|
| Every function has at least one test | Test mapping in Section 9 covers all functions from Section 5 |
| Edge cases have tests | Edge cases from Section 5 appear in test mapping |
| Input/output examples are testable | Test inputs and expected outputs are concrete, not abstract |
| Integration points are tested | Interactions between nodes/modules have test scenarios |

**Failure examples:**
- Section 5 defines 8 functions but Section 9 only maps tests for 3
- Test expects `{"result": "..."}` with literal ellipsis instead of actual value
- No test for the error path when a file is not found

---

## 3. Verdict Definitions

The readiness review produces one of three verdicts:

### 3.1 APPROVED

**Meaning:** The spec is ready for autonomous implementation.

**Criteria:** All six criterion categories pass with no blocking issues.

**Action:** Workflow proceeds to N6 (finalize_spec) and writes the approved spec.

**Minor issues:** The reviewer may include non-blocking suggestions in the feedback. These are advisory and do not prevent approval.

### 3.2 REVISE

**Meaning:** The spec needs specific improvements before it can be approved.

**Criteria:** One or more checkpoints fail, but the issues are fixable through revision.

**Action:** Workflow returns to N2 (generate_spec) with the reviewer's feedback. The feedback is incorporated into the revision prompt so Claude can address specific issues.

**Feedback requirements:** REVISE feedback must be actionable — it must specify:
1. Which criterion failed
2. Which specific checkpoint(s) within that criterion
3. What the current content says (or is missing)
4. What it should say instead

**Example feedback:**
```
CRITERION 3 (Function Implementability) - FAIL
- Checkpoint: Output examples match return types
- Issue: `parse_files_to_modify()` shows return type `list[FileToModify]`
  but the output example returns a plain dict without the `current_content` field
- Fix: Add `current_content: None` to the example since this is populated later in N1
```

### 3.3 BLOCKED

**Meaning:** The spec has fundamental issues that cannot be fixed through simple revision.

**Criteria:** The spec is missing critical sections, contradicts the LLD, or has structural problems that require human intervention.

**Action:** Workflow terminates. The spec draft and review feedback are saved to the audit trail for human review.

**Examples of blocking issues:**
- Spec describes changes to files not listed in the LLD
- Current state excerpts appear fabricated (don't match any real code)
- Fundamental architectural contradiction with the LLD's design decisions
- Spec proposes adding dependencies not approved in the LLD

---

## 4. Review Process

### 4.1 Input

The reviewer receives:

| Input | Source | Purpose |
|-------|--------|---------|
| Implementation Spec draft | N2 (generate_spec) output | The document being reviewed |
| Original LLD | N0 (load_lld) output | Reference for consistency checking |
| Issue number | Workflow state | Context identification |
| Review iteration | Workflow state | Awareness of revision history |

### 4.2 Review Steps

1. **Read the LLD** to understand the intended design
2. **Read the spec** end-to-end for overall coherence
3. **Evaluate each criterion** (Sections 2.1-2.6) systematically
4. **Check LLD consistency** — spec must not contradict LLD decisions
5. **Assess overall implementability** — could an AI agent implement this without asking questions?
6. **Render verdict** with structured feedback

### 4.3 Output Format

The reviewer produces a structured response:

```markdown
## Readiness Review

### Verdict: {APPROVED | REVISE | BLOCKED}

### Criterion Results

| # | Criterion | Result | Notes |
|---|-----------|--------|-------|
| 1 | Current State Accuracy | PASS / FAIL | {brief note} |
| 2 | Data Structure Clarity | PASS / FAIL | {brief note} |
| 3 | Function Implementability | PASS / FAIL | {brief note} |
| 4 | Change Instruction Precision | PASS / FAIL | {brief note} |
| 5 | Pattern Consistency | PASS / FAIL | {brief note} |
| 6 | Test Coverage Mapping | PASS / FAIL | {brief note} |

### Detailed Feedback

{For REVISE/BLOCKED: specific issues with actionable fixes}
{For APPROVED: optional suggestions for improvement}

### Suggestions (Non-Blocking)

{Optional improvements that don't affect the verdict}
```

### 4.4 Iteration Limits

| Parameter | Default | Configurable |
|-----------|---------|-------------|
| Max review iterations | 3 | Yes (`max_iterations` in state) |
| Behavior at max | BLOCKED | N/A |
| Feedback accumulation | Cumulative | N/A |

When the maximum iteration count is reached without an APPROVED verdict, the workflow terminates with a BLOCKED status. All accumulated feedback from previous iterations is preserved in the audit trail.

---

## 5. Reviewer Configuration

### 5.1 Default Reviewer

| Setting | Value |
|---------|-------|
| Model | `gemini:3-pro-preview` |
| Role | Implementation readiness reviewer |
| Temperature | Default (model-specific) |

### 5.2 Reviewer Prompt Structure

The reviewer receives a system prompt and user prompt:

**System prompt** (`docs/prompts/implementation_spec/reviewer_system.md`):
- Role definition: Implementation readiness reviewer
- Criteria definitions (from Section 2 of this document)
- Output format specification
- Instructions to be specific and actionable

**User prompt** (`docs/prompts/implementation_spec/reviewer_user.md`):
- The Implementation Spec draft
- The original LLD for reference
- Issue number and iteration context
- Request for structured verdict

### 5.3 Prompt Principles

The reviewer prompts follow these principles:

1. **Executability focus:** The reviewer evaluates whether code can be written from the spec, not whether the design is good (that was the LLD review's job)
2. **Concrete feedback:** Every FAIL must include what's wrong and what would fix it
3. **No new requirements:** The reviewer cannot add requirements beyond what the LLD specifies
4. **Pattern awareness:** The reviewer should flag deviations from existing codebase patterns
5. **Iteration awareness:** On revision rounds, the reviewer checks that previous feedback was addressed

---

## 6. Integration with Workflow

### 6.1 Routing Logic

```python
def route_after_review(state: ImplementationSpecState) -> str:
    """Route after N5: review_spec."""
    if state.get("review_verdict") == "APPROVED":
        return "N6_finalize_spec"
    if (
        state.get("review_verdict") == "REVISE"
        and state.get("review_iteration", 0) < state.get("max_iterations", 3)
    ):
        return "N2_generate_spec"
    return "END"  # BLOCKED or max iterations exceeded
```

### 6.2 State Updates

After N5 completes, the following state fields are updated:

| Field | Updated To |
|-------|------------|
| `review_verdict` | `"APPROVED"`, `"REVISE"`, or `"BLOCKED"` |
| `review_feedback` | Gemini's detailed review comments |
| `error_message` | Empty on success, error details on API failure |

### 6.3 Audit Trail

Every review interaction is saved to the audit trail:

| Artifact | Path Pattern | Contents |
|----------|-------------|----------|
| Review request | `audit/{issue}/NN-review-request.md` | Spec + LLD sent to Gemini |
| Review response | `audit/{issue}/NN-review-response.md` | Raw Gemini response |
| Parsed verdict | Embedded in state | Verdict + feedback |

---

## 7. Quality Metrics

### 7.1 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| First-try approval rate | >60% | Specs approved on iteration 1 |
| Overall approval rate | >90% | Specs approved within 3 iterations |
| Implementation success rate | >80% | Approved specs that implement successfully |
| False approval rate | <5% | Approved specs that fail implementation |

### 7.2 Monitoring

Track these metrics over time to tune review criteria:

- If **false approval rate is too high:** Tighten criteria (add checkpoints, raise thresholds)
- If **first-try approval rate is too low:** Review drafter prompt quality, check if criteria are too strict
- If **implementation success rate is low despite approvals:** Review criteria may be checking the wrong things

---

## 8. Examples

### 8.1 Example: APPROVED Review

```markdown
## Readiness Review

### Verdict: APPROVED

### Criterion Results

| # | Criterion | Result | Notes |
|---|-----------|--------|-------|
| 1 | Current State Accuracy | PASS | All 3 Modify files have accurate excerpts |
| 2 | Data Structure Clarity | PASS | TypedDicts match JSON examples |
| 3 | Function Implementability | PASS | All 7 functions have I/O examples |
| 4 | Change Instruction Precision | PASS | Diffs are line-specific |
| 5 | Pattern Consistency | PASS | Follows existing node pattern |
| 6 | Test Coverage Mapping | PASS | All functions mapped to tests |

### Suggestions (Non-Blocking)

- Consider adding a timeout constant for the API call in `generate_spec()`
- The pattern reference in Section 7.2 could include the error handling portion
```

### 8.2 Example: REVISE Review

```markdown
## Readiness Review

### Verdict: REVISE

### Criterion Results

| # | Criterion | Result | Notes |
|---|-----------|--------|-------|
| 1 | Current State Accuracy | PASS | Excerpts verified |
| 2 | Data Structure Clarity | PASS | Examples are realistic |
| 3 | Function Implementability | FAIL | Missing edge cases for 2 functions |
| 4 | Change Instruction Precision | FAIL | graph.py changes lack diff notation |
| 5 | Pattern Consistency | PASS | Follows conventions |
| 6 | Test Coverage Mapping | PASS | Coverage is adequate |

### Detailed Feedback

**Criterion 3 - Function Implementability:**
- `validate_completeness()`: No edge case for when `spec_draft` is empty string.
  Fix: Add edge case: `spec_draft=""` → returns `{"validation_passed": False,
  "completeness_issues": ["Empty spec draft"]}`
- `parse_review_verdict()`: No edge case for malformed Gemini response.
  Fix: Add edge case: response without verdict marker → returns
  `("BLOCKED", "Could not parse verdict from review response")`

**Criterion 4 - Change Instruction Precision:**
- `graph.py` (Modify): Section 6.2 says "add conditional edges" but doesn't
  show the diff. Current code at lines 45-60 is shown in Section 3 but the
  change instructions only describe the intent, not the actual code changes.
  Fix: Add diff notation showing the specific `add_conditional_edges()` calls
  with their routing functions.
```

### 8.3 Example: BLOCKED Review

```markdown
## Readiness Review

### Verdict: BLOCKED

### Criterion Results

| # | Criterion | Result | Notes |
|---|-----------|--------|-------|
| 1 | Current State Accuracy | FAIL | BLOCKING: Excerpts appear fabricated |
| 2 | Data Structure Clarity | FAIL | Contradicts LLD |
| 3 | Function Implementability | N/A | Cannot assess without valid state |
| 4 | Change Instruction Precision | N/A | Cannot assess |
| 5 | Pattern Consistency | N/A | Cannot assess |
| 6 | Test Coverage Mapping | N/A | Cannot assess |

### Detailed Feedback

**BLOCKING: Criterion 1 - Current State Accuracy:**
- `state.py` excerpt shows a `WorkflowConfig` class that does not exist in
  the current codebase. The actual `state.py` contains only `RequirementsState`.
  This appears to be hallucinated content. Human review required to provide
  accurate current state.

**BLOCKING: Criterion 2 - Data Structure Clarity:**
- The spec defines `ImplementationSpecState` with a `config: WorkflowConfig`
  field, but the LLD Section 2.3 does not include any `WorkflowConfig` type.
  The spec is introducing structures not present in the approved design.
```

---

## 9. Maintenance

### 9.1 Updating Criteria

When review criteria need updating:

1. Update this document (0702) with new/modified checkpoints
2. Update `docs/prompts/implementation_spec/reviewer_system.md` to match
3. Update `nodes/validate_completeness.py` if the change affects mechanical checks
4. Run existing test suite to verify no regressions

### 9.2 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-16 | Initial version (Issue #304) |

---

## References

- [0701-implementation-spec-template.md](0701-implementation-spec-template.md) — Template that specs must follow
- [LLD for Issue #304](../lld/) — Design document for this workflow
- [WORKFLOW.md](../../WORKFLOW.md) — Development workflow gates