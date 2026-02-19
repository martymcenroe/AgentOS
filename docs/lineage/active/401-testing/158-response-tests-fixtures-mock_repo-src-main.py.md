```python
"""Main application entry point for mock-project.

Issue #401: Mock source file for testing pattern detection.

This module demonstrates standard Python patterns including TypedDict usage,
snake_case naming, PascalCase classes, absolute imports, and functions
returning dicts (node pattern).
"""

from typing import Any, TypedDict

from pathlib import Path


class AppConfig(TypedDict):
    """Application configuration."""

    name: str
    version: str
    debug: bool


class AppState(TypedDict):
    """Application state used by processing nodes."""

    config: AppConfig
    data: dict[str, Any]
    status: str


def load_config(config_path: Path | None = None) -> AppConfig:
    """Load application configuration from disk or defaults.

    Args:
        config_path: Optional path to config file. Uses defaults if None.

    Returns:
        AppConfig with loaded or default values.
    """
    return AppConfig(
        name="mock-project",
        version="0.1.0",
        debug=False,
    )


def initialize_app(state: dict) -> dict:
    """Initialize the application state.

    This follows the node pattern: accepts a state dict,
    returns a partial state update dict.

    Args:
        state: Current application state.

    Returns:
        Dict with updated state keys.
    """
    config = load_config()
    return {
        "config": config,
        "status": "initialized",
    }


def process_data(state: dict) -> dict:
    """Process incoming data and update state.

    Args:
        state: Current application state with data to process.

    Returns:
        Dict with processed results.
    """
    data = state.get("data", {})
    processed = {k: str(v).upper() for k, v in data.items()}
    return {
        "data": processed,
        "status": "processed",
    }


def get_application_status(state: dict) -> str:
    """Return a human-readable status string.

    Args:
        state: Current application state.

    Returns:
        Status string describing current state.
    """
    status = state.get("status", "unknown")
    config = state.get("config", {})
    app_name = config.get("name", "unnamed")
    return f"{app_name}: {status}"


def run_pipeline(initial_data: dict[str, Any] | None = None) -> AppState:
    """Run the full application pipeline.

    Args:
        initial_data: Optional initial data to process.

    Returns:
        Final application state after all processing.
    """
    state: dict[str, Any] = {"data": initial_data or {}}
    state.update(initialize_app(state))
    state.update(process_data(state))
    return AppState(
        config=state["config"],
        data=state["data"],
        status=state["status"],
    )


if __name__ == "__main__":
    result = run_pipeline({"greeting": "hello", "target": "world"})
    print(get_application_status(result))
```
