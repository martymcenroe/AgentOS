```python
"""Generate implementation verification reports.

Issue #147: Implementation Completeness Gate (Anti-Stub Detection)
Related: #181 (Implementation Report)

Provides functions to:
- Generate implementation reports to docs/reports/active/{issue}-implementation-report.md
- Extract LLD requirements from Section 3
- Prepare review materials for Gemini semantic review (Layer 2)

Report generation is a side effect of the completeness gate — it does not
block the workflow. If report generation fails, the gate proceeds with
a warning logged.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import TypedDict

from assemblyzero.workflows.testing.completeness.ast_analyzer import (
    CompletenessCategory,
    CompletenessResult,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Data Structures
# =============================================================================


class RequirementVerification(TypedDict):
    """Single LLD requirement verification status."""

    requirement_id: int
    requirement_text: str
    status: str  # "IMPLEMENTED", "PARTIAL", "MISSING"
    evidence: str  # File:line or explanation


class ImplementationReport(TypedDict):
    """Full implementation verification report."""

    issue_number: int
    requirements: list[RequirementVerification]
    completeness_result: CompletenessResult
    generated_at: str  # ISO timestamp


class ReviewMaterials(TypedDict):
    """Materials prepared for Gemini semantic review."""

    lld_requirements: list[tuple[int, str]]  # (id, text) pairs
    code_snippets: dict[str, str]  # file_path -> relevant code
    issue_number: int


# =============================================================================
# Constants
# =============================================================================

REPORTS_ACTIVE_DIR = Path("docs/reports/active")

# Maximum source code size to include in review materials per file (bytes)
MAX_SNIPPET_SIZE = 50_000


# =============================================================================
# Requirement Extraction
# =============================================================================


def extract_lld_requirements(lld_path: Path) -> list[tuple[int, str]]:
    """Parse Section 3 requirements from LLD markdown.

    Issue #147, Requirement 10: Extracts numbered requirements from the
    LLD's Section 3 (Requirements) for verification against implementation.

    Expects requirements in the format:
        1. Requirement text here
        2. Another requirement
        ...

    within a section headed by "## 3. Requirements" (or similar).

    Args:
        lld_path: Path to the LLD markdown file.

    Returns:
        List of (requirement_id, requirement_text) tuples.
        Empty list if the file cannot be read or has no Section 3.
    """
    try:
        lld_content = lld_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        logger.warning("Cannot read LLD file %s: %s", lld_path, e)
        return []

    # Find Section 3 — match "## 3. Requirements" or "## 3 Requirements"
    # Also handles "## 3. Requirements\n" with trailing content
    section_pattern = re.compile(
        r"^##\s+3\.?\s+Requirements\s*$",
        re.MULTILINE | re.IGNORECASE,
    )
    match = section_pattern.search(lld_content)
    if not match:
        logger.warning("No Section 3 (Requirements) found in %s", lld_path)
        return []

    # Extract content from Section 3 until the next section (## N.)
    section_start = match.end()
    next_section = re.search(r"^##\s+\d+", lld_content[section_start:], re.MULTILINE)
    if next_section:
        section_text = lld_content[section_start : section_start + next_section.start()]
    else:
        section_text = lld_content[section_start:]

    # Parse numbered requirements: "1. Text here"
    req_pattern = re.compile(r"^\s*(\d+)\.\s+(.+?)$", re.MULTILINE)
    requirements: list[tuple[int, str]] = []

    for req_match in req_pattern.finditer(section_text):
        req_id = int(req_match.group(1))
        req_text = req_match.group(2).strip()
        if req_text:
            requirements.append((req_id, req_text))

    return requirements


# =============================================================================
# Requirement Verification
# =============================================================================


def _verify_requirements(
    requirements: list[tuple[int, str]],
    implementation_files: list[Path],
    completeness_result: CompletenessResult,
) -> list[RequirementVerification]:
    """Verify each LLD requirement against implementation files.

    Uses a simple heuristic: searches implementation file contents for
    keywords from each requirement. This is Layer 1 (mechanical) verification;
    Layer 2 (Gemini) provides deeper semantic analysis.

    Args:
        requirements: List of (id, text) requirement tuples.
        implementation_files: List of implementation file paths.
        completeness_result: AST analysis result for cross-referencing.

    Returns:
        List of RequirementVerification entries.
    """
    verifications: list[RequirementVerification] = []

    # Build a combined source index for keyword searching
    file_contents: dict[str, str] = {}
    for file_path in implementation_files:
        try:
            if file_path.exists() and file_path.suffix == ".py":
                content = file_path.read_text(encoding="utf-8")
                file_contents[str(file_path)] = content
        except (OSError, UnicodeDecodeError) as e:
            logger.warning("Cannot read implementation file %s: %s", file_path, e)

    for req_id, req_text in requirements:
        # Extract meaningful keywords from the requirement (3+ char words)
        words = re.findall(r"\b[a-zA-Z_]\w{2,}\b", req_text.lower())
        # Filter out common stop words
        stop_words = {
            "the", "and", "for", "from", "with", "that", "this", "are",
            "has", "have", "been", "into", "not", "but", "its", "was",
            "will", "can", "all", "each", "any", "when", "should",
        }
        keywords = [w for w in words if w not in stop_words]

        evidence_files: list[str] = []
        for fpath, content in file_contents.items():
            content_lower = content.lower()
            matched = sum(1 for kw in keywords if kw in content_lower)
            if keywords and matched >= max(1, len(keywords) // 3):
                evidence_files.append(fpath)

        if evidence_files:
            evidence = ", ".join(
                str(Path(f).name) for f in evidence_files[:3]
            )
            status = "IMPLEMENTED"
        else:
            evidence = "No matching implementation files found"
            status = "MISSING"

        verifications.append(
            RequirementVerification(
                requirement_id=req_id,
                requirement_text=req_text,
                status=status,
                evidence=evidence,
            )
        )

    return verifications


# =============================================================================
# Report Generation
# =============================================================================


def generate_implementation_report(
    issue_number: int,
    lld_path: Path,
    implementation_files: list[Path],
    completeness_result: CompletenessResult,
    repo_root: Path | None = None,
) -> Path:
    """Generate implementation report to docs/reports/active/{issue}-implementation-report.md.

    Issue #147, Requirement 9: Creates a markdown report containing:
    - LLD requirement verification table (Requirement 10)
    - Completeness analysis summary (Requirement 11)
    - List of implementation files analyzed

    The report is a side effect of the completeness gate. If generation
    fails, the error is logged and the function raises the exception
    for the caller to handle gracefully.

    Args:
        issue_number: GitHub issue number.
        lld_path: Path to the LLD markdown file.
        implementation_files: List of implementation file paths analyzed.
        completeness_result: Result from AST analysis (Layer 1).
        repo_root: Repository root path. If None, derived from lld_path.

    Returns:
        Path to the generated report file.
    """
    # Determine repo root
    if repo_root is None:
        # Walk up from lld_path to find a directory containing docs/
        repo_root = _find_repo_root(lld_path)

    reports_dir = repo_root / REPORTS_ACTIVE_DIR
    reports_dir.mkdir(parents=True, exist_ok=True)

    report_path = reports_dir / f"{issue_number}-implementation-report.md"

    # Extract and verify requirements
    requirements = extract_lld_requirements(lld_path)
    verifications = _verify_requirements(
        requirements, implementation_files, completeness_result
    )

    # Build report content
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    report = _format_report(
        issue_number=issue_number,
        lld_path=lld_path,
        implementation_files=implementation_files,
        completeness_result=completeness_result,
        verifications=verifications,
        generated_at=now,
    )

    report_path.write_text(report, encoding="utf-8")
    logger.info(
        "Implementation report generated: %s (%d requirements verified)",
        report_path,
        len(verifications),
    )

    return report_path


def _find_repo_root(start_path: Path) -> Path:
    """Walk up from start_path to find the repository root.

    Looks for a directory containing pyproject.toml or .git as indicators.

    Args:
        start_path: Path to start searching from.

    Returns:
        Repository root path, or start_path.parent if not found.
    """
    current = start_path if start_path.is_dir() else start_path.parent
    for _ in range(10):  # Safety limit on traversal depth
        if (current / "pyproject.toml").exists() or (current / ".git").exists():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent

    logger.warning(
        "Could not find repo root from %s, using parent directory", start_path
    )
    return start_path.parent


def _format_report(
    *,
    issue_number: int,
    lld_path: Path,
    implementation_files: list[Path],
    completeness_result: CompletenessResult,
    verifications: list[RequirementVerification],
    generated_at: str,
) -> str:
    """Format the implementation report as markdown.

    Args:
        issue_number: GitHub issue number.
        lld_path: Path to the LLD file.
        implementation_files: Files analyzed.
        completeness_result: AST analysis result.
        verifications: Requirement verification results.
        generated_at: ISO timestamp string.

    Returns:
        Formatted markdown string.
    """
    verdict = completeness_result["verdict"]
    issues = completeness_result["issues"]
    ast_ms = completeness_result["ast_analysis_ms"]

    # Header
    lines = [
        f"# Implementation Report: Issue #{issue_number}",
        "",
        f"**Generated:** {generated_at}",
        f"**LLD:** `{lld_path}`",
        f"**Verdict:** {verdict}",
        "",
    ]

    # Requirement Verification Table
    lines.append("## Requirement Verification")
    lines.append("")

    if verifications:
        lines.append(
            "| # | Requirement | Status | Evidence |"
        )
        lines.append(
            "|---|-------------|--------|----------|"
        )
        for v in verifications:
            status_icon = _status_icon(v["status"])
            # Escape pipe characters in text
            req_text = v["requirement_text"].replace("|", "\\|")
            evidence = v["evidence"].replace("|", "\\|")
            lines.append(
                f"| {v['requirement_id']} "
                f"| {req_text} "
                f"| {status_icon} {v['status']} "
                f"| {evidence} |"
            )
        lines.append("")

        # Summary counts
        implemented = sum(
            1 for v in verifications if v["status"] == "IMPLEMENTED"
        )
        partial = sum(1 for v in verifications if v["status"] == "PARTIAL")
        missing = sum(1 for v in verifications if v["status"] == "MISSING")
        total = len(verifications)
        lines.append(
            f"**Coverage:** {implemented}/{total} implemented, "
            f"{partial} partial, {missing} missing"
        )
        lines.append("")
    else:
        lines.append("*No requirements found in LLD Section 3.*")
        lines.append("")

    # Completeness Analysis Summary
    lines.append("## Completeness Analysis")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Verdict | **{verdict}** |")
    lines.append(f"| Issues Found | {len(issues)} |")
    lines.append(f"| AST Analysis Time | {ast_ms}ms |")

    error_count = sum(1 for i in issues if i["severity"] == "ERROR")
    warn_count = sum(1 for i in issues if i["severity"] == "WARNING")
    lines.append(f"| Errors | {error_count} |")
    lines.append(f"| Warnings | {warn_count} |")
    lines.append("")

    # Issues detail table
    if issues:
        lines.append("### Issues Detected")
        lines.append("")
        lines.append("| Severity | Category | File | Line | Description |")
        lines.append("|----------|----------|------|------|-------------|")
        for issue in issues:
            category = issue["category"]
            # Handle both enum and string values
            cat_value = (
                category.value
                if isinstance(category, CompletenessCategory)
                else str(category)
            )
            file_name = Path(issue["file_path"]).name
            desc = issue["description"].replace("|", "\\|")
            lines.append(
                f"| {issue['severity']} "
                f"| {cat_value} "
                f"| `{file_name}` "
                f"| {issue['line_number']} "
                f"| {desc} |"
            )
        lines.append("")

    # Implementation Files
    lines.append("## Files Analyzed")
    lines.append("")
    if implementation_files:
        for f in implementation_files:
            lines.append(f"- `{f}`")
    else:
        lines.append("*No implementation files provided.*")
    lines.append("")

    # Footer
    lines.append("---")
    lines.append("")
    lines.append("Generated by AssemblyZero Completeness Gate (Issue #147)")
    lines.append("")

    return "\n".join(lines)


def _status_icon(status: str) -> str:
    """Return a text icon for requirement verification status.

    Args:
        status: One of IMPLEMENTED, PARTIAL, MISSING.

    Returns:
        Text icon string.
    """
    icons = {
        "IMPLEMENTED": "[PASS]",
        "PARTIAL": "[WARN]",
        "MISSING": "[MISS]",
    }
    return icons.get(status, "[????]")


# =============================================================================
# Review Materials Preparation (Layer 2)
# =============================================================================


def prepare_review_materials(
    issue_number: int,
    lld_path: Path,
    implementation_files: list[Path],
) -> ReviewMaterials:
    """Prepare materials for Gemini semantic review submission by orchestrator.

    Issue #147, Requirement 13: Collects LLD requirements and relevant
    code snippets into a structured format that the orchestrator can
    submit to Gemini for Layer 2 semantic review.

    The orchestrator (not this function) is responsible for the actual
    Gemini API call, per WORKFLOW.md architectural constraints.

    Args:
        issue_number: GitHub issue number.
        lld_path: Path to the LLD markdown file.
        implementation_files: List of implementation file paths.

    Returns:
        ReviewMaterials with requirements and code snippets.
    """
    # Extract requirements from LLD
    lld_requirements = extract_lld_requirements(lld_path)

    # Collect code snippets from implementation files
    code_snippets: dict[str, str] = {}
    for file_path in implementation_files:
        if not file_path.exists():
            logger.warning(
                "Implementation file does not exist: %s", file_path
            )
            continue

        if file_path.suffix != ".py":
            continue

        try:
            content = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            logger.warning("Cannot read file %s: %s", file_path, e)
            continue

        # Truncate large files to prevent excessive token usage
        if len(content) > MAX_SNIPPET_SIZE:
            content = content[:MAX_SNIPPET_SIZE] + "\n# ... (truncated)\n"
            logger.warning(
                "Truncated file %s to %d bytes for review materials",
                file_path,
                MAX_SNIPPET_SIZE,
            )

        code_snippets[str(file_path)] = content

    return ReviewMaterials(
        lld_requirements=lld_requirements,
        code_snippets=code_snippets,
        issue_number=issue_number,
    )
```
