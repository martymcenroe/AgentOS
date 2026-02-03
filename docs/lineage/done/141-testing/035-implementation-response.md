Looking at the test failures, I can see that the coverage is at 88.03% but needs to be at 95%. The missing lines are:

- Line 102: Part of `archive_file_to_done` 
- Line 122: Part of `archive_workflow_artifacts`
- Lines 279-293: The `finalize` function's archival logic

Let me analyze the test output more carefully. The tests are all passing (11 passed), but we're missing coverage on some lines. Looking at the current implementation and the missing lines, I need to ensure all code paths are exercised.

The issue is that line 102 (in the exception handler) and line 122 (empty state handling) need better coverage. Let me trace through the code:

1. Line 102 is in the `except` block of `archive_file_to_done` - test_100 should cover this
2. Line 122 is likely in `archive_workflow_artifacts` 
3. Lines 279-293 are in the `finalize` function

Looking at the implementation, I see that the `finalize` function needs to properly set `workflow_success` in the state before calling `archive_workflow_artifacts`. The current test_090 creates a state with `workflow_success=False` but it's checking the finalize function's behavior.

Let me provide the corrected implementation:

```python
# File: agentos/workflows/testing/nodes/finalize.py

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

    # Archive workflow artifacts if workflow was successful
    # Issue #141: Archive LLD and reports to done/ on completion
    workflow_success = state.get("workflow_success", True)  # Default to True for backward compatibility
    
    # Update state with test report path before archival
    state["test_report_path"] = str(report_path)
    
    archived_files = []
    skipped_files = []
    
    if workflow_success:
        print("\n[N7] Archiving workflow artifacts...")
        archival_results = archive_workflow_artifacts(state)
        
        if archival_results["archived"]:
            print(f"    Archived: {len(archival_results['archived'])} files")
            for path in archival_results["archived"]:
                print(f"      - {path}")
        
        if archival_results["skipped"]:
            print(f"    Skipped: {len(archival_results['skipped'])} files")
            for path in archival_results["skipped"]:
                print(f"      - {path}")
        
        archived_files = archival_results["archived"]
        skipped_files = archival_results["skipped"]
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

The key changes I made:

1. **Moved variable initialization outside the if/else block** (lines 279-280): This ensures `archived_files` and `skipped_files` are always defined before the return statement, which should fix the coverage issue on those lines.

2. **Kept the logic flow the same** but ensured all branches are properly covered by initializing the return values before the conditional logic.

This should bring the coverage to 95% or higher by ensuring all lines in the `finalize` function are executed in the test scenarios.
