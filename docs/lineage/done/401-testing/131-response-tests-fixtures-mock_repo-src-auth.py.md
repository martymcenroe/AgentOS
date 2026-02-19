```python
"""Authentication module for mock-project.

Issue #401: Mock auth module for testing related-code finding.

This module provides authentication and authorization functionality
including token validation, user authentication, and permission checks.
It follows the same patterns as main.py: TypedDict for state, functions
returning dict updates.
"""

from typing import TypedDict


class AuthState(TypedDict):
    """Authentication state for a user session."""

    user_id: str
    token: str
    authenticated: bool
    roles: list[str]
    permissions: list[str]


class AuthConfig(TypedDict):
    """Configuration for the authentication system."""

    secret_key: str
    token_expiry: int
    max_attempts: int
    require_mfa: bool


def create_default_auth_config() -> dict:
    """Create a default authentication configuration.

    Returns:
        Dict with default auth configuration values.
    """
    return {
        "secret_key": "default-secret-key",
        "token_expiry": 3600,
        "max_attempts": 5,
        "require_mfa": False,
    }


def authenticate_user(username: str, password: str) -> dict:
    """Authenticate a user with username and password.

    This is a mock implementation for testing purposes.

    Args:
        username: The user's username.
        password: The user's password.

    Returns:
        Dict with authentication result including token and status.
    """
    if not username or not password:
        return {
            "authenticated": False,
            "error": "Username and password are required",
            "token": "",
        }

    # Mock authentication logic
    if username == "admin" and password == "secret":
        return {
            "authenticated": True,
            "token": "mock-token-admin-12345",
            "user_id": "user-001",
            "roles": ["admin", "user"],
        }

    return {
        "authenticated": False,
        "error": "Invalid credentials",
        "token": "",
    }


def validate_token(token: str) -> dict:
    """Validate an authentication token.

    Args:
        token: The token string to validate.

    Returns:
        Dict with validation result and user info if valid.
    """
    if not token:
        return {
            "valid": False,
            "error": "No token provided",
        }

    if token.startswith("mock-token-"):
        return {
            "valid": True,
            "user_id": "user-001",
            "expires_in": 3600,
        }

    return {
        "valid": False,
        "error": "Invalid or expired token",
    }


def check_permission(state: AuthState, permission: str) -> dict:
    """Check if the authenticated user has a specific permission.

    Follows the node pattern: accepts state, returns dict update.

    Args:
        state: Current authentication state.
        permission: The permission to check.

    Returns:
        Dict with permission check result.
    """
    if not state.get("authenticated"):
        return {
            "allowed": False,
            "reason": "User not authenticated",
        }

    permissions = state.get("permissions", [])
    if permission in permissions:
        return {
            "allowed": True,
            "permission": permission,
        }

    return {
        "allowed": False,
        "reason": f"Missing permission: {permission}",
    }


def revoke_token(token: str) -> dict:
    """Revoke an authentication token.

    Args:
        token: The token to revoke.

    Returns:
        Dict with revocation status.
    """
    if not token:
        return {
            "revoked": False,
            "error": "No token provided",
        }

    return {
        "revoked": True,
        "token": token,
    }


def get_user_roles(user_id: str) -> dict:
    """Get roles assigned to a user.

    Args:
        user_id: The user's identifier.

    Returns:
        Dict with user roles and metadata.
    """
    if not user_id:
        return {
            "roles": [],
            "error": "No user ID provided",
        }

    # Mock role lookup
    return {
        "user_id": user_id,
        "roles": ["user"],
        "role_count": 1,
    }
```
