```python
"""Utility to detect naming conventions, module patterns, framework usage from file contents.

Issue #401: Codebase Context Analysis for Requirements Workflow.

Provides regex-based heuristics for scanning existing code patterns
including naming conventions, state management approaches, test
conventions, import styles, and framework detection. All functions
return sensible defaults ("unknown" or empty lists) when patterns
cannot be detected.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import TypedDict

logger = logging.getLogger(__name__)


class PatternAnalysis(TypedDict):
    """Results of scanning existing code patterns."""

    naming_convention: str  # e.g., "snake_case modules, PascalCase classes"
    state_pattern: str  # e.g., "TypedDict-based LangGraph state"
    node_pattern: str  # e.g., "functions returning dict updates"
    test_pattern: str  # e.g., "pytest with fixtures in conftest.py"
    import_style: str  # e.g., "absolute imports from package root"


# Known package-to-display-name mappings for framework detection.
_FRAMEWORK_MAP: dict[str, str] = {
    "langgraph": "LangGraph",
    "langchain": "LangChain",
    "langchain-core": "LangChain Core",
    "langsmith": "LangSmith",
    "fastapi": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "starlette": "Starlette",
    "uvicorn": "Uvicorn",
    "pytest": "pytest",
    "unittest": "unittest",
    "pydantic": "Pydantic",
    "sqlalchemy": "SQLAlchemy",
    "alembic": "Alembic",
    "celery": "Celery",
    "redis": "Redis",
    "httpx": "httpx",
    "requests": "requests",
    "aiohttp": "aiohttp",
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
    "boto3": "AWS SDK (boto3)",
    "docker": "Docker SDK",
    "kubernetes": "Kubernetes SDK",
    "react": "React",
    "next": "Next.js",
    "express": "Express",
    "vue": "Vue.js",
    "angular": "Angular",
    "svelte": "Svelte",
    "tailwindcss": "Tailwind CSS",
}

# Import patterns that map to framework display names.
# Keys are regex patterns matched against import statements.
_IMPORT_FRAMEWORK_MAP: dict[str, str] = {
    r"(?:from|import)\s+langgraph": "LangGraph",
    r"(?:from|import)\s+langchain": "LangChain",
    r"(?:from|import)\s+fastapi": "FastAPI",
    r"(?:from|import)\s+flask": "Flask",
    r"(?:from|import)\s+django": "Django",
    r"(?:from|import)\s+starlette": "Starlette",
    r"(?:from|import)\s+pydantic": "Pydantic",
    r"(?:from|import)\s+sqlalchemy": "SQLAlchemy",
    r"(?:from|import)\s+celery": "Celery",
    r"(?:from|import)\s+httpx": "httpx",
    r"(?:from|import)\s+requests": "requests",
    r"(?:from|import)\s+aiohttp": "aiohttp",
    r"(?:from|import)\s+typer": "Typer",
    r"(?:from|import)\s+click": "Click",
    r"(?:from|import)\s+rich": "Rich",
    r"(?:from|import)\s+anthropic": "Anthropic SDK",
    r"(?:from|import)\s+openai": "OpenAI SDK",
    r"(?:from|import)\s+torch": "PyTorch",
    r"(?:from|import)\s+tensorflow": "TensorFlow",
    r"(?:from|import)\s+numpy": "NumPy",
    r"(?:from|import)\s+pandas": "pandas",
    r"(?:from|import)\s+streamlit": "Streamlit",
    r"(?:from|import)\s+gradio": "Gradio",
    r"(?:from|import)\s+boto3": "AWS SDK (boto3)",
    r"(?:from|import)\s+pytest": "pytest",
}

# Section header keywords that indicate conventions in CLAUDE.md.
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

    - **naming_convention**: checks for snake_case filenames, PascalCase classes
    - **state_pattern**: looks for TypedDict, dataclass, BaseModel imports
    - **node_pattern**: looks for functions returning dict
    - **test_pattern**: looks for pytest, unittest patterns
    - **import_style**: checks absolute vs relative import prevalence

    Args:
        file_contents: Mapping of file paths/names to their text content.

    Returns:
        ``PatternAnalysis`` with ``"unknown"`` for any undetectable field.
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
        file_contents: Mapping of file paths to contents.

    Returns:
        Description of naming convention or ``"unknown"``.
    """
    parts: list[str] = []

    # Check filenames for snake_case pattern
    snake_case_files = 0
    camel_case_files = 0
    total_files = 0

    for filepath in file_contents:
        name = Path(filepath).stem
        if name.startswith("__") or name.startswith("."):
            continue
        total_files += 1
        # snake_case: all lowercase with underscores
        if re.match(r"^[a-z][a-z0-9_]*$", name):
            snake_case_files += 1
        # camelCase or PascalCase filename
        elif re.match(r"^[a-zA-Z][a-zA-Z0-9]*$", name) and any(
            c.isupper() for c in name[1:]
        ):
            camel_case_files += 1

    if total_files > 0:
        if snake_case_files > camel_case_files:
            parts.append("snake_case modules")
        elif camel_case_files > snake_case_files:
            parts.append("camelCase modules")

    # Check for class naming patterns in content
    pascal_classes = 0
    all_classes = 0
    for content in file_contents.values():
        for match in re.finditer(r"^class\s+([A-Za-z_]\w*)", content, re.MULTILINE):
            all_classes += 1
            class_name = match.group(1)
            if re.match(r"^[A-Z][a-zA-Z0-9]*$", class_name):
                pascal_classes += 1

    if all_classes > 0 and pascal_classes > all_classes * 0.5:
        parts.append("PascalCase classes")

    # Check for function naming (snake_case functions)
    snake_funcs = 0
    all_funcs = 0
    for content in file_contents.values():
        for match in re.finditer(
            r"^(?:def|async\s+def)\s+([A-Za-z_]\w*)", content, re.MULTILINE
        ):
            func_name = match.group(1)
            if func_name.startswith("__"):
                continue
            all_funcs += 1
            if re.match(r"^[a-z_][a-z0-9_]*$", func_name):
                snake_funcs += 1

    if all_funcs > 0 and snake_funcs > all_funcs * 0.5:
        parts.append("snake_case functions")

    return ", ".join(parts) if parts else "unknown"


def _detect_state_pattern(file_contents: dict[str, str]) -> str:
    """Detect state management patterns from imports and class definitions.

    Args:
        file_contents: Mapping of file paths to contents.

    Returns:
        Description of state pattern or ``"unknown"``.
    """
    patterns_found: list[str] = []

    all_content = "\n".join(file_contents.values())

    # TypedDict
    if re.search(
        r"(?:from\s+typing(?:_extensions)?\s+import\s+.*TypedDict"
        r"|import\s+typing.*\bTypedDict\b"
        r"|class\s+\w+\(.*TypedDict.*\))",
        all_content,
    ):
        patterns_found.append("TypedDict")

    # dataclass
    if re.search(
        r"(?:from\s+dataclasses\s+import\s+.*dataclass"
        r"|@dataclass)",
        all_content,
    ):
        patterns_found.append("dataclass")

    # Pydantic BaseModel
    if re.search(
        r"(?:from\s+pydantic\s+import\s+.*BaseModel"
        r"|class\s+\w+\(.*BaseModel.*\))",
        all_content,
    ):
        patterns_found.append("Pydantic BaseModel")

    # attrs
    if re.search(
        r"(?:import\s+attr|from\s+attr[s]?\s+import|@attr\.s|@attrs)",
        all_content,
    ):
        patterns_found.append("attrs")

    # NamedTuple
    if re.search(
        r"(?:from\s+typing\s+import\s+.*NamedTuple"
        r"|class\s+\w+\(.*NamedTuple.*\))",
        all_content,
    ):
        patterns_found.append("NamedTuple")

    if not patterns_found:
        return "unknown"

    # Build descriptive string
    if "TypedDict" in patterns_found:
        # Check specifically for LangGraph state pattern
        if re.search(r"(?:langgraph|StateGraph|state_graph)", all_content):
            return "TypedDict-based LangGraph state"
        return "TypedDict-based state"

    return ", ".join(patterns_found)


def _detect_node_pattern(file_contents: dict[str, str]) -> str:
    """Detect node/function patterns (e.g., LangGraph node functions).

    Args:
        file_contents: Mapping of file paths to contents.

    Returns:
        Description of node pattern or ``"unknown"``.
    """
    all_content = "\n".join(file_contents.values())

    # Functions accepting state dict and returning dict
    dict_return_funcs = len(
        re.findall(
            r"def\s+\w+\(.*?(?:state|ctx).*?\).*?->.*?dict",
            all_content,
            re.IGNORECASE,
        )
    )

    # Functions with state: dict parameter
    state_param_funcs = len(
        re.findall(
            r"def\s+\w+\(\s*state\s*:\s*dict",
            all_content,
        )
    )

    # Check for explicit LangGraph node patterns
    has_langgraph = bool(re.search(r"langgraph|StateGraph|add_node", all_content))

    if has_langgraph and (dict_return_funcs > 0 or state_param_funcs > 0):
        return "LangGraph nodes: functions accepting state dict, returning dict updates"

    if dict_return_funcs > 0 or state_param_funcs > 0:
        return "functions returning dict updates"

    # Check for class-based handlers
    class_handlers = len(
        re.findall(
            r"class\s+\w+(?:Node|Handler|Processor|Worker)",
            all_content,
        )
    )
    if class_handlers > 0:
        return "class-based node/handler pattern"

    return "unknown"


def _detect_test_pattern(file_contents: dict[str, str]) -> str:
    """Detect testing framework and conventions.

    Args:
        file_contents: Mapping of file paths to contents.

    Returns:
        Description of test pattern or ``"unknown"``.
    """
    all_content = "\n".join(file_contents.values())
    parts: list[str] = []

    # pytest
    has_pytest = bool(
        re.search(r"(?:import\s+pytest|from\s+pytest|@pytest\.)", all_content)
    )
    if has_pytest:
        parts.append("pytest")

    # pytest fixtures
    has_fixtures = bool(re.search(r"@pytest\.fixture", all_content))
    if has_fixtures:
        parts.append("with fixtures")

    # Check for conftest.py in file paths
    has_conftest = any("conftest" in fp.lower() for fp in file_contents)
    if has_conftest:
        parts.append("in conftest.py")

    # unittest
    has_unittest = bool(
        re.search(
            r"(?:import\s+unittest|from\s+unittest|class\s+\w+\(.*TestCase.*\))",
            all_content,
        )
    )
    if has_unittest and not has_pytest:
        parts.append("unittest")

    # Check for test file naming pattern
    test_files = [
        fp for fp in file_contents if re.search(r"(?:^|/)test_\w+\.py$", fp)
    ]
    if test_files:
        parts.append("test_ prefix files")

    if not parts:
        return "unknown"

    return " ".join(parts)


def _detect_import_style(file_contents: dict[str, str]) -> str:
    """Detect absolute vs relative import prevalence.

    Args:
        file_contents: Mapping of file paths to contents.

    Returns:
        Description of import style or ``"unknown"``.
    """
    absolute_imports = 0
    relative_imports = 0

    for content in file_contents.values():
        # Absolute imports: from package.module import ...
        absolute_imports += len(
            re.findall(
                r"^from\s+[a-zA-Z_]\w*(?:\.[a-zA-Z_]\w*)+\s+import",
                content,
                re.MULTILINE,
            )
        )
        # Relative imports: from . import ... or from .module import ...
        relative_imports += len(
            re.findall(r"^from\s+\.+", content, re.MULTILINE)
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

    Maps known package names to display names::

        'langgraph' -> 'LangGraph', 'fastapi' -> 'FastAPI', etc.

    Also scans import statements in *file_contents* for additional detection.

    Args:
        dependency_list: List of dependency package names (e.g. from
            pyproject.toml or package.json).
        file_contents: Mapping of file paths to their text content.

    Returns:
        Human-readable list like ``['LangGraph', 'FastAPI', 'pytest']``.
        Returns empty list if nothing detected.
    """
    # Use a dict to preserve insertion order and deduplicate by display name
    detected: dict[str, None] = {}

    # 1. Match from dependency list
    for dep in dependency_list:
        dep_lower = dep.strip().lower()
        if dep_lower in _FRAMEWORK_MAP:
            display_name = _FRAMEWORK_MAP[dep_lower]
            if display_name not in detected:
                detected[display_name] = None

    # 2. Scan import statements in file contents
    all_content = "\n".join(file_contents.values()) if file_contents else ""

    if all_content:
        for pattern, display_name in _IMPORT_FRAMEWORK_MAP.items():
            if display_name not in detected and re.search(pattern, all_content):
                detected[display_name] = None

    return list(detected.keys())


def extract_conventions_from_claude_md(content: str) -> list[str]:
    """Parse CLAUDE.md to extract coding conventions, rules, and constraints
    that the LLD must respect.

    Looks for sections with headers containing 'convention', 'rule',
    'standard', 'constraint', 'style', or bullet-pointed lists under
    such headers. Also extracts content from code blocks labeled as rules.

    Args:
        content: Raw text content of a CLAUDE.md file.

    Returns:
        List of convention strings. Empty list if none found.
    """
    if not content or not content.strip():
        return []

    conventions: list[str] = []
    lines = content.splitlines()

    # Track whether we're inside a relevant section
    in_relevant_section = False
    # Track code blocks to extract rule-labeled blocks
    in_code_block = False
    code_block_is_rules = False
    code_block_lines: list[str] = []

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Handle code blocks
        if stripped.startswith("```"):
            if in_code_block:
                # Closing a code block
                if code_block_is_rules and code_block_lines:
                    # Extract the code block content as a convention
                    block_content = "\n".join(code_block_lines).strip()
                    if block_content:
                        conventions.append(block_content)
                in_code_block = False
                code_block_is_rules = False
                code_block_lines = []
                continue
            else:
                # Opening a code block — check if it's labeled as rules
                in_code_block = True
                label = stripped[3:].strip().lower()
                code_block_is_rules = any(
                    kw in label for kw in ("rule", "convention", "constraint")
                )
                code_block_lines = []
                continue

        if in_code_block:
            if code_block_is_rules:
                code_block_lines.append(stripped)
            continue

        # Check for headers that indicate convention sections
        header_match = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if header_match:
            header_text = header_match.group(2).lower()
            header_level = len(header_match.group(1))

            # Check if this header matches convention keywords
            if any(kw in header_text for kw in _CONVENTION_HEADER_KEYWORDS):
                in_relevant_section = True
                continue
            else:
                # A new section header that doesn't match — stop collecting
                # only if same level or higher (less specific)
                if in_relevant_section and header_level <= 3:
                    in_relevant_section = False
                continue

        # If in a relevant section, collect bullet points and table rows
        if in_relevant_section:
            # Bullet points (-, *, +)
            bullet_match = re.match(r"^[-*+]\s+(.+)$", stripped)
            if bullet_match:
                convention_text = bullet_match.group(1).strip()
                if convention_text and len(convention_text) >= 5:
                    conventions.append(convention_text)
                continue

            # Numbered list items
            numbered_match = re.match(r"^\d+[.)]\s+(.+)$", stripped)
            if numbered_match:
                convention_text = numbered_match.group(1).strip()
                if convention_text and len(convention_text) >= 5:
                    conventions.append(convention_text)
                continue

            # Table rows (pipes)
            if stripped.startswith("|") and stripped.endswith("|"):
                # Skip separator rows
                if re.match(r"^\|[\s\-:|]+\|$", stripped):
                    continue
                # Skip header rows (first row after a blank or heading)
                # Extract cells and add as convention if meaningful
                cells = [
                    c.strip()
                    for c in stripped.strip("|").split("|")
                    if c.strip()
                ]
                if cells and len(cells) >= 2:
                    row_text = " | ".join(cells)
                    if len(row_text) >= 5:
                        conventions.append(row_text)
                continue

            # Non-empty, non-bullet text in relevant section — could be
            # a paragraph rule. Only collect if not too long (likely prose).
            if stripped and len(stripped) >= 10 and len(stripped) <= 200:
                # Check it's not a table separator or decoration
                if not re.match(r"^[-=_*|]+$", stripped):
                    conventions.append(stripped)

    return conventions
```
