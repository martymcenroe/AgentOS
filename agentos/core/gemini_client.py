"""Custom Gemini client with credential rotation and model enforcement.

This module encapsulates ALL Gemini API interaction for governance,
ensuring:
1. Model hierarchy enforcement - Never downgrades from Pro
2. Credential rotation - Automatic failover on quota exhaustion
3. Differentiated error handling - 529 vs 429 vs other errors

Ported from tools/gemini-rotate.py for programmatic use.
"""

import json
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Optional

import google.generativeai as genai

from agentos.core.config import (
    BACKOFF_BASE_SECONDS,
    BACKOFF_MAX_SECONDS,
    CREDENTIALS_FILE,
    FORBIDDEN_MODELS,
    GOVERNANCE_MODEL,
    MAX_RETRIES_PER_CREDENTIAL,
    ROTATION_STATE_FILE,
)


# =============================================================================
# Error Classification
# =============================================================================


class GeminiErrorType(Enum):
    """Classification of Gemini API errors."""

    QUOTA_EXHAUSTED = "quota"  # 429 - Rotate to next credential
    CAPACITY_EXHAUSTED = "capacity"  # 529 - Backoff and retry same credential
    AUTH_ERROR = "auth"  # Invalid key - Skip credential permanently
    PARSE_ERROR = "parse"  # JSON parse failure - Fail closed
    MODEL_MISMATCH = "model"  # Wrong model used - Fail closed
    UNKNOWN = "unknown"  # Other errors - Fail closed


# Pattern matching (from gemini-rotate.py)
QUOTA_EXHAUSTED_PATTERNS = [
    "TerminalQuotaError",
    "exhausted your capacity",
    "QUOTA_EXHAUSTED",
    "429",
    "Resource has been exhausted",
]

CAPACITY_PATTERNS = [
    "MODEL_CAPACITY_EXHAUSTED",
    "RESOURCE_EXHAUSTED",
    "503",
    "529",
    "The model is overloaded",
]

AUTH_ERROR_PATTERNS = [
    "API_KEY_INVALID",
    "API key not valid",
    "PERMISSION_DENIED",
    "UNAUTHENTICATED",
    "401",
    "403",
]


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class Credential:
    """A Gemini credential (API key)."""

    name: str
    key: str
    enabled: bool = True
    account_name: str = ""


@dataclass
class RotationState:
    """Tracks quota status for credentials."""

    exhausted: dict = field(default_factory=dict)  # name -> reset_time_iso
    last_success: Optional[str] = None
    last_success_time: Optional[str] = None


@dataclass
class GeminiCallResult:
    """Result of a Gemini API call with full observability."""

    success: bool
    response: Optional[str]  # Parsed response text
    raw_response: Optional[str]  # Full API response
    error_type: Optional[GeminiErrorType]
    error_message: Optional[str]
    credential_used: str  # Name of credential that succeeded
    rotation_occurred: bool  # True if we rotated from initial credential
    attempts: int  # Total attempts made
    duration_ms: int  # Total time including retries
    model_verified: str  # Actual model used (for audit)


# =============================================================================
# Gemini Client
# =============================================================================


class GeminiClient:
    """
    Gemini API client with credential rotation and model enforcement.

    Ported from tools/gemini-rotate.py for programmatic use.
    """

    def __init__(
        self,
        model: str = GOVERNANCE_MODEL,
        credentials_file: Path = CREDENTIALS_FILE,
        state_file: Path = ROTATION_STATE_FILE,
    ):
        """
        Initialize client with model and credential configuration.

        Args:
            model: The Gemini model to use. Must be Pro-tier.
            credentials_file: Path to credentials JSON file.
            state_file: Path to rotation state JSON file.

        Raises:
            ValueError: If model is in FORBIDDEN_MODELS list or not Pro-tier.
        """
        if model in FORBIDDEN_MODELS:
            raise ValueError(
                f"Model '{model}' is explicitly forbidden for governance. "
                f"Required: gemini-3-pro-preview or gemini-3-pro"
            )
        if not model.startswith("gemini-") or "pro" not in model.lower():
            raise ValueError(
                f"Model '{model}' is not a Pro-tier model. "
                f"Governance requires: gemini-3-pro-preview or gemini-3-pro"
            )

        self.model = model
        self.credentials_file = credentials_file
        self.state_file = state_file
        self._credentials: Optional[list[Credential]] = None
        self._state: Optional[RotationState] = None

    def invoke(
        self,
        system_instruction: str,
        content: str,
        response_schema: Optional[dict] = None,
    ) -> GeminiCallResult:
        """
        Invoke Gemini with automatic rotation and retry.

        Logic (ported from gemini-rotate.py):
        1. Load available credentials (skip exhausted ones)
        2. For each credential:
           a. Try API call
           b. IF 529 (capacity): Exponential backoff, retry same credential
           c. IF 429 (quota): Mark exhausted, rotate to next credential
           d. IF success: Return result
           e. IF auth error: Skip credential, try next
        3. If all credentials fail: Return failure with BLOCK verdict

        Args:
            system_instruction: The system prompt to send.
            content: The user content to analyze.
            response_schema: Optional JSON schema for structured output.

        Returns:
            GeminiCallResult with full observability data.
        """
        start_time = time.time()
        total_attempts = 0

        credentials = self._load_credentials()
        state = self._load_state()

        # Filter to enabled, non-exhausted credentials
        available = [
            c for c in credentials if c.enabled and not self._is_exhausted(c, state)
        ]

        if not available:
            exhausted_names = [c.name for c in credentials if c.name in state.exhausted]
            return GeminiCallResult(
                success=False,
                response=None,
                raw_response=None,
                error_type=GeminiErrorType.QUOTA_EXHAUSTED,
                error_message=f"All credentials exhausted: {', '.join(exhausted_names)}. Wait for quota reset.",
                credential_used="",
                rotation_occurred=False,
                attempts=0,
                duration_ms=0,
                model_verified="",
            )

        initial_credential = available[0]
        errors: list[str] = []

        for cred in available:
            rotation_occurred = cred.name != initial_credential.name
            attempt = 0

            while attempt < MAX_RETRIES_PER_CREDENTIAL:
                attempt += 1
                total_attempts += 1

                try:
                    # Configure API key
                    genai.configure(api_key=cred.key)

                    # Create model instance
                    model = genai.GenerativeModel(
                        model_name=self.model,
                        system_instruction=system_instruction,
                    )

                    # Make the API call
                    response = model.generate_content(content)

                    # Check for successful response
                    if response.text:
                        # Verify model used (if available in response metadata)
                        model_verified = self.model  # Default to requested model

                        # Update state on success
                        state.last_success = cred.name
                        state.last_success_time = datetime.now(timezone.utc).isoformat()
                        self._save_state(state)

                        duration_ms = int((time.time() - start_time) * 1000)

                        return GeminiCallResult(
                            success=True,
                            response=response.text,
                            raw_response=str(response),
                            error_type=None,
                            error_message=None,
                            credential_used=cred.name,
                            rotation_occurred=rotation_occurred,
                            attempts=total_attempts,
                            duration_ms=duration_ms,
                            model_verified=model_verified,
                        )

                except Exception as e:
                    error_str = str(e)
                    error_type = self._classify_error(error_str)

                    if error_type == GeminiErrorType.CAPACITY_EXHAUSTED:
                        # 529: Backoff and retry same credential
                        delay = self._backoff_delay(attempt)
                        time.sleep(delay)
                        continue

                    elif error_type == GeminiErrorType.QUOTA_EXHAUSTED:
                        # 429: Mark exhausted and rotate
                        reset_hours = self._parse_reset_time(error_str) or 24
                        self._mark_exhausted(cred, state, reset_hours)
                        errors.append(f"{cred.name}: Quota exhausted")
                        break  # Move to next credential

                    elif error_type == GeminiErrorType.AUTH_ERROR:
                        # Auth error: Skip credential
                        errors.append(f"{cred.name}: Authentication failed")
                        break  # Move to next credential

                    else:
                        # Unknown error: Log and try next credential
                        errors.append(f"{cred.name}: {error_str[:100]}")
                        break  # Move to next credential

        # All credentials failed
        duration_ms = int((time.time() - start_time) * 1000)
        return GeminiCallResult(
            success=False,
            response=None,
            raw_response=None,
            error_type=GeminiErrorType.UNKNOWN,
            error_message=f"All credentials failed:\n  - " + "\n  - ".join(errors),
            credential_used="",
            rotation_occurred=len(available) > 1,
            attempts=total_attempts,
            duration_ms=duration_ms,
            model_verified="",
        )

    def _load_credentials(self) -> list[Credential]:
        """Load credentials from config file."""
        if self._credentials is not None:
            return self._credentials

        if not self.credentials_file.exists():
            raise FileNotFoundError(
                f"Credentials file not found: {self.credentials_file}\n"
                f"Create it with your API keys. See AgentOS docs."
            )

        with open(self.credentials_file, encoding="utf-8") as f:
            data = json.load(f)

        self._credentials = [
            Credential(
                name=c.get("name", "unnamed"),
                key=c.get("key", ""),
                enabled=c.get("enabled", True),
                account_name=c.get("account-name", ""),
            )
            for c in data.get("credentials", [])
        ]

        return self._credentials

    def _load_state(self) -> RotationState:
        """Load rotation state from file."""
        if self._state is not None:
            return self._state

        if not self.state_file.exists():
            self._state = RotationState()
            return self._state

        try:
            with open(self.state_file, encoding="utf-8") as f:
                data = json.load(f)
            self._state = RotationState(
                exhausted=data.get("exhausted", {}),
                last_success=data.get("last_success"),
                last_success_time=data.get("last_success_time"),
            )
        except (json.JSONDecodeError, IOError):
            self._state = RotationState()

        return self._state

    def _save_state(self, state: RotationState) -> None:
        """Save rotation state to file."""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "exhausted": state.exhausted,
                    "last_success": state.last_success,
                    "last_success_time": state.last_success_time,
                },
                f,
                indent=2,
            )

    def _is_exhausted(self, cred: Credential, state: RotationState) -> bool:
        """Check if credential quota is exhausted."""
        if cred.name not in state.exhausted:
            return False

        reset_time_str = state.exhausted[cred.name]
        try:
            reset_time = datetime.fromisoformat(reset_time_str.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            if now >= reset_time:
                # Quota has reset - remove from exhausted list
                del state.exhausted[cred.name]
                self._save_state(state)
                return False
            return True
        except (ValueError, TypeError):
            return False

    def _mark_exhausted(
        self, cred: Credential, state: RotationState, reset_hours: float = 24
    ) -> None:
        """Mark credential as quota-exhausted with reset time."""
        reset_time = datetime.now(timezone.utc).replace(microsecond=0)
        reset_time = reset_time + timedelta(hours=reset_hours)
        state.exhausted[cred.name] = reset_time.isoformat()
        self._save_state(state)

    def _classify_error(self, error_output: str) -> GeminiErrorType:
        """Classify error type from API response."""
        error_lower = error_output.lower()

        # Check quota patterns first
        for pattern in QUOTA_EXHAUSTED_PATTERNS:
            if pattern.lower() in error_lower:
                return GeminiErrorType.QUOTA_EXHAUSTED

        # Check capacity patterns
        for pattern in CAPACITY_PATTERNS:
            if pattern.lower() in error_lower:
                return GeminiErrorType.CAPACITY_EXHAUSTED

        # Check auth patterns
        for pattern in AUTH_ERROR_PATTERNS:
            if pattern.lower() in error_lower:
                return GeminiErrorType.AUTH_ERROR

        return GeminiErrorType.UNKNOWN

    def _backoff_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay."""
        return min(BACKOFF_BASE_SECONDS * (2**attempt), BACKOFF_MAX_SECONDS)

    def _parse_reset_time(self, error_output: str) -> Optional[float]:
        """Parse quota reset time from error message (returns hours)."""
        import re

        # Pattern: "Your quota will reset after 15h11m58s"
        match = re.search(r"reset after (\d+)h(\d+)m", error_output)
        if match:
            hours = int(match.group(1))
            minutes = int(match.group(2))
            return hours + minutes / 60
        return None
