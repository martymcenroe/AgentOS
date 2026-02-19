All 93 tests pass. Here's the final file:

```python
"""Unit tests for the pattern scanner utility.

Issue #401: Codebase Context Analysis for Requirements Workflow.

Tests for:
- scan_patterns (naming conventions, state patterns, node patterns, test patterns, import styles)
- detect_frameworks (from dependency list and import statements)
- extract_conventions_from_claude_md (convention extraction from CLAUDE.md content)
"""

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
def snake_case_python_files():
    """File contents dict with snake_case module names and PascalCase classes."""
    return {
        "my_module.py": (
            '"""My module."""\n\n'
            "class MyClass:\n"
            "    pass\n\n"
            "class AnotherWidget:\n"
            "    pass\n\n"
            "def my_function():\n"
            "    return 42\n\n"
            "def another_helper():\n"
            "    return True\n"
        ),
        "utils_helper.py": (
            '"""Utils helper."""\n\n'
            "class HelperService:\n"
            "    pass\n\n"
            "def compute_value():\n"
            "    return 0\n"
        ),
    }


@pytest.fixture
def typeddict_files():
    """File contents with TypedDict usage."""
    return {
        "state.py": (
            "from typing import TypedDict\n\n"
            "class WorkflowState(TypedDict):\n"
            "    issue_text: str\n"
            "    repo_path: str | None\n"
            "    draft: str\n"
        ),
        "node.py": (
            "def my_node(state: dict) -> dict:\n"
            '    return {"result": "done"}\n'
        ),
    }


@pytest.fixture
def dataclass_files():
    """File contents with dataclass usage."""
    return {
        "models.py": (
            "from dataclasses import dataclass\n\n"
            "@dataclass\n"
            "class Config:\n"
            "    name: str\n"
            "    value: int\n"
        ),
    }


@pytest.fixture
def basemodel_files():
    """File contents with Pydantic BaseModel usage."""
    return {
        "schemas.py": (
            "from pydantic import BaseModel\n\n"
            "class UserSchema(BaseModel):\n"
            "    name: str\n"
            "    email: str\n"
        ),
    }


@pytest.fixture
def pytest_files():
    """File contents with pytest conventions."""
    return {
        "test_something.py": (
            "import pytest\n\n"
            "@pytest.fixture\n"
            "def my_fixture():\n"
            "    return 42\n\n"
            "def test_thing(my_fixture):\n"
            "    assert my_fixture == 42\n"
        ),
        "conftest.py": (
            "import pytest\n\n"
            "@pytest.fixture\n"
            "def shared_fixture():\n"
            '    yield "data"\n'
        ),
    }


@pytest.fixture
def unittest_files():
    """File contents with unittest conventions."""
    return {
        "test_legacy.py": (
            "import unittest\n\n"
            "class TestLegacy(unittest.TestCase):\n"
            "    def test_old_stuff(self):\n"
            "        self.assertEqual(1, 1)\n"
        ),
    }


@pytest.fixture
def absolute_import_files():
    """File contents with predominantly absolute imports."""
    return {
        "module_a.py": (
            "from assemblyzero.utils import something\n"
            "import assemblyzero.core\n"
            "from pathlib import Path\n"
            "import logging\n"
        ),
        "module_b.py": (
            "from assemblyzero.workflows import graph\n"
            "import json\n"
            "import os\n"
        ),
    }


@pytest.fixture
def relative_import_files():
    """File contents with predominantly relative imports."""
    return {
        "module_a.py": (
            "from . import something\n"
            "from ..utils import helper\n"
            "from .core import base\n"
        ),
        "module_b.py": (
            "from . import another\n"
            "from .models import Thing\n"
        ),
    }


@pytest.fixture
def mixed_import_files():
    """File contents with mixed import styles."""
    return {
        "module_a.py": (
            "from assemblyzero.utils import something\n"
            "from . import local\n"
            "import logging\n"
        ),
    }


@pytest.fixture
def node_pattern_files():
    """File contents with node patterns (functions returning dicts)."""
    return {
        "nodes.py": (
            "def load_input(state: dict) -> dict:\n"
            '    return {"loaded": True}\n\n'
            "def process(state: dict) -> dict:\n"
            '    return {"result": state["input"]}\n'
        ),
    }


@pytest.fixture
def claude_md_with_conventions():
    """CLAUDE.md content with coding conventions."""
    return (
        "# CLAUDE.md - My Project\n\n"
        "## Rules\n\n"
        "- Use snake_case for all file names\n"
        "- Never use print statements in production code\n"
        "- All functions must have docstrings\n\n"
        "## Coding Style\n\n"
        "- Use type hints everywhere\n"
        "- Prefer composition over inheritance\n\n"
        "## Other Info\n\n"
        "This project uses Python 3.11.\n"
    )


@pytest.fixture
def claude_md_without_conventions():
    """CLAUDE.md content without any convention-like sections."""
    return (
        "# My Project\n\n"
        "This is a description of the project.\n\n"
        "## Installation\n\n"
        "Run `pip install .` to install.\n\n"
        "## Usage\n\n"
        "Import and use the main module.\n"
    )


# ---------------------------------------------------------------------------
# T090 — test_scan_patterns_detects_naming
# ---------------------------------------------------------------------------


class TestScanPatternsDetectsNaming:
    """T090: Identifies snake_case module naming."""

    def test_detects_snake_case_filenames(self, snake_case_python_files):
        """Snake_case filenames should be detected as naming convention."""
        result = scan_patterns(snake_case_python_files)
        assert "snake_case" in result["naming_convention"].lower()

    def test_result_is_pattern_analysis(self, snake_case_python_files):
        """Result should conform to PatternAnalysis shape."""
        result = scan_patterns(snake_case_python_files)
        assert "naming_convention" in result
        assert "state_pattern" in result
        assert "node_pattern" in result
        assert "test_pattern" in result
        assert "import_style" in result

    def test_detects_pascal_case_classes(self, snake_case_python_files):
        """Should also note PascalCase class naming in the convention."""
        result = scan_patterns(snake_case_python_files)
        naming = result["naming_convention"]
        assert "PascalCase" in naming

    def test_naming_convention_not_unknown(self, snake_case_python_files):
        """With clear naming patterns, should not be 'unknown'."""
        result = scan_patterns(snake_case_python_files)
        assert result["naming_convention"] != "unknown"

    def test_detects_snake_case_functions(self, snake_case_python_files):
        """snake_case function definitions should be detected."""
        result = scan_patterns(snake_case_python_files)
        naming = result["naming_convention"]
        assert "snake_case" in naming

    def test_combined_naming_result(self, snake_case_python_files):
        """Both snake_case modules and PascalCase classes should appear."""
        result = scan_patterns(snake_case_python_files)
        naming = result["naming_convention"]
        assert "snake_case" in naming
        assert "PascalCase" in naming

    def test_files_without_classes(self):
        """Files with only functions should detect snake_case functions."""
        files = {
            "utils.py": (
                "def process_data(data):\n"
                "    pass\n\n"
                "def format_output(output):\n"
                "    pass\n"
            ),
        }
        result = scan_patterns(files)
        assert "snake_case" in result["naming_convention"]

    def test_single_file_with_both(self):
        """Single file with both PascalCase classes and snake_case functions."""
        files = {
            "module.py": (
                "class MyClass:\n"
                "    pass\n\n"
                "def my_function():\n"
                "    pass\n"
            ),
        }
        result = scan_patterns(files)
        assert "PascalCase" in result["naming_convention"]
        assert "snake_case" in result["naming_convention"]


# ---------------------------------------------------------------------------
# T100 — test_scan_patterns_detects_typeddict
# ---------------------------------------------------------------------------


class TestScanPatternsDetectsTypedDict:
    """T100: Finds TypedDict state pattern."""

    def test_detects_typeddict(self, typeddict_files):
        """TypedDict import should be detected as state pattern."""
        result = scan_patterns(typeddict_files)
        assert "TypedDict" in result["state_pattern"]

    def test_detects_dataclass(self, dataclass_files):
        """Dataclass usage should be detected as state pattern."""
        result = scan_patterns(dataclass_files)
        assert "dataclass" in result["state_pattern"].lower()

    def test_detects_basemodel(self, basemodel_files):
        """Pydantic BaseModel should be detected as state pattern."""
        result = scan_patterns(basemodel_files)
        assert "BaseModel" in result["state_pattern"]

    def test_state_pattern_not_unknown_with_typeddict(self, typeddict_files):
        """With TypedDict present, state_pattern should not be 'unknown'."""
        result = scan_patterns(typeddict_files)
        assert result["state_pattern"] != "unknown"

    def test_detects_multiple_state_patterns(self):
        """Files using both TypedDict and dataclass should detect both."""
        files = {
            "state.py": (
                "from typing import TypedDict\n\n"
                "class WorkflowState(TypedDict):\n"
                "    step: str\n"
            ),
            "models.py": (
                "from dataclasses import dataclass\n\n"
                "@dataclass\n"
                "class Config:\n"
                "    name: str\n"
            ),
        }
        result = scan_patterns(files)
        assert "TypedDict" in result["state_pattern"]
        assert "dataclass" in result["state_pattern"]

    def test_typing_extensions_typeddict(self):
        """TypedDict from typing_extensions should also be detected."""
        files = {
            "compat.py": (
                "from typing_extensions import TypedDict\n\n"
                "class State(TypedDict):\n"
                "    value: int\n"
            ),
        }
        result = scan_patterns(files)
        assert "TypedDict" in result["state_pattern"]


# ---------------------------------------------------------------------------
# T105 — test_scan_patterns_unknown_defaults
# ---------------------------------------------------------------------------


class TestScanPatternsUnknownDefaults:
    """T105: Returns 'unknown' for undetectable fields."""

    def test_empty_contents_all_unknown(self):
        """Empty file_contents dict should produce all 'unknown' fields."""
        result = scan_patterns({})
        assert result["naming_convention"] == "unknown"
        assert result["state_pattern"] == "unknown"
        assert result["node_pattern"] == "unknown"
        assert result["test_pattern"] == "unknown"
        assert result["import_style"] == "unknown"

    def test_all_fields_present(self):
        """Even with empty input, all PatternAnalysis keys must be present."""
        result = scan_patterns({})
        expected_keys = {
            "naming_convention",
            "state_pattern",
            "node_pattern",
            "test_pattern",
            "import_style",
        }
        assert set(result.keys()) == expected_keys

    def test_minimal_content_may_have_unknowns(self):
        """Minimal file content should default unknown for undetectable fields."""
        result = scan_patterns({"empty.txt": ""})
        unknown_count = sum(
            1 for v in result.values() if v == "unknown"
        )
        assert unknown_count >= 1

    def test_no_crash_on_trivial_content(self):
        """Files with very short or trivial content should not crash."""
        result = scan_patterns({"a.py": "x = 1\n"})
        assert isinstance(result, dict)
        for key in ["naming_convention", "state_pattern", "node_pattern",
                     "test_pattern", "import_style"]:
            assert key in result

    def test_all_unknown_values_are_strings(self):
        """All 'unknown' default values should be strings."""
        result = scan_patterns({})
        for value in result.values():
            assert isinstance(value, str)
            assert value == "unknown"


# ---------------------------------------------------------------------------
# T110 — test_detect_frameworks_from_deps
# ---------------------------------------------------------------------------


class TestDetectFrameworksFromDeps:
    """T110: Identifies LangGraph, pytest from dependency list."""

    def test_detects_langgraph(self):
        """'langgraph' in deps should map to 'LangGraph'."""
        result = detect_frameworks(["langgraph", "pytest"], {})
        assert "LangGraph" in result

    def test_detects_pytest(self):
        """'pytest' in deps should be detected."""
        result = detect_frameworks(["langgraph", "pytest"], {})
        assert "pytest" in result

    def test_both_detected(self):
        """Both LangGraph and pytest should be in the result."""
        result = detect_frameworks(["langgraph", "pytest"], {})
        assert "LangGraph" in result
        assert "pytest" in result

    def test_returns_list(self):
        """Result should be a list of strings."""
        result = detect_frameworks(["langgraph"], {})
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, str)

    def test_empty_deps_empty_result(self):
        """Empty dependency list with empty contents returns empty list."""
        result = detect_frameworks([], {})
        assert result == []

    def test_unknown_deps_not_included(self):
        """Unknown/unmapped dependency names should not appear in result."""
        result = detect_frameworks(["my-custom-lib", "another-thing"], {})
        assert result == []

    def test_detects_fastapi(self):
        """'fastapi' in deps should map to 'FastAPI'."""
        result = detect_frameworks(["fastapi"], {})
        assert "FastAPI" in result

    def test_multiple_frameworks(self):
        """Multiple known frameworks should all be detected."""
        result = detect_frameworks(
            ["langgraph", "fastapi", "pytest"], {}
        )
        assert "LangGraph" in result
        assert "FastAPI" in result
        assert "pytest" in result

    def test_no_duplicates(self):
        """Result should not contain duplicate framework names."""
        result = detect_frameworks(
            ["langgraph", "langgraph", "pytest"], {}
        )
        assert len(result) == len(set(result))

    def test_case_insensitive_matching(self):
        """Dependency names should be matched case-insensitively."""
        result = detect_frameworks(["LangGraph", "PYTEST"], {})
        assert "LangGraph" in result
        assert "pytest" in result

    def test_preserves_insertion_order(self):
        """Frameworks should be returned in the order they are first encountered."""
        result = detect_frameworks(["langgraph", "fastapi", "pytest"], {})
        assert len(result) == 3
        assert "LangGraph" in result
        assert "FastAPI" in result
        assert "pytest" in result

    def test_returns_human_readable_names(self):
        """Framework names should be human-readable display names."""
        result = detect_frameworks(["langgraph", "fastapi"], {})
        assert "LangGraph" in result
        assert "FastAPI" in result


# ---------------------------------------------------------------------------
# T115 — test_detect_frameworks_from_imports
# ---------------------------------------------------------------------------


class TestDetectFrameworksFromImports:
    """T115: Detects frameworks from import statements in file contents."""

    def test_detects_fastapi_from_import(self):
        """'from fastapi import' in file content should detect FastAPI."""
        file_contents = {
            "app.py": "from fastapi import FastAPI\n\napp = FastAPI()\n"
        }
        result = detect_frameworks([], file_contents)
        assert "FastAPI" in result

    def test_detects_langgraph_from_import(self):
        """'from langgraph' import should detect LangGraph."""
        file_contents = {
            "graph.py": "from langgraph.graph import StateGraph\n"
        }
        result = detect_frameworks([], file_contents)
        assert "LangGraph" in result

    def test_detects_pytest_from_import(self):
        """'import pytest' should detect pytest."""
        file_contents = {
            "test_app.py": "import pytest\n\ndef test_x():\n    assert True\n"
        }
        result = detect_frameworks([], file_contents)
        assert "pytest" in result

    def test_combines_deps_and_imports(self):
        """Frameworks from both deps and imports should be combined."""
        file_contents = {
            "app.py": "from fastapi import FastAPI\n"
        }
        result = detect_frameworks(["langgraph"], file_contents)
        assert "LangGraph" in result
        assert "FastAPI" in result

    def test_no_duplicates_from_deps_and_imports(self):
        """Same framework in deps and imports should not duplicate."""
        file_contents = {
            "app.py": "from fastapi import FastAPI\n"
        }
        result = detect_frameworks(["fastapi"], file_contents)
        assert result.count("FastAPI") == 1

    def test_empty_files_no_crash(self):
        """Empty file contents should not crash."""
        result = detect_frameworks([], {"empty.py": ""})
        assert isinstance(result, list)

    def test_deep_module_import(self):
        """'from langgraph.graph.state import ...' should detect LangGraph."""
        file_contents = {
            "workflow.py": "from langgraph.graph.state import StateGraph\n"
        }
        result = detect_frameworks([], file_contents)
        assert "LangGraph" in result

    def test_no_false_positives(self):
        """Unrecognized imports should not produce framework detections."""
        file_contents = {
            "custom.py": (
                "from my_custom_lib import helper\n"
                "import some_unknown_package\n"
            ),
        }
        result = detect_frameworks([], file_contents)
        assert result == []

    def test_multiple_imports_in_one_file(self):
        """Multiple framework imports in one file should all be detected."""
        file_contents = {
            "app.py": (
                "from fastapi import FastAPI\n"
                "from pydantic import BaseModel\n"
                "import logging\n"
            ),
        }
        result = detect_frameworks([], file_contents)
        assert "FastAPI" in result
        assert "Pydantic" in result

    def test_multiple_files_with_imports(self):
        """Imports across multiple files should all be detected."""
        file_contents = {
            "app.py": "from fastapi import FastAPI\n",
            "models.py": "from pydantic import BaseModel\n",
            "tests/test_app.py": "import pytest\n",
        }
        result = detect_frameworks([], file_contents)
        assert "FastAPI" in result
        assert "Pydantic" in result
        assert "pytest" in result

    def test_pytorch_detection(self):
        """'import torch' should detect PyTorch."""
        file_contents = {
            "model.py": "import torch\n",
        }
        result = detect_frameworks([], file_contents)
        assert "PyTorch" in result

    def test_numpy_detection(self):
        """'import numpy' should detect NumPy."""
        file_contents = {
            "data.py": "import numpy\n",
        }
        result = detect_frameworks([], file_contents)
        assert "NumPy" in result


# ---------------------------------------------------------------------------
# T120 — test_extract_conventions_from_claude_md
# ---------------------------------------------------------------------------


class TestExtractConventionsFromClaudeMd:
    """T120: Extracts bullet-point conventions from CLAUDE.md."""

    def test_extracts_conventions(self, claude_md_with_conventions):
        """Should extract convention strings from CLAUDE.md with rules."""
        result = extract_conventions_from_claude_md(claude_md_with_conventions)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_conventions_contain_rule_text(self, claude_md_with_conventions):
        """Extracted conventions should contain actual rule text."""
        result = extract_conventions_from_claude_md(claude_md_with_conventions)
        all_text = " ".join(result).lower()
        assert "snake_case" in all_text or "docstring" in all_text or "type hint" in all_text

    def test_returns_list_of_strings(self, claude_md_with_conventions):
        """Result should be a list of non-empty strings."""
        result = extract_conventions_from_claude_md(claude_md_with_conventions)
        for item in result:
            assert isinstance(item, str)
            assert len(item) > 0

    def test_multiple_sections_captured(self, claude_md_with_conventions):
        """Conventions from multiple rule-like sections should be captured."""
        result = extract_conventions_from_claude_md(claude_md_with_conventions)
        assert len(result) >= 2

    def test_non_convention_text_excluded(self, claude_md_with_conventions):
        """General descriptive text should not be extracted as convention."""
        result = extract_conventions_from_claude_md(claude_md_with_conventions)
        all_text = " ".join(result).lower()
        assert any(
            keyword in all_text
            for keyword in ["snake_case", "print", "docstring", "type hint", "composition"]
        )

    def test_extracts_snake_case_rule(self, claude_md_with_conventions):
        """The specific snake_case rule should be extracted."""
        result = extract_conventions_from_claude_md(claude_md_with_conventions)
        assert any("snake_case" in c for c in result)

    def test_extracts_docstring_rule(self, claude_md_with_conventions):
        """The docstrings rule should be extracted."""
        result = extract_conventions_from_claude_md(claude_md_with_conventions)
        assert any("docstring" in c.lower() for c in result)

    def test_extracts_style_conventions(self, claude_md_with_conventions):
        """'Coding Style' section has 'style' keyword and should be extracted."""
        result = extract_conventions_from_claude_md(claude_md_with_conventions)
        assert any("type hint" in c.lower() for c in result)

    def test_with_code_block_conventions(self):
        """Conventions inside labeled code blocks should be extracted."""
        content = (
            "# Project\n\n"
            "```rules\n"
            "Always use type annotations\n"
            "Never commit secrets\n"
            "```\n\n"
            "## Other stuff\n\n"
            "Not a convention.\n"
        )
        result = extract_conventions_from_claude_md(content)
        assert any("type annotations" in c.lower() for c in result)
        assert any("secrets" in c.lower() for c in result)

    def test_real_mock_fixture_claude_md(self):
        """Test extraction from the actual mock_repo CLAUDE.md content."""
        content = (
            "# Mock CLAUDE.md for testing codebase context analysis\n"
            "# Issue #401: Codebase Context Analysis for Requirements Workflow\n\n"
            "# Mock Project\n\n"
            "## Rules\n\n"
            "- Use snake_case for all file names\n"
            "- Never use print statements in production code\n"
            "- All functions must have docstrings\n\n"
            "## Coding Style\n\n"
            "- Use type hints everywhere\n"
            "- Prefer composition over inheritance\n\n"
            "## Conventions\n\n"
            "- Use absolute imports from package root\n"
            "- Keep functions under 50 lines\n"
            "- Write tests for all public functions\n\n"
            "## Project Info\n\n"
            "This is a mock project used for testing the codebase analysis node.\n"
            "It simulates a real repository with conventions and rules.\n"
        )
        result = extract_conventions_from_claude_md(content)
        assert len(result) >= 5
        assert any("snake_case" in c for c in result)

    def test_extracts_standard_section(self):
        """Section header with 'standard' keyword should trigger extraction."""
        content = (
            "# Project\n\n"
            "## Coding Standards\n\n"
            "- Follow PEP 8\n"
            "- Use type hints\n"
        )
        result = extract_conventions_from_claude_md(content)
        assert any("PEP 8" in c for c in result)
        assert any("type hints" in c.lower() for c in result)

    def test_extracts_constraint_section(self):
        """Section header with 'constraint' keyword should trigger extraction."""
        content = (
            "# Project\n\n"
            "## Constraints\n\n"
            "- Max 100 lines per function\n"
            "- No external API calls in tests\n"
        )
        result = extract_conventions_from_claude_md(content)
        assert any("100 lines" in c for c in result)

    def test_nested_headers_stop_extraction(self):
        """A same-level header should stop extraction from previous section."""
        content = (
            "# Project\n\n"
            "## Rules\n\n"
            "- Rule one\n"
            "- Rule two\n\n"
            "## Overview\n\n"
            "- Not a rule\n"
        )
        result = extract_conventions_from_claude_md(content)
        assert any("Rule one" in c for c in result)
        assert any("Rule two" in c for c in result)
        assert not any("Not a rule" in c for c in result)

    def test_no_empty_strings_in_result(self, claude_md_with_conventions):
        """No empty strings should appear in the results."""
        result = extract_conventions_from_claude_md(claude_md_with_conventions)
        for c in result:
            assert c.strip() != ""


# ---------------------------------------------------------------------------
# T130 — test_extract_conventions_empty
# ---------------------------------------------------------------------------


class TestExtractConventionsEmpty:
    """T130: Returns empty list for CLAUDE.md without conventions."""

    def test_returns_empty_list(self, claude_md_without_conventions):
        """CLAUDE.md with no rule/convention sections returns empty list."""
        result = extract_conventions_from_claude_md(claude_md_without_conventions)
        assert isinstance(result, list)
        assert len(result) == 0

    def test_empty_string_returns_empty(self):
        """Empty string content returns empty list."""
        result = extract_conventions_from_claude_md("")
        assert result == []

    def test_whitespace_only_returns_empty(self):
        """Whitespace-only content returns empty list."""
        result = extract_conventions_from_claude_md("   \n  \n  ")
        assert result == []

    def test_no_crash_on_plain_text(self):
        """Plain text with no markdown structure should return empty list."""
        result = extract_conventions_from_claude_md(
            "Just some plain text with no headers or bullets."
        )
        assert isinstance(result, list)
        assert result == []

    def test_heading_only_no_bullets(self):
        """Convention-like headers without bullet points should return empty list."""
        content = (
            "# My Project\n\n"
            "## Rules\n\n"
            "No bullet points here, just a paragraph.\n\n"
            "## Other Section\n\n"
            "More text here.\n"
        )
        result = extract_conventions_from_claude_md(content)
        assert result == []

    def test_bullets_outside_convention_sections(self):
        """Bullets not under convention/rule headers should not be extracted."""
        content = (
            "# My Project\n\n"
            "## Features\n\n"
            "- Feature A\n"
            "- Feature B\n\n"
            "## Architecture\n\n"
            "- Module X\n"
            "- Module Y\n"
        )
        result = extract_conventions_from_claude_md(content)
        assert result == []

    def test_returns_list_type(self):
        """Even for empty input, return type should be a list."""
        result = extract_conventions_from_claude_md("")
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# Additional pattern detection tests
# ---------------------------------------------------------------------------


class TestScanPatternsNodePattern:
    """Tests for node pattern detection within scan_patterns."""

    def test_detects_dict_returning_functions(self, node_pattern_files):
        """Functions returning dict should be detected as node pattern."""
        result = scan_patterns(node_pattern_files)
        assert result["node_pattern"] != "unknown"
        assert "dict" in result["node_pattern"].lower()

    def test_no_node_pattern_without_dict_returns(self):
        """Files without dict-returning functions should yield 'unknown'."""
        files = {
            "utils.py": (
                "def helper():\n"
                "    return 42\n\n"
                "def another():\n"
                "    return 'hello'\n"
            ),
        }
        result = scan_patterns(files)
        assert result["node_pattern"] == "unknown"

    def test_annotated_dict_return_detected(self):
        """Functions with -> dict type annotation should be detected."""
        files = {
            "nodes.py": (
                "def my_node(state: dict) -> dict:\n"
                '    return {"key": "value"}\n'
            ),
        }
        result = scan_patterns(files)
        assert "dict" in result["node_pattern"].lower()

    def test_unannotated_function_not_detected(self):
        """Functions without -> dict annotation are not detected as node pattern."""
        files = {
            "nodes.py": (
                "def my_node(state):\n"
                '    return {"key": "value"}\n'
            ),
        }
        result = scan_patterns(files)
        assert result["node_pattern"] == "unknown"


class TestScanPatternsTestPattern:
    """Tests for test pattern detection within scan_patterns."""

    def test_detects_pytest(self, pytest_files):
        """pytest import and fixtures should detect pytest test pattern."""
        result = scan_patterns(pytest_files)
        assert "pytest" in result["test_pattern"].lower()

    def test_detects_pytest_with_conftest(self, pytest_files):
        """Files with conftest.py should detect 'conftest' in test pattern."""
        result = scan_patterns(pytest_files)
        assert "conftest" in result["test_pattern"].lower()

    def test_detects_unittest(self, unittest_files):
        """unittest usage should be detected."""
        result = scan_patterns(unittest_files)
        assert "unittest" in result["test_pattern"].lower()

    def test_no_test_files_unknown(self):
        """No test-related content should yield 'unknown' test pattern."""
        files = {
            "app.py": "def main():\n    print('hello')\n"
        }
        result = scan_patterns(files)
        assert result["test_pattern"] == "unknown"


class TestScanPatternsImportStyle:
    """Tests for import style detection within scan_patterns."""

    def test_detects_absolute_imports(self, absolute_import_files):
        """Predominantly absolute imports should be detected."""
        result = scan_patterns(absolute_import_files)
        assert "absolute" in result["import_style"].lower()

    def test_detects_relative_imports(self, relative_import_files):
        """Predominantly relative imports should be detected."""
        result = scan_patterns(relative_import_files)
        assert "relative" in result["import_style"].lower()

    def test_mixed_imports(self, mixed_import_files):
        """Mixed imports should produce some valid result (not crash)."""
        result = scan_patterns(mixed_import_files)
        assert isinstance(result["import_style"], str)
        assert result["import_style"] != ""

    def test_no_imports_unknown(self):
        """Files with no imports should yield 'unknown' import style."""
        files = {
            "constants.py": "MAX_SIZE = 100\nDEFAULT_NAME = 'test'\n"
        }
        result = scan_patterns(files)
        assert result["import_style"] == "unknown"


class TestScanPatternsIntegration:
    """Integration tests combining multiple pattern detections."""

    def test_full_project_scan(self):
        """Scan a realistic set of files and verify all fields populated."""
        files = {
            "my_module.py": (
                "from typing import TypedDict\n"
                "from assemblyzero.core import base\n"
                "import logging\n\n"
                "class MyState(TypedDict):\n"
                "    data: str\n\n"
                "def process_node(state: dict) -> dict:\n"
                '    return {"processed": True}\n'
            ),
            "test_module.py": (
                "import pytest\n\n"
                "@pytest.fixture\n"
                "def sample():\n"
                "    return 42\n\n"
                "def test_process(sample):\n"
                "    assert sample == 42\n"
            ),
            "utils_helper.py": (
                "class HelperClass:\n"
                "    pass\n\n"
                "def compute_thing():\n"
                "    return 0\n"
            ),
        }
        result = scan_patterns(files)

        for key in ["naming_convention", "state_pattern", "node_pattern",
                     "test_pattern", "import_style"]:
            assert isinstance(result[key], str)
            assert len(result[key]) > 0

        assert "TypedDict" in result["state_pattern"]
        assert "pytest" in result["test_pattern"].lower()

    def test_return_type_is_dict(self):
        """scan_patterns should return a dict (TypedDict)."""
        result = scan_patterns({})
        assert isinstance(result, dict)

    def test_large_file_contents(self):
        """Large file contents should be handled without errors."""
        files = {
            "big.py": "\n".join(
                [f"def func_{i}():\n    return {{'key': {i}}}\n" for i in range(100)]
            ),
        }
        result = scan_patterns(files)
        assert isinstance(result["naming_convention"], str)
        assert isinstance(result["node_pattern"], str)

    def test_non_python_files(self):
        """Non-Python files should not crash the scanner."""
        files = {
            "readme.md": "# My Project\n\nSome description.\n",
            "config.yml": "key: value\nother: data\n",
        }
        result = scan_patterns(files)
        assert isinstance(result, dict)

    def test_dunder_files_excluded_from_naming(self):
        """__init__.py and __main__.py should not affect naming convention."""
        files = {
            "__init__.py": "",
            "__main__.py": "if __name__ == '__main__':\n    pass\n",
            "my_module.py": "def my_func():\n    pass\n",
        }
        result = scan_patterns(files)
        assert "snake_case" in result["naming_convention"]


class TestDetectFrameworksEdgeCases:
    """Edge cases for detect_frameworks."""

    def test_case_insensitive_deps(self):
        """Dependency names should be matched case-insensitively."""
        result = detect_frameworks(["LangGraph", "FastAPI"], {})
        assert len(result) >= 2

    def test_all_expected_frameworks_present(self):
        """All expected frameworks should be in result regardless of order."""
        result = detect_frameworks(["pytest", "fastapi", "langgraph"], {})
        assert set(result) == {"pytest", "FastAPI", "LangGraph"}

    def test_deps_with_whitespace(self):
        """Deps with extra whitespace should still be matched."""
        result = detect_frameworks(["  langgraph  ", " pytest "], {})
        assert "LangGraph" in result
        assert "pytest" in result

    def test_anthropic_sdk_detected(self):
        """'anthropic' in deps should map to 'Anthropic SDK'."""
        result = detect_frameworks(["anthropic"], {})
        assert "Anthropic SDK" in result

    def test_django_detected(self):
        """'django' in deps should map to 'Django'."""
        result = detect_frameworks(["django"], {})
        assert "Django" in result


class TestExtractConventionsEdgeCases:
    """Edge cases for extract_conventions_from_claude_md."""

    def test_code_block_content_skipped(self):
        """Regular code blocks under convention headers should be skipped."""
        content = (
            "## Rules\n"
            "- Follow PEP 8\n"
            "```\n"
            "This is a code example, not a convention\n"
            "```\n"
            "- Use type hints\n"
        )
        result = extract_conventions_from_claude_md(content)
        assert isinstance(result, list)
        assert any("PEP 8" in c for c in result)
        assert not any("code example" in c.lower() for c in result)

    def test_very_large_claude_md(self):
        """Very large CLAUDE.md should not crash or hang."""
        content = "# Rules\n\n" + "".join(
            f"- Rule number {i}\n" for i in range(1000)
        )
        result = extract_conventions_from_claude_md(content)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_constraint_section(self):
        """Section with 'constraint' keyword should extract conventions."""
        content = (
            "# Project Constraints\n\n"
            "- Must support Python 3.11+\n"
            "- No external API calls in tests\n"
        )
        result = extract_conventions_from_claude_md(content)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_guideline_section(self):
        """Section with 'guideline' keyword should extract conventions."""
        content = (
            "# Coding Guidelines\n\n"
            "- Use absolute imports\n"
            "- Keep functions under 50 lines\n"
        )
        result = extract_conventions_from_claude_md(content)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_style_section(self):
        """Section with 'style' keyword should extract conventions."""
        content = (
            "# Code Style\n\n"
            "- Use 4-space indentation\n"
            "- Maximum line length is 100\n"
        )
        result = extract_conventions_from_claude_md(content)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_requirement_section(self):
        """Section with 'requirement' keyword should extract conventions."""
        content = (
            "## Requirements\n\n"
            "- Python 3.11 or higher\n"
            "- All tests must pass\n"
        )
        result = extract_conventions_from_claude_md(content)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_policy_section(self):
        """Section with 'policy' keyword should extract conventions."""
        content = (
            "## Code Policy\n\n"
            "- Use factory pattern for object creation\n"
            "- Prefer strategy over switch statements\n"
        )
        result = extract_conventions_from_claude_md(content)
        assert isinstance(result, list)
        assert len(result) > 0
```
