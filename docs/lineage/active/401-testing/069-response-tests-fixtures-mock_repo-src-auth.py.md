

```python
"""Mock authentication module for testing related-code finding.

Issue #401: Codebase Context Analysis for Requirements Workflow.

This file serves as a mock auth module in the test fixture repository.
It demonstrates typical authentication patterns that the related-code
finder should match when an issue mentions "authentication", "auth",
"login", or similar keywords.
"""

from __future__ import annotations

import logging
from typing import TypedDict

logger = logging.getLogger(__name__)


class AuthState(TypedDict):
    """Authentication state using TypedDict pattern."""

    user: str
    authenticated: bool
    token: str
    role: str


class AuthenticationError(Exception):
    """Raised when authentication fails."""

    pass


def authenticate_user(state: dict) -> dict:
    """Authenticate a user based on credentials in state.

    This function follows the LangGraph node pattern of accepting
    a state dict and returning a dict update.

    Args:
        state: Current state containing 'user' and 'password' keys.

    Returns:
        Dict with authentication results.
    """
    user = state.get("user", "")
    password = state.get("password", "")

    if not user or not password:
        logger.warning("Missing credentials for authentication")
        return {
            "authenticated": False,
            "token": "",
            "role": "anonymous",
        }

    # Mock authentication logic
    if user == "admin" and password == "secret":
        logger.info("User '%s' authenticated successfully", user)
        return {
            "authenticated": True,
            "token": "mock-jwt-token-12345",
            "role": "admin",
        }

    logger.warning("Authentication failed for user '%s'", user)
    return {
        "authenticated": False,
        "token": "",
        "role": "anonymous",
    }


def check_authorization(state: dict) -> dict:
    """Check if the authenticated user has required permissions.

    Args:
        state: Current state with authentication info.

    Returns:
        Dict with authorization check results.
    """
    authenticated = state.get("authenticated", False)
    role = state.get("role", "anonymous")

    if not authenticated:
        return {"authorized": False, "message": "Not authenticated"}

    if role == "admin":
        return {"authorized": True, "message": "Full access granted"}

    return {"authorized": False, "message": f"Insufficient role: {role}"}


def logout_user(state: dict) -> dict:
    """Log out the current user.

    Args:
        state: Current state with session info.

    Returns:
        Dict clearing authentication state.
    """
    user = state.get("user", "unknown")
    logger.info("User '%s' logged out", user)
    return {
        "authenticated": False,
        "token": "",
        "role": "anonymous",
    }
```
