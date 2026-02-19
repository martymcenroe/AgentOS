```python
"""Utility to detect naming conventions, module patterns, framework usage from file contents.

Issue #401: Codebase Context Analysis for Requirements Workflow.

Provides regex-based heuristic analysis of source code to detect patterns
such as naming conventions, state management approaches, test frameworks,
and import styles. All functions are pure and operate on string content
passed in — no filesystem access is performed here.
"""

from __future__ import annotations

import logging
import re
from typing import TypedDict

logger = logging.getLogger(__name__)


class PatternAnalysis(TypedDict):
    """Results of scanning existing code patterns."""

    naming_convention: str  # e.g., "snake_case modules, PascalCase classes"
    state_pattern: str  # e.g., "TypedDict-based LangGraph state"
    node_pattern: str  # e.g., "functions returning dict updates"
    test_pattern: str  # e.g., "pytest with fixtures in conftest.py"
    import_style: str  # e.g., "absolute imports from package root"


# Maps known package names (lowercased) to human-readable display names.
_FRAMEWORK_MAP: dict[str, str] = {
    "langgraph": "LangGraph",
    "langchain": "LangChain",
    "langchain-core": "LangChain Core",
    "langchain-community": "LangChain Community",
    "langsmith": "LangSmith",
    "fastapi": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "starlette": "Starlette",
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
    "typer": "Typer",
    "click": "Click",
    "rich": "Rich",
    "streamlit": "Streamlit",
    "gradio": "Gradio",
    "numpy": "NumPy",
    "pandas": "pandas",
    "scipy": "SciPy",
    "torch": "PyTorch",
    "tensorflow": "TensorFlow",
    "transformers": "Transformers",
    "openai": "OpenAI",
    "anthropic": "Anthropic",
    "boto3": "AWS SDK (boto3)",
    "google-cloud": "Google Cloud",
    "docker": "Docker SDK",
}

# Maps import module names to display names (for detecting via import statements).
_IMPORT_FRAMEWORK_MAP: dict[str, str] = {
    "langgraph": "LangGraph",
    "langchain": "LangChain",
    "langchain_core": "LangChain Core",
    "langchain_community": "LangChain Community",
    "langsmith": "LangSmith",
    "fastapi": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "starlette": "Starlette",
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
    "typer": "Typer",
    "click": "Click",
    "rich": "Rich",
    "streamlit": "Streamlit",
    "gradio": "Gradio",
    "numpy": "NumPy",
    "pandas": "pandas",
    "scipy": "SciPy",
    "torch": "PyTorch",
    "tensorflow": "TensorFlow",
    "transformers": "Transformers",
    "openai": "OpenAI",
    "anthropic": "Anthropic",
    "boto3": "AWS SDK (boto3)",
}


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
        file_contents: Mapping of filename -> file content strings.

    Returns:
        PatternAnalysis with ``"unknown"`` for any undetectable field.
    """
    result: PatternAnalysis = {
        "naming_convention": "unknown",
        "state_pattern": "unknown",
        "node_pattern": "unknown",
        "test_pattern": "unknown",
        "import_style": "unknown",
    }

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
        file_contents: Mapping of filename -> content.

    Returns:
        Human-readable naming convention string, or ``"unknown"``.
    """
    conventions: list[str] = []

    # Check filenames for snake_case pattern
    snake_case_files = 0
    camel_case_files = 0
    total_py_files = 0

    for filename in file_contents:
        # Extract just the base filename
        base = filename.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
        if base.endswith(".py"):
            total_py_files += 1
            name_part = base[:-3]  # Remove .py
            if name_part.startswith("__"):
                continue  # Skip __init__.py etc.
            if re.match(r"^[a-z][a-z0-9_]*$", name_part):
                snake_case_files += 1
            elif re.match(r"^[A-Z][a-zA-Z0-9]*$", name_part):
                camel_case_files += 1

    if snake_case_files > 0 and snake_case_files >= camel_case_files:
        conventions.append("snake_case modules")
    elif camel_case_files > 0:
        conventions.append("PascalCase modules")

    # Check for class naming patterns in content
    pascal_classes = 0
    all_content = "\n".join(file_contents.values())

    class_matches = re.findall(r"^class\s+([A-Za-z_]\w*)", all_content, re.MULTILINE)
    for class_name in class_matches:
        if re.match(r"^[A-Z][a-zA-Z0-9]*", class_name):
            pascal_classes += 1

    if pascal_classes > 0:
        conventions.append("PascalCase classes")

    # Check for function naming patterns
    func_matches = re.findall(
        r"^def\s+([a-zA-Z_]\w*)", all_content, re.MULTILINE
    )
    snake_funcs = sum(
        1 for f in func_matches if re.match(r"^[a-z_][a-z0-9_]*$", f)
    )
    if snake_funcs > 0:
        conventions.append("snake_case functions")

    if conventions:
        return ", ".join(conventions)
    return "unknown"


def _detect_state_pattern(file_contents: dict[str, str]) -> str:
    """Detect state management patterns from imports and usage.

    Args:
        file_contents: Mapping of filename -> content.

    Returns:
        Description of state pattern or ``"unknown"``.
    """
    all_content = "\n".join(file_contents.values())
    patterns_found: list[str] = []

    # TypedDict detection
    if re.search(
        r"(?:from\s+typing(?:_extensions)?\s+import\s+.*TypedDict|"
        r"import\s+typing.*TypedDict|"
        r"class\s+\w+\(TypedDict\))",
        all_content,
    ):
        # Check if it's used with LangGraph
        if re.search(r"langgraph", all_content, re.IGNORECASE):
            patterns_found.append("TypedDict-based LangGraph state")
        else:
            patterns_found.append("TypedDict-based state")

    # dataclass detection
    if re.search(
        r"(?:from\s+dataclasses\s+import\s+.*dataclass|@dataclass)",
        all_content,
    ):
        patterns_found.append("dataclass-based state")

    # Pydantic BaseModel detection
    if re.search(
        r"(?:from\s+pydantic\s+import\s+.*BaseModel|"
        r"class\s+\w+\(BaseModel\))",
        all_content,
    ):
        patterns_found.append("Pydantic BaseModel state")

    if patterns_found:
        return ", ".join(patterns_found)
    return "unknown"


def _detect_node_pattern(file_contents: dict[str, str]) -> str:
    """Detect function/node patterns (e.g., LangGraph node style).

    Args:
        file_contents: Mapping of filename -> content.

    Returns:
        Description of node pattern or ``"unknown"``.
    """
    all_content = "\n".join(file_contents.values())
    patterns_found: list[str] = []

    # Functions returning dict (LangGraph node pattern)
    if re.search(
        r"def\s+\w+\([^)]*\)\s*->\s*dict",
        all_content,
    ):
        patterns_found.append("functions returning dict updates")

    # Functions with state parameter
    if re.search(
        r"def\s+\w+\(\s*state\s*:\s*dict",
        all_content,
    ):
        patterns_found.append("state-accepting node functions")

    # Class-based nodes
    if re.search(
        r"class\s+\w+Node",
        all_content,
    ):
        patterns_found.append("class-based nodes")

    if patterns_found:
        return ", ".join(patterns_found)
    return "unknown"


def _detect_test_pattern(file_contents: dict[str, str]) -> str:
    """Detect test framework and patterns.

    Args:
        file_contents: Mapping of filename -> content.

    Returns:
        Description of test pattern or ``"unknown"``.
    """
    all_content = "\n".join(file_contents.values())
    patterns_found: list[str] = []

    # pytest detection
    has_pytest = bool(
        re.search(r"(?:import\s+pytest|from\s+pytest\s+import)", all_content)
    )
    has_pytest_fixtures = bool(
        re.search(r"@pytest\.fixture", all_content)
    )
    has_conftest = any(
        "conftest" in filename for filename in file_contents
    )

    if has_pytest or has_pytest_fixtures:
        parts = ["pytest"]
        if has_pytest_fixtures:
            if has_conftest:
                parts.append("with fixtures in conftest.py")
            else:
                parts.append("with fixtures")
        patterns_found.append(" ".join(parts))

    # unittest detection
    if re.search(
        r"(?:import\s+unittest|from\s+unittest\s+import|"
        r"class\s+\w+\((?:unittest\.)?TestCase\))",
        all_content,
    ):
        patterns_found.append("unittest TestCase")

    # Test function naming
    test_funcs = re.findall(r"def\s+(test_\w+)", all_content)
    if test_funcs and not patterns_found:
        patterns_found.append("test_ prefixed functions")

    if patterns_found:
        return ", ".join(patterns_found)
    return "unknown"


def _detect_import_style(file_contents: dict[str, str]) -> str:
    """Detect whether imports are absolute or relative.

    Args:
        file_contents: Mapping of filename -> content.

    Returns:
        Description of import style or ``"unknown"``.
    """
    absolute_imports = 0
    relative_imports = 0

    for content in file_contents.values():
        # Count absolute imports (from package.module import ...)
        absolute_imports += len(
            re.findall(
                r"^from\s+[a-zA-Z_]\w*(?:\.[a-zA-Z_]\w*)+\s+import",
                content,
                re.MULTILINE,
            )
        )
        # Count relative imports (from . import ... or from ..module import ...)
        relative_imports += len(
            re.findall(
                r"^from\s+\.+\w*\s+import",
                content,
                re.MULTILINE,
            )
        )

    if absolute_imports > 0 and relative_imports == 0:
        return "absolute imports from package root"
    elif relative_imports > 0 and absolute_imports == 0:
        return "relative imports"
    elif absolute_imports > 0 and relative_imports > 0:
        if absolute_imports >= relative_imports:
            return "mixed imports, primarily absolute"
        else:
            return "mixed imports, primarily relative"
    return "unknown"


def detect_frameworks(
    dependency_list: list[str],
    file_contents: dict[str, str],
) -> list[str]:
    """Identify frameworks in use from dependency names and import statements.

    Maps known package names to display names:
        ``'langgraph'`` -> ``'LangGraph'``, ``'fastapi'`` -> ``'FastAPI'``, etc.
    Also scans import statements in *file_contents* for additional detection.

    Args:
        dependency_list: List of dependency package names (e.g. from
            pyproject.toml).
        file_contents: Mapping of filename -> file content for import
            scanning.

    Returns:
        Human-readable list like ``['LangGraph', 'FastAPI', 'pytest']``.
        Returns empty list if nothing detected.
    """
    detected: dict[str, str] = {}  # display_name -> display_name (for dedup)

    # Phase 1: Match from dependency list
    for dep in dependency_list:
        dep_lower = dep.lower().strip()
        if dep_lower in _FRAMEWORK_MAP:
            display = _FRAMEWORK_MAP[dep_lower]
            detected[display] = display

    # Phase 2: Scan import statements in file contents
    all_content = "\n".join(file_contents.values()) if file_contents else ""

    if all_content:
        # Match 'import X' and 'from X import ...'
        import_matches = re.findall(
            r"^(?:import|from)\s+([a-zA-Z_]\w*)",
            all_content,
            re.MULTILINE,
        )
        for module_name in import_matches:
            module_lower = module_name.lower()
            if module_lower in _IMPORT_FRAMEWORK_MAP:
                display = _IMPORT_FRAMEWORK_MAP[module_lower]
                detected[display] = display

    # Return as sorted list for deterministic output
    return sorted(detected.values())


def extract_conventions_from_claude_md(content: str) -> list[str]:
    """Parse CLAUDE.md to extract coding conventions, rules, and constraints
    that the LLD must respect.

    Looks for sections with headers containing 'convention', 'rule',
    'standard', 'constraint', 'style', or bullet-pointed lists under
    such headers. Also extracts content from code blocks labeled as rules.

    Args:
        content: The raw text content of a CLAUDE.md file.

    Returns:
        List of convention strings. Empty list if none found.
    """
    if not content or not content.strip():
        return []

    conventions: list[str] = []

    # Keywords that signal a conventions/rules section
    section_keywords = re.compile(
        r"convention|rule|standard|constraint|style|safety|requirement|"
        r"important|must|never|always",
        re.IGNORECASE,
    )

    # Split content into sections by markdown headers
    sections = re.split(r"^(#{1,6}\s+.+)$", content, flags=re.MULTILINE)

    # Process sections: sections list alternates between content and headers
    # [pre-header content, header1, content1, header2, content2, ...]
    i = 0
    while i < len(sections):
        section = sections[i]

        # Check if this is a header that matches our keywords
        is_relevant_header = bool(
            re.match(r"^#{1,6}\s+", section) and section_keywords.search(section)
        )

        if is_relevant_header and i + 1 < len(sections):
            # Get the content following this header
            section_content = sections[i + 1]
            # Extract bullet points from this section
            bullets = re.findall(
                r"^\s*[-*]\s+(.+)$", section_content, re.MULTILINE
            )
            for bullet in bullets:
                cleaned = bullet.strip()
                if cleaned and len(cleaned) > 3:  # Skip trivially short items
                    conventions.append(cleaned)

            # Extract content from code blocks labeled as rules
            code_blocks = re.findall(
                r"```(?:rules?|conventions?)?\n(.*?)```",
                section_content,
                re.DOTALL | re.IGNORECASE,
            )
            for block in code_blocks:
                block_lines = block.strip().split("\n")
                for line in block_lines:
                    line = line.strip()
                    if line and len(line) > 3:
                        conventions.append(line)

            i += 2
            continue

        i += 1

    # Also look for standalone bullet lists with convention-like keywords
    # even outside explicitly headed sections
    if not conventions:
        # Look for lines that start with bullet points and contain rule-like language
        rule_bullets = re.findall(
            r"^\s*[-*]\s+((?:NEVER|ALWAYS|MUST|DO NOT|IMPORTANT)[\s:].+)$",
            content,
            re.MULTILINE | re.IGNORECASE,
        )
        for bullet in rule_bullets:
            cleaned = bullet.strip()
            if cleaned and len(cleaned) > 3:
                conventions.append(cleaned)

    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: list[str] = []
    for conv in conventions:
        if conv not in seen:
            seen.add(conv)
            unique.append(conv)

    return unique
```
