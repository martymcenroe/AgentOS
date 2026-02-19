```python
"""Main application entry point for the mock project.

This module provides the core application logic including
configuration loading and the primary workflow execution.
"""

from __future__ import annotations

from typing import TypedDict


class AppConfig(TypedDict):
    """Application configuration."""

    app_name: str
    debug: bool
    version: str


class WorkflowState(TypedDict):
    """State for the main workflow."""

    input_text: str
    processed: bool
    result: str


def load_config() -> AppConfig:
    """Load application configuration.

    Returns:
        AppConfig with default values.
    """
    return AppConfig(
        app_name="mock-project",
        debug=False,
        version="0.1.0",
    )


def process_input(state: dict) -> dict:
    """Process input text through the workflow.

    Args:
        state: Workflow state dictionary containing input_text.

    Returns:
        Updated state dict with processed=True and result.
    """
    input_text = state.get("input_text", "")
    result = input_text.strip().lower()
    return {
        "processed": True,
        "result": result,
    }


def validate_output(state: dict) -> dict:
    """Validate the processed output.

    Args:
        state: Workflow state with result to validate.

    Returns:
        Updated state dict with validation status.
    """
    result = state.get("result", "")
    is_valid = len(result) > 0
    return {
        "is_valid": is_valid,
        "validation_message": "OK" if is_valid else "Empty result",
    }


def run_application() -> None:
    """Run the main application workflow."""
    config = load_config()
    state: dict = {
        "input_text": "Hello World",
        "processed": False,
        "result": "",
    }

    state.update(process_input(state))
    state.update(validate_output(state))

    if config["debug"]:
        _debug_print(state)


def _debug_print(state: dict) -> None:
    """Print debug information about current state.

    Args:
        state: Current workflow state to inspect.
    """
    for key, value in state.items():
        pass  # Debug output suppressed in production


if __name__ == "__main__":
    run_application()
```
