#!/usr/bin/env python3
"""CLI runner for LLD Governance workflow.

Issue #86: LLD Creation & Governance Review Workflow
LLD: docs/LLDs/active/LLD-086-lld-governance-workflow.md

Usage:
    python tools/run_lld_workflow.py --issue 42
    python tools/run_lld_workflow.py --issue 42 --auto
    python tools/run_lld_workflow.py --issue 42 --mock
    python tools/run_lld_workflow.py --issue 42 --context file.py --context another.md
    python tools/run_lld_workflow.py --issue 42 --resume

Options:
    --issue <number>      GitHub issue number (required)
    --context <path>      Additional context files (can specify multiple)
    --auto                Auto mode: skip VS Code, auto-send to Gemini
    --mock                Mock mode: use fixtures instead of real APIs
    --resume              Resume interrupted workflow from checkpoint
    --max-iterations <n>  Maximum review iterations (default: 5)
    --help                Show this help message
"""

import argparse
import os
import sys
import warnings
from pathlib import Path

# Disable LangSmith telemetry to avoid authentication errors
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGCHAIN_API_KEY"] = ""

# Suppress deprecation warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

from langgraph.checkpoint.sqlite import SqliteSaver

from agentos.workflows.lld.graph import build_lld_workflow
from agentos.workflows.lld.state import LLDWorkflowState


def get_checkpoint_db_path() -> Path:
    """Get path to checkpoint database.

    Uses AGENTOS_WORKFLOW_DB environment variable if set,
    otherwise defaults to ~/.agentos/lld_workflow.db.

    Returns:
        Path to SQLite database file.
    """
    env_path = os.environ.get("AGENTOS_WORKFLOW_DB")
    if env_path:
        return Path(env_path)

    # Default location
    agentos_dir = Path.home() / ".agentos"
    agentos_dir.mkdir(parents=True, exist_ok=True)
    return agentos_dir / "lld_workflow.db"


def run_workflow(
    issue_number: int,
    context_files: list[str] | None = None,
    auto_mode: bool = False,
    mock_mode: bool = False,
    resume: bool = False,
    max_iterations: int = 5,
) -> int:
    """Run the LLD governance workflow.

    Args:
        issue_number: GitHub issue number.
        context_files: Optional list of context file paths.
        auto_mode: If True, skip VS Code and auto-send to review.
        mock_mode: If True, use fixtures instead of real APIs.
        resume: If True, resume from checkpoint.
        max_iterations: Maximum review iterations.

    Returns:
        Exit code (0 for success, non-zero for error).
    """
    # Build workflow
    workflow = build_lld_workflow()

    # Thread ID for checkpointing
    thread_id = f"lld-{issue_number}"

    # Get checkpoint database path
    db_path = get_checkpoint_db_path()

    print(f"\n{'=' * 60}")
    print(f"LLD Governance Workflow - Issue #{issue_number}")
    print(f"{'=' * 60}")

    if mock_mode:
        print("Mode: MOCK (using fixtures)")
    elif auto_mode:
        print("Mode: AUTO (unattended)")
    else:
        print("Mode: INTERACTIVE")

    if context_files:
        print(f"Context files: {len(context_files)}")

    print(f"Checkpoint DB: {db_path}")
    print(f"{'=' * 60}\n")

    # Initial state
    initial_state: LLDWorkflowState = {
        "issue_number": issue_number,
        "context_files": context_files or [],
        "auto_mode": auto_mode,
        "mock_mode": mock_mode,
        "iteration_count": 0,
        "draft_count": 0,
        "verdict_count": 0,
    }

    # Run with checkpointer
    with SqliteSaver.from_conn_string(str(db_path)) as memory:
        app = workflow.compile(checkpointer=memory)
        config = {"configurable": {"thread_id": thread_id}}

        if resume:
            # Check if checkpoint exists
            state = app.get_state(config)
            if state.values:
                print(f"Resuming from checkpoint...")
                print(f"  Iteration: {state.values.get('iteration_count', 0)}")
                print(f"  Drafts: {state.values.get('draft_count', 0)}")
                print(f"  Verdicts: {state.values.get('verdict_count', 0)}")
                print()

                # Resume with None to continue from checkpoint
                input_state = None
            else:
                print("No checkpoint found. Starting fresh.")
                input_state = initial_state
        else:
            input_state = initial_state

        # Stream workflow events
        final_state = None
        try:
            for event in app.stream(input_state, config):
                # Event is dict of {node_name: state_updates}
                for node_name, state_update in event.items():
                    final_state = state_update

                    # Check for errors
                    error = state_update.get("error_message", "")
                    if error:
                        if "MANUAL" in error:
                            print(f"\n[EXIT] {error}")
                            return 0  # Manual exit is not an error
                        elif "Max iterations" in error:
                            print(f"\n[EXIT] {error}")
                            return 1
                        else:
                            print(f"\n[ERROR] {error}")
                            return 1

        except KeyboardInterrupt:
            print("\n\n[INTERRUPTED] Workflow interrupted. Use --resume to continue.")
            return 130  # Standard exit code for SIGINT

    # Check final outcome
    if final_state:
        final_lld_path = final_state.get("final_lld_path", "")
        if final_lld_path:
            print(f"\n{'=' * 60}")
            print(f"SUCCESS: LLD approved and saved!")
            print(f"  Path: {final_lld_path}")
            print(f"  Iterations: {final_state.get('iteration_count', 0)}")
            print(f"  Drafts: {final_state.get('draft_count', 0)}")
            print(f"  Verdicts: {final_state.get('verdict_count', 0)}")
            print(f"{'=' * 60}\n")
            return 0

        error = final_state.get("error_message", "")
        if error:
            print(f"\n[ERROR] {error}")
            return 1

    return 0


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="LLD Governance Workflow - Generate and review LLDs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Basic usage - generate LLD for issue
    python tools/run_lld_workflow.py --issue 42

    # Auto mode - unattended execution
    python tools/run_lld_workflow.py --issue 42 --auto

    # Mock mode - test without API calls
    python tools/run_lld_workflow.py --issue 42 --mock

    # With context files
    python tools/run_lld_workflow.py --issue 42 --context src/main.py --context docs/spec.md

    # Resume interrupted workflow
    python tools/run_lld_workflow.py --issue 42 --resume
""",
    )

    parser.add_argument(
        "--issue",
        type=int,
        required=True,
        help="GitHub issue number",
    )
    parser.add_argument(
        "--context",
        action="append",
        default=[],
        help="Additional context files (can specify multiple)",
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Auto mode: skip VS Code, auto-send to Gemini",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Mock mode: use fixtures instead of real APIs",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume interrupted workflow from checkpoint",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=5,
        help="Maximum review iterations (default: 5)",
    )

    args = parser.parse_args()

    return run_workflow(
        issue_number=args.issue,
        context_files=args.context,
        auto_mode=args.auto,
        mock_mode=args.mock,
        resume=args.resume,
        max_iterations=args.max_iterations,
    )


if __name__ == "__main__":
    sys.exit(main())
