"""Utility to detect naming conventions, module patterns, framework usage from file contents.

Issue #401: Codebase Context Analysis for Requirements Workflow.

Provides functions for:
- Scanning code patterns (naming, state management, node patterns, tests, imports)
- Detecting frameworks from dependencies and import statements
- Extracting coding conventions from CLAUDE.md files
"""

from __future__ import annotations

import logging
import re
from typing import TypedDict

logger = logging.getLogger(__name__)


class PatternAnalysis(TypedDict):
    """Results of scanning existing code patterns."""

    naming_convention: str
    state_pattern: str
    node_pattern: str
    test_pattern: str
    import_style: str


# Known package-to-display-name mappings for framework detection.
FRAMEWORK_MAP: dict[str, str] = {
    "langgraph": "LangGraph",
    "langchain": "LangChain",
    "langchain-core": "LangChain Core",
    "langchain-openai": "LangChain OpenAI",
    "langsmith": "LangSmith",
    "fastapi": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "pytest": "pytest",
    "unittest": "unittest",
    "pydantic": "Pydantic",
    "sqlalchemy": "SQLAlchemy",
    "alembic": "Alembic",
    "celery": "Celery",
    "redis": "Redis",
    "httpx": "httpx",
    "requests": "Requests",
    "aiohttp": "aiohttp",
    "starlette": "Starlette",
    "uvicorn": "Uvicorn",
    "click": "Click",
    "typer": "Typer",
    "rich": "Rich",
    "numpy": "NumPy",
    "pandas": "pandas",
    "scipy": "SciPy",
    "torch": "PyTorch",
    "tensorflow": "TensorFlow",
    "streamlit": "Streamlit",
    "gradio": "Gradio",
}

# Mapping from import module names to display names (for import-based detection).
IMPORT_MODULE_MAP: dict[str, str] = {
    "langgraph": "LangGraph",
    "langchain": "LangChain",
    "langchain_core": "LangChain Core",
    "langchain_openai": "LangChain OpenAI",
    "langsmith": "LangSmith",
    "fastapi": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "pytest": "pytest",
    "unittest": "unittest",
    "pydantic": "Pydantic",
    "sqlalchemy": "SQLAlchemy",
    "alembic": "Alembic",
    "celery": "Celery",
    "redis": "Redis",
    "httpx": "httpx",
    "requests": "Requests",
    "aiohttp": "aiohttp",
    "starlette": "Starlette",
    "uvicorn": "Uvicorn",
    "click": "Click",
    "typer": "Typer",
    "rich": "Rich",
    "numpy": "NumPy",
    "pandas": "pandas",
    "scipy": "SciPy",
    "torch": "PyTorch",
    "tensorflow": "TensorFlow",
    "streamlit": "Streamlit",
    "gradio": "Gradio",
}

# Headers that indicate convention/rule sections in CLAUDE.md.
_CONVENTION_HEADER_KEYWORDS: list[str] = [
    "convention",
    "rule",
    "standard",
    "constraint",
    "style",
    "guideline",
    "requirement",
    "policy",
]


def scan_patterns(file_contents: dict[str, str]) -> PatternAnalysis:
    """Analyze file contents to detect naming conventions, design patterns,
    state management approach, test conventions, and import styles.

    Uses regex-based heuristics:
    - naming_convention: checks for snake_case filenames, PascalCase classes
    - state_pattern: looks for TypedDict, dataclass, BaseModel imports
    - node_pattern: looks for functions returning dict
    - test_pattern: looks for pytest, unittest patterns
    - import_style: checks absolute vs relative import prevalence

    Args:
        file_contents: Dict mapping filename to file content string.

    Returns:
        PatternAnalysis with "unknown" for any undetectable field.
    """
    result = PatternAnalysis(
        naming_convention="unknown",
        state_pattern="unknown",
        node_pattern="unknown",
        test_pattern="unknown",
        import_style="unknown",
    )

    if not file_contents:
        return result

    # --- Naming convention detection ---
    result["naming_convention"] = _detect_naming_convention(file_contents)

    # --- State pattern detection ---
    result["state_pattern"] = _detect_state_pattern(file_contents)

    # --- Node pattern detection ---
    result["node_pattern"] = _detect_node_pattern(file_contents)

    # --- Test pattern detection ---
    result["test_pattern"] = _detect_test_pattern(file_contents)

    # --- Import style detection ---
    result["import_style"] = _detect_import_style(file_contents)

    return result


def _detect_naming_convention(file_contents: dict[str, str]) -> str:
    """Detect naming conventions from filenames and class definitions.

    Args:
        file_contents: Dict mapping filename to file content.

    Returns:
        Human-readable naming convention string, or "unknown".
    """
    conventions: list[str] = []

    # Check filenames for snake_case pattern
    snake_case_files = 0
    total_py_files = 0
    for filename in file_contents:
        # Extract just the filename without path
        name = filename.replace("\\", "/").split("/")[-1]
        if name.endswith(".py"):
            total_py_files += 1
            # snake_case: lowercase with underscores, no uppercase
            base = name[:-3]  # remove .py
            if base and re.match(r"^[a-z][a-z0-9_]*$", base):
                snake_case_files += 1

    if total_py_files > 0 and snake_case_files >= total_py_files * 0.5:
        conventions.append("snake_case modules")

    # Check for PascalCase class definitions
    pascal_classes = 0
    total_classes = 0
    for content in file_contents.values():
        class_matches = re.findall(r"class\s+(\w+)", content)
        for cls_name in class_matches:
            total_classes += 1
            if re.match(r"^[A-Z][a-zA-Z0-9]*$", cls_name):
                pascal_classes += 1

    if total_classes > 0 and pascal_classes >= total_classes * 0.5:
        conventions.append("PascalCase classes")

    # Check for snake_case function definitions
    snake_funcs = 0
    total_funcs = 0
    for content in file_contents.values():
        func_matches = re.findall(r"def\s+(\w+)", content)
        for func_name in func_matches:
            if func_name.startswith("_"):
                func_name = func_name.lstrip("_")
            if not func_name:
                continue
            total_funcs += 1
            if re.match(r"^[a-z][a-z0-9_]*$", func_name):
                snake_funcs += 1

    if total_funcs > 0 and snake_funcs >= total_funcs * 0.5:
        conventions.append("snake_case functions")

    if conventions:
        return ", ".join(conventions)
    return "unknown"


def _detect_state_pattern(file_contents: dict[str, str]) -> str:
    """Detect state management patterns from imports and usage.

    Args:
        file_contents: Dict mapping filename to file content.

    Returns:
        Human-readable state pattern string, or "unknown".
    """
    patterns: list[str] = []

    all_content = "\n".join(file_contents.values())

    # Check for TypedDict usage
    if re.search(r"from\s+typing(?:_extensions)?\s+import\s+.*\bTypedDict\b", all_content) or \
       re.search(r"class\s+\w+\(TypedDict\)", all_content):
        patterns.append("TypedDict")

    # Check for dataclass usage
    if re.search(r"from\s+dataclasses\s+import\s+.*\bdataclass\b", all_content) or \
       re.search(r"@dataclass", all_content):
        patterns.append("dataclass")

    # Check for Pydantic BaseModel usage
    if re.search(r"from\s+pydantic\s+import\s+.*\bBaseModel\b", all_content) or \
       re.search(r"class\s+\w+\(BaseModel\)", all_content):
        patterns.append("BaseModel")

    # Check for LangGraph state pattern
    if "TypedDict" in patterns and re.search(r"langgraph", all_content, re.IGNORECASE):
        return "TypedDict-based LangGraph state"

    if patterns:
        return ", ".join(patterns) + "-based state"
    return "unknown"


def _detect_node_pattern(file_contents: dict[str, str]) -> str:
    """Detect node/function patterns.

    Args:
        file_contents: Dict mapping filename to file content.

    Returns:
        Human-readable node pattern string, or "unknown".
    """
    all_content = "\n".join(file_contents.values())

    # Check for functions returning dict (LangGraph node pattern)
    dict_return_funcs = re.findall(
        r"def\s+\w+\([^)]*\)\s*->\s*dict", all_content
    )
    if dict_return_funcs:
        return "functions returning dict updates"

    # Check for functions with state parameter returning dict
    state_funcs = re.findall(
        r"def\s+\w+\(\s*state\s*:", all_content
    )
    if state_funcs:
        return "state-based node functions"

    return "unknown"


def _detect_test_pattern(file_contents: dict[str, str]) -> str:
    """Detect testing patterns and conventions.

    Args:
        file_contents: Dict mapping filename to file content.

    Returns:
        Human-readable test pattern string, or "unknown".
    """
    patterns: list[str] = []

    all_content = "\n".join(file_contents.values())

    # Check for pytest
    if re.search(r"import\s+pytest|from\s+pytest\s+import", all_content) or \
       re.search(r"@pytest\.", all_content):
        patterns.append("pytest")

    # Check for pytest fixtures in conftest
    has_conftest = any(
        "conftest" in filename for filename in file_contents
    )
    if has_conftest:
        patterns.append("fixtures in conftest.py")

    # Check for unittest
    if re.search(r"import\s+unittest|from\s+unittest\s+import", all_content) or \
       re.search(r"class\s+\w+\(.*TestCase.*\)", all_content):
        if "pytest" not in patterns:
            patterns.append("unittest")

    # Check for test function naming conventions
    test_funcs = re.findall(r"def\s+(test_\w+)", all_content)
    if test_funcs and "pytest" not in patterns and "unittest" not in patterns:
        patterns.append("pytest-style test functions")

    if patterns:
        return " with ".join(patterns)
    return "unknown"


def _detect_import_style(file_contents: dict[str, str]) -> str:
    """Detect import style (absolute vs relative).

    Args:
        file_contents: Dict mapping filename to file content.

    Returns:
        Human-readable import style string, or "unknown".
    """
    absolute_imports = 0
    relative_imports = 0

    for content in file_contents.values():
        # Count absolute imports (from package.module import ...)
        absolute_imports += len(
            re.findall(r"^from\s+[a-zA-Z]\w*(?:\.\w+)*\s+import", content, re.MULTILINE)
        )
        # Count relative imports (from . import ..., from .module import ...)
        relative_imports += len(
            re.findall(r"^from\s+\.+\w*\s+import", content, re.MULTILINE)
        )

    total = absolute_imports + relative_imports
    if total == 0:
        return "unknown"

    if absolute_imports > relative_imports:
        if relative_imports == 0:
            return "absolute imports from package root"
        return "primarily absolute imports"
    elif relative_imports > absolute_imports:
        if absolute_imports == 0:
            return "relative imports"
        return "primarily relative imports"
    else:
        return "mixed absolute and relative imports"


def detect_frameworks(
    dependency_list: list[str],
    file_contents: dict[str, str],
) -> list[str]:
    """Identify frameworks in use from dependency names and import statements.

    Maps known package names to display names:
        'langgraph' -> 'LangGraph', 'fastapi' -> 'FastAPI', etc.
    Also scans import statements in file_contents for additional detection.

    Args:
        dependency_list: List of dependency package names (e.g., from pyproject.toml).
        file_contents: Dict mapping filename to file content.

    Returns:
        Human-readable list like ['LangGraph', 'FastAPI', 'pytest'].
        Returns empty list if nothing detected.
    """
    detected: dict[str, str] = {}  # display_name -> display_name (dedup)

    # Detect from dependency list
    for dep in dependency_list:
        dep_lower = dep.strip().lower()
        if dep_lower in FRAMEWORK_MAP:
            display = FRAMEWORK_MAP[dep_lower]
            detected[display] = display

    # Detect from import statements in file contents
    all_content = "\n".join(file_contents.values())

    for module_name, display_name in IMPORT_MODULE_MAP.items():
        if display_name in detected:
            continue
        # Match: import module_name, from module_name import, from module_name.sub import
        pattern = (
            rf"(?:^import\s+{re.escape(module_name)}\b|"
            rf"^from\s+{re.escape(module_name)}\b)"
        )
        if re.search(pattern, all_content, re.MULTILINE):
            detected[display_name] = display_name

    return sorted(detected.keys())


def extract_conventions_from_claude_md(content: str) -> list[str]:
    """Parse CLAUDE.md to extract coding conventions, rules, and constraints
    that the LLD must respect.

    Looks for sections with headers containing 'convention', 'rule',
    'standard', 'constraint', 'style', or bullet-pointed lists under
    such headers. Also extracts content from code blocks labeled as rules.

    Args:
        content: The full text content of a CLAUDE.md file.

    Returns:
        List of convention strings. Empty list if none found.
    """
    if not content or not content.strip():
        return []

    conventions: list[str] = []

    # Split content into lines for processing
    lines = content.split("\n")

    # Track whether we're in a convention-related section
    in_convention_section = False
    current_section_level = 0

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Check if this is a header line
        header_match = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if header_match:
            level = len(header_match.group(1))
            header_text = header_match.group(2).lower()

            # Check if header contains convention-related keywords
            is_convention_header = any(
                kw in header_text for kw in _CONVENTION_HEADER_KEYWORDS
            )

            if is_convention_header:
                in_convention_section = True
                current_section_level = level
            elif in_convention_section and level <= current_section_level:
                # Left the convention section (same or higher level header)
                in_convention_section = False
            continue

        # If we're in a convention section, extract bullet points
        if in_convention_section and stripped:
            bullet_match = re.match(r"^[-*+]\s+(.+)$", stripped)
            if bullet_match:
                convention_text = bullet_match.group(1).strip()
                if convention_text and len(convention_text) > 3:
                    conventions.append(convention_text)
            # Also extract numbered list items
            numbered_match = re.match(r"^\d+[.)]\s+(.+)$", stripped)
            if numbered_match:
                convention_text = numbered_match.group(1).strip()
                if convention_text and len(convention_text) > 3:
                    conventions.append(convention_text)

    # Also extract from code blocks labeled as rules/conventions
    code_block_pattern = re.compile(
        r"```(?:rules?|conventions?|constraints?)\s*\n(.*?)```",
        re.DOTALL | re.IGNORECASE,
    )
    for match in code_block_pattern.finditer(content):
        block_content = match.group(1).strip()
        for block_line in block_content.split("\n"):
            block_line = block_line.strip()
            if block_line and len(block_line) > 3:
                # Remove bullet markers if present
                cleaned = re.sub(r"^[-*+]\s+", "", block_line)
                cleaned = re.sub(r"^\d+[.)]\s+", "", cleaned)
                if cleaned:
                    conventions.append(cleaned)

    # Deduplicate while preserving order
    seen: set[str] = set()
    unique_conventions: list[str] = []
    for conv in conventions:
        if conv not in seen:
            seen.add(conv)
            unique_conventions.append(conv)

    return unique_conventions