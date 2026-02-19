```python
"""Main application entry point for mock-project.

Issue #401: Mock source file for testing pattern detection.

This module provides the core application logic including state management
and request processing. It uses TypedDict for state definitions and follows
the node pattern of functions returning dict updates.
"""

from typing import TypedDict

from pathlib import Path


class AppState(TypedDict):
    """Application state managed throughout the request lifecycle."""

    user_id: str
    request_path: str
    authenticated: bool
    response_body: str
    status_code: int


class AppConfig(TypedDict):
    """Configuration for the application."""

    debug: bool
    host: str
    port: int
    log_level: str


def create_default_config() -> dict:
    """Create a default application configuration.

    Returns:
        Dict with default configuration values.
    """
    return {
        "debug": False,
        "host": "0.0.0.0",
        "port": 8000,
        "log_level": "INFO",
    }


def initialize_app(config: dict) -> dict:
    """Initialize the application with the given configuration.

    Args:
        config: Application configuration dictionary.

    Returns:
        Dict with initialization status and app metadata.
    """
    return {
        "initialized": True,
        "config": config,
        "version": "1.0.0",
    }


def process_request(state: AppState) -> dict:
    """Process an incoming request and update state.

    This follows the node pattern: accepts state, returns dict update.

    Args:
        state: Current application state.

    Returns:
        Dict with updated state fields.
    """
    if not state.get("authenticated"):
        return {
            "status_code": 401,
            "response_body": "Unauthorized",
        }

    path = state.get("request_path", "/")
    if path == "/":
        return {
            "status_code": 200,
            "response_body": "Welcome to mock-project",
        }
    elif path == "/health":
        return {
            "status_code": 200,
            "response_body": "OK",
        }
    else:
        return {
            "status_code": 404,
            "response_body": f"Not found: {path}",
        }


def build_response(state: AppState) -> dict:
    """Build the final HTTP response from state.

    Args:
        state: Application state after processing.

    Returns:
        Dict containing the formatted response.
    """
    return {
        "status": state.get("status_code", 500),
        "body": state.get("response_body", "Internal Server Error"),
        "headers": {"Content-Type": "text/plain"},
    }


def get_app_info() -> dict:
    """Return application metadata.

    Returns:
        Dict with app name, version, and description.
    """
    return {
        "name": "mock-project",
        "version": "1.0.0",
        "description": "A mock project for testing codebase context analysis",
    }


def run_app(config: dict | None = None) -> None:
    """Run the application with optional configuration.

    Args:
        config: Optional configuration override. Uses defaults if None.
    """
    if config is None:
        config = create_default_config()

    app = initialize_app(config)
    if app["initialized"]:
        print(f"App running on {config['host']}:{config['port']}")


if __name__ == "__main__":
    run_app()
```
