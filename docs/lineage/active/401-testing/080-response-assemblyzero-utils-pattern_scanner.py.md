```python
"""Utility to detect naming conventions, module patterns, framework usage from file contents.

Issue #401: Codebase Context Analysis for Requirements Workflow.

Provides functions for scanning existing code to detect:
- Naming conventions (snake_case, PascalCase, etc.)
- State management patterns (TypedDict, dataclass, BaseModel)
- Node/function patterns (functions returning dicts)
- Test conventions (pytest, unittest)
- Import styles (absolute vs relative)
- Framework detection from dependencies and imports
- Convention extraction from CLAUDE.md files
"""

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


# Mapping of known package names to human-readable display names
FRAMEWORK_MAP: dict[str, str] = {
    "langgraph": "LangGraph",
    "langchain": "LangChain",
    "langchain-core": "LangChain Core",
    "langchain-openai": "LangChain OpenAI",
    "langchain-anthropic": "LangChain Anthropic",
    "langchain-community": "LangChain Community",
    "langsmith": "LangSmith",
    "fastapi": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "pytest": "pytest",
    "unittest": "unittest",
    "sqlalchemy": "SQLAlchemy",
    "pydantic": "Pydantic",
    "httpx": "httpx",
    "requests": "requests",
    "celery": "Celery",
    "redis": "Redis",
    "asyncio": "asyncio",
    "aiohttp": "aiohttp",
    "uvicorn": "uvicorn",
    "gunicorn": "gunicorn",
    "alembic": "Alembic",
    "typer": "Typer",
    "click": "Click",
    "rich": "Rich",
    "streamlit": "Streamlit",
    "gradio": "Gradio",
    "anthropic": "Anthropic SDK",
    "openai": "OpenAI SDK",
    "transformers": "Hugging Face Transformers",
    "torch": "PyTorch",
    "tensorflow": "TensorFlow",
    "numpy": "NumPy",
    "pandas": "pandas",
    "scipy": "SciPy",
    "matplotlib": "Matplotlib",
    "starlette": "Starlette",
}

# Mapping of import names to display names (for detecting via import statements)
IMPORT_FRAMEWORK_MAP: dict[str, str] = {
    "langgraph": "LangGraph",
    "langchain": "LangChain",
    "langchain_core": "LangChain Core",
    "langchain_openai": "LangChain OpenAI",
    "langchain_anthropic": "LangChain Anthropic",
    "langchain_community": "LangChain Community",
    "langsmith": "LangSmith",
    "fastapi": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "pytest": "pytest",
    "unittest": "unittest",
    "sqlalchemy": "SQLAlchemy",
    "pydantic": "Pydantic",
    "httpx": "httpx",
    "requests": "requests",
    "celery": "Celery",
    "redis": "Redis",
    "aiohttp": "aiohttp",
    "uvicorn": "uvicorn",
    "alembic": "Alembic",
    "typer": "Typer",
    "click": "Click",
    "rich": "Rich",
    "streamlit": "Streamlit",
    "gradio": "Gradio",
    "anthropic": "Anthropic SDK",
    "openai": "OpenAI SDK",
    "transformers": "Hugging Face Transformers",
    "torch": "PyTorch",
    "tensorflow": "TensorFlow",
    "numpy": "NumPy",
    "pandas": "pandas",
    "scipy": "SciPy",
    "matplotlib": "Matplotlib",
    "starlette": "Starlette",
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
        file_contents: Dict mapping filename to file content string.

    Returns:
        PatternAnalysis with "unknown" for any undetectable field.
    """
    if not file_contents:
        return PatternAnalysis(
            naming_convention="unknown",
            state_pattern="unknown",
            node_pattern="unknown",
            test_pattern="unknown",
            import_style="unknown",
        )

    naming_convention = _detect_naming_convention(file_contents)
    state_pattern = _detect_state_pattern(file_contents)
    node_pattern = _detect_node_pattern(file_contents)
    test_pattern = _detect_test_pattern(file_contents)
    import_style = _detect_import_style(file_contents)

    return PatternAnalysis(
        naming_convention=naming_convention,
        state_pattern=state_pattern,
        node_pattern=node_pattern,
        test_pattern=test_pattern,
        import_style=import_style,
    )


def _detect_naming_convention(file_contents: dict[str, str]) -> str:
    """Detect naming conventions from filenames and class definitions.

    Args:
        file_contents: Dict mapping filename to file content.

    Returns:
        String describing detected naming convention, or "unknown".
    """
    conventions: list[str] = []

    # Check filenames for snake_case modules
    snake_case_files = 0
    total_py_files = 0
    for filename in file_contents:
        # Extract just the filename part (handle paths with / or \)
        basename = filename.replace("\\", "/").split("/")[-1]
        if basename.endswith(".py"):
            total_py_files += 1
            name_part = basename[:-3]  # Remove .py
            if name_part == "__init__":
                continue
            # snake_case: lowercase with underscores
            if re.match(r"^[a-z][a-z0-9_]*$", name_part):
                snake_case_files += 1

    if total_py_files > 0 and snake_case_files > 0:
        conventions.append("snake_case modules")

    # Check for PascalCase classes
    pascal_classes = 0
    for content in file_contents.values():
        pascal_classes += len(
            re.findall(r"^class\s+[A-Z][a-zA-Z0-9]*", content, re.MULTILINE)
        )

    if pascal_classes > 0:
        conventions.append("PascalCase classes")

    # Check for snake_case functions
    snake_funcs = 0
    for content in file_contents.values():
        snake_funcs += len(
            re.findall(r"^def\s+[a-z][a-z0-9_]*\s*\(", content, re.MULTILINE)
        )

    if snake_funcs > 0:
        conventions.append("snake_case functions")

    if conventions:
        return ", ".join(conventions)
    return "unknown"


def _detect_state_pattern(file_contents: dict[str, str]) -> str:
    """Detect state management patterns from imports and usage.

    Args:
        file_contents: Dict mapping filename to file content.

    Returns:
        String describing detected state pattern, or "unknown".
    """
    patterns_found: list[str] = []

    all_content = "\n".join(file_contents.values())

    # Check for TypedDict
    if re.search(
        r"(?:from\s+typing(?:_extensions)?\s+import\s+.*TypedDict|"
        r"import\s+typing.*TypedDict|"
        r"class\s+\w+\(TypedDict\))",
        all_content,
    ):
        patterns_found.append("TypedDict-based state")

    # Check for dataclass
    if re.search(
        r"(?:from\s+dataclasses\s+import\s+.*dataclass|"
        r"@dataclass)",
        all_content,
    ):
        patterns_found.append("dataclass-based state")

    # Check for Pydantic BaseModel
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
    """Detect node/function patterns.

    Args:
        file_contents: Dict mapping filename to file content.

    Returns:
        String describing detected node pattern, or "unknown".
    """
    all_content = "\n".join(file_contents.values())

    # Check for functions returning dict (LangGraph node pattern)
    dict_return_funcs = re.findall(
        r"def\s+\w+\(.*?\)\s*->\s*dict", all_content
    )

    if dict_return_funcs:
        return "functions returning dict updates"

    # Check for async functions
    async_funcs = re.findall(
        r"async\s+def\s+\w+\(.*?\)\s*->\s*dict", all_content
    )

    if async_funcs:
        return "async functions returning dict updates"

    return "unknown"


def _detect_test_pattern(file_contents: dict[str, str]) -> str:
    """Detect test conventions.

    Args:
        file_contents: Dict mapping filename to file content.

    Returns:
        String describing detected test pattern, or "unknown".
    """
    patterns: list[str] = []
    all_content = "\n".join(file_contents.values())

    # Check for pytest
    has_pytest = bool(
        re.search(r"(?:import\s+pytest|from\s+pytest\s+import)", all_content)
    )
    has_pytest_fixtures = bool(
        re.search(r"@pytest\.fixture", all_content)
    )
    has_conftest = any(
        "conftest" in filename for filename in file_contents
    )

    if has_pytest:
        parts = ["pytest"]
        if has_pytest_fixtures:
            if has_conftest:
                parts.append("with fixtures in conftest.py")
            else:
                parts.append("with fixtures")
        patterns.append(" ".join(parts))

    # Check for unittest
    has_unittest = bool(
        re.search(
            r"(?:import\s+unittest|from\s+unittest\s+import|"
            r"class\s+\w+\(.*TestCase.*\))",
            all_content,
        )
    )

    if has_unittest and not has_pytest:
        patterns.append("unittest")

    if patterns:
        return ", ".join(patterns)
    return "unknown"


def _detect_import_style(file_contents: dict[str, str]) -> str:
    """Detect import style (absolute vs relative).

    Args:
        file_contents: Dict mapping filename to file content.

    Returns:
        String describing detected import style, or "unknown".
    """
    absolute_imports = 0
    relative_imports = 0

    for content in file_contents.values():
        # Count absolute imports (from package import ...)
        absolute_imports += len(
            re.findall(r"^from\s+[a-zA-Z][a-zA-Z0-9_.]*\s+import", content, re.MULTILINE)
        )
        # Count relative imports (from . import ... or from .module import ...)
        relative_imports += len(
            re.findall(r"^from\s+\.+[a-zA-Z0-9_.]*\s+import", content, re.MULTILINE)
        )

    if absolute_imports == 0 and relative_imports == 0:
        return "unknown"

    if absolute_imports > relative_imports:
        return "absolute imports from package root"
    elif relative_imports > absolute_imports:
        return "relative imports"
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
        dependency_list: List of dependency/package names from project config.
        file_contents: Dict mapping filename to file content for import scanning.

    Returns:
        Human-readable list like ['LangGraph', 'FastAPI', 'pytest'].
        Returns empty list if nothing detected.
    """
    detected: list[str] = []

    # Detect from dependency list
    for dep in dependency_list:
        dep_lower = dep.strip().lower()
        if dep_lower in FRAMEWORK_MAP:
            display_name = FRAMEWORK_MAP[dep_lower]
            if display_name not in detected:
                detected.append(display_name)

    # Detect from import statements in file contents
    all_content = "\n".join(file_contents.values())

    # Match "import X" and "from X import ..."
    import_matches = re.findall(
        r"^(?:import|from)\s+([a-zA-Z][a-zA-Z0-9_]*)",
        all_content,
        re.MULTILINE,
    )

    for import_name in import_matches:
        import_lower = import_name.lower()
        if import_lower in IMPORT_FRAMEWORK_MAP:
            display_name = IMPORT_FRAMEWORK_MAP[import_lower]
            if display_name not in detected:
                detected.append(display_name)

    return detected


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

    # Keywords that indicate convention/rule sections
    section_keywords = [
        "convention",
        "rule",
        "standard",
        "constraint",
        "style",
        "safety",
        "requirement",
        "guideline",
        "policy",
        "important",
    ]

    # Split into lines for processing
    lines = content.split("\n")

    in_relevant_section = False
    in_code_block = False

    for line in lines:
        stripped = line.strip()

        # Track code blocks
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue

        # Skip content inside code blocks
        if in_code_block:
            continue

        # Check for headers
        header_match = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if header_match:
            header_text = header_match.group(2).lower()
            # Check if this header indicates a conventions section
            in_relevant_section = any(
                kw in header_text for kw in section_keywords
            )
            continue

        # Extract bullet points from relevant sections
        if in_relevant_section:
            # Match bullet points (-, *, or numbered)
            bullet_match = re.match(r"^[-*]\s+(.+)$", stripped)
            if not bullet_match:
                bullet_match = re.match(r"^\d+[.)]\s+(.+)$", stripped)

            if bullet_match:
                convention_text = bullet_match.group(1).strip()
                # Filter out very short or empty conventions
                if len(convention_text) >= 5:
                    conventions.append(convention_text)

            # Also capture non-bullet text lines in relevant sections
            # (but not empty lines or table formatting)
            elif (
                stripped
                and not stripped.startswith("|")
                and not stripped.startswith("---")
                and len(stripped) >= 10
            ):
                conventions.append(stripped)

    return conventions
```
