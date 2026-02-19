```python
"""Shared utility for reading and summarizing codebase files with token-budget awareness.

Issue #401: Codebase Context Analysis for Requirements Workflow.

Provides functions for:
- Reading individual files with token budget constraints
- Reading multiple files within total and per-file token budgets
- Detecting sensitive files that should not be read
- Parsing project metadata from pyproject.toml or package.json
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TypedDict

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore[no-redef]

logger = logging.getLogger(__name__)

# Sensitive file patterns - files matching these are never read.
# Issue #401: REQ-9
SENSITIVE_PATTERNS: list[str] = [".env", ".secrets", ".key", ".pem", "credentials"]


class FileReadResult(TypedDict):
    """Result of reading a single file with budget tracking."""

    path: str
    content: str
    truncated: bool
    token_estimate: int


def _estimate_tokens(text: str) -> int:
    """Estimate token count using chars / 4 approximation.

    Args:
        text: The text to estimate tokens for.

    Returns:
        Approximate token count.
    """
    return len(text) // 4


def is_sensitive_file(file_path: Path) -> bool:
    """Check if a file path matches any sensitive pattern.

    Checks filename and all parent directory names against SENSITIVE_PATTERNS.
    Dot-prefixed patterns (.env, .pem, .key, .secrets) match filenames that
    start with or end with the pattern. The ``credentials`` pattern matches
    exact directory or file names.

    Args:
        file_path: Path to check.

    Returns:
        True if the file matches a sensitive pattern, False otherwise.
    """
    name = file_path.name.lower()

    for pattern in SENSITIVE_PATTERNS:
        p = pattern.lower()
        if p.startswith("."):
            # Dot-prefixed patterns:
            #   .env  -> matches ".env", ".env.local"
            #   .pem  -> matches "server.pem", ".pem"
            #   .key  -> matches "server.key", ".key"
            #   .secrets -> matches ".secrets", ".secrets.json"
            if name == p or name.endswith(p) or name.startswith(p):
                return True
        else:
            # Non-dot patterns: match exact filename
            if name == p:
                return True

    # Check all parent directory names (exclude the filename itself)
    for part in file_path.parts[:-1] if file_path.parts else []:
        part_lower = part.lower()
        for pattern in SENSITIVE_PATTERNS:
            if part_lower == pattern.lower():
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

    Returns FileReadResult with empty content and token_estimate=0
    if file is binary, missing, unreadable, or matches SENSITIVE_PATTERNS.

    Args:
        file_path: Path to the file to read.
        max_tokens: Maximum number of tokens to read (default 2000).
        encoding: File encoding (default utf-8).
        repo_root: Optional repo root path for symlink boundary validation.

    Returns:
        FileReadResult with file content and metadata.

    Raises:
        No exceptions — all errors caught and logged.
    """
    empty_result = FileReadResult(
        path=str(file_path),
        content="",
        truncated=False,
        token_estimate=0,
    )

    # Check sensitive patterns
    if is_sensitive_file(file_path):
        logger.debug("Skipping sensitive file: %s", file_path)
        return empty_result

    # Check file exists
    try:
        if not file_path.exists():
            logger.debug("File does not exist: %s", file_path)
            return empty_result

        if not file_path.is_file():
            logger.debug("Not a regular file: %s", file_path)
            return empty_result
    except OSError as e:
        logger.debug("Error checking file %s: %s", file_path, e)
        return empty_result

    # Resolve symlinks and check boundary
    try:
        resolved = file_path.resolve()
        if repo_root is not None:
            repo_resolved = repo_root.resolve()
            try:
                resolved.relative_to(repo_resolved)
            except ValueError:
                logger.warning(
                    "Symlink escape detected: %s resolves to %s (outside %s)",
                    file_path,
                    resolved,
                    repo_resolved,
                )
                return empty_result
    except OSError as e:
        logger.debug("Error resolving path %s: %s", file_path, e)
        return empty_result

    # Read file content
    try:
        max_chars = max_tokens * 4
        content = file_path.read_text(encoding=encoding)

        truncated = False
        if len(content) > max_chars:
            content = content[:max_chars]
            truncated = True

        token_estimate = _estimate_tokens(content)

        return FileReadResult(
            path=str(file_path),
            content=content,
            truncated=truncated,
            token_estimate=token_estimate,
        )
    except UnicodeDecodeError:
        logger.debug("Binary or non-text file (decode error): %s", file_path)
        return empty_result
    except OSError as e:
        logger.debug("Error reading file %s: %s", file_path, e)
        return empty_result


def read_files_within_budget(
    file_paths: list[Path],
    total_budget: int = 15000,
    per_file_budget: int = 3000,
    repo_root: Path | None = None,
) -> list[FileReadResult]:
    """Read multiple files respecting per-file and total token budgets.

    Files are read in order; stops when total budget is exhausted.
    Skips files that match SENSITIVE_PATTERNS.

    Args:
        file_paths: List of file paths to read, in priority order.
        total_budget: Maximum total tokens across all files (default 15000).
        per_file_budget: Maximum tokens per individual file (default 3000).
        repo_root: Optional repo root path for symlink boundary validation.

    Returns:
        List of FileReadResult for files that were actually read
        (excluding skipped/empty files).
    """
    results: list[FileReadResult] = []
    tokens_used = 0

    for file_path in file_paths:
        # Skip sensitive files early
        if is_sensitive_file(file_path):
            logger.debug("Skipping sensitive file in batch: %s", file_path)
            continue

        # Check remaining budget
        remaining = total_budget - tokens_used
        if remaining <= 0:
            logger.debug(
                "Total token budget exhausted (%d/%d), stopping reads",
                tokens_used,
                total_budget,
            )
            break

        # Use the smaller of per-file budget and remaining total budget
        effective_budget = min(per_file_budget, remaining)

        result = read_file_with_budget(
            file_path,
            max_tokens=effective_budget,
            repo_root=repo_root,
        )

        # Only include files that were actually read (non-empty content)
        if result["content"]:
            results.append(result)
            tokens_used += result["token_estimate"]

    return results


def parse_project_metadata(repo_path: Path) -> dict[str, str]:
    """Parse pyproject.toml or package.json to extract project metadata.

    Tries pyproject.toml first (using tomllib), falls back to package.json.
    Returns empty dict if neither exists or parsing fails.

    Args:
        repo_path: Path to the repository root.

    Returns:
        Dict with keys: 'name', 'version', 'description', 'dependencies'
        where 'dependencies' is a comma-separated string of package names.
    """
    # Try pyproject.toml first
    pyproject_path = repo_path / "pyproject.toml"
    if pyproject_path.exists():
        try:
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)

            result: dict[str, str] = {}

            # Extract from [project] (PEP 621) or [tool.poetry] sections
            project = data.get("project", {})
            poetry = data.get("tool", {}).get("poetry", {})

            # Name
            name = project.get("name") or poetry.get("name", "")
            if name:
                result["name"] = str(name)

            # Version
            version = project.get("version") or poetry.get("version", "")
            if version:
                result["version"] = str(version)

            # Description
            description = project.get("description") or poetry.get(
                "description", ""
            )
            if description:
                result["description"] = str(description)

            # Dependencies
            deps: list[str] = []

            # PEP 621 dependencies
            if "dependencies" in project:
                for dep in project["dependencies"]:
                    # Parse "package>=1.0" style version specifiers
                    dep_str = str(dep)
                    dep_name = (
                        dep_str.split(">=")[0]
                        .split("<=")[0]
                        .split("==")[0]
                        .split("!=")[0]
                        .split("<")[0]
                        .split(">")[0]
                        .split("[")[0]
                        .split(";")[0]
                        .strip()
                    )
                    if dep_name:
                        deps.append(dep_name)

            # Poetry dependencies
            poetry_deps = poetry.get("dependencies", {})
            if isinstance(poetry_deps, dict):
                for dep_name in poetry_deps:
                    if dep_name.lower() != "python":
                        deps.append(str(dep_name))

            if deps:
                result["dependencies"] = ", ".join(deps)

            return result

        except Exception as e:
            logger.debug("Error parsing pyproject.toml: %s", e)

    # Fall back to package.json
    package_json_path = repo_path / "package.json"
    if package_json_path.exists():
        try:
            with open(package_json_path, encoding="utf-8") as f:
                data = json.load(f)

            result = {}

            if "name" in data:
                result["name"] = str(data["name"])
            if "version" in data:
                result["version"] = str(data["version"])
            if "description" in data:
                result["description"] = str(data["description"])

            deps = []
            for section in ("dependencies", "devDependencies"):
                if section in data and isinstance(data[section], dict):
                    deps.extend(str(k) for k in data[section])

            if deps:
                result["dependencies"] = ", ".join(deps)

            return result

        except Exception as e:
            logger.debug("Error parsing package.json: %s", e)

    return {}
```
