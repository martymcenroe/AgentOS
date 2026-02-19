```python
"""Main application entry point for the mock repository.

This module demonstrates typical patterns used in a LangGraph-based
application, including TypedDict state definitions, node functions
that accept and return dicts, and absolute imports.
"""

from __future__ import annotations

import logging
from typing import Any, TypedDict

from src.auth import authenticate_user, create_session

logger = logging.getLogger(__name__)


class AppState(TypedDict):
    """Application state passed between workflow nodes."""

    user_id: str
    session_token: str
    is_authenticated: bool
    messages: list[str]
    metadata: dict[str, Any]


class AppConfig(TypedDict):
    """Configuration for the application."""

    debug: bool
    log_level: str
    max_retries: int


def initialize_app(state: dict) -> dict:
    """Initialize the application state with defaults.

    This is a LangGraph-style node function that accepts a state dict
    and returns a partial state update dict.

    Args:
        state: Current application state.

    Returns:
        Dict with initialized default values.
    """
    logger.info("Initializing application")
    return {
        "user_id": state.get("user_id", ""),
        "session_token": "",
        "is_authenticated": False,
        "messages": [],
        "metadata": {"version": "0.1.0"},
    }


def process_login(state: dict) -> dict:
    """Process a user login request.

    Args:
        state: Current application state with user_id.

    Returns:
        Dict with authentication results.
    """
    user_id = state.get("user_id", "")
    if not user_id:
        logger.warning("No user_id provided for login")
        return {"is_authenticated": False, "messages": ["No user ID provided"]}

    auth_result = authenticate_user(user_id)
    if auth_result:
        session = create_session(user_id)
        return {
            "is_authenticated": True,
            "session_token": session,
            "messages": [f"User {user_id} logged in successfully"],
        }

    return {"is_authenticated": False, "messages": ["Authentication failed"]}


def handle_request(state: dict) -> dict:
    """Handle an incoming request after authentication.

    Args:
        state: Current application state.

    Returns:
        Dict with request processing results.
    """
    if not state.get("is_authenticated"):
        return {"messages": state.get("messages", []) + ["Unauthorized request"]}

    return {
        "messages": state.get("messages", []) + ["Request processed successfully"],
        "metadata": {**state.get("metadata", {}), "last_action": "handle_request"},
    }


def build_response(state: dict) -> dict:
    """Build the final response from application state.

    Args:
        state: Current application state.

    Returns:
        Dict with formatted response data.
    """
    return {
        "metadata": {
            **state.get("metadata", {}),
            "response_ready": True,
            "message_count": len(state.get("messages", [])),
        },
    }


def main() -> None:
    """Run the application."""
    logging.basicConfig(level=logging.INFO)
    state: dict[str, Any] = {"user_id": "test_user"}

    state.update(initialize_app(state))
    state.update(process_login(state))
    state.update(handle_request(state))
    state.update(build_response(state))

    for message in state.get("messages", []):
        logger.info("Message: %s", message)


if __name__ == "__main__":
    main()
```
