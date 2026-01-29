"""Audit trail utilities for LLD Governance workflow.

Issue #86: LLD Creation & Governance Review Workflow
LLD: docs/LLDs/active/LLD-086-lld-governance-workflow.md

Provides functions for:
- Sequential file numbering (001, 002, 003...)
- Saving audit files (issue, draft, verdict, approved.json)
- LLD output to docs/LLDs/active/
"""

import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import TypedDict


class ApprovedMetadata(TypedDict):
    """Schema for approved.json metadata file."""

    issue_number: int
    issue_title: str
    approved_at: str  # ISO8601
    final_lld_path: str
    total_iterations: int
    draft_count: int
    verdict_count: int


# Base directories relative to repo root
AUDIT_ACTIVE_DIR = Path("docs/audit/active")
LLD_ACTIVE_DIR = Path("docs/LLDs/active")


def get_repo_root() -> Path:
    """Detect repository root via git rev-parse.

    Returns:
        Path to repository root.

    Raises:
        RuntimeError: If not in a git repository.
    """
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Not in a git repository: {result.stderr.strip()}")
    return Path(result.stdout.strip())


def create_lld_audit_dir(issue_number: int, repo_root: Path | None = None) -> Path:
    """Create audit directory for this LLD workflow.

    Args:
        issue_number: GitHub issue number.
        repo_root: Repository root path. Auto-detected if None.

    Returns:
        Path to created directory (docs/audit/active/{issue_number}-lld/).
    """
    root = repo_root or get_repo_root()
    audit_dir = root / AUDIT_ACTIVE_DIR / f"{issue_number}-lld"

    audit_dir.mkdir(parents=True, exist_ok=True)
    return audit_dir


def next_file_number(audit_dir: Path) -> int:
    """Get next sequential file number.

    Scans audit_dir for NNN-*.* files and returns max + 1.

    Args:
        audit_dir: Path to the audit directory.

    Returns:
        Next file number (starts at 1 if directory is empty).
    """
    if not audit_dir.exists():
        return 1

    max_num = 0
    for f in audit_dir.iterdir():
        if f.is_file():
            match = re.match(r"^(\d{3})-", f.name)
            if match:
                num = int(match.group(1))
                max_num = max(max_num, num)

    return max_num + 1


def save_audit_file(
    audit_dir: Path,
    number: int,
    suffix: str,
    content: str,
) -> Path:
    """Save an audit file with sequential numbering.

    Args:
        audit_dir: Path to the audit directory.
        number: File number (1-999).
        suffix: File suffix (e.g., "issue.md", "draft.md", "verdict.md").
        content: File content.

    Returns:
        Path to the saved file.
    """
    filename = f"{number:03d}-{suffix}"
    file_path = audit_dir / filename
    file_path.write_text(content, encoding="utf-8")
    return file_path


def save_approved_metadata(
    audit_dir: Path,
    number: int,
    issue_number: int,
    issue_title: str,
    final_lld_path: str,
    total_iterations: int,
    draft_count: int,
    verdict_count: int,
) -> Path:
    """Save approved.json metadata file.

    Args:
        audit_dir: Path to the audit directory.
        number: File number.
        issue_number: GitHub issue number.
        issue_title: Issue title.
        final_lld_path: Path to final LLD in docs/LLDs/active/.
        total_iterations: Total loop iterations.
        draft_count: Number of drafts generated.
        verdict_count: Number of verdicts received.

    Returns:
        Path to the saved approved.json file.
    """
    metadata: ApprovedMetadata = {
        "issue_number": issue_number,
        "issue_title": issue_title,
        "approved_at": datetime.now(timezone.utc).isoformat(),
        "final_lld_path": final_lld_path,
        "total_iterations": total_iterations,
        "draft_count": draft_count,
        "verdict_count": verdict_count,
    }

    filename = f"{number:03d}-approved.json"
    file_path = audit_dir / filename
    file_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return file_path


def save_final_lld(
    issue_number: int,
    lld_content: str,
    repo_root: Path | None = None,
) -> Path:
    """Save approved LLD to docs/LLDs/active/.

    Args:
        issue_number: GitHub issue number.
        lld_content: Final LLD content.
        repo_root: Repository root path. Auto-detected if None.

    Returns:
        Path to saved LLD file.
    """
    root = repo_root or get_repo_root()
    lld_dir = root / LLD_ACTIVE_DIR
    lld_dir.mkdir(parents=True, exist_ok=True)

    lld_path = lld_dir / f"LLD-{issue_number:03d}.md"
    lld_path.write_text(lld_content, encoding="utf-8")
    return lld_path


def validate_context_path(context_path: str, repo_root: Path | None = None) -> Path:
    """Validate and resolve a context file path.

    Security check per LLD Section 7: Reject paths outside project root.

    Args:
        context_path: User-provided path (may be relative or absolute).
        repo_root: Repository root path. Auto-detected if None.

    Returns:
        Resolved absolute Path if valid.

    Raises:
        ValueError: If path is outside project root or doesn't exist.
    """
    root = repo_root or get_repo_root()
    path = Path(context_path)

    # Resolve to absolute path
    if not path.is_absolute():
        path = (root / path).resolve()
    else:
        path = path.resolve()

    # Security check: must be under repo root
    try:
        path.relative_to(root)
    except ValueError:
        raise ValueError(
            f"Context path outside project root: {context_path}\n"
            f"All paths must be within: {root}"
        )

    # Existence check
    if not path.exists():
        raise ValueError(f"Context path does not exist: {context_path}")

    return path


def assemble_context(context_files: list[str], repo_root: Path | None = None) -> str:
    """Assemble context content from multiple files.

    Args:
        context_files: List of paths to context files.
        repo_root: Repository root path. Auto-detected if None.

    Returns:
        Assembled context as a single string with file headers.
    """
    if not context_files:
        return ""

    root = repo_root or get_repo_root()
    context_parts = []

    for ctx_path in context_files:
        try:
            path = validate_context_path(ctx_path, root)

            if path.is_file():
                content = path.read_text(encoding="utf-8", errors="replace")
                context_parts.append(
                    f"## Reference: {path.name}\n\n```\n{content}\n```"
                )
            elif path.is_dir():
                # Read all text files in directory
                for f in sorted(path.iterdir()):
                    if f.is_file() and f.suffix in (".md", ".py", ".json", ".yaml", ".txt"):
                        content = f.read_text(encoding="utf-8", errors="replace")
                        context_parts.append(
                            f"## Reference: {f.name}\n\n```\n{content}\n```"
                        )
        except ValueError as e:
            print(f"[WARN] Skipping context: {e}")
            continue

    return "\n\n".join(context_parts)
