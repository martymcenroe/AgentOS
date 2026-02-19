```python
"""Utility to detect naming conventions, module patterns, framework usage from file contents.

Issue #401: Codebase Context Analysis for Requirements Workflow.

Provides functions for scanning existing code to detect:
- Naming conventions (snake_case, PascalCase, etc.)
- State management patterns (TypedDict, dataclass, BaseModel)
- Node/function patterns (functions returning dicts)
- Test conventions (pytest, unittest)
- Import styles (absolute vs relative)
- Framework usage from dependencies and imports
- Coding conventions from CLAUDE.md files
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


# Mapping of known package names to display names for framework detection
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
    "httpx": "httpx",
    "requests": "Requests",
    "aiohttp": "aiohttp",
    "celery": "Celery",
    "redis": "Redis",
    "boto3": "AWS SDK (boto3)",
    "anthropic": "Anthropic SDK",
    "openai": "OpenAI SDK",
    "transformers": "Hugging Face Transformers",
    "torch": "PyTorch",
    "tensorflow": "TensorFlow",
    "numpy": "NumPy",
    "pandas": "pandas",
    "click": "Click",
    "typer": "Typer",
    "rich": "Rich",
    "starlette": "Starlette",
    "uvicorn": "Uvicorn",
}

# Mapping of import module names to display names (for import-based detection)
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
    "httpx": "httpx",
    "requests": "Requests",
    "aiohttp": "aiohttp",
    "celery": "Celery",
    "redis": "Redis",
    "boto3": "AWS SDK (boto3)",
    "anthropic": "Anthropic SDK",
    "openai": "OpenAI SDK",
    "transformers": "Hugging Face Transformers",
    "torch": "PyTorch",
    "tensorflow": "TensorFlow",
    "numpy": "NumPy",
    "pandas": "pandas",
    "click": "Click",
    "typer": "Typer",
    "rich": "Rich",
    "starlette": "Starlette",
    "uvicorn": "Uvicorn",
}

# Headers that indicate convention/rule sections in CLAUDE.md
_CONVENTION_HEADER_KEYWORDS = [
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
    if not file_contents:
        return PatternAnalysis(
            naming_convention="unknown",
            state_pattern="unknown",
            node_pattern="unknown",
            test_pattern="unknown",
            import_style="unknown",
        )

    naming = _detect_naming_convention(file_contents)
    state = _detect_state_pattern(file_contents)
    node = _detect_node_pattern(file_contents)
    test = _detect_test_pattern(file_contents)
    imports = _detect_import_style(file_contents)

    return PatternAnalysis(
        naming_convention=naming,
        state_pattern=state,
        node_pattern=node,
        test_pattern=test,
        import_style=imports,
    )


def _detect_naming_convention(file_contents: dict[str, str]) -> str:
    """Detect naming conventions from filenames and class definitions.

    Args:
        file_contents: Dict mapping filename to file content string.

    Returns:
        Description of detected naming convention, or "unknown".
    """
    conventions: list[str] = []

    # Check filenames for snake_case pattern
    snake_case_files = 0
    total_py_files = 0
    for filename in file_contents:
        # Extract just the filename without path
        basename = filename.rsplit("/", 1)[-1] if "/" in filename else filename
        basename = basename.rsplit("\\", 1)[-1] if "\\" in basename else basename

        if basename.endswith(".py"):
            total_py_files += 1
            # snake_case: lowercase with underscores, no uppercase
            name_part = basename[:-3]  # Remove .py
            if name_part and re.match(r"^[a-z_][a-z0-9_]*$", name_part):
                snake_case_files += 1

    if total_py_files > 0 and snake_case_files >= total_py_files * 0.5:
        conventions.append("snake_case modules")

    # Check for PascalCase class definitions
    pascal_classes = 0
    total_classes = 0
    for content in file_contents.values():
        class_matches = re.findall(r"class\s+([A-Za-z_]\w*)", content)
        for cls_name in class_matches:
            total_classes += 1
            # PascalCase: starts with uppercase, has at least one lowercase
            if re.match(r"^[A-Z][a-zA-Z0-9]*$", cls_name) and any(
                c.islower() for c in cls_name
            ):
                pascal_classes += 1

    if total_classes > 0 and pascal_classes >= total_classes * 0.5:
        conventions.append("PascalCase classes")

    # Check for snake_case function names
    snake_funcs = 0
    total_funcs = 0
    for content in file_contents.values():
        func_matches = re.findall(r"def\s+([A-Za-z_]\w*)", content)
        for func_name in func_matches:
            if func_name.startswith("__"):
                continue  # Skip dunder methods
            total_funcs += 1
            if re.match(r"^[a-z_][a-z0-9_]*$", func_name):
                snake_funcs += 1

    if total_funcs > 0 and snake_funcs >= total_funcs * 0.5:
        if "snake_case modules" not in conventions:
            conventions.append("snake_case functions")
        else:
            conventions.append("snake_case functions")

    if not conventions:
        return "unknown"

    return ", ".join(conventions)


def _detect_state_pattern(file_contents: dict[str, str]) -> str:
    """Detect state management patterns from imports and usage.

    Args:
        file_contents: Dict mapping filename to file content string.

    Returns:
        Description of detected state pattern, or "unknown".
    """
    patterns_found: list[str] = []

    all_content = "\n".join(file_contents.values())

    # Check for TypedDict
    if re.search(
        r"(?:from\s+typing(?:_extensions)?\s+import\s+.*TypedDict|"
        r"import\s+typing.*TypedDict|"
        r"class\s+\w+\s*\(\s*TypedDict\s*\))",
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
        r"class\s+\w+\s*\(\s*BaseModel\s*\))",
        all_content,
    ):
        patterns_found.append("Pydantic BaseModel state")

    # Check for LangGraph state specifically
    if re.search(r"langgraph", all_content, re.IGNORECASE) and "TypedDict" in str(
        patterns_found
    ):
        return "TypedDict-based LangGraph state"

    if not patterns_found:
        return "unknown"

    return ", ".join(patterns_found)


def _detect_node_pattern(file_contents: dict[str, str]) -> str:
    """Detect node/function patterns.

    Args:
        file_contents: Dict mapping filename to file content string.

    Returns:
        Description of detected node pattern, or "unknown".
    """
    all_content = "\n".join(file_contents.values())

    # Check for functions returning dict (LangGraph node pattern)
    # Look for "-> dict" return type annotations
    dict_return_funcs = re.findall(
        r"def\s+\w+\s*\([^)]*\)\s*->\s*dict", all_content
    )

    if len(dict_return_funcs) >= 2:
        return "functions returning dict updates"

    # Check for class-based nodes
    if re.search(r"class\s+\w+Node", all_content):
        return "class-based nodes"

    # Single function returning dict
    if dict_return_funcs:
        return "functions returning dict updates"

    return "unknown"


def _detect_test_pattern(file_contents: dict[str, str]) -> str:
    """Detect test conventions.

    Args:
        file_contents: Dict mapping filename to file content string.

    Returns:
        Description of detected test pattern, or "unknown".
    """
    all_content = "\n".join(file_contents.values())
    patterns: list[str] = []

    # Check for pytest
    has_pytest = bool(
        re.search(r"(?:import\s+pytest|from\s+pytest|@pytest\.)", all_content)
    )
    if has_pytest:
        patterns.append("pytest")

    # Check for pytest fixtures
    has_fixtures = bool(re.search(r"@pytest\.fixture", all_content))
    if has_fixtures:
        patterns.append("fixtures")

    # Check for conftest.py
    has_conftest = any("conftest" in filename for filename in file_contents)
    if has_conftest:
        patterns.append("conftest.py")

    # Check for unittest
    has_unittest = bool(
        re.search(
            r"(?:import\s+unittest|from\s+unittest|class\s+\w+\(.*TestCase\))",
            all_content,
        )
    )
    if has_unittest and not has_pytest:
        patterns.append("unittest")

    if not patterns:
        return "unknown"

    if "pytest" in patterns:
        extras = [p for p in patterns if p != "pytest"]
        if extras:
            return "pytest with " + " and ".join(extras)
        return "pytest"

    return ", ".join(patterns)


def _detect_import_style(file_contents: dict[str, str]) -> str:
    """Detect import style (absolute vs relative).

    Args:
        file_contents: Dict mapping filename to file content string.

    Returns:
        Description of detected import style, or "unknown".
    """
    absolute_count = 0
    relative_count = 0

    for content in file_contents.values():
        # Count absolute imports (from package.module import ...)
        absolute_matches = re.findall(
            r"^from\s+[a-zA-Z_]\w*(?:\.[a-zA-Z_]\w*)*\s+import", content, re.MULTILINE
        )
        absolute_count += len(absolute_matches)

        # Count relative imports (from . import ... or from .module import ...)
        relative_matches = re.findall(
            r"^from\s+\.+\w*\s+import", content, re.MULTILINE
        )
        relative_count += len(relative_matches)

    total = absolute_count + relative_count
    if total == 0:
        return "unknown"

    if absolute_count > relative_count * 2:
        return "absolute imports from package root"
    elif relative_count > absolute_count * 2:
        return "relative imports"
    elif absolute_count > 0 and relative_count > 0:
        return "mixed absolute and relative imports"
    elif absolute_count > 0:
        return "absolute imports from package root"
    elif relative_count > 0:
        return "relative imports"

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
        file_contents: Dict mapping filename to file content string.

    Returns:
        Human-readable list like ['LangGraph', 'FastAPI', 'pytest'].
        Returns empty list if nothing detected.
    """
    detected: list[str] = []
    seen_display_names: set[str] = set()

    # Detect from dependency list
    for dep in dependency_list:
        dep_lower = dep.lower().strip()
        if dep_lower in FRAMEWORK_MAP:
            display_name = FRAMEWORK_MAP[dep_lower]
            if display_name not in seen_display_names:
                detected.append(display_name)
                seen_display_names.add(display_name)

    # Detect from import statements in file contents
    all_content = "\n".join(file_contents.values())

    # Match "import X" and "from X import ..." patterns
    import_matches = re.findall(
        r"^(?:import|from)\s+([a-zA-Z_]\w*)", all_content, re.MULTILINE
    )

    for module_name in import_matches:
        module_lower = module_name.lower()
        if module_lower in IMPORT_FRAMEWORK_MAP:
            display_name = IMPORT_FRAMEWORK_MAP[module_lower]
            if display_name not in seen_display_names:
                detected.append(display_name)
                seen_display_names.add(display_name)

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
    lines = content.split("\n")

    in_convention_section = False
    in_code_block = False
    code_block_is_rules = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Track code blocks
        if stripped.startswith("```"):
            if in_code_block:
                in_code_block = False
                code_block_is_rules = False
                continue
            else:
                in_code_block = True
                # Check if code block label suggests rules
                block_label = stripped[3:].strip().lower()
                if any(
                    kw in block_label for kw in _CONVENTION_HEADER_KEYWORDS
                ):
                    code_block_is_rules = True
                continue

        # Extract from rule-labeled code blocks
        if in_code_block and code_block_is_rules:
            if stripped:
                conventions.append(stripped)
            continue

        # Skip content inside non-rule code blocks
        if in_code_block:
            continue

        # Check for section headers containing convention keywords
        if stripped.startswith("#"):
            header_text = stripped.lstrip("#").strip().lower()
            in_convention_section = any(
                kw in header_text for kw in _CONVENTION_HEADER_KEYWORDS
            )
            continue

        # Extract bullet points under convention sections
        if in_convention_section:
            # Match bullet points: "- item", "* item", "• item"
            bullet_match = re.match(r"^\s*[-*•]\s+(.+)$", line)
            if bullet_match:
                bullet_text = bullet_match.group(1).strip()
                if bullet_text:
                    conventions.append(bullet_text)
            # Empty line might end the section (but only if followed by
            # non-bullet content)
            elif not stripped:
                # Look ahead: if next non-empty line is not a bullet, end section
                for j in range(i + 1, min(i + 3, len(lines))):
                    next_stripped = lines[j].strip()
                    if next_stripped:
                        if not re.match(r"^\s*[-*•]\s+", lines[j]):
                            # Check if it's a sub-header that's also a convention header
                            if next_stripped.startswith("#"):
                                next_header = next_stripped.lstrip("#").strip().lower()
                                if not any(
                                    kw in next_header
                                    for kw in _CONVENTION_HEADER_KEYWORDS
                                ):
                                    in_convention_section = False
                            else:
                                in_convention_section = False
                        break
            # Non-header, non-bullet, non-empty text might also be a convention
            # if it's a continuation or a table row
            elif stripped.startswith("|"):
                # Table row - extract cell contents
                cells = [c.strip() for c in stripped.split("|") if c.strip()]
                if cells and not all(c.startswith("-") for c in cells):
                    convention_text = " | ".join(cells)
                    if convention_text:
                        conventions.append(convention_text)

    return conventions
```
