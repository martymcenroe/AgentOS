```python
"""Utility to detect naming conventions, module patterns, framework usage from file contents.

Issue #401: Codebase Context Analysis for Requirements Workflow.

Provides regex-based heuristic analysis of source code files to detect:
- Naming conventions (snake_case, PascalCase, etc.)
- State management patterns (TypedDict, dataclass, BaseModel)
- Node/function patterns (functions returning dicts)
- Test conventions (pytest, unittest)
- Import styles (absolute vs relative)
- Framework detection from dependencies and import statements
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
_FRAMEWORK_MAP: dict[str, str] = {
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
    "starlette": "Starlette",
    "uvicorn": "Uvicorn",
}

# Import name -> display name for scanning import statements
_IMPORT_FRAMEWORK_MAP: dict[str, str] = {
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
    "starlette": "Starlette",
    "uvicorn": "Uvicorn",
}

# Regex patterns for detection
_SNAKE_CASE_RE = re.compile(r"^[a-z][a-z0-9_]*$")
_PASCAL_CASE_RE = re.compile(r"^[A-Z][a-zA-Z0-9]*$")
_CLASS_DEF_RE = re.compile(r"^class\s+([A-Za-z_]\w*)", re.MULTILINE)
_FUNCTION_DEF_RE = re.compile(r"^def\s+([a-z_]\w*)", re.MULTILINE)
_RETURN_DICT_RE = re.compile(
    r"(?:->.*dict|return\s+\{|return\s+dict\()", re.MULTILINE | re.IGNORECASE
)
_TYPEDDICT_RE = re.compile(
    r"(?:from\s+typing(?:_extensions)?\s+import\s+.*TypedDict|"
    r"class\s+\w+\(TypedDict\))",
    re.MULTILINE,
)
_DATACLASS_RE = re.compile(
    r"(?:from\s+dataclasses\s+import\s+.*dataclass|@dataclass)", re.MULTILINE
)
_BASEMODEL_RE = re.compile(
    r"(?:from\s+pydantic\s+import\s+.*BaseModel|class\s+\w+\(BaseModel\))",
    re.MULTILINE,
)
_PYTEST_RE = re.compile(
    r"(?:import\s+pytest|from\s+pytest\s+import|@pytest\.|def\s+test_)", re.MULTILINE
)
_UNITTEST_RE = re.compile(
    r"(?:import\s+unittest|from\s+unittest\s+import|class\s+\w+\(.*TestCase\))",
    re.MULTILINE,
)
_CONFTEST_RE = re.compile(r"@pytest\.fixture", re.MULTILINE)
_ABSOLUTE_IMPORT_RE = re.compile(
    r"^(?:from|import)\s+(?!\.)[a-zA-Z_]\w*", re.MULTILINE
)
_RELATIVE_IMPORT_RE = re.compile(r"^from\s+\.", re.MULTILINE)

# Convention header keywords for CLAUDE.md parsing
_CONVENTION_KEYWORDS = [
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

    # --- Naming conventions ---
    result["naming_convention"] = _detect_naming_convention(file_contents)

    # --- State pattern ---
    result["state_pattern"] = _detect_state_pattern(file_contents)

    # --- Node pattern ---
    result["node_pattern"] = _detect_node_pattern(file_contents)

    # --- Test pattern ---
    result["test_pattern"] = _detect_test_pattern(file_contents)

    # --- Import style ---
    result["import_style"] = _detect_import_style(file_contents)

    return result


def _detect_naming_convention(file_contents: dict[str, str]) -> str:
    """Detect naming conventions from filenames and class/function definitions.

    Args:
        file_contents: Dict mapping filename to file content.

    Returns:
        Description of detected naming convention, or "unknown".
    """
    parts: list[str] = []

    # Check filenames for snake_case
    python_files = [
        f for f in file_contents if f.endswith(".py") and f != "__init__.py"
    ]
    snake_case_files = 0
    for filename in python_files:
        # Get just the filename stem (no path, no extension)
        name = filename.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
        stem = name.rsplit(".", 1)[0]
        if _SNAKE_CASE_RE.match(stem):
            snake_case_files += 1

    if python_files and snake_case_files > 0:
        ratio = snake_case_files / len(python_files)
        if ratio >= 0.5:
            parts.append("snake_case modules")

    # Check for PascalCase classes
    pascal_classes = 0
    total_classes = 0
    for content in file_contents.values():
        class_matches = _CLASS_DEF_RE.findall(content)
        for class_name in class_matches:
            total_classes += 1
            if _PASCAL_CASE_RE.match(class_name):
                pascal_classes += 1

    if total_classes > 0 and pascal_classes > 0:
        ratio = pascal_classes / total_classes
        if ratio >= 0.5:
            parts.append("PascalCase classes")

    # Check for snake_case functions
    snake_functions = 0
    total_functions = 0
    for content in file_contents.values():
        func_matches = _FUNCTION_DEF_RE.findall(content)
        for func_name in func_matches:
            total_functions += 1
            if _SNAKE_CASE_RE.match(func_name):
                snake_functions += 1

    if total_functions > 0 and snake_functions > 0:
        ratio = snake_functions / total_functions
        if ratio >= 0.5:
            parts.append("snake_case functions")

    if parts:
        return ", ".join(parts)
    return "unknown"


def _detect_state_pattern(file_contents: dict[str, str]) -> str:
    """Detect state management pattern from file contents.

    Args:
        file_contents: Dict mapping filename to file content.

    Returns:
        Description of detected state pattern, or "unknown".
    """
    patterns_found: list[str] = []

    all_content = "\n".join(file_contents.values())

    if _TYPEDDICT_RE.search(all_content):
        patterns_found.append("TypedDict-based state")

    if _DATACLASS_RE.search(all_content):
        patterns_found.append("dataclass-based state")

    if _BASEMODEL_RE.search(all_content):
        patterns_found.append("Pydantic BaseModel state")

    if patterns_found:
        return ", ".join(patterns_found)
    return "unknown"


def _detect_node_pattern(file_contents: dict[str, str]) -> str:
    """Detect node/function patterns from file contents.

    Args:
        file_contents: Dict mapping filename to file content.

    Returns:
        Description of detected node pattern, or "unknown".
    """
    all_content = "\n".join(file_contents.values())

    dict_return_count = len(_RETURN_DICT_RE.findall(all_content))

    if dict_return_count >= 2:
        return "functions returning dict updates"
    elif dict_return_count == 1:
        return "functions returning dict updates"

    return "unknown"


def _detect_test_pattern(file_contents: dict[str, str]) -> str:
    """Detect test framework conventions from file contents.

    Args:
        file_contents: Dict mapping filename to file content.

    Returns:
        Description of detected test pattern, or "unknown".
    """
    all_content = "\n".join(file_contents.values())

    has_pytest = bool(_PYTEST_RE.search(all_content))
    has_unittest = bool(_UNITTEST_RE.search(all_content))
    has_conftest = bool(_CONFTEST_RE.search(all_content))

    parts: list[str] = []
    if has_pytest:
        if has_conftest:
            parts.append("pytest with fixtures in conftest.py")
        else:
            parts.append("pytest")
    if has_unittest:
        parts.append("unittest")

    if parts:
        return ", ".join(parts)
    return "unknown"


def _detect_import_style(file_contents: dict[str, str]) -> str:
    """Detect import style (absolute vs relative) from file contents.

    Args:
        file_contents: Dict mapping filename to file content.

    Returns:
        Description of detected import style, or "unknown".
    """
    absolute_count = 0
    relative_count = 0

    for content in file_contents.values():
        absolute_count += len(_ABSOLUTE_IMPORT_RE.findall(content))
        relative_count += len(_RELATIVE_IMPORT_RE.findall(content))

    total = absolute_count + relative_count
    if total == 0:
        return "unknown"

    abs_ratio = absolute_count / total
    rel_ratio = relative_count / total

    if abs_ratio >= 0.7:
        return "absolute imports from package root"
    elif rel_ratio >= 0.7:
        return "relative imports"
    elif absolute_count > 0 and relative_count > 0:
        return "mixed absolute and relative imports"

    return "unknown"


def detect_frameworks(
    dependency_list: list[str],
    file_contents: dict[str, str],
) -> list[str]:
    """Identify frameworks in use from dependency names and import statements.

    Maps known package names to display names:
        'langgraph' -> 'LangGraph', 'fastapi' -> 'FastAPI', etc.
    Also scans import statements in file_contents for additional detection.

    Args:
        dependency_list: List of dependency/package names (e.g., from pyproject.toml).
        file_contents: Dict mapping filename to file content for import scanning.

    Returns:
        Human-readable list like ['LangGraph', 'FastAPI', 'pytest'].
        Returns empty list if nothing detected.
    """
    detected: list[str] = []

    # Check dependency list against known frameworks
    for dep in dependency_list:
        # Normalize: lowercase, strip whitespace
        dep_normalized = dep.strip().lower()
        if dep_normalized in _FRAMEWORK_MAP:
            display_name = _FRAMEWORK_MAP[dep_normalized]
            if display_name not in detected:
                detected.append(display_name)

    # Scan import statements in file contents
    all_content = "\n".join(file_contents.values())

    # Match 'import X' and 'from X import ...'
    import_pattern = re.compile(
        r"^(?:import|from)\s+([a-zA-Z_][a-zA-Z0-9_]*)", re.MULTILINE
    )
    import_matches = import_pattern.findall(all_content)

    for import_name in import_matches:
        import_lower = import_name.lower()
        if import_lower in _IMPORT_FRAMEWORK_MAP:
            display_name = _IMPORT_FRAMEWORK_MAP[import_lower]
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

    # Split into lines for processing
    lines = content.split("\n")

    # Track whether we're in a convention-related section
    in_convention_section = False
    # Track code block state
    in_code_block = False
    code_block_is_rules = False

    for line in lines:
        stripped = line.strip()

        # Track code blocks
        if stripped.startswith("```"):
            if in_code_block:
                # Closing code block
                in_code_block = False
                code_block_is_rules = False
                continue
            else:
                # Opening code block - check if labeled as rules
                in_code_block = True
                block_label = stripped[3:].strip().lower()
                if any(kw in block_label for kw in _CONVENTION_KEYWORDS):
                    code_block_is_rules = True
                continue

        # Inside a rules-labeled code block, capture content
        if in_code_block and code_block_is_rules:
            if stripped:
                conventions.append(stripped)
            continue

        # Skip other code block content
        if in_code_block:
            continue

        # Check if this is a header line
        if stripped.startswith("#"):
            header_text = stripped.lstrip("#").strip().lower()
            in_convention_section = any(
                kw in header_text for kw in _CONVENTION_KEYWORDS
            )
            continue

        # If we're in a convention section, extract bullet points
        if in_convention_section:
            # Match bullet points: -, *, or numbered lists
            bullet_match = re.match(r"^[\-\*]\s+(.+)$", stripped)
            if bullet_match:
                convention_text = bullet_match.group(1).strip()
                if convention_text:
                    conventions.append(convention_text)
                continue

            numbered_match = re.match(r"^\d+[\.\)]\s+(.+)$", stripped)
            if numbered_match:
                convention_text = numbered_match.group(1).strip()
                if convention_text:
                    conventions.append(convention_text)
                continue

            # Non-empty, non-bullet line in convention section - include it
            # but only if it looks like content (not empty)
            if stripped and not stripped.startswith("|"):
                # Could be a paragraph under a convention header
                # Only add if it's substantial enough
                if len(stripped) > 10:
                    conventions.append(stripped)

    return conventions
```
