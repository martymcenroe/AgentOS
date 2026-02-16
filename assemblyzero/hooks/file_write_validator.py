"""Pre-write validation hook for LLD path enforcement.

Issue #188: Validates that file writes target paths specified in the LLD.
Rejects writes to non-LLD paths with helpful error messages including
the closest matching LLD path suggestion.
"""

from difflib import SequenceMatcher
from pathlib import PurePosixPath
from typing import TypedDict


class PathValidationResult(TypedDict):
    """Result of validating a file write path."""

    allowed: bool
    requested_path: str
    closest_match: str | None
    reason: str


def validate_file_write(
    requested_path: str,
    allowed_paths: set[str],
    strict: bool = True,
) -> PathValidationResult:
    """Validate a file write request against LLD-specified paths.

    Args:
        requested_path: The path being written to.
        allowed_paths: Set of LLD-allowed paths.
        strict: If True, reject non-LLD paths. If False, warn only.

    Returns:
        PathValidationResult with allow/reject decision.
    """
    normalized = _normalize_path(requested_path)

    # Check for path traversal
    if _is_path_traversal(normalized):
        return {
            "allowed": False,
            "requested_path": requested_path,
            "closest_match": None,
            "reason": f"Rejected: path traversal attempt detected in '{requested_path}'",
        }

    # Exact match
    if normalized in allowed_paths:
        return {
            "allowed": True,
            "requested_path": requested_path,
            "closest_match": None,
            "reason": "Path matches LLD specification",
        }

    # Normalized match (try with/without leading components)
    for allowed in allowed_paths:
        if _paths_equivalent(normalized, allowed):
            return {
                "allowed": True,
                "requested_path": requested_path,
                "closest_match": allowed,
                "reason": f"Path matches LLD specification (normalized from '{allowed}')",
            }

    # Not allowed
    closest = find_closest_lld_path(normalized, allowed_paths)
    suggestion = f" Did you mean '{closest}'?" if closest else ""

    return {
        "allowed": False,
        "requested_path": requested_path,
        "closest_match": closest,
        "reason": f"Rejected: '{requested_path}' not in LLD-specified paths.{suggestion}",
    }


def find_closest_lld_path(
    requested_path: str, allowed_paths: set[str]
) -> str | None:
    """Find the most similar allowed path using sequence matching.

    Args:
        requested_path: The rejected path.
        allowed_paths: Set of allowed LLD paths.

    Returns:
        Most similar path, or None if no paths are close enough.
    """
    if not allowed_paths:
        return None

    best_match = None
    best_ratio = 0.0

    for allowed in allowed_paths:
        ratio = SequenceMatcher(None, requested_path, allowed).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_match = allowed

    # Only suggest if similarity is reasonable (> 40%)
    if best_ratio > 0.4:
        return best_match
    return None


def _normalize_path(path: str) -> str:
    """Normalize a file path for comparison."""
    if not path:
        return ""
    normalized = str(PurePosixPath(path))
    if normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def _paths_equivalent(path1: str, path2: str) -> bool:
    """Check if two paths refer to the same file after normalization."""
    return _normalize_path(path1) == _normalize_path(path2)


def _is_path_traversal(path: str) -> bool:
    """Check if a path contains directory traversal attempts."""
    return ".." in PurePosixPath(path).parts
