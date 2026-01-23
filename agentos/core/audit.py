"""Audit logging infrastructure for AgentOS governance.

This module provides persistent audit logging for governance decisions,
with JSONL format for append-only, line-by-line reading.
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, TypedDict

from agentos.core.config import DEFAULT_AUDIT_LOG_PATH


class GovernanceLogEntry(TypedDict):
    """Single entry in the governance audit log."""

    id: str  # UUID as string
    sequence_id: int  # From state.iteration_count
    timestamp: str  # ISO8601 format
    node: str  # Node name (e.g., "review_lld")
    model: str  # Model requested (e.g., "gemini-3-pro-preview")
    model_verified: str  # Actual model from API response
    issue_id: int  # GitHub issue being reviewed
    verdict: str  # "APPROVED" or "BLOCK"
    critique: str  # Gemini's feedback
    tier_1_issues: list[str]  # Blocking issues found
    raw_response: str  # Full Gemini response
    duration_ms: int  # Call duration including retries
    # Credential observability (per Gemini review feedback)
    credential_used: str  # Name of credential that succeeded
    rotation_occurred: bool  # True if rotation happened during call
    attempts: int  # Total API call attempts


class GeminiReviewResponse(TypedDict):
    """Structured output schema for Gemini LLD reviews."""

    verdict: str  # "APPROVED" or "BLOCK"
    critique: str  # Summary feedback
    tier_1_issues: list[str]  # Blocking issues (empty if approved)


class GovernanceAuditLog:
    """Persistent audit log for governance decisions.

    Uses JSONL format for append-only, line-by-line reading.
    Each line is a complete JSON object representing one governance decision.
    """

    def __init__(self, log_path: Path = DEFAULT_AUDIT_LOG_PATH):
        """Initialize with log file path.

        Args:
            log_path: Path to the JSONL log file. Parent directories
                will be created if they don't exist.
        """
        self.log_path = log_path

    def log(self, entry: GovernanceLogEntry) -> None:
        """Append entry to JSONL file.

        Args:
            entry: The governance log entry to write.
        """
        # Ensure parent directory exists
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

        # Serialize to JSON string
        json_line = json.dumps(entry, ensure_ascii=False)

        # Append with newline
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json_line + "\n")
            f.flush()

    def tail(self, n: int = 10) -> list[GovernanceLogEntry]:
        """Return last N entries from log.

        Args:
            n: Number of entries to return.

        Returns:
            List of the last N entries, oldest first.
        """
        if not self.log_path.exists():
            return []

        entries: list[GovernanceLogEntry] = []

        with open(self.log_path, encoding="utf-8") as f:
            lines = f.readlines()

        # Get last N lines
        for line in lines[-n:]:
            line = line.strip()
            if line:
                try:
                    entry = json.loads(line)
                    entries.append(entry)
                except json.JSONDecodeError:
                    # Skip malformed lines
                    continue

        return entries

    def __iter__(self) -> Iterator[GovernanceLogEntry]:
        """Iterate over all entries.

        Yields:
            Each governance log entry in chronological order.
        """
        if not self.log_path.exists():
            return

        with open(self.log_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        yield json.loads(line)
                    except json.JSONDecodeError:
                        # Skip malformed lines
                        continue

    def count(self) -> int:
        """Return total number of entries.

        Returns:
            Count of log entries.
        """
        if not self.log_path.exists():
            return 0

        count = 0
        with open(self.log_path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    count += 1
        return count


def create_log_entry(
    node: str,
    model: str,
    model_verified: str,
    issue_id: int,
    verdict: str,
    critique: str,
    tier_1_issues: list[str],
    raw_response: str,
    duration_ms: int,
    credential_used: str,
    rotation_occurred: bool,
    attempts: int,
    sequence_id: int = 0,
) -> GovernanceLogEntry:
    """Factory function to create a governance log entry.

    Args:
        node: Node name (e.g., "review_lld").
        model: Model requested.
        model_verified: Actual model used.
        issue_id: GitHub issue number.
        verdict: "APPROVED" or "BLOCK".
        critique: Gemini's feedback.
        tier_1_issues: List of blocking issues.
        raw_response: Full Gemini response.
        duration_ms: Call duration in milliseconds.
        credential_used: Name of credential that succeeded.
        rotation_occurred: Whether rotation happened.
        attempts: Total API call attempts.
        sequence_id: Sequence number from state.

    Returns:
        A complete GovernanceLogEntry.
    """
    return GovernanceLogEntry(
        id=str(uuid.uuid4()),
        sequence_id=sequence_id,
        timestamp=datetime.now(timezone.utc).isoformat(),
        node=node,
        model=model,
        model_verified=model_verified,
        issue_id=issue_id,
        verdict=verdict,
        critique=critique,
        tier_1_issues=tier_1_issues,
        raw_response=raw_response,
        duration_ms=duration_ms,
        credential_used=credential_used,
        rotation_occurred=rotation_occurred,
        attempts=attempts,
    )
