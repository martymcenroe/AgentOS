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


# =============================================================================
# Constants
# =============================================================================

# Template path relative to assemblyzero_root
SPEC_TEMPLATE_PATH = Path("docs/standards/0701-implementation-spec-template.md")

# Default drafter model spec
DEFAULT_DRAFTER = "claude:opus-4.5"

# Maximum characters for pattern reference excerpts in the prompt
MAX_PATTERN_EXCERPT_CHARS = 3_000

# Maximum characters for a single file snapshot in the prompt
MAX_SNAPSHOT_CHARS = 10_000

# Maximum total prompt content chars (to avoid token limits)
MAX_TOTAL_PROMPT_CHARS = 120_000


# =============================================================================
# System Prompt
# =============================================================================

DRAFTER_SYSTEM_PROMPT = """\
You are a technical architect creating an Implementation Specification.

An Implementation Spec bridges the gap between a Low-Level Design (LLD) and \
autonomous code implementation. It must contain enough concrete detail for an \
AI agent to implement the changes with >80% first-try success rate.

CRITICAL FORMATTING RULES:
- Start DIRECTLY with the document title (# heading)
- Do NOT include any preamble, explanation, or meta-commentary
- Output ONLY the raw markdown content
- First line MUST be the title starting with #

QUALITY REQUIREMENTS:
- Every "Modify" file MUST include a current state excerpt showing the code \
that will be changed
- Every data structure MUST have at least one concrete JSON/YAML example \
with realistic values (not just TypedDict definitions)
- Every function signature MUST have input/output examples with actual values
- Change instructions MUST be specific enough to generate diffs \
(line-level guidance, before/after snippets)
- Pattern references MUST include file:line locations pointing to real code

STRUCTURE:
Follow the provided template exactly. Include ALL sections. \
Do not skip or abbreviate any section."""


# =============================================================================
# Main Node
# =============================================================================


async def generate_spec(state: ImplementationSpecState) -> dict[str, Any]:
    """N2: Generate Implementation Spec draft using Claude.

    Issue #304: Implementation Readiness Review Workflow

    Steps:
    1. Determine if this is an initial draft or revision
    2. Load Implementation Spec template from assemblyzero_root
    3. Build prompt with LLD content, codebase snapshots, and patterns
    4. Call configured drafter LLM
    5. Strip any preamble from response
    6. Save draft to audit trail
    7. Return state updates

    Args:
        state: Current workflow state. Requires:
            - lld_content: Raw LLD markdown (from N0)
            - current_state_snapshots: File excerpts (from N1)
            - pattern_references: Similar patterns (from N1)
            - assemblyzero_root: Path to AssemblyZero installation
            - repo_root: Target repository root path

    Returns:
        Dict with state field updates:
        - spec_draft: Generated Implementation Spec markdown
        - spec_path: Path where the draft was saved
        - review_iteration: Updated iteration count
        - error_message: "" on success, error text on failure
    """
    # Extract state
    assemblyzero_root = Path(state.get("assemblyzero_root", ""))
    repo_root = state.get("repo_root", "")
    mock_mode = state.get("config_mock_mode", False)
    issue_number = state.get("issue_number", 0)

    # Determine revision state
    review_iteration = state.get("review_iteration", 0)
    existing_draft = state.get("spec_draft", "")
    review_feedback = state.get("review_feedback", "")
    completeness_issues = state.get("completeness_issues", [])
    validation_passed = state.get("validation_passed", False)

    is_revision = bool(
        existing_draft and (review_feedback or completeness_issues)
    )

    if is_revision:
        review_iteration += 1
        print(
            f"\n[N2] Generating Implementation Spec revision "
            f"(iteration {review_iteration})..."
        )
    else:
        print("\n[N2] Generating initial Implementation Spec draft...")

    # -------------------------------------------------------------------------
    # Load template
    # -------------------------------------------------------------------------
    try:
        template = load_template(SPEC_TEMPLATE_PATH, assemblyzero_root)
    except FileNotFoundError as e:
        print(f"    ERROR: Template not found: {e}")
        return {"error_message": str(e)}

    # -------------------------------------------------------------------------
    # Build prompt
    # -------------------------------------------------------------------------
    prompt = build_drafter_prompt(
        lld_content=state.get("lld_content", ""),
        current_state=state.get("current_state_snapshots", {}),
        patterns=state.get("pattern_references", []),
        template=template,
        issue_number=issue_number,
        existing_draft=existing_draft if is_revision else "",
        review_feedback=review_feedback if is_revision else "",
        completeness_issues=completeness_issues if is_revision else [],
        repo_root=repo_root,
        files_to_modify=state.get("files_to_modify", []),
    )

    # -------------------------------------------------------------------------
    # Get drafter provider
    # -------------------------------------------------------------------------
    if mock_mode:
        drafter_spec = "mock:draft"
    else:
        drafter_spec = state.get("config_drafter", DEFAULT_DRAFTER)

    try:
        drafter = get_provider(drafter_spec)
    except ValueError as e:
        print(f"    ERROR: Invalid drafter: {e}")
        return {"error_message": f"Invalid drafter: {e}"}

    print(f"    Drafter: {drafter_spec}")

    # -------------------------------------------------------------------------
    # Call drafter LLM
    # -------------------------------------------------------------------------
    result = drafter.invoke(
        system_prompt=DRAFTER_SYSTEM_PROMPT,
        content=prompt,
    )

    if not result.success:
        print(f"    ERROR: {result.error_message}")
        return {"error_message": f"Drafter failed: {result.error_message}"}

    spec_content = result.response or ""

    # -------------------------------------------------------------------------
    # Strip preamble (safety: Claude sometimes adds text before the # heading)
    # -------------------------------------------------------------------------
    spec_content = _strip_preamble(spec_content)

    # -------------------------------------------------------------------------
    # Save to audit trail
    # -------------------------------------------------------------------------
    audit_dir_str = state.get("audit_dir", "")
    audit_dir = Path(audit_dir_str) if audit_dir_str else None

    spec_path = None
    if audit_dir and audit_dir.exists():
        file_num = next_file_number(audit_dir)
        spec_path = save_audit_file(
            audit_dir, file_num, "spec-draft.md", spec_content
        )

    # -------------------------------------------------------------------------
    # Report results
    # -------------------------------------------------------------------------
    draft_lines = len(spec_content.splitlines()) if spec_content else 0
    print(f"    Generated {draft_lines} lines")
    if spec_path:
        print(f"    Saved: {spec_path.name}")

    return {
        "spec_draft": spec_content,
        "spec_path": str(spec_path) if spec_path else "",
        "review_iteration": review_iteration,
        "completeness_issues": [],  # Clear after use
        "review_feedback": "",  # Clear after use
        "error_message": "",
    }


# =============================================================================
# Prompt Building
# =============================================================================


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
    files_to_modify: list | None = None,
) -> str:
    """Build the prompt for Claude spec generation.

    Constructs either an initial draft prompt or a revision prompt
    depending on whether existing_draft and feedback are provided.

    The prompt includes:
    - Full LLD content
    - Current state snapshots for each file to be modified
    - Pattern references with code excerpts
    - Implementation Spec template (if available)
    - Revision feedback (if revising)

    Args:
        lld_content: Raw LLD markdown content.
        current_state: Mapping of file_path → code excerpt.
        patterns: List of PatternRef for similar implementation patterns.
        template: Implementation Spec template content.
        issue_number: GitHub issue number.
        existing_draft: Current spec draft (for revision mode).
        review_feedback: Feedback from Gemini review (for revision).
        completeness_issues: List of completeness check failures (for revision).
        repo_root: Target repository root path (for repo structure display).
        files_to_modify: List of FileToModify dicts from the LLD.

    Returns:
        Complete prompt string for the drafter LLM.
    """
    if completeness_issues is None:
        completeness_issues = []
    if files_to_modify is None:
        files_to_modify = []

    is_revision = bool(existing_draft and (review_feedback or completeness_issues))

    if is_revision:
        return _build_revision_prompt(
            lld_content=lld_content,
            current_state=current_state,
            patterns=patterns,
            template=template,
            issue_number=issue_number,
            existing_draft=existing_draft,
            review_feedback=review_feedback,
            completeness_issues=completeness_issues,
            repo_root=repo_root,
            files_to_modify=files_to_modify,
        )
    else:
        return _build_initial_prompt(
            lld_content=lld_content,
            current_state=current_state,
            patterns=patterns,
            template=template,
            issue_number=issue_number,
            files_to_modify=files_to_modify,
        )


# =============================================================================
# Initial Prompt
# =============================================================================


def _build_initial_prompt(
    lld_content: str,
    current_state: dict[str, str],
    patterns: list[PatternRef],
    template: str,
    issue_number: int,
    files_to_modify: list,
) -> str:
    """Build prompt for initial spec generation.

    Args:
        lld_content: Raw LLD markdown content.
        current_state: File path → code excerpt mapping.
        patterns: Pattern references from codebase analysis.
        template: Implementation Spec template.
        issue_number: GitHub issue number.
        files_to_modify: List of FileToModify dicts.

    Returns:
        Initial draft prompt string.
    """
    sections: list[str] = []

    sections.append(
        "IMPORTANT: Output ONLY the markdown content. "
        "Start with # title. No preamble."
    )

    # LLD content
    sections.append(f"## LLD Content (Issue #{issue_number})\n\n{lld_content}")

    # Current state snapshots
    snapshot_section = _format_current_state_section(current_state, files_to_modify)
    if snapshot_section:
        sections.append(snapshot_section)

    # Pattern references
    pattern_section = _format_patterns_section(patterns)
    if pattern_section:
        sections.append(pattern_section)

    # Template
    if template:
        sections.append(f"## Implementation Spec Template (follow this structure)\n\n{template}")

    # Final instruction
    sections.append(
        "Create a complete Implementation Spec following the template structure.\n"
        "Ensure EVERY file listed in the LLD has concrete implementation guidance.\n"
        f"This spec is for Issue #{issue_number}.\n"
        "START YOUR RESPONSE WITH THE # HEADING. NO PREAMBLE."
    )

    prompt = "\n\n".join(sections)

    # Guard against excessively large prompts
    if len(prompt) > MAX_TOTAL_PROMPT_CHARS:
        prompt = _truncate_prompt(prompt)

    return prompt


# =============================================================================
# Revision Prompt
# =============================================================================


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
    files_to_modify: list,
) -> str:
    """Build prompt for spec revision based on feedback.

    Args:
        lld_content: Raw LLD markdown content.
        current_state: File path → code excerpt mapping.
        patterns: Pattern references from codebase analysis.
        template: Implementation Spec template.
        issue_number: GitHub issue number.
        existing_draft: Current spec draft to revise.
        review_feedback: Gemini review feedback.
        completeness_issues: Completeness check failures.
        repo_root: Target repo root (for structure display).
        files_to_modify: List of FileToModify dicts.

    Returns:
        Revision prompt string.
    """
    sections: list[str] = []

    sections.append(
        "IMPORTANT: Output ONLY the markdown content. "
        "Start with # title. No preamble."
    )

    # Completeness issues (highest priority — from N3 mechanical validation)
    if completeness_issues:
        issues_text = "## MECHANICAL COMPLETENESS ERRORS (MUST FIX FIRST)\n\n"
        issues_text += (
            "The following errors were found by automated completeness "
            "validation. These MUST be fixed before the spec can proceed:\n\n"
        )
        for issue in completeness_issues:
            issues_text += f"- **ERROR:** {issue}\n"

        # Show repo structure to help fix path-related issues
        if repo_root:
            repo_structure = get_repo_structure(repo_root)
            issues_text += "\n## ACTUAL REPOSITORY STRUCTURE\n\n"
            issues_text += (
                "**Use ONLY these existing directories** "
                "(or explicitly document new ones):\n\n"
            )
            issues_text += f"```\n{repo_structure}\n```\n"

        sections.append(issues_text)

    # Review feedback (from N5 Gemini review)
    if review_feedback:
        sections.append(
            "## Gemini Readiness Review Feedback\n\n"
            f"{review_feedback}"
        )

    # Current draft to revise
    sections.append(f"## Current Draft (to revise)\n\n{existing_draft}")

    # Current state snapshots (for reference during revision)
    snapshot_section = _format_current_state_section(current_state, files_to_modify)
    if snapshot_section:
        sections.append(snapshot_section)

    # Original LLD for reference
    sections.append(f"## Original LLD (Issue #{issue_number})\n\n{lld_content}")

    # Template
    if template:
        sections.append(
            f"## Implementation Spec Template (REQUIRED STRUCTURE)\n\n{template}"
        )

    # Revision instructions
    sections.append(
        "CRITICAL REVISION INSTRUCTIONS:\n"
        "1. Fix ALL mechanical completeness errors FIRST "
        "(missing excerpts, missing examples)\n"
        "2. Implement EVERY change requested by Gemini review feedback\n"
        "3. PRESERVE sections that weren't flagged\n"
        "4. ONLY modify sections that need changes\n"
        "5. Keep ALL template sections intact\n"
        "6. Ensure every Modify file has a current state excerpt\n"
        "7. Ensure every function has concrete input/output examples\n"
        "8. Ensure every data structure has a concrete JSON/YAML example\n\n"
        "Revise the draft to address ALL feedback above.\n"
        "START YOUR RESPONSE WITH THE # HEADING. NO PREAMBLE."
    )

    prompt = "\n\n".join(sections)

    # Guard against excessively large prompts
    if len(prompt) > MAX_TOTAL_PROMPT_CHARS:
        prompt = _truncate_prompt(prompt)

    return prompt


# =============================================================================
# Prompt Section Formatters
# =============================================================================


def _format_current_state_section(
    current_state: dict[str, str],
    files_to_modify: list,
) -> str:
    """Format current state snapshots into a prompt section.

    Args:
        current_state: File path → code excerpt mapping.
        files_to_modify: List of FileToModify dicts for metadata.

    Returns:
        Formatted section string, or empty string if no snapshots.
    """
    if not current_state:
        return ""

    parts: list[str] = ["## Current State of Files to Modify\n"]

    # Build a lookup for change types
    change_types: dict[str, str] = {}
    descriptions: dict[str, str] = {}
    for f in files_to_modify:
        path = f.get("path", "") if isinstance(f, dict) else ""
        change_types[path] = f.get("change_type", "Modify") if isinstance(f, dict) else "Modify"
        descriptions[path] = f.get("description", "") if isinstance(f, dict) else ""

    for file_path, excerpt in current_state.items():
        change_type = change_types.get(file_path, "Modify")
        description = descriptions.get(file_path, "")

        # Truncate very large excerpts
        if len(excerpt) > MAX_SNAPSHOT_CHARS:
            excerpt = excerpt[:MAX_SNAPSHOT_CHARS] + "\n# ... (truncated)\n"

        header = f"### `{file_path}` ({change_type})"
        if description:
            header += f"\n*{description}*"

        parts.append(f"{header}\n\n```python\n{excerpt}\n```")

    return "\n\n".join(parts)


def _format_patterns_section(patterns: list[PatternRef]) -> str:
    """Format pattern references into a prompt section.

    Args:
        patterns: List of PatternRef dicts from codebase analysis.

    Returns:
        Formatted section string, or empty string if no patterns.
    """
    if not patterns:
        return ""

    parts: list[str] = [
        "## Similar Implementation Patterns\n\n"
        "Use these existing patterns as reference for consistent implementation style:"
    ]

    for ref in patterns:
        file_path = ref.get("file_path", "")
        start_line = ref.get("start_line", 0)
        end_line = ref.get("end_line", 0)
        pattern_type = ref.get("pattern_type", "")
        relevance = ref.get("relevance", "")

        parts.append(
            f"- **{pattern_type}** at `{file_path}:{start_line}-{end_line}`"
            f"\n  {relevance}"
        )

    return "\n".join(parts)


# =============================================================================
# Utility Functions
# =============================================================================


def _strip_preamble(content: str) -> str:
    """Strip any preamble text before the first # heading.

    Claude sometimes adds explanatory text before the actual spec content
    despite system prompt instructions. This strips it.

    Args:
        content: Raw LLM response content.

    Returns:
        Content starting from the first # heading.
    """
    if not content:
        return content

    match = re.search(r"^#\s+", content, re.MULTILINE)
    if match:
        heading_pos = match.start()
        if heading_pos > 0:
            stripped = content[:heading_pos].strip()
            if stripped:
                print(
                    f"    [WARN] Stripped {len(stripped)} chars of preamble "
                    f"before # heading"
                )
            return content[heading_pos:]

    return content


def _truncate_prompt(prompt: str) -> str:
    """Truncate prompt to stay within token limits.

    Preserves the beginning (instructions, feedback) and end (template,
    final instructions) while trimming the middle (file excerpts).

    Args:
        prompt: Full prompt content.

    Returns:
        Truncated prompt.
    """
    if len(prompt) <= MAX_TOTAL_PROMPT_CHARS:
        return prompt

    # Keep first 40% and last 30%, truncate middle
    keep_start = int(MAX_TOTAL_PROMPT_CHARS * 0.4)
    keep_end = int(MAX_TOTAL_PROMPT_CHARS * 0.3)

    start = prompt[:keep_start]
    end = prompt[-keep_end:]

    truncation_notice = (
        "\n\n<!-- CONTEXT TRUNCATED: Prompt exceeded size limit. "
        "Some file excerpts were removed. -->\n\n"
    )

    print(
        f"    [WARN] Prompt truncated from {len(prompt):,} to "
        f"~{MAX_TOTAL_PROMPT_CHARS:,} chars"
    )

    return start + truncation_notice + end
```
