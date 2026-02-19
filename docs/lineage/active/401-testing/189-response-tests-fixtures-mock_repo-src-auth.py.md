

```python
"""Mock authentication module for testing related-code finding.

Issue #401: Codebase Context Analysis for Requirements Workflow.

This module provides authentication utilities for the mock project.
It is used to test that the codebase analysis node can find files
related to authentication-themed issues.
"""

from __future__ import annotations

from typing import TypedDict


class AuthCredentials(TypedDict):
    """User authentication credentials."""

    username: str
    password: str


class AuthResult(TypedDict):
    """Result of an authentication attempt."""

    authenticated: bool
    user_id: str
    token: str
    error: str


class UserSession(TypedDict):
    """Active user session data."""

    user_id: str
    token: str
    expires_at: int


def authenticate_user(credentials: AuthCredentials) -> AuthResult:
    """Authenticate a user with the given credentials.

    Args:
        credentials: Dictionary with username and password.

    Returns:
        AuthResult with authentication status and token.
    """
    username = credentials.get("username", "")
    password = credentials.get("password", "")

    if not username or not password:
        return AuthResult(
            authenticated=False,
            user_id="",
            token="",
            error="Missing credentials",
        )

    # Mock authentication logic
    if username == "admin" and password == "secret":
        return AuthResult(
            authenticated=True,
            user_id="user-001",
            token="mock-token-abc123",
            error="",
        )

    return AuthResult(
        authenticated=False,
        user_id="",
        token="",
        error="Invalid credentials",
    )


def validate_token(token: str) -> bool:
    """Validate an authentication token.

    Args:
        token: The token string to validate.

    Returns:
        True if the token is valid, False otherwise.
    """
    if not token:
        return False
    return token.startswith("mock-token-")


def create_session(auth_result: AuthResult) -> UserSession:
    """Create a user session from a successful authentication.

    Args:
        auth_result: Successful authentication result.

    Returns:
        UserSession with session details.
    """
    if not auth_result.get("authenticated"):
        return UserSession(
            user_id="",
            token="",
            expires_at=0,
        )

    return UserSession(
        user_id=auth_result["user_id"],
        token=auth_result["token"],
        expires_at=3600,
    )


def revoke_session(session: UserSession) -> dict:
    """Revoke an active user session.

    Args:
        session: The session to revoke.

    Returns:
        Dict with revocation status.
    """
    if not session.get("token"):
        return {"revoked": False, "error": "No active session"}

    return {"revoked": True, "error": ""}
```
