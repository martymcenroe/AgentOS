# Implementation Spec Reviewer — User Prompt Template

<!-- Prompt Metadata -->
| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Last Updated** | 2026-02-16 |
| **Role** | User prompt for Implementation Spec readiness review |
| **Purpose** | Provide the Implementation Spec draft and original LLD to the Gemini reviewer |
| **Model** | Gemini (3 Pro Preview) |
| **Issue** | #304 |

---

## Review Mode

Use this prompt when sending an Implementation Spec draft for readiness review.

---

### Prompt Template (Review)

```
Review the following Implementation Spec for implementation readiness.

## Issue

Issue #{issue_number}

## Review Iteration

This is review iteration {review_iteration} of maximum {max_iterations}.

## Original LLD

The following is the approved Low-Level Design that the spec was generated from. Use it to verify completeness and consistency — every file in LLD Section 2.1 must have implementation instructions in the spec.

<lld>
{lld_content}
</lld>

## Implementation Spec Draft

This is the spec to review. Evaluate it against all six readiness criteria defined in your system prompt.

<spec>
{spec_draft}
</spec>

## Review Instructions

1. Evaluate the spec against all six criteria:
   - Criterion 1: Current State Accuracy
   - Criterion 2: Data Structure Concreteness
   - Criterion 3: Function Specification Quality
   - Criterion 4: Change Instruction Specificity
   - Criterion 5: Pattern Consistency
   - Criterion 6: Completeness and Coherence

2. For each criterion, assess whether the checkpoints are met.

3. Issue your verdict: APPROVED, REVISE, or BLOCKED.

4. For REVISE or BLOCKED verdicts, provide specific, actionable fixes with exact section and file references.

5. Use the exact output format specified in your system prompt.
```

---

## Revision Review Mode

Use this prompt when reviewing a **revised** spec (iteration > 1). Includes previous feedback so the reviewer can check if issues were addressed.

---

### Prompt Template (Revision Review)

```
Review the following REVISED Implementation Spec for implementation readiness.

## Issue

Issue #{issue_number}

## Review Iteration

This is review iteration {review_iteration} of maximum {max_iterations}.

IMPORTANT: This is a revision review. Focus primarily on whether the previous feedback was addressed. Do NOT introduce entirely new concerns unless they are critical. Be progressively more lenient on minor issues in later iterations.

## Original LLD

<lld>
{lld_content}
</lld>

## Previous Review Feedback

The following feedback was provided in the previous review iteration. Verify that each required fix has been addressed.

<previous_feedback>
{review_feedback}
</previous_feedback>

## Revised Implementation Spec Draft

<spec>
{spec_draft}
</spec>

## Review Instructions

1. First, check whether each item from the previous feedback was addressed:
   - For each required fix, note whether it was FIXED, PARTIALLY FIXED, or NOT FIXED
   - Summarize the improvement delta at the top of your assessment

2. Then evaluate the spec against all six criteria:
   - Criterion 1: Current State Accuracy
   - Criterion 2: Data Structure Concreteness
   - Criterion 3: Function Specification Quality
   - Criterion 4: Change Instruction Specificity
   - Criterion 5: Pattern Consistency
   - Criterion 6: Completeness and Coherence

3. Issue your verdict: APPROVED, REVISE, or BLOCKED.

4. For REVISE or BLOCKED verdicts, provide specific, actionable fixes. Only list NEW issues or issues that were NOT FIXED from previous feedback.

5. If the same issue persists after 2 revision cycles, escalate to BLOCKED.

6. Use the exact output format specified in your system prompt.
```

---

## Variable Reference

| Variable | Source | Description |
|----------|--------|-------------|
| `{issue_number}` | `state.issue_number` | GitHub issue number |
| `{review_iteration}` | `state.review_iteration` | Current review round (1-indexed) |
| `{max_iterations}` | `state.max_iterations` | Maximum allowed iterations (default: 3) |
| `{lld_content}` | `state.lld_content` | Full approved LLD markdown content |
| `{spec_draft}` | `state.spec_draft` | Generated Implementation Spec draft |
| `{review_feedback}` | `state.review_feedback` | Previous iteration's review feedback (revision mode only) |

---

## Mode Selection Logic

The `_build_review_content()` function in `nodes/review_spec.py` selects the prompt mode:

```python
if review_iteration <= 1:
    # First review — use Review Mode template
    prompt = REVIEW_TEMPLATE.format(...)
else:
    # Subsequent reviews — use Revision Review Mode template
    prompt = REVISION_REVIEW_TEMPLATE.format(...)
```

---

## Token Budget Notes

- **LLD content:** Typically 5-30KB (fits within Gemini context)
- **Spec draft:** Typically 10-50KB depending on complexity
- **Previous feedback:** Typically 1-5KB
- **Total prompt:** Should stay under 100K tokens for reliable review quality
- If the combined content exceeds limits, the spec draft takes priority — truncate LLD before truncating spec