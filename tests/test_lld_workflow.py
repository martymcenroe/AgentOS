"""Tests for LLD Governance workflow (Issue #86).

Tests cover:
- State schema validation
- Audit trail utilities
- Node implementations (with mocks)
- Graph routing functions
- Mock mode E2E scenarios
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agentos.workflows.lld.audit import (
    assemble_context,
    create_lld_audit_dir,
    next_file_number,
    save_approved_metadata,
    save_audit_file,
    save_final_lld,
    validate_context_path,
)
from agentos.workflows.lld.graph import (
    build_lld_workflow,
    route_after_design,
    route_after_fetch,
    route_after_human_edit,
    route_after_review,
)
from agentos.workflows.lld.state import HumanDecision, LLDWorkflowState


class TestStateSchema:
    """Test LLDWorkflowState TypedDict and enums."""

    def test_human_decision_values(self):
        """Test HumanDecision enum values."""
        assert HumanDecision.SEND.value == "S"
        assert HumanDecision.REVISE.value == "R"
        assert HumanDecision.MANUAL.value == "M"

    def test_state_can_be_instantiated(self):
        """Test LLDWorkflowState can be created."""
        state: LLDWorkflowState = {
            "issue_number": 42,
            "context_files": [],
            "auto_mode": False,
            "mock_mode": True,
        }
        assert state["issue_number"] == 42
        assert state["mock_mode"] is True


class TestAuditFileNumbering:
    """Test sequential file numbering in audit trail."""

    def test_empty_directory(self, tmp_path):
        """Test first file gets number 1."""
        assert next_file_number(tmp_path) == 1

    def test_increments_after_existing(self, tmp_path):
        """Test increments past existing files."""
        (tmp_path / "001-issue.md").touch()
        (tmp_path / "002-draft.md").touch()
        assert next_file_number(tmp_path) == 3

    def test_handles_gaps(self, tmp_path):
        """Test finds max even with gaps."""
        (tmp_path / "001-issue.md").touch()
        (tmp_path / "005-verdict.md").touch()
        assert next_file_number(tmp_path) == 6

    def test_ignores_non_numbered(self, tmp_path):
        """Test ignores files without NNN- prefix."""
        (tmp_path / "readme.md").touch()
        (tmp_path / "001-issue.md").touch()
        assert next_file_number(tmp_path) == 2


class TestAuditFileSaving:
    """Test audit file saving."""

    def test_save_creates_file(self, tmp_path):
        """Test file is created with correct name."""
        path = save_audit_file(tmp_path, 1, "issue.md", "# Issue")
        assert path.exists()
        assert path.name == "001-issue.md"

    def test_save_content_correct(self, tmp_path):
        """Test content is saved correctly."""
        content = "# Test Content\n\nWith multiple lines."
        path = save_audit_file(tmp_path, 42, "draft.md", content)
        assert path.read_text() == content


class TestApprovedMetadata:
    """Test approved.json metadata."""

    def test_creates_json(self, tmp_path):
        """Test JSON file is created."""
        path = save_approved_metadata(
            tmp_path,
            number=10,
            issue_number=42,
            issue_title="Test Feature",
            final_lld_path="/path/to/lld.md",
            total_iterations=3,
            draft_count=2,
            verdict_count=2,
        )
        assert path.exists()
        assert path.name == "010-approved.json"

    def test_json_content(self, tmp_path):
        """Test JSON contains correct fields."""
        path = save_approved_metadata(
            tmp_path,
            number=1,
            issue_number=99,
            issue_title="My Feature",
            final_lld_path="/docs/LLDs/active/LLD-099.md",
            total_iterations=5,
            draft_count=3,
            verdict_count=2,
        )
        data = json.loads(path.read_text())
        assert data["issue_number"] == 99
        assert data["issue_title"] == "My Feature"
        assert data["total_iterations"] == 5
        assert "approved_at" in data


class TestSaveFinalLLD:
    """Test final LLD saving."""

    @patch("agentos.workflows.lld.audit.get_repo_root")
    def test_saves_to_correct_path(self, mock_root, tmp_path):
        """Test LLD saved to docs/LLDs/active/."""
        mock_root.return_value = tmp_path

        content = "# LLD Content"
        path = save_final_lld(42, content)

        assert path.exists()
        assert path.name == "LLD-042.md"
        assert path.read_text() == content
        # Check path contains LLDs/active (works with both / and \ separators)
        assert path.parent.name == "active"
        assert path.parent.parent.name == "LLDs"


class TestContextValidation:
    """Test context path validation."""

    @patch("agentos.workflows.lld.audit.get_repo_root")
    def test_valid_path_inside_project(self, mock_root, tmp_path):
        """Test valid path inside project root."""
        mock_root.return_value = tmp_path

        # Create a file inside project
        test_file = tmp_path / "src" / "main.py"
        test_file.parent.mkdir(parents=True)
        test_file.write_text("print('hello')")

        result = validate_context_path("src/main.py", tmp_path)
        assert result == test_file

    @patch("agentos.workflows.lld.audit.get_repo_root")
    def test_rejects_path_outside_project(self, mock_root, tmp_path):
        """Test path outside project root is rejected."""
        mock_root.return_value = tmp_path

        with pytest.raises(ValueError, match="outside project root"):
            validate_context_path("/etc/passwd", tmp_path)

    @patch("agentos.workflows.lld.audit.get_repo_root")
    def test_rejects_nonexistent_path(self, mock_root, tmp_path):
        """Test nonexistent path is rejected."""
        mock_root.return_value = tmp_path

        with pytest.raises(ValueError, match="does not exist"):
            validate_context_path("nonexistent.py", tmp_path)


class TestContextAssembly:
    """Test context file assembly."""

    @patch("agentos.workflows.lld.audit.get_repo_root")
    def test_assembles_single_file(self, mock_root, tmp_path):
        """Test assembling context from single file."""
        mock_root.return_value = tmp_path

        # Create context file
        ctx_file = tmp_path / "context.md"
        ctx_file.write_text("# Context\n\nSome content.")

        result = assemble_context(["context.md"], tmp_path)

        assert "## Reference: context.md" in result
        assert "Some content." in result

    @patch("agentos.workflows.lld.audit.get_repo_root")
    def test_assembles_multiple_files(self, mock_root, tmp_path):
        """Test assembling context from multiple files."""
        mock_root.return_value = tmp_path

        # Create context files
        (tmp_path / "file1.md").write_text("Content 1")
        (tmp_path / "file2.py").write_text("print('hello')")

        result = assemble_context(["file1.md", "file2.py"], tmp_path)

        assert "## Reference: file1.md" in result
        assert "## Reference: file2.py" in result
        assert "Content 1" in result
        assert "print('hello')" in result

    @patch("agentos.workflows.lld.audit.get_repo_root")
    def test_empty_context_files(self, mock_root, tmp_path):
        """Test empty context files list."""
        mock_root.return_value = tmp_path

        result = assemble_context([], tmp_path)
        assert result == ""


class TestGraphRouting:
    """Test graph conditional routing functions."""

    def test_route_after_fetch_success(self):
        """Test routing to design after successful fetch."""
        state: LLDWorkflowState = {"error_message": ""}
        result = route_after_fetch(state)
        assert result == "N1_design"

    def test_route_after_fetch_error(self):
        """Test routing to end on fetch error."""
        state: LLDWorkflowState = {"error_message": "Issue not found"}
        result = route_after_fetch(state)
        assert result == "end"

    def test_route_after_design_success(self):
        """Test routing to human_edit after successful design."""
        state: LLDWorkflowState = {"error_message": "", "design_status": "DRAFTED"}
        result = route_after_design(state)
        assert result == "N2_human_edit"

    def test_route_after_design_failed(self):
        """Test routing to end on design failure."""
        state: LLDWorkflowState = {"error_message": "", "design_status": "FAILED"}
        result = route_after_design(state)
        assert result == "end"

    def test_route_after_human_edit_send(self):
        """Test routing to review when user sends."""
        state: LLDWorkflowState = {"next_node": "N3_review", "error_message": ""}
        result = route_after_human_edit(state)
        assert result == "N3_review"

    def test_route_after_human_edit_revise(self):
        """Test routing to design when user revises."""
        state: LLDWorkflowState = {"next_node": "N1_design", "error_message": ""}
        result = route_after_human_edit(state)
        assert result == "N1_design"

    def test_route_after_human_edit_manual(self):
        """Test routing to end on manual exit."""
        state: LLDWorkflowState = {"next_node": "END", "error_message": "MANUAL: User exit"}
        result = route_after_human_edit(state)
        assert result == "end"

    def test_route_after_review_approved(self):
        """Test routing to finalize on approval."""
        state: LLDWorkflowState = {"next_node": "N4_finalize", "error_message": ""}
        result = route_after_review(state)
        assert result == "N4_finalize"

    def test_route_after_review_rejected(self):
        """Test routing to human_edit on rejection."""
        state: LLDWorkflowState = {"next_node": "N2_human_edit", "error_message": ""}
        result = route_after_review(state)
        assert result == "N2_human_edit"


class TestGraphCompilation:
    """Test that the graph compiles without errors."""

    def test_build_graph(self):
        """Test graph builds successfully."""
        workflow = build_lld_workflow()
        assert workflow is not None

    def test_graph_has_all_nodes(self):
        """Test all expected nodes exist."""
        workflow = build_lld_workflow()
        nodes = workflow.nodes
        expected = [
            "N0_fetch_issue",
            "N1_design",
            "N2_human_edit",
            "N3_review",
            "N4_finalize",
        ]
        for node in expected:
            assert node in nodes, f"Missing node: {node}"


class TestMockModeE2E:
    """End-to-end tests using mock mode."""

    @patch("agentos.workflows.lld.audit.get_repo_root")
    def test_happy_path_mock(self, mock_root, tmp_path):
        """Test full workflow with mock mode - approve on second iteration."""
        mock_root.return_value = tmp_path

        # Create necessary directories
        (tmp_path / "docs" / "LLDs" / "active").mkdir(parents=True)
        (tmp_path / "docs" / "LLDs" / "drafts").mkdir(parents=True)
        (tmp_path / "docs" / "audit" / "active").mkdir(parents=True)

        from agentos.workflows.lld.nodes import (
            fetch_issue,
            design,
            human_edit,
            review,
            finalize,
        )

        # Initial state
        state: LLDWorkflowState = {
            "issue_number": 42,
            "context_files": [],
            "auto_mode": True,
            "mock_mode": True,
            "iteration_count": 0,
            "draft_count": 0,
            "verdict_count": 0,
        }

        # N0: Fetch issue
        result = fetch_issue(state)
        state.update(result)
        assert state.get("issue_title") == "Mock Issue #42"
        assert state.get("error_message") == ""

        # N1: Design
        result = design(state)
        state.update(result)
        assert state.get("design_status") == "DRAFTED"
        assert state.get("lld_content") is not None

        # N2: Human edit (auto mode)
        result = human_edit(state)
        state.update(result)
        assert state.get("next_node") == "N3_review"

        # N3: Review (first iteration - reject)
        result = review(state)
        state.update(result)
        assert state.get("lld_status") == "BLOCKED"
        assert state.get("next_node") == "N2_human_edit"

        # N2: Human edit again (auto mode)
        result = human_edit(state)
        state.update(result)
        assert state.get("next_node") == "N3_review"

        # N3: Review (second iteration - approve)
        result = review(state)
        state.update(result)
        assert state.get("lld_status") == "APPROVED"
        assert state.get("next_node") == "N4_finalize"

        # N4: Finalize
        result = finalize(state)
        state.update(result)
        assert state.get("final_lld_path") is not None
        assert Path(state.get("final_lld_path")).exists()


class TestMaxIterations:
    """Test maximum iteration enforcement."""

    @patch("agentos.workflows.lld.audit.get_repo_root")
    def test_max_iterations_enforced(self, mock_root, tmp_path):
        """Test workflow exits after max iterations."""
        mock_root.return_value = tmp_path

        # Create necessary directories
        (tmp_path / "docs" / "audit" / "active").mkdir(parents=True)

        from agentos.workflows.lld.nodes import review

        # State at max iterations
        state: LLDWorkflowState = {
            "issue_number": 42,
            "mock_mode": True,
            "iteration_count": 5,  # At max
            "audit_dir": str(tmp_path / "docs" / "audit" / "active" / "42-lld"),
            "verdict_count": 4,
        }

        # Create audit dir
        Path(state["audit_dir"]).mkdir(parents=True)

        # Review should reject and set error
        result = review(state)

        assert "Max iterations" in result.get("error_message", "")
        assert result.get("next_node") == "END"
