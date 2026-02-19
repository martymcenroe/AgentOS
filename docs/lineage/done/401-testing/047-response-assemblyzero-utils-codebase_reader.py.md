```python
"""Shared utility for reading and summarizing codebase files with token-budget awareness.

Issue #401: Codebase Context Analysis for Requirements Workflow.

Provides functions for safely reading repository files while respecting
token budgets, detecting sensitive files, and parsing project metadata.
All functions are designed to fail gracefully — no exceptions propagate
to callers.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TypedDict

try:
    import tomllib
except ImportError:  # Python < 3.11
    tomllib = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)

# Patterns for files that must never be read (Issue #401, Section 7.1).
SENSITIVE_PATTERNS: list[str] = [
    ".env",
    ".secrets",
    ".key",
    ".pem",
    "credentials",
]


class FileReadResult(TypedDict):
    """Result of reading a single file with budget tracking."""

    path: str  # Relative file path
    content: str  # File content (possibly truncated)
    truncated: bool  # Whether content was truncated
    token_estimate: int  # Approximate token count


def _estimate_tokens(text: str) -> int:
    """Approximate token count using chars / 4 heuristic.

    Args:
        text: The text to estimate tokens for.

    Returns:
        Estimated number of tokens (minimum 0).
    """
    return max(0, len(text) // 4)


def is_sensitive_file(file_path: Path) -> bool:
    """Check if a file path matches any sensitive pattern.

    Checks the filename and all parent directory names against
    ``SENSITIVE_PATTERNS``.  Matching is case-insensitive and uses
    substring containment for directory names and suffix/full-name
    matching for files.

    Args:
        file_path: Path to check (absolute or relative).

    Returns:
        True if the file matches a sensitive pattern.
    """
    # Check the filename itself
    name_lower = file_path.name.lower()
    for pattern in SENSITIVE_PATTERNS:
        pattern_lower = pattern.lower()
        # Match exact name, suffix, or if the pattern is contained in the name
        if (
            name_lower == pattern_lower
            or name_lower.endswith(pattern_lower)
            or pattern_lower in name_lower
        ):
            return True

    # Check all parent directory names
    for part in file_path.parts[:-1]:  # Exclude the filename itself
        part_lower = part.lower()
        for pattern in SENSITIVE_PATTERNS:
            pattern_lower = pattern.lower()
            if pattern_lower in part_lower:
                return True

    return False


def read_file_with_budget(
    file_path: Path,
    max_tokens: int = 2000,
    encoding: str = "utf-8",
    repo_root: Path | None = None,
) -> FileReadResult:
    """Read a file's content, truncating if it exceeds the token budget.

    Uses approximate token counting (chars / 4).

    Returns ``FileReadResult`` with empty content and ``token_estimate=0``
    if the file is binary, missing, unreadable, or matches
    ``SENSITIVE_PATTERNS``.

    If *repo_root* is provided, symlinks are resolved and the resolved path
    must be within the *repo_root* boundary.  Paths escaping the boundary
    are treated as unreadable.

    Args:
        file_path: Absolute path to the file to read.
        max_tokens: Maximum token budget for this file.
        encoding: Text encoding to use (default utf-8).
        repo_root: Optional repository root for symlink boundary checks.

    Returns:
        A ``FileReadResult`` dict.  Never raises.
    """
    empty_result: FileReadResult = {
        "path": str(file_path),
        "content": "",
        "truncated": False,
        "token_estimate": 0,
    }

    # Sensitive file check
    if is_sensitive_file(file_path):
        logger.debug("Skipping sensitive file: %s", file_path)
        return empty_result

    # Existence check
    if not file_path.exists():
        logger.debug("File does not exist: %s", file_path)
        return empty_result

    # Symlink boundary check
    if repo_root is not None:
        try:
            resolved = file_path.resolve()
            resolved_root = repo_root.resolve()
            resolved.relative_to(resolved_root)
        except (ValueError, OSError):
            logger.warning(
                "File %s resolves outside repo boundary %s, skipping",
                file_path,
                repo_root,
            )
            return empty_result

    # Read the file
    try:
        max_chars = max_tokens * 4
        # Read up to max_chars + 1 to detect truncation
        raw = file_path.read_text(encoding=encoding)
    except UnicodeDecodeError:
        logger.debug("Binary or non-%s file skipped: %s", encoding, file_path)
        return empty_result
    except OSError as exc:
        logger.warning("Could not read file %s: %s", file_path, exc)
        return empty_result

    # Truncate if needed
    truncated = False
    content = raw
    if len(raw) > max_chars:
        content = raw[:max_chars]
        truncated = True

    token_estimate = _estimate_tokens(content)

    return {
        "path": str(file_path),
        "content": content,
        "truncated": truncated,
        "token_estimate": token_estimate,
    }


def read_files_within_budget(
    file_paths: list[Path],
    total_budget: int = 15000,
    per_file_budget: int = 3000,
    repo_root: Path | None = None,
) -> list[FileReadResult]:
    """Read multiple files respecting per-file and total token budgets.

    Files are read in order; stops when total budget is exhausted.
    Skips files that match ``SENSITIVE_PATTERNS``.

    Args:
        file_paths: Ordered list of file paths to read.
        total_budget: Total token budget across all files.
        per_file_budget: Maximum token budget per individual file.
        repo_root: Optional repo root for symlink boundary checks.
            If ``None``, attempts to infer from the first file path's
            parents, but boundary checking is skipped.

    Returns:
        List of ``FileReadResult`` for files that were actually read
        (excluding skipped files).
    """
    results: list[FileReadResult] = []
    tokens_remaining = total_budget

    for fp in file_paths:
        if tokens_remaining <= 0:
            break

        # Skip sensitive files before attempting read
        if is_sensitive_file(fp):
            logger.debug("Skipping sensitive file in batch: %s", fp)
            continue

        # Determine per-file budget: min of per_file_budget and tokens_remaining
        effective_budget = min(per_file_budget, tokens_remaining)

        result = read_file_with_budget(
            fp,
            max_tokens=effective_budget,
            repo_root=repo_root,
        )

        # Only include files that produced content
        if result["content"]:
            results.append(result)
            tokens_remaining -= result["token_estimate"]

    return results


def parse_project_metadata(repo_path: Path) -> dict[str, str]:
    """Parse pyproject.toml or package.json to extract project metadata.

    Tries ``pyproject.toml`` first (using ``tomllib`` on Python 3.11+),
    falls back to ``package.json``.  Returns empty dict if neither
    exists or parsing fails.

    Args:
        repo_path: Absolute path to the repository root.

    Returns:
        Dict with keys ``name``, ``version``, ``description``,
        ``dependencies`` where ``dependencies`` is a comma-separated
        string of package names.  Missing keys are omitted.
    """
    result: dict[str, str] = {}

    # Try pyproject.toml first
    pyproject_path = repo_path / "pyproject.toml"
    if pyproject_path.is_file():
        parsed = _parse_pyproject_toml(pyproject_path)
        if parsed:
            return parsed

    # Fallback to package.json
    package_json_path = repo_path / "package.json"
    if package_json_path.is_file():
        parsed = _parse_package_json(package_json_path)
        if parsed:
            return parsed

    return result


def _parse_pyproject_toml(path: Path) -> dict[str, str]:
    """Parse a pyproject.toml file for project metadata.

    Args:
        path: Path to pyproject.toml.

    Returns:
        Metadata dict or empty dict on failure.
    """
    result: dict[str, str] = {}

    if tomllib is not None:
        try:
            with open(path, "rb") as f:
                data = tomllib.load(f)
            project = data.get("project", {})
            # Also check [tool.poetry] section as fallback
            poetry = data.get("tool", {}).get("poetry", {})

            name = project.get("name") or poetry.get("name", "")
            if name:
                result["name"] = str(name)

            version = project.get("version") or poetry.get("version", "")
            if version:
                result["version"] = str(version)

            description = project.get("description") or poetry.get("description", "")
            if description:
                result["description"] = str(description)

            # Extract dependency names
            deps: list[str] = []

            # From [project.dependencies] (PEP 621 format)
            project_deps = project.get("dependencies", [])
            if isinstance(project_deps, list):
                for dep in project_deps:
                    dep_name = _extract_dep_name(str(dep))
                    if dep_name:
                        deps.append(dep_name)

            # From [tool.poetry.dependencies]
            poetry_deps = poetry.get("dependencies", {})
            if isinstance(poetry_deps, dict):
                for dep_name in poetry_deps:
                    if dep_name.lower() != "python":
                        deps.append(dep_name)

            # From [dependency-groups]
            dep_groups = data.get("dependency-groups", {})
            if isinstance(dep_groups, dict):
                for _group_name, group_deps in dep_groups.items():
                    if isinstance(group_deps, list):
                        for dep in group_deps:
                            dep_name = _extract_dep_name(str(dep))
                            if dep_name:
                                deps.append(dep_name)

            if deps:
                # Deduplicate while preserving order
                seen: set[str] = set()
                unique_deps: list[str] = []
                for d in deps:
                    d_lower = d.lower()
                    if d_lower not in seen:
                        seen.add(d_lower)
                        unique_deps.append(d)
                result["dependencies"] = ", ".join(unique_deps)

            return result
        except Exception as exc:
            logger.warning("Failed to parse pyproject.toml with tomllib: %s", exc)
            # Fall through to regex-based parsing

    # Fallback: basic regex parsing for Python < 3.11
    return _parse_pyproject_toml_regex(path)


def _parse_pyproject_toml_regex(path: Path) -> dict[str, str]:
    """Regex-based fallback for parsing pyproject.toml on Python < 3.11.

    Args:
        path: Path to pyproject.toml.

    Returns:
        Metadata dict with whatever could be extracted.
    """
    import re

    result: dict[str, str] = {}

    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        logger.warning("Could not read pyproject.toml: %s", exc)
        return result

    # Extract name
    match = re.search(r'^name\s*=\s*"([^"]+)"', content, re.MULTILINE)
    if match:
        result["name"] = match.group(1)

    # Extract version
    match = re.search(r'^version\s*=\s*"([^"]+)"', content, re.MULTILINE)
    if match:
        result["version"] = match.group(1)

    # Extract description
    match = re.search(r'^description\s*=\s*"([^"]+)"', content, re.MULTILINE)
    if match:
        result["description"] = match.group(1)

    # Extract dependencies from dependencies = [...] block
    dep_match = re.search(
        r'^dependencies\s*=\s*\[(.*?)\]', content, re.MULTILINE | re.DOTALL
    )
    if dep_match:
        dep_block = dep_match.group(1)
        dep_names = []
        for dep_str in re.findall(r'"([^"]+)"', dep_block):
            dep_name = _extract_dep_name(dep_str)
            if dep_name:
                dep_names.append(dep_name)
        if dep_names:
            result["dependencies"] = ", ".join(dep_names)

    return result


def _extract_dep_name(dep_spec: str) -> str:
    """Extract the package name from a PEP 508 dependency specifier.

    Examples::

        "requests>=2.0" -> "requests"
        "typing-extensions (>=4.0,<5.0)" -> "typing-extensions"
        "numpy" -> "numpy"

    Args:
        dep_spec: A dependency specification string.

    Returns:
        The bare package name, or empty string if unparseable.
    """
    import re

    # Handle dict-style specs like {'include-group': 'dev'}
    if dep_spec.startswith("{"):
        return ""

    # Strip leading/trailing whitespace and quotes
    dep_spec = dep_spec.strip().strip('"').strip("'")
    if not dep_spec:
        return ""

    # Extract name before version specifiers
    match = re.match(r"^([a-zA-Z0-9_][a-zA-Z0-9._-]*)", dep_spec)
    if match:
        return match.group(1)

    return ""


def _parse_package_json(path: Path) -> dict[str, str]:
    """Parse a package.json file for project metadata.

    Args:
        path: Path to package.json.

    Returns:
        Metadata dict or empty dict on failure.
    """
    result: dict[str, str] = {}

    try:
        content = path.read_text(encoding="utf-8")
        data = json.loads(content)
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("Failed to parse package.json: %s", exc)
        return result

    if not isinstance(data, dict):
        return result

    name = data.get("name")
    if name:
        result["name"] = str(name)

    version = data.get("version")
    if version:
        result["version"] = str(version)

    description = data.get("description")
    if description:
        result["description"] = str(description)

    # Extract dependency names from dependencies + devDependencies
    deps: list[str] = []
    for dep_key in ("dependencies", "devDependencies"):
        dep_dict = data.get(dep_key, {})
        if isinstance(dep_dict, dict):
            deps.extend(dep_dict.keys())

    if deps:
        # Deduplicate while preserving order
        seen: set[str] = set()
        unique_deps: list[str] = []
        for d in deps:
            if d not in seen:
                seen.add(d)
                unique_deps.append(d)
        result["dependencies"] = ", ".join(unique_deps)

    return result
```
