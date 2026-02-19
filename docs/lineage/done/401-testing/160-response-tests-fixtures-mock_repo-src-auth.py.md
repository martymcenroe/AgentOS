

```python
"""Mock authentication module for testing related-code finding.

Issue #401: Mock auth module for testing codebase context analysis.

This module demonstrates authentication patterns including user validation,
token generation, and session management. It is used by tests to verify
that the codebase analysis node can find related files when an issue
mentions "authentication", "auth", or related keywords.
"""

from typing import Any, TypedDict


class AuthToken(TypedDict):
    """Authentication token structure."""

    user_id: str
    token: str
    expires_at: int


class UserCredentials(TypedDict):
    """User login credentials."""

    username: str
    password_hash: str


def authenticate_user(credentials: UserCredentials) -> AuthToken | None:
    """Authenticate a user with the provided credentials.

    Args:
        credentials: User credentials containing username and password hash.

    Returns:
        AuthToken if authentication succeeds, None otherwise.
    """
    username = credentials.get("username", "")
    if not username:
        return None
    return AuthToken(
        user_id=username,
        token="mock-token-12345",
        expires_at=9999999999,
    )


def validate_token(token: str) -> bool:
    """Validate an authentication token.

    Args:
        token: The token string to validate.

    Returns:
        True if the token is valid, False otherwise.
    """
    return bool(token and token.startswith("mock-token-"))


def refresh_token(old_token: AuthToken) -> AuthToken:
    """Refresh an expired authentication token.

    Args:
        old_token: The expired token to refresh.

    Returns:
        A new AuthToken with extended expiration.
    """
    return AuthToken(
        user_id=old_token["user_id"],
        token="mock-token-refreshed",
        expires_at=old_token["expires_at"] + 3600,
    )


def get_user_permissions(user_id: str) -> list[str]:
    """Get permissions for a user.

    Args:
        user_id: The user identifier.

    Returns:
        List of permission strings.
    """
    return ["read", "write"]


def create_session(state: dict) -> dict:
    """Create a new user session (node pattern).

    Args:
        state: Current state dict with user credentials.

    Returns:
        Dict with session information.
    """
    credentials = state.get("credentials", {})
    token = authenticate_user(credentials)
    if token is None:
        return {"session": None, "authenticated": False}
    return {
        "session": token,
        "authenticated": True,
        "permissions": get_user_permissions(token["user_id"]),
    }
```
