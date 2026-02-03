# Implementation Request

## Context

You are implementing code for Issue #141 using TDD.
This is iteration 9 of the implementation.

## Requirements

The tests have been scaffolded and need implementation code to pass.

### LLD Summary

# 141 - Fix: Implementation Workflow Should Archive LLD and Reports to done/ on Completion

<!-- Template Metadata
Last Updated: 2025-01-10
Updated By: LLD Workflow
Update Reason: Initial draft for Issue #141
-->

## 1. Context & Goal
* **Issue:** #141
* **Objective:** Automatically archive LLD and report files from `active/` to `done/` directories when the implementation workflow completes successfully.
* **Status:** Draft
* **Related Issues:** #139 (Rename workflows/testing/ to workflows/implementation/), #140 (Inhume deprecated workflows)

### Open Questions

- [x] Should archival happen on any completion or only on success? → Only on success (failed workflows may need rework)
- [x] What happens if `done/` directory doesn't exist? → Create it automatically
- [x] Should we handle the case where LLD doesn't exist (manual implementations)? → Yes, gracefully skip with log message

## 2. Proposed Changes

*This section is the **source of truth** for implementation. Describe exactly what will be built.*

### 2.1 Files Changed

| File | Change Type | Description |
|------|-------------|-------------|
| `agentos/workflows/testing/nodes/finalize.py` | Modify | Add archival logic for LLD and reports |
| `tests/workflows/testing/nodes/test_finalize.py` | Modify | Add tests for archival functionality |

### 2.2 Dependencies

*No new dependencies required.*

```toml
# pyproject.toml additions (if any)
# None
```

### 2.3 Data Structures

```python
# No new data structures - uses existing TestingWorkflowState
# Relevant existing fields:
class TestingWorkflowState(TypedDict):
    lld_path: str  # Path to the active LLD file
    report_paths: list[str]  # Paths to generated reports in active/
    issue_number: int  # For logging purposes
```

### 2.4 Function Signatures

```python
# New helper function in finalize.py
def archive_file_to_done(active_path: Path) -> Path | None:
    """
    Move a file from active/ to done/ directory.
    
    Returns the new path if successful, No...

### Test Scenarios

- **test_010**: Happy path - LLD archived | integration | State with valid LLD path in active/ | LLD moved to done/, path returned | File exists in done/, not in active/, log contains success message
  - Requirement: 
  - Type: integration

- **test_020**: Happy path - Reports archived | integration | State with report paths in active/ | Reports moved to done/ | Files exist in done/, not in active/, log contains success message
  - Requirement: 
  - Type: integration

- **test_030**: LLD not found | integration | State with non-existent LLD path | Warning logged, None returned | No exception, log contains warning
  - Requirement: 
  - Type: integration

- **test_040**: LLD not in active/ | integration | State with LLD in arbitrary path | Skip archival, None returned | File unchanged, log indicates skip
  - Requirement: 
  - Type: integration

- **test_050**: done/ doesn't exist | integration | Valid LLD, no done/ directory | done/ created, LLD moved | Directory created, file moved
  - Requirement: 
  - Type: integration

- **test_060**: Destination file exists | integration | LLD exists in both active/ and done/ | Append timestamp to new name | No overwrite, both files preserved
  - Requirement: 
  - Type: integration

- **test_070**: Empty state | unit | State with no paths | Graceful no-op | No exception, empty archival list
  - Requirement: 
  - Type: unit

- **test_080**: Mixed success | integration | Some files exist, some don't | Archive existing, log missing | Partial archival succeeds
  - Requirement: 
  - Type: integration

- **test_090**: Workflow failed - no archival | integration | State with workflow_success=False, valid LLD path | No files moved, skip logged | Files remain in active/, log indicates skip
  - Requirement: 
  - Type: integration

### Test File: C:\Users\mcwiz\Projects\AgentOS-167\tests\test_issue_141.py

```python
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
```

### Source Files to Modify

These are the existing files you need to modify:

#### agentos/workflows/testing/nodes/finalize.py (Modify)

Add archival logic for LLD and reports

```python
"""N7: Finalize node for TDD Testing Workflow.

Generates test report and archives the audit trail:
- Creates docs/reports/active/{issue}-test-report.md
- Saves metadata to audit trail
- Logs workflow completion
- Archives LLD and reports to done/ directories on success
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from agentos.workflows.testing.audit import (
    TestReportMetadata,
    generate_test_report,
    get_repo_root,
    log_workflow_execution,
    next_file_number,
    parse_pytest_output,
    save_audit_file,
    save_test_report_metadata,
)
from agentos.workflows.testing.state import TestingWorkflowState

logger = logging.getLogger(__name__)


def archive_file_to_done(active_path: Path) -> Path | None:
    """
    Move a file from active/ to done/ directory.
    
    Args:
        active_path: Path to file in active/ directory.
    
    Returns:
        The new path if successful, None if file doesn't exist or isn't in active/.
    
    Implementation for Issue #141.
    """
    # Check if file exists
    if not active_path.exists():
        logger.warning(f"Archive skipped: File not found: {active_path}")
        return None
    
    # Check if "active" is in the path parts (not just filename)
    if "active" not in active_path.parts:
        logger.info(f"Archive skipped: File not in active/ directory: {active_path}")
        return None
    
    # Calculate done/ path by replacing "active" with "done" in path parts
    parts = list(active_path.parts)
    active_idx = parts.index("active")
    parts[active_idx] = "done"
    done_path = Path(*parts)
    
    # Create done/ directory if needed
    done_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Handle destination file already exists - append timestamp
    if done_path.exists():
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        stem = done_path.stem
        suffix = done_path.suffix
        done_path = done_path.parent / f"{stem}-{timestamp}{suffix}"
        logger.info(f"Destination exists, using timestamped name: {done_path.name}")
    
    # Move file
    try:
        active_path.rename(done_path)
        logger.info(f"Archived: {active_path.name} -> {done_path}")
        return done_path
    except Exception as e:
        logger.error(f"Archive failed for {active_path}: {e}")
        return None


def archive_workflow_artifacts(state: TestingWorkflowState) -> dict[str, list[str]]:
    """
    Archive all workflow artifacts (LLD, reports) to done/ directories.
    
    Args:
        state: Current workflow state.
    
    Returns:
        Dict with 'archived' and 'skipped' file lists.
    
    Implementation for Issue #141.
    """
    archived = []
    skipped = []
    
    # Archive LLD if present
    lld_path_str = state.get("lld_path", "")
    if lld_path_str:
        lld_path = Path(lld_path_str)
        result = archive_file_to_done(lld_path)
        if result:
            archived.append(str(result))
        else:
            skipped.append(lld_path_str)
    
    # Archive test report if present
    test_report_path_str = state.get("test_report_path", "")
    if test_report_path_str:
        test_report_path = Path(test_report_path_str)
        result = archive_file_to_done(test_report_path)
        if result:
            archived.append(str(result))
        else:
            skipped.append(test_report_path_str)
    
    # Archive implementation report if present
    impl_report_path_str = state.get("implementation_report_path", "")
    if impl_report_path_str:
        impl_report_path = Path(impl_report_path_str)
        result = archive_file_to_done(impl_report_path)
        if result:
            archived.append(str(result))
        else:
            skipped.append(impl_report_path_str)
    
    return {
        "archived": archived,
        "skipped": skipped,
    }


def _generate_summary(metadata: TestReportMetadata) -> str:
    """Generate a summary markdown for the audit trail.

    Args:
        metadata: Test report metadata.

    Returns:
        Summary markdown string.
    """
    e2e_status = "Passed" if metadata["e2e_passed"] else (
        "Skipped" if metadata["e2e_passed"] is None else "Failed"
    )

    return f"""# Testing Workflow Summary

## Issue #{metadata["issue_number"]}

**Completed:** {metadata["completed_at"]}

## Results

| Metric | Value |
|--------|-------|
| Total Tests | {metadata["test_count"]} |
| Passed | {metadata["passed_count"]} |
| Failed | {metadata["failed_count"]} |
| Coverage | {metadata["coverage_achieved"]:.1f}% |
| Target | {metadata["coverage_target"]}% |
| E2E Status | {e2e_status} |
| Iterations | {metadata["total_iterations"]} |

## Files

### Test Files
{chr(10).join(f"- {f}" for f in metadata["test_files"])}

### Implementation Files
{chr(10).join(f"- {f}" for f in metadata["implementation_files"])}

## LLD

{metadata["lld_path"]}

---

Generated by AgentOS TDD Testing Workflow
"""


def finalize(state: TestingWorkflowState) -> dict[str, Any]:
    """N7: Generate test report and complete workflow.

    Args:
        state: Current workflow state.

    Returns:
        State updates with report paths and archival results.
    """
    print("\n[N7] Finalizing workflow...")

    issue_number = state.get("issue_number", 0)
    repo_root_str = state.get("repo_root", "")
    repo_root = Path(repo_root_str) if repo_root_str else get_repo_root()

    # Check workflow success status early
    workflow_success = state.get("workflow_success", True)

    # Gather metrics
    test_files = state.get("test_files", [])
    implementation_files = state.get("implementation_files", [])
    coverage_achieved = state.get("coverage_achieved", 0.0)
    coverage_target = state.get("coverage_target", 90)
    iteration_count = state.get("iteration_count", 0)
    lld_path = state.get("lld_path", "")

    # Parse test output for counts
    green_output = state.get("green_phase_output", "")
    parsed = parse_pytest_output(green_output)
    test_count = parsed.get("passed", 0) + parsed.get("failed", 0) + parsed.get("errors", 0)
    passed_count = parsed.get("passed", 0)
    failed_count = parsed.get("failed", 0) + parsed.get("errors", 0)

    # E2E status
    e2e_output = state.get("e2e_output", "")
    e2e_passed = "passed" in e2e_output.lower() and "failed" not in e2e_output.lower()
    if state.get("skip_e2e"):
        e2e_passed = None  # Skipped

    print(f"    Issue: #{issue_number}")
    print(f"    Tests: {passed_count}/{test_count} passed")
    print(f"    Coverage: {coverage_achieved:.1f}%")
    print(f"    Iterations: {iteration_count}")

    # Create metadata
    metadata: TestReportMetadata = {
        "issue_number": issue_number,
        "lld_path": lld_path,
        "completed_at": datetime.now().isoformat(),
        "test_files": test_files,
        "implementation_files": implementation_files,
        "coverage_achieved": coverage_achieved,
        "coverage_target": coverage_target,
        "total_iterations": iteration_count,
        "test_count": test_count,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "e2e_passed": e2e_passed,
    }

    # Generate test report
    report_path = generate_test_report(
        issue_number=issue_number,
        metadata=metadata,
        test_output=green_output,
        repo_root=repo_root,
    )
    print(f"    Test report: {report_path}")

    # Save to audit trail
    audit_dir = Path(state.get("audit_dir", ""))
    if audit_dir.exists():
        file_num = next_file_number(audit_dir)
        save_test_report_metadata(audit_dir, file_num, metadata)

        # Save summary
        file_num = next_file_number(audit_dir)
        summary = _generate_summary(metadata)
        save_audit_file(audit_dir, file_num, "summary.md", summary)

    # Log workflow completion
    log_workflow_execution(
        target_repo=repo_root,
        issue_number=issue_number,
        workflow_type="testing",
        event="complete",
        details={
            "test_count": test_count,
            "passed_count": passed_count,
            "coverage": coverage_achieved,
            "iterations": iteration_count,
            "report_path": str(report_path),
        },
    )

    # Update state with test report path before archival
    state["test_report_path"] = str(report_path)
    
    archived_files: list[str] = []
    skipped_files: list[str] = []
    
    # Archive workflow artifacts if workflow was successful
    # Issue #141: Archive LLD and reports to done/ on completion
    if workflow_success:
        print("\n[N7] Archiving workflow artifacts...")
        archival_results = archive_workflow_artifacts(state)
        
        archived_files = archival_results["archived"]
        skipped_files = archival_results["skipped"]
        
        if archived_files:
            print(f"    Archived: {len(archived_files)} files")
            for path in archived_files:
                print(f"      - {path}")
        
        if skipped_files:
            print(f"    Skipped: {len(skipped_files)} files")
            for path in skipped_files:
                print(f"      - {path}")
    else:
        print("\n[N7] Workflow failed - skipping archival")
        logger.info("Archival skipped: workflow_success=False")

    print(f"\n    Testing workflow COMPLETE for issue #{issue_number}!")
    print(f"    Report: {report_path}")

    return {
        "test_report_path": str(report_path),
        "error_message": "",
        "archived_files": archived_files,
        "skipped_files": skipped_files,
    }
```

### Previous Test Run (FAILED)

The previous implementation attempt failed. Here's the test output:

```
ackages\pydantic\v1\typing.py:77
..\..\AppData\Local\pypoetry\Cache\virtualenvs\unleashed-Zukdy2xA-py3.14\Lib\site-packages\pydantic\v1\typing.py:77
..\..\AppData\Local\pypoetry\Cache\virtualenvs\unleashed-Zukdy2xA-py3.14\Lib\site-packages\pydantic\v1\typing.py:77
..\..\AppData\Local\pypoetry\Cache\virtualenvs\unleashed-Zukdy2xA-py3.14\Lib\site-packages\pydantic\v1\typing.py:77
..\..\AppData\Local\pypoetry\Cache\virtualenvs\unleashed-Zukdy2xA-py3.14\Lib\site-packages\pydantic\v1\typing.py:77
  C:\Users\mcwiz\AppData\Local\pypoetry\Cache\virtualenvs\unleashed-Zukdy2xA-py3.14\Lib\site-packages\pydantic\v1\typing.py:77: DeprecationWarning: ForwardRef._evaluate is a private API and is retained for compatibility, but will be removed in Python 3.16. Use ForwardRef.evaluate() or typing.evaluate_forward_ref() instead.
    return cast(Any, type_)._evaluate(globalns, localns, type_params=(), recursive_guard=set())

agentos\workflows\testing\state.py:36
  C:\Users\mcwiz\Projects\AgentOS-167\agentos\workflows\testing\state.py:36: PytestCollectionWarning: cannot collect test class 'TestingWorkflowState' because it has a __init__ constructor (from: tests/test_issue_141.py)
    class TestingWorkflowState(TypedDict, total=False):

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=============================== tests coverage ================================
_______________ coverage: platform win32, python 3.14.0-final-0 _______________

Name                                          Stmts   Miss  Cover   Missing
---------------------------------------------------------------------------
agentos\workflows\testing\nodes\finalize.py     117     14    88%   102, 122, 283-297
---------------------------------------------------------------------------
TOTAL                                           117     14    88%
FAIL Required test coverage of 95% not reached. Total coverage: 88.03%
======================= 11 passed, 9 warnings in 0.35s ========================


```

Please fix the issues and provide updated implementation.

## Instructions

1. Generate implementation code that makes all tests pass
2. Follow the patterns established in the codebase
3. Ensure proper error handling
4. Add type hints where appropriate
5. Keep the implementation minimal - only what's needed to pass tests

## Output Format (CRITICAL - MUST FOLLOW EXACTLY)

For EACH file you need to create or modify, provide a code block with this EXACT format:

```python
# File: path/to/implementation.py

def function_name():
    ...
```

**Rules:**
- The `# File: path/to/file` comment MUST be the FIRST line inside the code block
- Use the language-appropriate code fence (```python, ```gitignore, ```yaml, etc.)
- Path must be relative to repository root (e.g., `src/module/file.py`)
- Do NOT include "(append)" or other annotations in the path
- Provide complete file contents, not patches or diffs

**Example for .gitignore:**
```gitignore
# File: .gitignore

# Existing patterns...
*.pyc
__pycache__/

# New pattern
.agentos/
```

If multiple files are needed, provide each in a separate code block with its own `# File:` header.
