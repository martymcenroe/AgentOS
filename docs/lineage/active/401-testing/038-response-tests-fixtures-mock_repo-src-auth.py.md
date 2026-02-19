

```python
"""Authentication module for the mock repository.

This module provides user authentication and session management
functions. It demonstrates typical patterns found in a Python
project including type hints, docstrings, and logging.
"""

from __future__ import annotations

import hashlib
import logging
import secrets
from typing import Any

logger = logging.getLogger(__name__)

# Simulated user database
_USERS: dict[str, dict[str, Any]] = {
    "test_user": {
        "password_hash": "hashed_password_123",
        "role": "admin",
        "active": True,
    },
    "readonly_user": {
        "password_hash": "hashed_password_456",
        "role": "reader",
        "active": True,
    },
    "disabled_user": {
        "password_hash": "hashed_password_789",
        "role": "admin",
        "active": False,
    },
}

# Active sessions store
_SESSIONS: dict[str, str] = {}


def authenticate_user(user_id: str, password: str | None = None) -> bool:
    """Authenticate a user by their user ID.

    Checks if the user exists and is active in the user database.

    Args:
        user_id: The unique identifier for the user.
        password: Optional password for authentication.

    Returns:
        True if the user is authenticated, False otherwise.
    """
    user = _USERS.get(user_id)
    if user is None:
        logger.warning("Authentication failed: user '%s' not found", user_id)
        return False

    if not user.get("active", False):
        logger.warning("Authentication failed: user '%s' is disabled", user_id)
        return False

    logger.info("User '%s' authenticated successfully", user_id)
    return True


def create_session(user_id: str) -> str:
    """Create a new session token for an authenticated user.

    Generates a secure random token and stores it in the session store.

    Args:
        user_id: The unique identifier for the user.

    Returns:
        A session token string.
    """
    token = secrets.token_hex(32)
    _SESSIONS[token] = user_id
    logger.info("Session created for user '%s'", user_id)
    return token


def validate_session(token: str) -> str | None:
    """Validate a session token and return the associated user ID.

    Args:
        token: The session token to validate.

    Returns:
        The user ID if the session is valid, None otherwise.
    """
    user_id = _SESSIONS.get(token)
    if user_id is None:
        logger.warning("Invalid session token")
        return None

    logger.info("Session validated for user '%s'", user_id)
    return user_id


def revoke_session(token: str) -> bool:
    """Revoke a session token, logging the user out.

    Args:
        token: The session token to revoke.

    Returns:
        True if the session was revoked, False if it didn't exist.
    """
    if token in _SESSIONS:
        user_id = _SESSIONS.pop(token)
        logger.info("Session revoked for user '%s'", user_id)
        return True

    logger.warning("Attempted to revoke non-existent session")
    return False


def get_user_role(user_id: str) -> str | None:
    """Get the role assigned to a user.

    Args:
        user_id: The unique identifier for the user.

    Returns:
        The user's role string, or None if user not found.
    """
    user = _USERS.get(user_id)
    if user is None:
        return None
    return user.get("role")


def hash_password(password: str) -> str:
    """Hash a password using SHA-256.

    Args:
        password: The plaintext password to hash.

    Returns:
        The hexadecimal digest of the hashed password.
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest()
```
