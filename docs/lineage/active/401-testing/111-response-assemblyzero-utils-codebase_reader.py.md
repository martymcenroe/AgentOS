The existing `codebase_reader.py` already looks fully implemented and correct. The test failures are from TDD stub tests (`assert False`), not from bugs in this file. Let me output the complete file:

```python
"""Shared utility for reading and summarizing codebase files with token-budget awareness.

Issue #401: Codebase Context Analysis for Requirements Workflow.

Provides functions for safely reading files from a target repository with:
- Token budget management (per-file and total)
- Sensitive file detection and exclusion
- Symlink boundary enforcement
- Project metadata parsing (pyproject.toml / package.json)
- Graceful handling of binary, missing, and unreadable files
"""

import json
import logging
import tomllib
from pathlib import Path
from typing import TypedDict

logger = logging.getLogger(__name__)

SENSITIVE_PATTERNS: list[str] = [".env", ".secrets", ".key", ".pem", "credentials"]


class FileReadResult(TypedDict):
    """Result of reading a single file with budget tracking."""

    path: str  # Relative file path
    content: str  # File content (possibly truncated)
    truncated: bool  # Whether content was truncated
    token_estimate: int  # Approximate token count


def _estimate_tokens(text: str) -> int:
    """Approximate token count using chars / 4.

    Args:
        text: The text to estimate tokens for.

    Returns:
        Approximate token count.
    """
    return len(text) // 4


def is_sensitive_file(file_path: Path) -> bool:
    """Check if a file path matches any sensitive pattern.

    Checks filename and all parent directory names against SENSITIVE_PATTERNS.
    Matching is case-insensitive for directory components and checks both
    exact matches and suffix matches for filenames.

    Args:
        file_path: Path to check for sensitivity.

    Returns:
        True if the file matches a sensitive pattern, False otherwise.
    """
    name = file_path.name.lower()

    # Check filename against patterns
    for pattern in SENSITIVE_PATTERNS:
        pattern_lower = pattern.lower()
        # Exact match (e.g., ".env" matches ".env")
        if name == pattern_lower:
            return True
        # Suffix match for extensions (e.g., "server.pem" matches ".pem")
        if pattern_lower.startswith(".") and name.endswith(pattern_lower):
            return True

    # Check all path parts (directory names) against patterns
    for part in file_path.parts:
        part_lower = part.lower()
        for pattern in SENSITIVE_PATTERNS:
            pattern_lower = pattern.lower()
            if part_lower == pattern_lower:
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

    When repo_root is provided, resolves symlinks and verifies the resolved
    path is within the repo_root boundary to prevent symlink escape attacks.

    Args:
        file_path: Path to the file to read.
        max_tokens: Maximum token budget for this file.
        encoding: Text encoding to use for reading.
        repo_root: Optional repository root for symlink boundary checking.

    Raises:
        No exceptions — all errors caught and logged.
    """
    path_str = str(file_path)
    empty_result = FileReadResult(
        path=path_str,
        content="",
        truncated=False,
        token_estimate=0,
    )

    try:
        # Check sensitive patterns first
        if is_sensitive_file(file_path):
            logger.warning("Skipping sensitive file: %s", file_path)
            return empty_result

        # Check file exists
        if not file_path.exists():
            logger.warning("File not found: %s", file_path)
            return empty_result

        # Check if it's a regular file (not a directory)
        if not file_path.is_file():
            logger.warning("Not a regular file: %s", file_path)
            return empty_result

        # Symlink boundary check
        if repo_root is not None:
            resolved = file_path.resolve()
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

        # Calculate max chars from token budget
        max_chars = max_tokens * 4

        # Read file content
        content = file_path.read_text(encoding=encoding)

        # Truncate if exceeding budget
        truncated = False
        if len(content) > max_chars:
            content = content[:max_chars]
            truncated = True

        token_estimate = _estimate_tokens(content)

        return FileReadResult(
            path=path_str,
            content=content,
            truncated=truncated,
            token_estimate=token_estimate,
        )

    except UnicodeDecodeError:
        logger.warning("Binary or non-text file skipped: %s", file_path)
        return empty_result
    except OSError as e:
        logger.warning("Error reading file %s: %s", file_path, e)
        return empty_result
    except Exception as e:
        logger.warning("Unexpected error reading file %s: %s", file_path, e)
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
        file_paths: Ordered list of file paths to read.
        total_budget: Maximum total token budget across all files.
        per_file_budget: Maximum token budget per individual file.
        repo_root: Optional repository root for symlink boundary checking.

    Returns:
        List of FileReadResult for files that were actually read
        (excluding skipped files with empty content).
    """
    results: list[FileReadResult] = []
    tokens_used = 0

    for file_path in file_paths:
        # Check if total budget is exhausted
        remaining = total_budget - tokens_used
        if remaining <= 0:
            logger.info(
                "Total token budget exhausted (%d/%d), stopping reads",
                tokens_used,
                total_budget,
            )
            break

        # Skip sensitive files
        if is_sensitive_file(file_path):
            logger.warning("Skipping sensitive file in batch: %s", file_path)
            continue

        # Use the smaller of per-file budget and remaining total budget
        effective_budget = min(per_file_budget, remaining)

        result = read_file_with_budget(
            file_path,
            max_tokens=effective_budget,
            repo_root=repo_root,
        )

        # Only include files that were actually read (non-empty content)
        if not result["content"]:
            continue

        results.append(result)
        tokens_used += result["token_estimate"]

    return results


def parse_project_metadata(repo_path: Path) -> dict[str, str]:
    """Parse pyproject.toml or package.json to extract project metadata.

    Tries pyproject.toml first (using tomllib), falls back to package.json.
    Returns empty dict if neither exists or parsing fails.

    Args:
        repo_path: Path to the repository root directory.

    Returns:
        Dict with keys: 'name', 'version', 'description', 'dependencies'
        where 'dependencies' is a comma-separated string of package names.
        Returns empty dict if no config file found or parsing fails.
    """
    # Try pyproject.toml first
    pyproject_path = repo_path / "pyproject.toml"
    if pyproject_path.exists():
        try:
            raw = pyproject_path.read_bytes()
            data = tomllib.loads(raw.decode("utf-8"))

            # Extract from [project] section (PEP 621) or [tool.poetry]
            project = data.get("project", {})
            tool_poetry = data.get("tool", {}).get("poetry", {})

            name = project.get("name", "") or tool_poetry.get("name", "")
            version = project.get("version", "") or tool_poetry.get("version", "")
            description = (
                project.get("description", "")
                or tool_poetry.get("description", "")
            )

            # Collect dependency names
            deps: list[str] = []

            # From [project.dependencies] (PEP 508 strings)
            project_deps = project.get("dependencies", [])
            if isinstance(project_deps, list):
                for dep_str in project_deps:
                    # Parse PEP 508: "package>=1.0" -> "package"
                    dep_name = (
                        dep_str.split(">")[0]
                        .split("<")[0]
                        .split("=")[0]
                        .split("[")[0]
                        .split(";")[0]
                        .split("~")[0]
                        .split("!")[0]
                        .strip()
                    )
                    if dep_name and dep_name not in deps:
                        deps.append(dep_name)

            # From [tool.poetry.dependencies]
            poetry_deps = tool_poetry.get("dependencies", {})
            if isinstance(poetry_deps, dict):
                for dep_name in poetry_deps:
                    if dep_name.lower() != "python" and dep_name not in deps:
                        deps.append(dep_name)

            # From [tool.poetry.group.*.dependencies]
            groups = tool_poetry.get("group", {})
            if isinstance(groups, dict):
                for group_data in groups.values():
                    if isinstance(group_data, dict):
                        group_deps = group_data.get("dependencies", {})
                        if isinstance(group_deps, dict):
                            for dep_name in group_deps:
                                if dep_name not in deps:
                                    deps.append(dep_name)

            return {
                "name": name,
                "version": version,
                "description": description,
                "dependencies": ", ".join(deps),
            }
        except Exception as e:
            logger.warning("Error parsing pyproject.toml at %s: %s", pyproject_path, e)

    # Fall back to package.json
    package_json_path = repo_path / "package.json"
    if package_json_path.exists():
        try:
            content = package_json_path.read_text(encoding="utf-8")
            data = json.loads(content)

            name = data.get("name", "")
            version = data.get("version", "")
            description = data.get("description", "")

            deps: list[str] = []
            for section_key in ("dependencies", "devDependencies"):
                section = data.get(section_key, {})
                if isinstance(section, dict):
                    for dep_name in section:
                        if dep_name not in deps:
                            deps.append(dep_name)

            return {
                "name": name,
                "version": version,
                "description": description,
                "dependencies": ", ".join(deps),
            }
        except Exception as e:
            logger.warning(
                "Error parsing package.json at %s: %s", package_json_path, e
            )

    return {}
```
