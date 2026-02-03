"""Test file for Issue #141.

Tests archival functionality for LLD and report files.
"""

import logging
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pytest

from agentos.workflows.testing.nodes.finalize import (
    _generate_summary,
    archive_file_to_done,
    archive_workflow_artifacts,
)
from agentos.workflows.testing.state import TestingWorkflowState


# Integration/E2E fixtures
@pytest.fixture
def temp_repo():
    """Create a temporary repository structure for testing."""
    with TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)
        
        # Create directory structure
        (repo / "docs" / "lld" / "active").mkdir(parents=True, exist_ok=True)
        (repo / "docs" / "reports" / "active").mkdir(parents=True, exist_ok=True)
        
        yield repo


@pytest.fixture
def test_client():
    """Test client for API calls."""
    # Not needed for these tests but required by test scaffolding
    yield None


# Unit Tests
# -----------

def test_070():
    """
    Empty state | unit | State with no paths | Graceful no-op | No
    exception, empty archival list
    """
    # TDD: Arrange
    state: TestingWorkflowState = {
        "issue_number": 141,
        "lld_path": "",
        "repo_root": "",
        "worktree_path": "",
        "original_repo_root": "",
        "lld_content": "",
        "test_plan_section": "",
        "test_scenarios": [],
        "detected_test_types": [],
        "coverage_target": 90,
        "requirements": [],
        "files_to_modify": [],
        "audit_dir": "",
        "file_counter": 1,
        "iteration_count": 0,
        "max_iterations": 10,
        "test_files": [],
        "implementation_files": [],
        "coverage_module": "",
        "red_phase_output": "",
        "green_phase_output": "",
        "coverage_achieved": 0.0,
        "e2e_output": "",
        "test_plan_review_prompt": "",
        "test_plan_verdict": "",
        "test_plan_status": "PENDING",
        "gemini_feedback": "",
        "next_node": "",
        "implementation_exists": False,
        "test_report_path": "",
        "implementation_report_path": "",
        "error_message": "",
        "auto_mode": False,
        "mock_mode": False,
        "skip_e2e": False,
        "scaffold_only": False,
        "green_only": False,
        "sandbox_repo": "",
        "e2e_max_issues": 0,
        "e2e_max_prs": 0,
        "doc_wiki_path": "",
        "doc_runbook_path": "",
        "doc_lessons_path": "",
        "doc_readme_updated": False,
        "doc_cp_paths": [],
        "skip_docs": False,
        "doc_scope": "auto",
    }

    # TDD: Act
    result = archive_workflow_artifacts(state)

    # TDD: Assert
    assert result["archived"] == []
    assert result["skipped"] == []


def test_110_generate_summary():
    """
    Test _generate_summary function for coverage.
    Coverage for lines 228-241.
    """
    # TDD: Arrange
    from agentos.workflows.testing.audit import TestReportMetadata
    
    metadata: TestReportMetadata = {
        "issue_number": 141,
        "lld_path": "docs/lld/active/LLD-141.md",
        "completed_at": "2025-01-01T00:00:00",
        "test_files": ["tests/test_foo.py", "tests/test_bar.py"],
        "implementation_files": ["src/foo.py", "src/bar.py"],
        "coverage_achieved": 95.5,
        "coverage_target": 90,
        "total_iterations": 2,
        "test_count": 10,
        "passed_count": 10,
        "failed_count": 0,
        "e2e_passed": True,
    }
    
    # TDD: Act
    result = _generate_summary(metadata)
    
    # TDD: Assert
    assert "Issue #141" in result
    assert "95.5%" in result
    assert "tests/test_foo.py" in result
    assert "src/foo.py" in result
    assert "Passed" in result  # E2E status


# Integration Tests
# -----------------

def test_010(temp_repo, test_client, caplog):
    """
    Happy path - LLD archived | integration | State with valid LLD path
    in active/ | LLD moved to done/, path returned | File exists in done/,
    not in active/, log contains success message
    """
    # TDD: Arrange
    caplog.set_level(logging.INFO)
    lld_path = temp_repo / "docs" / "lld" / "active" / "LLD-141.md"
    lld_path.write_text("# Test LLD")
    
    # TDD: Act
    result = archive_file_to_done(lld_path)
    
    # TDD: Assert
    assert result is not None
    done_path = temp_repo / "docs" / "lld" / "done" / "LLD-141.md"
    assert done_path.exists()
    assert not lld_path.exists()
    assert "Archived" in caplog.text
    assert "LLD-141.md" in caplog.text


def test_020(temp_repo, test_client, caplog):
    """
    Happy path - Reports archived | integration | State with report paths
    in active/ | Reports moved to done/ | Files exist in done/, not in
    active/, log contains success message
    """
    # TDD: Arrange
    caplog.set_level(logging.INFO)
    report1 = temp_repo / "docs" / "reports" / "active" / "141-test-report.md"
    report2 = temp_repo / "docs" / "reports" / "active" / "141-impl-report.md"
    report1.write_text("# Test Report")
    report2.write_text("# Impl Report")
    
    state: TestingWorkflowState = {
        "issue_number": 141,
        "test_report_path": str(report1),
        "implementation_report_path": str(report2),
    }  # type: ignore
    
    # TDD: Act
    result = archive_workflow_artifacts(state)
    
    # TDD: Assert
    assert len(result["archived"]) == 2
    assert not report1.exists()
    assert not report2.exists()
    done1 = temp_repo / "docs" / "reports" / "done" / "141-test-report.md"
    done2 = temp_repo / "docs" / "reports" / "done" / "141-impl-report.md"
    assert done1.exists()
    assert done2.exists()
    assert "Archived" in caplog.text


def test_030(test_client, caplog):
    """
    LLD not found | integration | State with non-existent LLD path |
    Warning logged, None returned | No exception, log contains warning
    """
    # TDD: Arrange
    caplog.set_level(logging.WARNING)
    non_existent = Path("/tmp/does-not-exist/docs/lld/active/LLD-999.md")
    
    # TDD: Act
    result = archive_file_to_done(non_existent)
    
    # TDD: Assert
    assert result is None
    assert "Archive skipped" in caplog.text
    assert "File not found" in caplog.text


def test_040(temp_repo, test_client, caplog):
    """
    LLD not in active/ | integration | State with LLD in arbitrary path |
    Skip archival, None returned | File unchanged, log indicates skip
    """
    # TDD: Arrange
    caplog.set_level(logging.INFO)
    arbitrary_path = temp_repo / "docs" / "arbitrary" / "file.md"
    arbitrary_path.parent.mkdir(parents=True, exist_ok=True)
    arbitrary_path.write_text("# Test")
    
    # TDD: Act
    result = archive_file_to_done(arbitrary_path)
    
    # TDD: Assert
    assert result is None
    assert arbitrary_path.exists()
    assert "Archive skipped" in caplog.text
    assert "not in active/" in caplog.text


def test_050(temp_repo, test_client):
    """
    done/ doesn't exist | integration | Valid LLD, no done/ directory |
    done/ created, LLD moved | Directory created, file moved
    """
    # TDD: Arrange
    lld_path = temp_repo / "docs" / "lld" / "active" / "LLD-141.md"
    lld_path.write_text("# Test LLD")
    done_dir = temp_repo / "docs" / "lld" / "done"
    assert not done_dir.exists()
    
    # TDD: Act
    result = archive_file_to_done(lld_path)
    
    # TDD: Assert
    assert result is not None
    assert done_dir.exists()
    assert (done_dir / "LLD-141.md").exists()
    assert not lld_path.exists()


def test_060(temp_repo, test_client, caplog):
    """
    Destination file exists | integration | LLD exists in both active/
    and done/ | Append timestamp to new name | No overwrite, both files
    preserved
    """
    # TDD: Arrange
    caplog.set_level(logging.INFO)
    lld_active = temp_repo / "docs" / "lld" / "active" / "LLD-141.md"
    lld_done = temp_repo / "docs" / "lld" / "done" / "LLD-141.md"
    lld_done.parent.mkdir(parents=True, exist_ok=True)
    
    lld_active.write_text("# New LLD")
    lld_done.write_text("# Old LLD")
    
    # TDD: Act
    result = archive_file_to_done(lld_active)
    
    # TDD: Assert
    assert result is not None
    assert lld_done.exists()  # Original preserved
    assert lld_done.read_text() == "# Old LLD"  # Original unchanged
    assert not lld_active.exists()  # Source moved
    # New file should have timestamp in name
    assert "timestamped name" in caplog.text
    # Find the timestamped file
    timestamped_files = list(lld_done.parent.glob("LLD-141-*.md"))
    assert len(timestamped_files) == 1
    assert timestamped_files[0].read_text() == "# New LLD"


def test_080(temp_repo, test_client, caplog):
    """
    Mixed success | integration | Some files exist, some don't | Archive
    existing, log missing | Partial archival succeeds
    """
    # TDD: Arrange
    caplog.set_level(logging.WARNING)
    lld_path = temp_repo / "docs" / "lld" / "active" / "LLD-141.md"
    lld_path.write_text("# Test LLD")
    
    state: TestingWorkflowState = {
        "issue_number": 141,
        "lld_path": str(lld_path),
        "test_report_path": "/tmp/does-not-exist.md",
    }  # type: ignore
    
    # TDD: Act
    result = archive_workflow_artifacts(state)
    
    # TDD: Assert
    assert len(result["archived"]) == 1  # LLD archived
    assert len(result["skipped"]) == 1  # Report skipped
    assert not lld_path.exists()  # LLD moved
    done_lld = temp_repo / "docs" / "lld" / "done" / "LLD-141.md"
    assert done_lld.exists()
    assert "File not found" in caplog.text


def test_090(temp_repo, test_client, caplog):
    """
    Workflow failed - no archival | integration | State with
    workflow_success=False, valid LLD path | No files moved, skip logged |
    Files remain in active/, log indicates skip
    """
    # TDD: Arrange
    from agentos.workflows.testing.nodes.finalize import finalize
    
    caplog.set_level(logging.INFO)
    lld_path = temp_repo / "docs" / "lld" / "active" / "LLD-141.md"
    lld_path.write_text("# Test LLD")
    
    # Create audit dir
    audit_dir = temp_repo / "audit"
    audit_dir.mkdir(parents=True, exist_ok=True)
    
    # Create minimal state for finalize function
    state: TestingWorkflowState = {
        "issue_number": 141,
        "lld_path": str(lld_path),
        "repo_root": str(temp_repo),
        "workflow_success": False,  # Workflow failed
        "test_files": [],
        "implementation_files": [],
        "coverage_achieved": 0.0,
        "coverage_target": 90,
        "iteration_count": 0,
        "green_phase_output": "",
        "skip_e2e": True,
        "audit_dir": str(audit_dir),
    }  # type: ignore
    
    # TDD: Act
    result = finalize(state)
    
    # TDD: Assert
    assert lld_path.exists()  # File not moved
    assert "workflow_success=False" in caplog.text or "Workflow failed" in caplog.text
    assert result["archived_files"] == []
    assert result["skipped_files"] == []


def test_100_archive_file_exception(temp_repo, test_client, caplog):
    """
    Test exception handling in archive_file_to_done.
    Coverage for lines 74-76.
    """
    # TDD: Arrange
    caplog.set_level(logging.ERROR)
    lld_path = temp_repo / "docs" / "lld" / "active" / "LLD-141.md"
    lld_path.write_text("# Test LLD")

    # TDD: Act - Mock rename to raise exception
    with patch.object(Path, 'rename', side_effect=OSError("Permission denied")):
        result = archive_file_to_done(lld_path)

    # TDD: Assert
    assert result is None
    assert "Archive failed" in caplog.text
    assert "Permission denied" in caplog.text


def test_120_lld_archival_fails_via_wrapper(temp_repo, test_client, caplog):
    """
    Test LLD archival failure through archive_workflow_artifacts.
    Coverage for line 102: skipped.append(lld_path_str)
    """
    # TDD: Arrange
    caplog.set_level(logging.INFO)
    # LLD exists but not in active/ directory - will return None
    lld_path = temp_repo / "docs" / "arbitrary" / "LLD-141.md"
    lld_path.parent.mkdir(parents=True, exist_ok=True)
    lld_path.write_text("# Test LLD")

    state: TestingWorkflowState = {
        "issue_number": 141,
        "lld_path": str(lld_path),
    }  # type: ignore

    # TDD: Act
    result = archive_workflow_artifacts(state)

    # TDD: Assert
    assert len(result["archived"]) == 0
    assert len(result["skipped"]) == 1
    assert str(lld_path) in result["skipped"]


def test_130_impl_report_archival_fails(temp_repo, test_client, caplog):
    """
    Test impl report archival failure through archive_workflow_artifacts.
    Coverage for line 122: skipped.append(impl_report_path_str)
    """
    # TDD: Arrange
    caplog.set_level(logging.INFO)
    # Impl report exists but not in active/ directory
    impl_report = temp_repo / "docs" / "arbitrary" / "impl-report.md"
    impl_report.parent.mkdir(parents=True, exist_ok=True)
    impl_report.write_text("# Impl Report")

    state: TestingWorkflowState = {
        "issue_number": 141,
        "implementation_report_path": str(impl_report),
    }  # type: ignore

    # TDD: Act
    result = archive_workflow_artifacts(state)

    # TDD: Assert
    assert len(result["archived"]) == 0
    assert len(result["skipped"]) == 1
    assert str(impl_report) in result["skipped"]


def test_140_finalize_with_e2e_output(temp_repo, test_client, caplog):
    """
    Test finalize with skip_e2e=False and e2e_output.
    Coverage for line 218: e2e_passed evaluation.
    """
    # TDD: Arrange
    from agentos.workflows.testing.nodes.finalize import finalize

    caplog.set_level(logging.INFO)

    # Create audit dir
    audit_dir = temp_repo / "audit"
    audit_dir.mkdir(parents=True, exist_ok=True)

    state: TestingWorkflowState = {
        "issue_number": 141,
        "lld_path": "",
        "repo_root": str(temp_repo),
        "workflow_success": False,  # Keep False to avoid archival complexity
        "test_files": ["tests/test_foo.py"],
        "implementation_files": ["src/foo.py"],
        "coverage_achieved": 95.0,
        "coverage_target": 90,
        "iteration_count": 2,
        "green_phase_output": "2 passed in 0.5s",
        "skip_e2e": False,  # Enable E2E evaluation
        "e2e_output": "All tests passed successfully",  # E2E output
        "audit_dir": str(audit_dir),
    }  # type: ignore

    # TDD: Act
    result = finalize(state)

    # TDD: Assert
    assert result["test_report_path"] != ""


def test_150_finalize_workflow_success_with_archival(temp_repo, test_client, caplog):
    """
    Test finalize with workflow_success=True triggers archival.
    Coverage for lines 287-301: success archival branch.
    """
    # TDD: Arrange
    from agentos.workflows.testing.nodes.finalize import finalize

    caplog.set_level(logging.INFO)

    # Create LLD in active/
    lld_path = temp_repo / "docs" / "lld" / "active" / "LLD-141.md"
    lld_path.write_text("# Test LLD")

    # Create audit dir
    audit_dir = temp_repo / "audit"
    audit_dir.mkdir(parents=True, exist_ok=True)

    state: TestingWorkflowState = {
        "issue_number": 141,
        "lld_path": str(lld_path),
        "repo_root": str(temp_repo),
        "workflow_success": True,  # Success triggers archival
        "test_files": ["tests/test_foo.py"],
        "implementation_files": ["src/foo.py"],
        "coverage_achieved": 95.0,
        "coverage_target": 90,
        "iteration_count": 2,
        "green_phase_output": "2 passed in 0.5s",
        "skip_e2e": True,
        "audit_dir": str(audit_dir),
    }  # type: ignore

    # TDD: Act
    result = finalize(state)

    # TDD: Assert
    assert len(result["archived_files"]) >= 1  # LLD should be archived
    assert not lld_path.exists()  # LLD moved from active/
    done_lld = temp_repo / "docs" / "lld" / "done" / "LLD-141.md"
    assert done_lld.exists()
    assert "Archived" in caplog.text  # Log message from archive_file_to_done