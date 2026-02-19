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


# Known package name -> display name mapping for framework detection
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
    "sqlalchemy": "SQLAlchemy",
    "pydantic": "Pydantic",
    "celery": "Celery",
    "redis": "Redis",
    "httpx": "httpx",
    "requests": "requests",
    "aiohttp": "aiohttp",
    "starlette": "Starlette",
    "typer": "Typer",
    "click": "Click",
    "rich": "Rich",
    "anthropic": "Anthropic SDK",
    "openai": "OpenAI SDK",
    "torch": "PyTorch",
    "tensorflow": "TensorFlow",
    "numpy": "NumPy",
    "pandas": "pandas",
    "scipy": "SciPy",
    "streamlit": "Streamlit",
    "gradio": "Gradio",
}

# Import name -> display name mapping (for import statement scanning)
IMPORT_FRAMEWORK_MAP: dict[str, str] = {
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
    "sqlalchemy": "SQLAlchemy",
    "pydantic": "Pydantic",
    "celery": "Celery",
    "redis": "Redis",
    "httpx": "httpx",
    "requests": "requests",
    "aiohttp": "aiohttp",
    "starlette": "Starlette",
    "typer": "Typer",
    "click": "Click",
    "rich": "Rich",
    "anthropic": "Anthropic SDK",
    "openai": "OpenAI SDK",
    "torch": "PyTorch",
    "tensorflow": "TensorFlow",
    "numpy": "NumPy",
    "pandas": "pandas",
    "scipy": "SciPy",
    "streamlit": "Streamlit",
    "gradio": "Gradio",
}

# Regex patterns for detecting naming conventions
_SNAKE_CASE_RE = re.compile(r"^[a-z][a-z0-9_]*$")
_PASCAL_CASE_RE = re.compile(r"^[A-Z][a-zA-Z0-9]*$")
_CAMEL_CASE_RE = re.compile(r"^[a-z][a-zA-Z0-9]*$")

# Regex for detecting class definitions with PascalCase
_CLASS_DEF_RE = re.compile(r"^class\s+([A-Z][a-zA-Z0-9_]*)")

# Regex for detecting function definitions
_FUNC_DEF_RE = re.compile(r"^def\s+([a-z_][a-z0-9_]*)\s*\(")

# Regex for detecting functions returning dict
_RETURN_DICT_RE = re.compile(r"return\s+\{")

# Regex for import statements
_IMPORT_RE = re.compile(r"^\s*(?:from\s+([\w.]+)\s+import|import\s+([\w.]+))")

# Regex for relative imports
_RELATIVE_IMPORT_RE = re.compile(r"^\s*from\s+\.+")

# Regex for absolute imports
_ABSOLUTE_IMPORT_RE = re.compile(r"^\s*(?:from\s+[a-zA-Z][\w.]*\s+import|import\s+[a-zA-Z][\w.]*)")

# State pattern detection regexes
_TYPEDDICT_RE = re.compile(r"(?:from\s+typing(?:_extensions)?\s+import\s+.*TypedDict|TypedDict)")
_DATACLASS_RE = re.compile(r"(?:from\s+dataclasses\s+import\s+.*dataclass|@dataclass)")
_BASEMODEL_RE = re.compile(r"(?:from\s+pydantic\s+import\s+.*BaseModel|class\s+\w+\(.*BaseModel.*\))")

# Test pattern detection regexes
_PYTEST_RE = re.compile(r"(?:import\s+pytest|from\s+pytest\s+import|@pytest\.)")
_UNITTEST_RE = re.compile(r"(?:import\s+unittest|from\s+unittest\s+import|class\s+\w+\(.*TestCase.*\))")
_CONFTEST_RE = re.compile(r"conftest\.py")

# Convention section header patterns for CLAUDE.md parsing
_CONVENTION_HEADER_RE = re.compile(
    r"^#{1,6}\s+.*(?:convention|rule|standard|constraint|style|guideline|requirement|pattern)",
    re.IGNORECASE,
)

# Bullet point pattern
_BULLET_RE = re.compile(r"^\s*[-*+]\s+(.+)$")

# Code block pattern (rules in fenced code blocks)
_CODE_BLOCK_START_RE = re.compile(r"^```(?:rules?|conventions?|standards?|constraints?)?$", re.IGNORECASE)
_CODE_BLOCK_END_RE = re.compile(r"^```\s*$")


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
        file_contents: Dict mapping filename -> file content string.

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
    """Detect naming conventions from filenames and class/function definitions.

    Args:
        file_contents: Dict mapping filename -> file content string.

    Returns:
        Description of naming convention, or "unknown" if undetectable.
    """
    conventions: list[str] = []

    # Check filenames for snake_case modules
    snake_case_files = 0
    total_py_files = 0
    for filename in file_contents:
        # Extract just the filename without path and extension
        basename = filename.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
        if basename.endswith(".py"):
            total_py_files += 1
            name_without_ext = basename[:-3]
            if name_without_ext.startswith("__"):
                continue  # Skip __init__, __main__, etc.
            if _SNAKE_CASE_RE.match(name_without_ext):
                snake_case_files += 1

    if total_py_files > 0 and snake_case_files > 0:
        conventions.append("snake_case modules")

    # Check for PascalCase classes and snake_case functions
    has_pascal_classes = False
    has_snake_functions = False

    for content in file_contents.values():
        for line in content.splitlines():
            stripped = line.strip()
            class_match = _CLASS_DEF_RE.match(stripped)
            if class_match:
                class_name = class_match.group(1)
                if _PASCAL_CASE_RE.match(class_name):
                    has_pascal_classes = True

            func_match = _FUNC_DEF_RE.match(stripped)
            if func_match:
                has_snake_functions = True

    if has_pascal_classes:
        conventions.append("PascalCase classes")
    if has_snake_functions:
        conventions.append("snake_case functions")

    if conventions:
        return ", ".join(conventions)
    return "unknown"


def _detect_state_pattern(file_contents: dict[str, str]) -> str:
    """Detect state management patterns from file contents.

    Args:
        file_contents: Dict mapping filename -> file content string.

    Returns:
        Description of state pattern, or "unknown" if undetectable.
    """
    patterns: list[str] = []

    all_content = "\n".join(file_contents.values())

    if _TYPEDDICT_RE.search(all_content):
        patterns.append("TypedDict-based state")
    if _DATACLASS_RE.search(all_content):
        patterns.append("dataclass-based state")
    if _BASEMODEL_RE.search(all_content):
        patterns.append("Pydantic BaseModel state")

    if patterns:
        return ", ".join(patterns)
    return "unknown"


def _detect_node_pattern(file_contents: dict[str, str]) -> str:
    """Detect function/node patterns from file contents.

    Args:
        file_contents: Dict mapping filename -> file content string.

    Returns:
        Description of node pattern, or "unknown" if undetectable.
    """
    dict_return_count = 0
    func_count = 0

    for content in file_contents.values():
        for line in content.splitlines():
            stripped = line.strip()
            if _FUNC_DEF_RE.match(stripped):
                func_count += 1
            if _RETURN_DICT_RE.search(stripped):
                dict_return_count += 1

    if dict_return_count > 0 and func_count > 0:
        return "functions returning dict updates"
    return "unknown"


def _detect_test_pattern(file_contents: dict[str, str]) -> str:
    """Detect test conventions from file contents.

    Args:
        file_contents: Dict mapping filename -> file content string.

    Returns:
        Description of test pattern, or "unknown" if undetectable.
    """
    patterns: list[str] = []

    all_content = "\n".join(file_contents.values())
    all_filenames = " ".join(file_contents.keys())

    has_pytest = bool(_PYTEST_RE.search(all_content))
    has_unittest = bool(_UNITTEST_RE.search(all_content))
    has_conftest = bool(_CONFTEST_RE.search(all_filenames))

    if has_pytest:
        if has_conftest:
            patterns.append("pytest with fixtures in conftest.py")
        else:
            patterns.append("pytest")
    if has_unittest:
        patterns.append("unittest")

    if patterns:
        return ", ".join(patterns)
    return "unknown"


def _detect_import_style(file_contents: dict[str, str]) -> str:
    """Detect import style (absolute vs relative) from file contents.

    Args:
        file_contents: Dict mapping filename -> file content string.

    Returns:
        Description of import style, or "unknown" if undetectable.
    """
    absolute_count = 0
    relative_count = 0

    for content in file_contents.values():
        for line in content.splitlines():
            if _RELATIVE_IMPORT_RE.match(line):
                relative_count += 1
            elif _ABSOLUTE_IMPORT_RE.match(line):
                absolute_count += 1

    if absolute_count == 0 and relative_count == 0:
        return "unknown"

    if absolute_count > relative_count:
        if relative_count > 0:
            return "mostly absolute imports"
        return "absolute imports from package root"
    elif relative_count > absolute_count:
        if absolute_count > 0:
            return "mostly relative imports"
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
        dependency_list: List of dependency package names (e.g., from pyproject.toml).
        file_contents: Dict mapping filename -> file content string.

    Returns:
        Human-readable list like ['LangGraph', 'FastAPI', 'pytest'].
        Returns empty list if nothing detected.
    """
    detected: dict[str, str] = {}  # display_name -> display_name (for dedup)

    # Check dependency list against known frameworks
    for dep in dependency_list:
        dep_lower = dep.lower().strip()
        if dep_lower in FRAMEWORK_MAP:
            display_name = FRAMEWORK_MAP[dep_lower]
            detected[display_name] = display_name

    # Scan import statements in file contents
    for content in file_contents.values():
        for line in content.splitlines():
            match = _IMPORT_RE.match(line)
            if match:
                # Get the top-level module name from the import
                module = match.group(1) or match.group(2)
                if module:
                    top_level = module.split(".")[0]
                    top_lower = top_level.lower()
                    if top_lower in IMPORT_FRAMEWORK_MAP:
                        display_name = IMPORT_FRAMEWORK_MAP[top_lower]
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
    lines = content.splitlines()

    in_convention_section = False
    in_rule_code_block = False
    section_depth = 0

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Check for code block boundaries
        if in_rule_code_block:
            if _CODE_BLOCK_END_RE.match(stripped):
                in_rule_code_block = False
                i += 1
                continue
            # Content inside a rules code block is a convention
            if stripped:
                conventions.append(stripped)
            i += 1
            continue

        # Check for rules/conventions code block start
        if _CODE_BLOCK_START_RE.match(stripped) and stripped != "```":
            in_rule_code_block = True
            i += 1
            continue

        # Check for regular code block (skip it entirely)
        if stripped.startswith("```"):
            i += 1
            # Skip until closing ```
            while i < len(lines):
                if lines[i].strip().startswith("```"):
                    break
                i += 1
            i += 1
            continue

        # Check for convention-related header
        if _CONVENTION_HEADER_RE.match(stripped):
            in_convention_section = True
            # Determine header depth for section scoping
            header_match = re.match(r"^(#{1,6})\s+", stripped)
            if header_match:
                section_depth = len(header_match.group(1))
            i += 1
            continue

        # Check if we've left the convention section (hit a same-or-higher-level header)
        if in_convention_section and stripped.startswith("#"):
            header_match = re.match(r"^(#{1,6})\s+", stripped)
            if header_match:
                new_depth = len(header_match.group(1))
                if new_depth <= section_depth:
                    in_convention_section = False
                    # Check if this new header is also a convention header
                    if _CONVENTION_HEADER_RE.match(stripped):
                        in_convention_section = True
                        section_depth = new_depth
            i += 1
            continue

        # Extract bullet points from convention sections
        if in_convention_section:
            bullet_match = _BULLET_RE.match(line)
            if bullet_match:
                convention_text = bullet_match.group(1).strip()
                if convention_text:
                    conventions.append(convention_text)

        i += 1

    return conventions
```
