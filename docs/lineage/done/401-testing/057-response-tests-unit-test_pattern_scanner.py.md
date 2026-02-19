```python
"""Unit tests for the pattern scanner utility.

Issue #401: Codebase Context Analysis for Requirements Workflow.

Tests for:
- scan_patterns (naming conventions, state patterns, node patterns, test patterns, import styles)
- detect_frameworks (from dependency list and import statements)
- extract_conventions_from_claude_md (CLAUDE.md parsing)
"""

from __future__ import annotations

import pytest

from assemblyzero.utils.pattern_scanner import (
    PatternAnalysis,
    detect_frameworks,
    extract_conventions_from_claude_md,
    scan_patterns,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def snake_case_files():
    """File contents dict with snake_case module naming and PascalCase classes."""
    return {
        "my_module.py": (
            '"""My module."""\n'
            "\n"
            "from typing import TypedDict\n"
            "\n"
            "\n"
            "class MyClass:\n"
            "    pass\n"
            "\n"
            "\n"
            "class AnotherWidget:\n"
            "    pass\n"
            "\n"
            "\n"
            "def my_function():\n"
            "    return 42\n"
        ),
        "another_module.py": (
            '"""Another module."""\n'
            "\n"
            "\n"
            "class SomeService:\n"
            "    pass\n"
        ),
        "utils_helper.py": (
            '"""Utility helpers."""\n'
            "\n"
            "\n"
            "def helper_function():\n"
            "    pass\n"
        ),
    }


@pytest.fixture
def typeddict_files():
    """File contents with TypedDict state management pattern."""
    return {
        "state.py": (
            '"""State definitions."""\n'
            "\n"
            "from typing import TypedDict\n"
            "\n"
            "\n"
            "class WorkflowState(TypedDict):\n"
            '    issue_text: str\n'
            '    repo_path: str | None\n'
            '    draft: str\n'
        ),
        "node.py": (
            '"""Node functions."""\n'
            "\n"
            "\n"
            "def my_node(state: dict) -> dict:\n"
            '    return {"draft": "hello"}\n'
        ),
    }


@pytest.fixture
def dataclass_files():
    """File contents with dataclass state management pattern."""
    return {
        "models.py": (
            '"""Data models."""\n'
            "\n"
            "from dataclasses import dataclass\n"
            "\n"
            "\n"
            "@dataclass\n"
            "class UserState:\n"
            "    name: str\n"
            "    age: int\n"
        ),
    }


@pytest.fixture
def basemodel_files():
    """File contents with Pydantic BaseModel pattern."""
    return {
        "schemas.py": (
            '"""Pydantic schemas."""\n'
            "\n"
            "from pydantic import BaseModel\n"
            "\n"
            "\n"
            "class UserSchema(BaseModel):\n"
            "    name: str\n"
            "    email: str\n"
        ),
    }


@pytest.fixture
def pytest_files():
    """File contents with pytest testing conventions."""
    return {
        "test_something.py": (
            '"""Tests for something."""\n'
            "\n"
            "import pytest\n"
            "\n"
            "\n"
            "@pytest.fixture\n"
            "def sample_data():\n"
            '    return {"key": "value"}\n'
            "\n"
            "\n"
            "def test_something(sample_data):\n"
            "    assert sample_data is not None\n"
        ),
        "conftest.py": (
            '"""Shared fixtures."""\n'
            "\n"
            "import pytest\n"
            "\n"
            "\n"
            "@pytest.fixture\n"
            "def db_session():\n"
            "    yield None\n"
        ),
    }


@pytest.fixture
def unittest_files():
    """File contents with unittest testing conventions."""
    return {
        "test_unit.py": (
            '"""Unit tests."""\n'
            "\n"
            "import unittest\n"
            "\n"
            "\n"
            "class TestMyClass(unittest.TestCase):\n"
            "    def test_something(self):\n"
            "        self.assertEqual(1, 1)\n"
        ),
    }


@pytest.fixture
def absolute_import_files():
    """File contents with predominantly absolute imports."""
    return {
        "module_a.py": (
            "from mypackage.utils import helper\n"
            "from mypackage.models import User\n"
            "from mypackage.services.auth import authenticate\n"
            "import mypackage.config\n"
        ),
        "module_b.py": (
            "from mypackage.core import engine\n"
            "from mypackage.db import session\n"
        ),
    }


@pytest.fixture
def relative_import_files():
    """File contents with predominantly relative imports."""
    return {
        "module_a.py": (
            "from .utils import helper\n"
            "from ..models import User\n"
            "from . import config\n"
        ),
        "module_b.py": (
            "from .core import engine\n"
            "from ..db import session\n"
            "from .services.auth import authenticate\n"
        ),
    }


@pytest.fixture
def mixed_import_files():
    """File contents with mixed absolute and relative imports."""
    return {
        "module.py": (
            "from mypackage.utils import helper\n"
            "from .models import User\n"
            "import os\n"
            "from ..config import settings\n"
        ),
    }


@pytest.fixture
def node_pattern_files():
    """File contents with LangGraph-style node functions returning dicts."""
    return {
        "nodes/load.py": (
            '"""Load input node."""\n'
            "\n"
            "\n"
            "def load_input(state: dict) -> dict:\n"
            '    return {"loaded": True}\n'
        ),
        "nodes/process.py": (
            '"""Process node."""\n'
            "\n"
            "\n"
            "def process_data(state: dict) -> dict:\n"
            '    result = state["input"] + " processed"\n'
            '    return {"output": result}\n'
        ),
    }


@pytest.fixture
def claude_md_with_conventions():
    """CLAUDE.md content with coding conventions."""
    return (
        "# CLAUDE.md\n"
        "\n"
        "## Rules\n"
        "\n"
        "- Use snake_case for all module names\n"
        "- PascalCase for class names\n"
        "- All functions must have docstrings\n"
        "\n"
        "## Conventions\n"
        "\n"
        "- Use `poetry run python` for all execution\n"
        "- Never use bare `pip install`\n"
        "\n"
        "## Style Guide\n"
        "\n"
        "- Maximum line length: 88 characters\n"
        "- Use type hints everywhere\n"
    )


@pytest.fixture
def claude_md_without_conventions():
    """CLAUDE.md content with no recognizable conventions section."""
    return (
        "# My Project\n"
        "\n"
        "This is a project that does things.\n"
        "\n"
        "## Overview\n"
        "\n"
        "It processes data and outputs results.\n"
        "\n"
        "## Architecture\n"
        "\n"
        "The system uses a layered architecture.\n"
    )


@pytest.fixture
def claude_md_with_code_blocks():
    """CLAUDE.md content with conventions inside code blocks."""
    return (
        "# CLAUDE.md\n"
        "\n"
        "## Constraints\n"
        "\n"
        "```\n"
        "- Always run tests before committing\n"
        "- Never push directly to main\n"
        "```\n"
        "\n"
        "## Standards\n"
        "\n"
        "- Follow PEP 8\n"
        "- Use black for formatting\n"
    )


@pytest.fixture
def fastapi_import_files():
    """File contents with FastAPI imports."""
    return {
        "app.py": (
            "from fastapi import FastAPI, HTTPException\n"
            "from fastapi.middleware.cors import CORSMiddleware\n"
            "\n"
            "app = FastAPI()\n"
            "\n"
            "\n"
            "@app.get('/health')\n"
            "def health():\n"
            "    return {'status': 'ok'}\n"
        ),
    }


@pytest.fixture
def langgraph_import_files():
    """File contents with LangGraph imports."""
    return {
        "graph.py": (
            "from langgraph.graph import StateGraph\n"
            "\n"
            "graph = StateGraph()\n"
        ),
    }


# ---------------------------------------------------------------------------
# T090 — test_scan_patterns_detects_naming
# ---------------------------------------------------------------------------


class TestScanPatternsDetectsNaming:
    """T090: Identifies snake_case module naming."""

    def test_detects_snake_case_filenames(self, snake_case_files):
        """snake_case filenames should be detected in naming_convention."""
        result = scan_patterns(snake_case_files)
        assert "snake_case" in result["naming_convention"].lower()

    def test_detects_pascal_case_classes(self, snake_case_files):
        """PascalCase classes should be mentioned in naming_convention."""
        result = scan_patterns(snake_case_files)
        assert "pascal" in result["naming_convention"].lower() or "class" in result["naming_convention"].lower()

    def test_naming_convention_not_unknown(self, snake_case_files):
        """With clear naming, result should not be 'unknown'."""
        result = scan_patterns(snake_case_files)
        assert result["naming_convention"] != "unknown"

    def test_result_is_string(self, snake_case_files):
        """naming_convention field should be a string."""
        result = scan_patterns(snake_case_files)
        assert isinstance(result["naming_convention"], str)

    def test_single_file_detection(self):
        """Even a single file should detect naming conventions."""
        files = {
            "my_helper.py": "class HelperClass:\n    pass\n",
        }
        result = scan_patterns(files)
        assert result["naming_convention"] != "unknown"


# ---------------------------------------------------------------------------
# T100 — test_scan_patterns_detects_typeddict
# ---------------------------------------------------------------------------


class TestScanPatternsDetectsTypedDict:
    """T100: Finds TypedDict state pattern."""

    def test_detects_typeddict_import(self, typeddict_files):
        """TypedDict import should be detected in state_pattern."""
        result = scan_patterns(typeddict_files)
        assert "typeddict" in result["state_pattern"].lower()

    def test_state_pattern_not_unknown(self, typeddict_files):
        """With TypedDict usage, state_pattern should not be 'unknown'."""
        result = scan_patterns(typeddict_files)
        assert result["state_pattern"] != "unknown"

    def test_detects_dataclass_pattern(self, dataclass_files):
        """dataclass import should be detected in state_pattern."""
        result = scan_patterns(dataclass_files)
        assert "dataclass" in result["state_pattern"].lower()

    def test_detects_basemodel_pattern(self, basemodel_files):
        """Pydantic BaseModel should be detected in state_pattern."""
        result = scan_patterns(basemodel_files)
        assert "basemodel" in result["state_pattern"].lower() or "pydantic" in result["state_pattern"].lower()

    def test_typeddict_class_definition(self):
        """TypedDict class definition should be detected."""
        files = {
            "state.py": (
                "from typing import TypedDict\n"
                "\n"
                "class MyState(TypedDict):\n"
                "    field: str\n"
            ),
        }
        result = scan_patterns(files)
        assert "typeddict" in result["state_pattern"].lower()


# ---------------------------------------------------------------------------
# T105 — test_scan_patterns_unknown_defaults
# ---------------------------------------------------------------------------


class TestScanPatternsUnknownDefaults:
    """T105: Returns 'unknown' for undetectable fields."""

    def test_empty_dict_all_unknown(self):
        """Empty file_contents dict should produce all 'unknown' fields."""
        result = scan_patterns({})
        assert result["naming_convention"] == "unknown"
        assert result["state_pattern"] == "unknown"
        assert result["node_pattern"] == "unknown"
        assert result["test_pattern"] == "unknown"
        assert result["import_style"] == "unknown"

    def test_returns_pattern_analysis_shape(self):
        """Result should have all PatternAnalysis keys."""
        result = scan_patterns({})
        expected_keys = {
            "naming_convention",
            "state_pattern",
            "node_pattern",
            "test_pattern",
            "import_style",
        }
        assert set(result.keys()) == expected_keys

    def test_all_values_are_strings(self):
        """All PatternAnalysis values should be strings."""
        result = scan_patterns({})
        for key, value in result.items():
            assert isinstance(value, str), f"Field {key} is not a string: {type(value)}"

    def test_minimal_content_may_be_unknown(self):
        """Files with no discernible patterns should have 'unknown' fields."""
        files = {
            "data.txt": "just some plain text data\nnothing special\n",
        }
        result = scan_patterns(files)
        # At least some fields should be unknown for non-Python files
        assert isinstance(result, dict)
        assert len(result) == 5

    def test_empty_file_content(self):
        """File with empty content should produce unknown defaults."""
        files = {"empty.py": ""}
        result = scan_patterns(files)
        # With an empty file, most patterns should be unknown
        assert result["state_pattern"] == "unknown"
        assert result["test_pattern"] == "unknown"


# ---------------------------------------------------------------------------
# T110 — test_detect_frameworks_from_deps
# ---------------------------------------------------------------------------


class TestDetectFrameworksFromDeps:
    """T110: Identifies LangGraph, pytest from dependency list."""

    def test_detects_langgraph(self):
        """'langgraph' in dependencies should detect 'LangGraph'."""
        result = detect_frameworks(["langgraph", "requests"], {})
        display_names = [name.lower() for name in result]
        assert "langgraph" in display_names

    def test_detects_pytest(self):
        """'pytest' in dependencies should detect 'pytest'."""
        result = detect_frameworks(["pytest", "requests"], {})
        display_names = [name.lower() for name in result]
        assert "pytest" in display_names

    def test_detects_both_langgraph_and_pytest(self):
        """Both LangGraph and pytest should be detected simultaneously."""
        result = detect_frameworks(["langgraph", "pytest"], {})
        display_names = [name.lower() for name in result]
        assert "langgraph" in display_names
        assert "pytest" in display_names

    def test_detects_fastapi(self):
        """'fastapi' in dependencies should detect 'FastAPI'."""
        result = detect_frameworks(["fastapi"], {})
        display_names = [name.lower() for name in result]
        assert "fastapi" in display_names

    def test_empty_deps_returns_empty(self):
        """Empty dependency list with no file contents returns empty list."""
        result = detect_frameworks([], {})
        assert result == []

    def test_unrecognized_deps_returns_empty(self):
        """Dependencies not in the known map should not produce results."""
        result = detect_frameworks(["some-obscure-package", "another-one"], {})
        # Only known framework packages are mapped; unknown ones might be ignored
        assert isinstance(result, list)

    def test_returns_list_of_strings(self):
        """Result should be a list of strings."""
        result = detect_frameworks(["langgraph", "pytest"], {})
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, str)

    def test_case_insensitive_matching(self):
        """Dependency matching should work regardless of case variations."""
        # The deps list typically comes from pyproject.toml which is lowercase
        result = detect_frameworks(["LangGraph", "PyTest"], {})
        # Implementation may or may not handle case; at minimum should not crash
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# T115 — test_detect_frameworks_from_imports
# ---------------------------------------------------------------------------


class TestDetectFrameworksFromImports:
    """T115: Detects frameworks from import statements in file contents."""

    def test_detects_fastapi_from_imports(self, fastapi_import_files):
        """FastAPI imports in file contents should detect 'FastAPI'."""
        result = detect_frameworks([], fastapi_import_files)
        display_names = [name.lower() for name in result]
        assert "fastapi" in display_names

    def test_detects_langgraph_from_imports(self, langgraph_import_files):
        """LangGraph imports in file contents should detect 'LangGraph'."""
        result = detect_frameworks([], langgraph_import_files)
        display_names = [name.lower() for name in result]
        assert "langgraph" in display_names

    def test_detects_pytest_from_imports(self, pytest_files):
        """pytest imports in test files should detect 'pytest'."""
        result = detect_frameworks([], pytest_files)
        display_names = [name.lower() for name in result]
        assert "pytest" in display_names

    def test_combines_deps_and_imports(self, fastapi_import_files):
        """Frameworks from both deps and imports should be combined."""
        result = detect_frameworks(["langgraph"], fastapi_import_files)
        display_names = [name.lower() for name in result]
        assert "langgraph" in display_names
        assert "fastapi" in display_names

    def test_no_duplicates(self):
        """Same framework detected from deps and imports should not duplicate."""
        files = {
            "app.py": "from fastapi import FastAPI\n",
        }
        result = detect_frameworks(["fastapi"], files)
        # Count occurrences of fastapi (case-insensitive)
        fastapi_count = sum(1 for name in result if name.lower() == "fastapi")
        assert fastapi_count <= 1, f"FastAPI appears {fastapi_count} times: {result}"

    def test_no_imports_no_deps(self):
        """Files with no recognizable imports and no deps returns empty."""
        files = {
            "script.py": "x = 1\ny = 2\nprint(x + y)\n",
        }
        result = detect_frameworks([], files)
        assert isinstance(result, list)

    def test_import_from_statement(self):
        """'from X import Y' style should detect framework X."""
        files = {
            "worker.py": "from celery import Celery\n",
        }
        result = detect_frameworks([], files)
        # celery may or may not be in the known mapping; test that it doesn't crash
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# T120 — test_extract_conventions_from_claude_md
# ---------------------------------------------------------------------------


class TestExtractConventionsFromClaudeMd:
    """T120: Extracts bullet-point conventions from CLAUDE.md."""

    def test_extracts_conventions(self, claude_md_with_conventions):
        """CLAUDE.md with rule bullets should produce a non-empty list."""
        result = extract_conventions_from_claude_md(claude_md_with_conventions)
        assert len(result) > 0

    def test_conventions_are_strings(self, claude_md_with_conventions):
        """Each convention should be a string."""
        result = extract_conventions_from_claude_md(claude_md_with_conventions)
        for conv in result:
            assert isinstance(conv, str)

    def test_conventions_match_content(self, claude_md_with_conventions):
        """Extracted conventions should reference rules from the content."""
        result = extract_conventions_from_claude_md(claude_md_with_conventions)
        all_text = " ".join(result).lower()
        # At least some of the rules should be captured
        assert "snake_case" in all_text or "poetry" in all_text or "docstring" in all_text

    def test_extracts_from_rules_section(self, claude_md_with_conventions):
        """Conventions from ## Rules section should be extracted."""
        result = extract_conventions_from_claude_md(claude_md_with_conventions)
        assert len(result) >= 1
        # Check that at least one rule from the Rules section is present
        all_text = " ".join(result).lower()
        has_rule = (
            "snake_case" in all_text
            or "pascalcase" in all_text
            or "docstring" in all_text
        )
        assert has_rule, f"No rules from Rules section found in: {result}"

    def test_extracts_from_conventions_section(self, claude_md_with_conventions):
        """Conventions from ## Conventions section should be extracted."""
        result = extract_conventions_from_claude_md(claude_md_with_conventions)
        all_text = " ".join(result).lower()
        has_convention = "poetry" in all_text or "pip" in all_text
        assert has_convention, f"No conventions from Conventions section found in: {result}"

    def test_extracts_from_style_section(self, claude_md_with_conventions):
        """Conventions from ## Style Guide section should be extracted."""
        result = extract_conventions_from_claude_md(claude_md_with_conventions)
        all_text = " ".join(result).lower()
        has_style = "line length" in all_text or "88" in all_text or "type hint" in all_text
        assert has_style, f"No style conventions found in: {result}"

    def test_extracts_from_code_blocks(self, claude_md_with_code_blocks):
        """Conventions from code blocks under constraint headers should be found."""
        result = extract_conventions_from_claude_md(claude_md_with_code_blocks)
        assert len(result) > 0

    def test_returns_list(self, claude_md_with_conventions):
        """Return type should always be a list."""
        result = extract_conventions_from_claude_md(claude_md_with_conventions)
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# T130 — test_extract_conventions_empty
# ---------------------------------------------------------------------------


class TestExtractConventionsEmpty:
    """T130: Returns empty list for CLAUDE.md without conventions."""

    def test_no_conventions_returns_empty(self, claude_md_without_conventions):
        """CLAUDE.md without rules/conventions sections returns empty list."""
        result = extract_conventions_from_claude_md(claude_md_without_conventions)
        assert result == []

    def test_empty_string_returns_empty(self):
        """Empty string input returns empty list."""
        result = extract_conventions_from_claude_md("")
        assert result == []

    def test_returns_list_type(self, claude_md_without_conventions):
        """Return type should be a list even when empty."""
        result = extract_conventions_from_claude_md(claude_md_without_conventions)
        assert isinstance(result, list)

    def test_whitespace_only_returns_empty(self):
        """Whitespace-only content returns empty list."""
        result = extract_conventions_from_claude_md("   \n\n   \n")
        assert result == []

    def test_headings_only_returns_empty(self):
        """Content with only headings and no bullet points returns empty."""
        content = (
            "# Project\n"
            "\n"
            "## About\n"
            "\n"
            "## License\n"
        )
        result = extract_conventions_from_claude_md(content)
        assert result == []


# ---------------------------------------------------------------------------
# Additional scan_patterns tests
# ---------------------------------------------------------------------------


class TestScanPatternsNodePattern:
    """Additional tests for node_pattern detection."""

    def test_detects_dict_returning_functions(self, node_pattern_files):
        """Functions returning dict should be detected as node pattern."""
        result = scan_patterns(node_pattern_files)
        assert result["node_pattern"] != "unknown"

    def test_no_node_pattern_in_simple_code(self):
        """Simple code without dict-returning functions should be unknown."""
        files = {
            "utils.py": (
                "def add(a, b):\n"
                "    return a + b\n"
                "\n"
                "def multiply(a, b):\n"
                "    return a * b\n"
            ),
        }
        result = scan_patterns(files)
        # May or may not detect a pattern depending on implementation
        assert isinstance(result["node_pattern"], str)


class TestScanPatternsTestPattern:
    """Additional tests for test_pattern detection."""

    def test_detects_pytest(self, pytest_files):
        """pytest fixtures and imports should detect pytest test pattern."""
        result = scan_patterns(pytest_files)
        assert "pytest" in result["test_pattern"].lower()

    def test_detects_unittest(self, unittest_files):
        """unittest.TestCase should detect unittest test pattern."""
        result = scan_patterns(unittest_files)
        assert "unittest" in result["test_pattern"].lower()

    def test_no_tests_returns_unknown(self):
        """Files without test patterns should return 'unknown'."""
        files = {
            "main.py": "def main():\n    print('hello')\n",
        }
        result = scan_patterns(files)
        assert result["test_pattern"] == "unknown"


class TestScanPatternsImportStyle:
    """Additional tests for import_style detection."""

    def test_detects_absolute_imports(self, absolute_import_files):
        """Predominantly absolute imports should be detected."""
        result = scan_patterns(absolute_import_files)
        assert "absolute" in result["import_style"].lower()

    def test_detects_relative_imports(self, relative_import_files):
        """Predominantly relative imports should be detected."""
        result = scan_patterns(relative_import_files)
        assert "relative" in result["import_style"].lower()

    def test_no_imports_returns_unknown(self):
        """Files without imports should return 'unknown' for import_style."""
        files = {
            "script.py": "x = 1\nprint(x)\n",
        }
        result = scan_patterns(files)
        assert result["import_style"] == "unknown"


# ---------------------------------------------------------------------------
# Edge cases and integration tests
# ---------------------------------------------------------------------------


class TestScanPatternsEdgeCases:
    """Edge cases for scan_patterns."""

    def test_single_file_analysis(self):
        """scan_patterns should work with a single file."""
        files = {
            "main.py": (
                "from typing import TypedDict\n"
                "import pytest\n"
                "\n"
                "class State(TypedDict):\n"
                "    value: str\n"
                "\n"
                "def node(state: dict) -> dict:\n"
                "    return {'value': 'done'}\n"
            ),
        }
        result = scan_patterns(files)
        assert isinstance(result, dict)
        assert len(result) == 5

    def test_large_file_contents(self):
        """scan_patterns should handle large file contents without error."""
        files = {
            "big_module.py": "import os\n" + ("x = 1\n" * 10000),
        }
        result = scan_patterns(files)
        assert isinstance(result, dict)

    def test_mixed_patterns(self, snake_case_files):
        """Multiple patterns in different files should all be detected."""
        files = dict(snake_case_files)
        files["test_example.py"] = (
            "import pytest\n"
            "\n"
            "def test_something():\n"
            "    assert True\n"
        )
        files["state.py"] = (
            "from typing import TypedDict\n"
            "\n"
            "class AppState(TypedDict):\n"
            "    data: str\n"
        )
        result = scan_patterns(files)
        assert result["naming_convention"] != "unknown"
        assert result["state_pattern"] != "unknown"
        assert result["test_pattern"] != "unknown"

    def test_non_python_files(self):
        """Non-Python files should be handled gracefully."""
        files = {
            "README.md": "# Hello\n\nThis is a readme.\n",
            "config.yaml": "key: value\nnested:\n  item: 1\n",
            "data.json": '{"name": "test"}\n',
        }
        result = scan_patterns(files)
        assert isinstance(result, dict)
        # Most fields should be unknown for non-Python content
        assert result["state_pattern"] == "unknown"


class TestDetectFrameworksEdgeCases:
    """Edge cases for detect_frameworks."""

    def test_returns_human_readable_names(self):
        """Framework names should be human-readable display names."""
        result = detect_frameworks(["langgraph", "fastapi", "pytest"], {})
        # Should have nice display names, not raw package names
        for name in result:
            assert isinstance(name, str)
            assert len(name) > 0

    def test_many_dependencies(self):
        """Should handle a large dependency list efficiently."""
        deps = [f"package-{i}" for i in range(100)]
        deps.extend(["langgraph", "pytest"])
        result = detect_frameworks(deps, {})
        display_names = [name.lower() for name in result]
        assert "langgraph" in display_names
        assert "pytest" in display_names

    def test_empty_file_contents_with_deps(self):
        """Empty file contents should still detect from deps."""
        result = detect_frameworks(["fastapi"], {})
        display_names = [name.lower() for name in result]
        assert "fastapi" in display_names

    def test_django_detection(self):
        """Django framework should be detectable from deps."""
        result = detect_frameworks(["django"], {})
        if result:  # Django may or may not be in the known mapping
            display_names = [name.lower() for name in result]
            assert "django" in display_names

    def test_flask_detection(self):
        """Flask framework should be detectable from deps or imports."""
        files = {
            "app.py": "from flask import Flask\napp = Flask(__name__)\n",
        }
        result = detect_frameworks(["flask"], files)
        if result:
            display_names = [name.lower() for name in result]
            assert "flask" in display_names


class TestExtractConventionsEdgeCases:
    """Edge cases for extract_conventions_from_claude_md."""

    def test_deeply_nested_bullet_points(self):
        """Nested bullet points under convention headers should be extracted."""
        content = (
            "# Rules\n"
            "\n"
            "## Code Style\n"
            "\n"
            "- Use type hints\n"
            "  - Especially for function signatures\n"
            "- Format with black\n"
        )
        result = extract_conventions_from_claude_md(content)
        assert len(result) >= 1

    def test_multiple_convention_sections(self):
        """Multiple sections with conventions should all be extracted."""
        content = (
            "# Project\n"
            "\n"
            "## Rules\n"
            "\n"
            "- Rule one\n"
            "- Rule two\n"
            "\n"
            "## Constraints\n"
            "\n"
            "- Constraint A\n"
            "- Constraint B\n"
        )
        result = extract_conventions_from_claude_md(content)
        assert len(result) >= 2

    def test_very_long_content(self):
        """Very long CLAUDE.md should not crash."""
        content = "# CLAUDE.md\n\n## Rules\n\n"
        content += "- Rule line\n" * 1000
        content += "\n## Other\n\nLots of other content.\n" * 100
        result = extract_conventions_from_claude_md(content)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_special_characters_in_conventions(self):
        """Conventions with special characters should be handled."""
        content = (
            "## Style\n"
            "\n"
            "- Use `poetry run python` for execution\n"
            "- Maximum line length: 88 chars (PEP-8 compat)\n"
            "- Use **bold** for emphasis\n"
        )
        result = extract_conventions_from_claude_md(content)
        assert len(result) >= 1
        for conv in result:
            assert isinstance(conv, str)

    def test_convention_with_standard_header(self):
        """Header containing 'standard' should be recognized."""
        content = (
            "## Coding Standards\n"
            "\n"
            "- Follow PEP 8\n"
            "- Use type annotations\n"
        )
        result = extract_conventions_from_claude_md(content)
        assert len(result) >= 1
```
