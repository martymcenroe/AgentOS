# Implementation Spec Drafter — User Prompt Template

<!-- Prompt Metadata -->
| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Last Updated** | 2026-02-16 |
| **Role** | User prompt for Implementation Spec generation |
| **Purpose** | Provide LLD content, codebase analysis, and pattern references to the drafter |
| **Model** | Claude (Opus 4.5 / Sonnet) |
| **Issue** | #304 |

---

## Initial Draft Mode

Use this prompt when generating the first draft of an Implementation Spec.

---

### Prompt Template (Initial)

```
Generate a complete Implementation Spec for Issue #{issue_number}.

## Source LLD

The following is the approved Low-Level Design document:

<lld>
{lld_content}
</lld>

## Current State of Files to Modify

These are excerpts from the actual codebase for files that will be modified or deleted. Use these EXACTLY — do not fabricate code.

<current_state>
{current_state_section}
</current_state>

## Pattern References

These are existing implementations in the codebase that follow similar patterns. Use them to match conventions, naming, and structure.

<patterns>
{patterns_section}
</patterns>

## Repository Structure

<repo_structure>
{repo_structure}
</repo_structure>

## Files to Implement

The LLD specifies these files in Section 2.1. Your spec MUST cover ALL of them:

<files_to_modify>
{files_to_modify_list}
</files_to_modify>

## Implementation Spec Template

Follow this template EXACTLY. Include ALL sections. Do not skip or abbreviate.

<template>
{template_content}
</template>

## Instructions

1. Generate a complete Implementation Spec following the template above
2. For every "Modify" file, include the current state excerpt from <current_state>
3. For every data structure, include at least one concrete JSON/YAML example with realistic values
4. For every function, include input/output examples with actual values
5. For every "Add" file, provide the complete file contents
6. For every "Modify" file, provide diff-level change instructions (before/after with line references)
7. Reference patterns from <patterns> where applicable, citing file:line locations
8. Start DIRECTLY with `# Implementation Spec:` — no preamble
9. Output ONLY the raw markdown — no code fences wrapping the entire document
```

---

## Revision Mode

Use this prompt when revising a spec based on N3 (completeness) or N5 (review) feedback.

---

### Prompt Template (Revision)

```
Revise the Implementation Spec for Issue #{issue_number}.

## Feedback to Address

The following issues were found in the previous draft. You MUST fix ALL of them.

### Mechanical Completeness Issues (N3)

<completeness_issues>
{completeness_issues}
</completeness_issues>

### Readiness Review Feedback (N5)

<review_feedback>
{review_feedback}
</review_feedback>

## Current Draft

This is the spec draft that needs revision:

<current_draft>
{existing_draft}
</current_draft>

## Source LLD

The original approved Low-Level Design document:

<lld>
{lld_content}
</lld>

## Current State of Files to Modify

These are excerpts from the actual codebase. Use these EXACTLY — do not fabricate code.

<current_state>
{current_state_section}
</current_state>

## Pattern References

Existing implementations in the codebase that follow similar patterns.

<patterns>
{patterns_section}
</patterns>

## Repository Structure

<repo_structure>
{repo_structure}
</repo_structure>

## Implementation Spec Template

The template that the spec MUST follow:

<template>
{template_content}
</template>

## Revision Instructions

1. Fix ALL mechanical completeness issues listed above FIRST
2. Address EVERY point in the readiness review feedback
3. PRESERVE sections that were NOT flagged — do not regress working sections
4. ONLY modify sections that need changes based on the feedback
5. Keep ALL template sections intact — do not remove or skip any
6. Verify your fixes against each specific issue raised
7. For missing excerpts: use the provided <current_state> data
8. For missing examples: create concrete, realistic examples matching the types
9. For vague instructions: add diff-level specificity with line references
10. Start DIRECTLY with `# Implementation Spec:` — no preamble
11. Output ONLY the raw markdown — no code fences wrapping the entire document
```

---

## Variable Reference

| Variable | Source | Description |
|----------|--------|-------------|
| `{issue_number}` | `state.issue_number` | GitHub issue number |
| `{lld_content}` | `state.lld_content` | Full LLD markdown content |
| `{current_state_section}` | `_format_current_state_section()` | Formatted file excerpts from N1 |
| `{patterns_section}` | `_format_patterns_section()` | Formatted pattern references from N1 |
| `{repo_structure}` | `get_repo_structure()` | Repository directory tree |
| `{files_to_modify_list}` | `state.files_to_modify` | Formatted list of files from LLD 2.1 |
| `{template_content}` | `0701-implementation-spec-template.md` | Implementation Spec template |
| `{existing_draft}` | `state.spec_draft` | Previous draft (revision mode only) |
| `{review_feedback}` | `state.review_feedback` | Gemini review feedback (revision mode only) |
| `{completeness_issues}` | `state.completeness_issues` | N3 validation issues (revision mode only) |

---

## Formatting Rules for Variables

### `{current_state_section}`

Each file is formatted as:

```
### {file_path} ({change_type})

\`\`\`python
{code_excerpt}
\`\`\`
```

If no current content is available (Add files), the entry reads:

```
### {file_path} (Add)

*New file — no current state.*
```

### `{patterns_section}`

Each pattern is formatted as:

```
### Pattern: {pattern_type}
- **File:** `{file_path}` (lines {start_line}-{end_line})
- **Relevance:** {relevance}

\`\`\`python
{pattern_code_excerpt}
\`\`\`
```

### `{files_to_modify_list}`

Each file is formatted as a table row:

```
| {order} | `{path}` | {change_type} | {description} |
```

### `{completeness_issues}`

Each issue is formatted as a numbered item:

```
1. **{check_name}**: {details}
2. **{check_name}**: {details}
```

If no completeness issues exist, the section reads: `No mechanical completeness issues found.`

### `{review_feedback}`

Raw feedback text from Gemini review. If no review feedback exists (first iteration), the section reads: `No previous review feedback.`