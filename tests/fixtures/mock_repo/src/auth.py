"""Authentication module for the mock project.

This module provides user authentication and authorization
functionality including token management and session handling.
"""

from __future__ import annotations

import hashlib
import logging
from typing import TypedDict

logger = logging.getLogger(__name__)


class UserCredentials(TypedDict):
    """User authentication credentials."""

    username: str
    password_hash: str
    role: str


class AuthToken(TypedDict):
    """Authentication token issued after successful login."""

    token: str
    user: str
    expires_in: int


class AuthenticationError(Exception):
    """Raised when authentication fails."""


def hash_password(password: str) -> str:
    """Hash a password using SHA-256.

    Args:
        password: The plaintext password to hash.

    Returns:
        Hex digest of the hashed password.
    """
    return hashlib.sha256(password.encode()).hexdigest()


def authenticate_user(
    username: str, password: str, user_store: dict[str, UserCredentials]
) -> AuthToken:
    """Authenticate a user against the user store.

    Args:
        username: The username to authenticate.
        password: The plaintext password to verify.
        user_store: Dictionary mapping usernames to credentials.

    Returns:
        AuthToken on successful authentication.

    Raises:
        AuthenticationError: If credentials are invalid.
    """
    if username not in user_store:
        logger.warning("Authentication failed: unknown user %s", username)
        raise AuthenticationError(f"Unknown user: {username}")

    credentials = user_store[username]
    if credentials["password_hash"] != hash_password(password):
        logger.warning("Authentication failed: bad password for %s", username)
        raise AuthenticationError("Invalid password")

    logger.info("User %s authenticated successfully", username)
    return AuthToken(
        token=hashlib.sha256(f"{username}:session".encode()).hexdigest(),
        user=username,
        expires_in=3600,
    )


def verify_token(token: str, valid_tokens: list[str]) -> bool:
    """Verify that an authentication token is valid.

    Args:
        token: The token string to verify.
        valid_tokens: List of currently valid token strings.

    Returns:
        True if the token is valid, False otherwise.
    """
    return token in valid_tokens


def authorize_action(user: UserCredentials, action: str) -> dict:
    """Check if a user is authorized to perform an action.

    Args:
        user: The user's credentials including role.
        action: The action to authorize.

    Returns:
        Dict with 'allowed' bool and 'reason' string.
    """
    admin_actions = {"delete_user", "modify_config", "reset_system"}

    if action in admin_actions and user["role"] != "admin":
        logger.info("User %s denied action %s", user["username"], action)
        return {"allowed": False, "reason": f"Action '{action}' requires admin role"}

    return {"allowed": True, "reason": "authorized"}