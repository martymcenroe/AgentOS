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
        # Check path contains lld/active (works with both / and \ separators)
        assert path.parent.name == "active"
        assert path.parent.parent.name == "lld"


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
        """Test full workflow with mock mode - approve on second design iteration.

        Flow: fetch → design → human_edit → review (BLOCKED)
              → human_edit → design (revision) → human_edit → review (APPROVED)
              → finalize
        """
        mock_root.return_value = tmp_path

        # Create necessary directories
        (tmp_path / "docs" / "lld" / "active").mkdir(parents=True)
        (tmp_path / "docs" / "llds" / "drafts").mkdir(parents=True)
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

        # N1: Design (first draft)
        result = design(state)
        state.update(result)
        assert state.get("design_status") == "DRAFTED"
        assert state.get("lld_content") is not None

        # N2: Human edit (auto mode, no critique yet → review)
        result = human_edit(state)
        state.update(result)
        assert state.get("next_node") == "N3_review"

        # N3: Review (first iteration - mock rejects)
        result = review(state)
        state.update(result)
        assert state.get("lld_status") == "BLOCKED"
        assert state.get("next_node") == "N2_human_edit"
        assert state.get("gemini_critique")  # Should have critique

        # N2: Human edit (auto mode, has critique → design)
        result = human_edit(state)
        state.update(result)
        assert state.get("next_node") == "N1_design"
        assert state.get("user_feedback")  # Should have feedback for designer

        # N1: Design (revision with feedback)
        result = design(state)
        state.update(result)
        assert state.get("design_status") == "DRAFTED"
        assert state.get("gemini_critique") == ""  # Cleared after new draft

        # N2: Human edit (auto mode, no critique after new draft → review)
        result = human_edit(state)
        state.update(result)
        assert state.get("next_node") == "N3_review"

        # N3: Review (second iteration - mock approves)
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

        # State at max iterations (explicitly set max_iterations for test)
        state: LLDWorkflowState = {
            "issue_number": 42,
            "mock_mode": True,
            "iteration_count": 5,  # At max
            "max_iterations": 5,  # Explicit max for test
            "audit_dir": str(tmp_path / "docs" / "audit" / "active" / "42-lld"),
            "verdict_count": 4,
        }

        # Create audit dir
        Path(state["audit_dir"]).mkdir(parents=True)

        # Review should reject and set error
        result = review(state)

        assert "MAX_ITERATIONS" in result.get("error_message", "")
        assert result.get("next_node") == "END"


class TestProductionFetchIssue:
    """Test production fetch_issue code path (non-mock mode).

    These tests exercise the production code by mocking external dependencies
    (subprocess.run) rather than using mock_mode=True.
    """

    @patch("agentos.workflows.lld.audit.get_repo_root")
    @patch("agentos.workflows.lld.nodes.subprocess.run")
    def test_fetch_issue_calls_gh_cli_correctly(self, mock_run, mock_root, tmp_path):
        """Test that gh CLI is called with correct arguments."""
        mock_root.return_value = tmp_path
        (tmp_path / "docs" / "audit" / "active").mkdir(parents=True)

        # Mock successful gh CLI response
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"title": "Test Issue", "body": "Test body"}',
            stderr="",
        )

        from agentos.workflows.lld.nodes import fetch_issue

        state: LLDWorkflowState = {
            "issue_number": 123,
            "context_files": [],
            "mock_mode": False,  # Production mode!
        }

        result = fetch_issue(state)

        # Verify gh CLI was called correctly
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert call_args[0][0] == ["gh", "issue", "view", "123", "--json", "title,body"]
        assert call_args[1]["capture_output"] is True
        assert call_args[1]["text"] is True
        assert call_args[1]["timeout"] == 30

        # Verify result
        assert result["issue_title"] == "Test Issue"
        assert result["issue_body"] == "Test body"
        assert result["error_message"] == ""

    @patch("agentos.workflows.lld.audit.get_repo_root")
    @patch("agentos.workflows.lld.nodes.subprocess.run")
    def test_fetch_issue_handles_gh_cli_failure(self, mock_run, mock_root, tmp_path):
        """Test error handling when gh CLI fails."""
        mock_root.return_value = tmp_path

        # Mock failed gh CLI response
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="Could not resolve to an Issue with the number 999",
        )

        from agentos.workflows.lld.nodes import fetch_issue

        state: LLDWorkflowState = {
            "issue_number": 999,
            "context_files": [],
            "mock_mode": False,
        }

        result = fetch_issue(state)

        assert "Issue #999 not found" in result["error_message"]

    @patch("agentos.workflows.lld.audit.get_repo_root")
    @patch("agentos.workflows.lld.nodes.subprocess.run")
    def test_fetch_issue_handles_timeout(self, mock_run, mock_root, tmp_path):
        """Test error handling when gh CLI times out."""
        mock_root.return_value = tmp_path

        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="gh", timeout=30)

        from agentos.workflows.lld.nodes import fetch_issue

        state: LLDWorkflowState = {
            "issue_number": 42,
            "context_files": [],
            "mock_mode": False,
        }

        result = fetch_issue(state)

        assert "Timeout" in result["error_message"]

    @patch("agentos.workflows.lld.audit.get_repo_root")
    @patch("agentos.workflows.lld.nodes.subprocess.run")
    def test_fetch_issue_handles_invalid_json(self, mock_run, mock_root, tmp_path):
        """Test error handling when gh CLI returns invalid JSON."""
        mock_root.return_value = tmp_path

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="not valid json",
            stderr="",
        )

        from agentos.workflows.lld.nodes import fetch_issue

        state: LLDWorkflowState = {
            "issue_number": 42,
            "context_files": [],
            "mock_mode": False,
        }

        result = fetch_issue(state)

        assert "Failed to parse issue data" in result["error_message"]


class TestProductionDesign:
    """Test production design code path (non-mock mode).

    These tests exercise the production code by mocking the designer node.
    The designer node is imported lazily inside the function, so we mock
    the module where it's imported from.
    """

    @patch("agentos.workflows.lld.audit.get_repo_root")
    @patch("agentos.nodes.designer.design_lld_node")
    def test_design_calls_designer_node(self, mock_designer, mock_root, tmp_path):
        """Test that designer node is called with correct state."""
        mock_root.return_value = tmp_path
        (tmp_path / "docs" / "audit" / "active" / "42-lld").mkdir(parents=True)

        # Mock successful design response
        mock_designer.return_value = {
            "design_status": "DRAFTED",
            "lld_content": "# Test LLD Content",
            "lld_draft_path": str(tmp_path / "draft.md"),
        }

        from agentos.workflows.lld.nodes import design

        state: LLDWorkflowState = {
            "issue_id": 42,
            "issue_number": 42,
            "iteration_count": 0,
            "draft_count": 0,
            "audit_dir": str(tmp_path / "docs" / "audit" / "active" / "42-lld"),
            "mock_mode": False,  # Production mode!
        }

        result = design(state)

        # Verify designer was called
        mock_designer.assert_called_once()
        call_args = mock_designer.call_args[0][0]
        assert call_args["issue_id"] == 42
        assert call_args["iteration_count"] == 0

        # Verify result
        assert result["design_status"] == "DRAFTED"
        assert result["lld_content"] == "# Test LLD Content"
        assert result["draft_count"] == 1
        assert result["error_message"] == ""

    @patch("agentos.workflows.lld.audit.get_repo_root")
    @patch("agentos.nodes.designer.design_lld_node")
    def test_design_handles_failure(self, mock_designer, mock_root, tmp_path):
        """Test error handling when designer node fails."""
        mock_root.return_value = tmp_path

        mock_designer.return_value = {
            "design_status": "FAILED",
            "lld_content": "",
            "lld_draft_path": "",
        }

        from agentos.workflows.lld.nodes import design

        state: LLDWorkflowState = {
            "issue_id": 42,
            "mock_mode": False,
        }

        result = design(state)

        assert result["design_status"] == "FAILED"
        assert "Designer node failed" in result["error_message"]


class TestProductionReview:
    """Test production review code path (non-mock mode).

    These tests exercise the production code by mocking the governance node.
    The governance node is imported lazily inside the function, so we mock
    the module where it's imported from.
    """

    @patch("agentos.workflows.lld.audit.get_repo_root")
    @patch("agentos.nodes.governance.review_lld_node")
    def test_review_calls_governance_node(self, mock_governance, mock_root, tmp_path):
        """Test that governance node is called with correct state."""
        mock_root.return_value = tmp_path
        (tmp_path / "docs" / "audit" / "active" / "42-lld").mkdir(parents=True)

        mock_governance.return_value = {
            "lld_status": "APPROVED",
            "gemini_critique": "All good!",
        }

        from agentos.workflows.lld.nodes import review

        state: LLDWorkflowState = {
            "issue_id": 42,
            "lld_content": "# LLD Content",
            "lld_draft_path": "/path/to/draft.md",
            "iteration_count": 2,
            "verdict_count": 1,
            "audit_dir": str(tmp_path / "docs" / "audit" / "active" / "42-lld"),
            "mock_mode": False,  # Production mode!
        }

        result = review(state)

        # Verify governance was called
        mock_governance.assert_called_once()
        call_args = mock_governance.call_args[0][0]
        assert call_args["issue_id"] == 42
        assert call_args["lld_content"] == "# LLD Content"
        assert call_args["iteration_count"] == 2

        # Verify result
        assert result["lld_status"] == "APPROVED"
        assert result["next_node"] == "N4_finalize"
        assert result["error_message"] == ""

    @patch("agentos.workflows.lld.audit.get_repo_root")
    @patch("agentos.nodes.governance.review_lld_node")
    def test_review_routes_to_human_edit_on_block(self, mock_governance, mock_root, tmp_path):
        """Test routing to human_edit when review blocks."""
        mock_root.return_value = tmp_path
        (tmp_path / "docs" / "audit" / "active" / "42-lld").mkdir(parents=True)

        mock_governance.return_value = {
            "lld_status": "BLOCKED",
            "gemini_critique": "Missing section 5",
        }

        from agentos.workflows.lld.nodes import review

        state: LLDWorkflowState = {
            "issue_id": 42,
            "lld_content": "# LLD Content",
            "iteration_count": 1,
            "verdict_count": 0,
            "audit_dir": str(tmp_path / "docs" / "audit" / "active" / "42-lld"),
            "mock_mode": False,
        }

        result = review(state)

        assert result["lld_status"] == "BLOCKED"
        assert result["next_node"] == "N2_human_edit"
        assert result["gemini_critique"] == "Missing section 5"

    @patch("agentos.workflows.lld.audit.get_repo_root")
    @patch("agentos.nodes.governance.review_lld_node")
    def test_review_enforces_max_iterations_production(self, mock_governance, mock_root, tmp_path):
        """Test max iterations enforcement in production mode."""
        mock_root.return_value = tmp_path
        (tmp_path / "docs" / "audit" / "active" / "42-lld").mkdir(parents=True)

        mock_governance.return_value = {
            "lld_status": "BLOCKED",
            "gemini_critique": "Still not good enough",
        }

        from agentos.workflows.lld.nodes import review

        state: LLDWorkflowState = {
            "issue_id": 42,
            "lld_content": "# LLD Content",
            "iteration_count": 5,  # At max
            "max_iterations": 5,  # Explicit max for test
            "verdict_count": 4,
            "audit_dir": str(tmp_path / "docs" / "audit" / "active" / "42-lld"),
            "mock_mode": False,
        }

        result = review(state)

        assert "MAX_ITERATIONS" in result["error_message"]
        assert result["next_node"] == "END"


class TestAutoModeLLDContent:
    """Test that auto mode properly reads and saves LLD content.

    These tests specifically verify the bug where auto_mode=True was
    not reading LLD content from disk, resulting in empty LLDs being
    sent to review and saved to the final location.

    Bug scenario:
    1. designer.py generates LLD and saves to disk, returns empty lld_content
    2. human_edit in auto mode skipped reading from disk
    3. review received empty content
    4. finalize saved empty/minimal content

    The fix ensures human_edit reads from disk in auto mode.
    """

    @patch("agentos.workflows.lld.audit.get_repo_root")
    def test_auto_mode_reads_lld_from_disk(self, mock_root, tmp_path):
        """Test human_edit in auto mode reads LLD from draft file.

        This is the core bug fix: when designer saves LLD to disk but
        returns empty lld_content, auto mode must read from disk.
        """
        mock_root.return_value = tmp_path

        # Create draft file with actual content
        drafts_dir = tmp_path / "docs" / "LLDs" / "drafts"
        drafts_dir.mkdir(parents=True)
        draft_path = drafts_dir / "42-LLD.md"
        draft_content = """# LLD-042: Real Feature

## 1. Context & Goal

This is the actual LLD content that was saved to disk.

## 2. Proposed Changes

Real implementation details here.
"""
        draft_path.write_text(draft_content, encoding="utf-8")

        from agentos.workflows.lld.nodes import human_edit

        # Simulate state where designer returned empty lld_content
        # but saved actual content to lld_draft_path
        state: LLDWorkflowState = {
            "issue_number": 42,
            "auto_mode": True,
            "mock_mode": False,  # Not using mock mode!
            "iteration_count": 0,
            "lld_content": "",  # Empty! Bug scenario
            "lld_draft_path": str(draft_path),  # But path exists
        }

        result = human_edit(state)

        # Key assertion: lld_content must be populated from disk
        assert result.get("lld_content") == draft_content
        assert "## 1. Context & Goal" in result.get("lld_content", "")
        assert len(result.get("lld_content", "")) > 100

    @patch("agentos.workflows.lld.audit.get_repo_root")
    def test_auto_mode_e2e_saves_actual_content(self, mock_root, tmp_path):
        """Test full auto mode E2E saves real LLD content, not just header.

        This verifies the complete flow: design → human_edit → review → finalize
        results in a final LLD with actual content.
        """
        mock_root.return_value = tmp_path

        # Create necessary directories
        (tmp_path / "docs" / "lld" / "active").mkdir(parents=True)
        (tmp_path / "docs" / "LLDs" / "drafts").mkdir(parents=True)
        (tmp_path / "docs" / "audit" / "active").mkdir(parents=True)

        from agentos.workflows.lld.nodes import (
            fetch_issue,
            design,
            human_edit,
            review,
            finalize,
        )

        # Run full workflow in auto + mock mode
        state: LLDWorkflowState = {
            "issue_number": 99,
            "context_files": [],
            "auto_mode": True,
            "mock_mode": True,
            "iteration_count": 0,
        }

        # N0: Fetch
        result = fetch_issue(state)
        state.update(result)

        # N1: Design (creates draft with content)
        result = design(state)
        state.update(result)

        # Verify design created real content
        assert state.get("lld_draft_path")
        assert Path(state.get("lld_draft_path")).exists()
        draft_on_disk = Path(state.get("lld_draft_path")).read_text(encoding="utf-8")
        assert "## 1. Context & Goal" in draft_on_disk

        # N2: Human edit (auto mode - should read from disk)
        result = human_edit(state)
        state.update(result)

        # KEY ASSERTION: lld_content must have the actual content
        assert "## 1. Context & Goal" in state.get("lld_content", "")
        assert len(state.get("lld_content", "")) > 200

        # N3: Review (first iteration rejects in mock)
        result = review(state)
        state.update(result)

        # N2: Human edit again
        result = human_edit(state)
        state.update(result)

        # Content should still be present
        assert "## 1. Context & Goal" in state.get("lld_content", "")

        # N3: Review (second iteration approves in mock)
        result = review(state)
        state.update(result)
        assert state.get("lld_status") == "APPROVED"

        # N4: Finalize
        result = finalize(state)
        state.update(result)

        # CRITICAL: Final saved LLD must have actual content
        final_path = Path(state.get("final_lld_path"))
        assert final_path.exists()

        final_content = final_path.read_text(encoding="utf-8")

        # Must contain original LLD sections, not just review header
        assert "## 1. Context & Goal" in final_content
        assert "## 2. Proposed Changes" in final_content

        # Review header should also be present (embedded)
        assert "Review Summary" in final_content or "APPROVED" in final_content

        # Content should be substantial, not just ~150 bytes
        assert len(final_content) > 500, f"Final LLD too short: {len(final_content)} bytes"

    @patch("agentos.workflows.lld.audit.get_repo_root")
    def test_finalize_reads_from_disk_when_content_empty(self, mock_root, tmp_path):
        """Test finalize safety check reads from disk if lld_content is empty."""
        mock_root.return_value = tmp_path

        # Create directories and draft file
        (tmp_path / "docs" / "lld" / "active").mkdir(parents=True)
        (tmp_path / "docs" / "audit" / "active" / "42-lld").mkdir(parents=True)

        draft_content = """# LLD-042: Recovery Test

## 1. Context & Goal
This content should be recovered from disk.

## 2. Implementation
Details here.
"""
        draft_path = tmp_path / "draft.md"
        draft_path.write_text(draft_content, encoding="utf-8")

        from agentos.workflows.lld.nodes import finalize

        # Simulate buggy state where lld_content is empty
        state: LLDWorkflowState = {
            "issue_id": 42,
            "issue_title": "Test Issue",
            "lld_content": "",  # Empty - the bug scenario
            "lld_draft_path": str(draft_path),
            "verdict_count": 1,
            "audit_dir": str(tmp_path / "docs" / "audit" / "active" / "42-lld"),
        }

        result = finalize(state)

        # Should succeed, not error
        assert result.get("error_message") == ""
        assert result.get("final_lld_path")

        # Final file should have actual content
        final_path = Path(result.get("final_lld_path"))
        final_content = final_path.read_text(encoding="utf-8")
        assert "## 1. Context & Goal" in final_content
        assert "recovered from disk" in final_content

    @patch("agentos.workflows.lld.audit.get_repo_root")
    def test_finalize_errors_when_no_content_available(self, mock_root, tmp_path):
        """Test finalize returns error when both content and file are missing."""
        mock_root.return_value = tmp_path

        (tmp_path / "docs" / "lld" / "active").mkdir(parents=True)

        from agentos.workflows.lld.nodes import finalize

        state: LLDWorkflowState = {
            "issue_id": 42,
            "issue_title": "Test Issue",
            "lld_content": "",  # Empty
            "lld_draft_path": "/nonexistent/path.md",  # Doesn't exist
            "verdict_count": 1,
        }

        result = finalize(state)

        # Should return error
        assert "No LLD content" in result.get("error_message", "")
        assert not result.get("final_lld_path")


class TestAutoModeRevisionFlow:
    """Test that auto mode properly handles revision cycles.

    When Gemini returns BLOCKED, auto mode should:
    1. Go back to N1_design (not N3_review)
    2. Pass critique as user_feedback
    3. Designer generates revised draft
    4. New draft is saved to audit trail

    Bug scenario (issue #7):
    - First draft created: 002-draft.md
    - Review rejects: 003-verdict.md
    - Auto mode loops N2→N3→N2→N3... without creating new drafts
    - Result: Only one draft, 27 verdicts, all reviewing same content
    """

    @patch("agentos.workflows.lld.audit.get_repo_root")
    def test_auto_mode_with_critique_goes_to_design(self, mock_root, tmp_path):
        """Test human_edit routes to N1_design when there's critique feedback."""
        mock_root.return_value = tmp_path

        from agentos.workflows.lld.nodes import human_edit

        state: LLDWorkflowState = {
            "issue_number": 42,
            "auto_mode": True,
            "iteration_count": 1,
            "gemini_critique": "Missing safety section. Add error handling.",
            "lld_content": "# Old draft",
        }

        result = human_edit(state)

        # Should go to design, not review
        assert result.get("next_node") == "N1_design"
        # Feedback should contain the critique
        assert "Missing safety section" in result.get("user_feedback", "")

    @patch("agentos.workflows.lld.audit.get_repo_root")
    def test_auto_mode_without_critique_goes_to_review(self, mock_root, tmp_path):
        """Test human_edit routes to N3_review when no critique (first iteration)."""
        mock_root.return_value = tmp_path

        drafts_dir = tmp_path / "docs" / "LLDs" / "drafts"
        drafts_dir.mkdir(parents=True)
        draft_path = drafts_dir / "42-LLD.md"
        draft_path.write_text("# Initial draft content", encoding="utf-8")

        from agentos.workflows.lld.nodes import human_edit

        state: LLDWorkflowState = {
            "issue_number": 42,
            "auto_mode": True,
            "iteration_count": 0,
            "gemini_critique": "",  # No critique yet
            "lld_content": "",
            "lld_draft_path": str(draft_path),
        }

        result = human_edit(state)

        # Should go to review
        assert result.get("next_node") == "N3_review"
        # Content should be read from disk
        assert "Initial draft content" in result.get("lld_content", "")

    @patch("agentos.workflows.lld.audit.get_repo_root")
    def test_revision_flow_creates_multiple_drafts(self, mock_root, tmp_path):
        """Test full revision flow creates new draft on each design iteration.

        This is the key test: verify that each design iteration creates a
        new draft file in the audit trail.
        """
        mock_root.return_value = tmp_path

        # Create directories
        (tmp_path / "docs" / "lld" / "active").mkdir(parents=True)
        (tmp_path / "docs" / "llds" / "drafts").mkdir(parents=True)
        (tmp_path / "docs" / "audit" / "active").mkdir(parents=True)

        from agentos.workflows.lld.nodes import (
            fetch_issue,
            design,
            human_edit,
            review,
        )

        # Initial state
        state: LLDWorkflowState = {
            "issue_number": 42,
            "context_files": [],
            "auto_mode": True,
            "mock_mode": True,
            "iteration_count": 0,
        }

        # N0: Fetch
        result = fetch_issue(state)
        state.update(result)
        audit_dir = Path(state.get("audit_dir"))

        # N1: First design
        result = design(state)
        state.update(result)

        # Count draft files after first design
        draft_files_1 = list(audit_dir.glob("*-draft.md"))
        assert len(draft_files_1) == 1, "First design should create one draft"
        first_draft_size = draft_files_1[0].stat().st_size
        assert first_draft_size > 100, "First draft should have content"

        # N2: Human edit (auto - no critique, goes to review)
        result = human_edit(state)
        state.update(result)
        assert state.get("next_node") == "N3_review"

        # N3: Review (mock rejects on first iteration)
        result = review(state)
        state.update(result)
        assert state.get("lld_status") == "BLOCKED"
        assert state.get("next_node") == "N2_human_edit"

        # N2: Human edit again (auto - has critique, goes to design)
        result = human_edit(state)
        state.update(result)
        assert state.get("next_node") == "N1_design", "Should return to design after BLOCKED"
        assert state.get("user_feedback"), "Should have feedback for designer"

        # N1: Second design (revision)
        result = design(state)
        state.update(result)

        # Count draft files after second design
        draft_files_2 = list(audit_dir.glob("*-draft.md"))
        assert len(draft_files_2) == 2, f"Second design should create another draft, got {len(draft_files_2)}"

        # Both drafts should have content
        for draft in draft_files_2:
            assert draft.stat().st_size > 100, f"Draft {draft.name} should have content"


class TestSharedAuditHelpers:
    """Test the shared audit helper functions."""

    @patch("agentos.workflows.lld.audit.get_repo_root")
    def test_save_draft_to_audit_creates_file(self, mock_root, tmp_path):
        """Test _save_draft_to_audit creates file correctly."""
        mock_root.return_value = tmp_path
        audit_dir = tmp_path / "audit"
        audit_dir.mkdir()

        from agentos.workflows.lld.nodes import _save_draft_to_audit

        state: LLDWorkflowState = {
            "draft_count": 0,
            "file_counter": 0,
        }

        file_num, draft_count = _save_draft_to_audit(
            audit_dir, "# Draft Content", state
        )

        assert file_num == 1
        assert draft_count == 1
        assert (audit_dir / "001-draft.md").exists()
        assert (audit_dir / "001-draft.md").read_text() == "# Draft Content"

    @patch("agentos.workflows.lld.audit.get_repo_root")
    def test_save_verdict_to_audit_creates_file(self, mock_root, tmp_path):
        """Test _save_verdict_to_audit creates file correctly."""
        mock_root.return_value = tmp_path
        audit_dir = tmp_path / "audit"
        audit_dir.mkdir()

        from agentos.workflows.lld.nodes import _save_verdict_to_audit

        state: LLDWorkflowState = {
            "verdict_count": 0,
            "file_counter": 0,
        }

        file_num, verdict_count = _save_verdict_to_audit(
            audit_dir, "APPROVED", "All good!", state
        )

        assert file_num == 1
        assert verdict_count == 1
        assert (audit_dir / "001-verdict.md").exists()
        content = (audit_dir / "001-verdict.md").read_text()
        assert "APPROVED" in content
        assert "All good!" in content
