"""LLM Provider abstraction for pluggable model support.

Issue #101: Unified Governance Workflow

Provides a unified interface for calling different LLM providers:
- Claude (via claude -p CLI, uses Max subscription)
- Gemini (via GeminiClient with credential rotation)
- OpenAI (future)
- Ollama (future)

Spec format: provider:model (e.g. "claude:opus-4.5", "gemini:2.5-pro")
"""

import json
import shutil
import subprocess
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class LLMCallResult:
    """Result of an LLM API call with full observability.

    Attributes:
        success: Whether the call succeeded.
        response: Parsed response text (None on failure).
        raw_response: Full API response for debugging.
        error_message: Error description on failure.
        provider: Provider name ("claude", "gemini", "openai", "ollama").
        model_used: Actual model that generated the response.
        duration_ms: Total time including retries.
        attempts: Number of API call attempts made.
        credential_used: Which credential was used (for rotation tracking).
        rotation_occurred: True if we rotated from initial credential.
        input_tokens: Input token count (0 if unavailable).
        output_tokens: Output token count (0 if unavailable).
        cache_read_tokens: Prompt cache read tokens (claude -p only).
        cache_creation_tokens: Prompt cache creation tokens (claude -p only).
        cost_usd: Cost in USD (0.0 if unavailable).
        rate_limited: True if a 429 was encountered during this call.
    """

    success: bool
    response: Optional[str]
    raw_response: Optional[str]
    error_message: Optional[str]
    provider: str
    model_used: str
    duration_ms: int
    attempts: int
    credential_used: str = ""
    rotation_occurred: bool = False
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_creation_tokens: int = 0
    cost_usd: float = 0.0
    rate_limited: bool = False


def log_llm_call(result: LLMCallResult) -> None:
    """Log token usage and cost for an LLM call.

    Issue #398: Prints a structured line after every LLM call.
    Issue #399: Includes rate limit warning if 429 was hit.
    """
    duration_s = result.duration_ms / 1000.0
    parts = [
        f"[LLM] provider={result.provider}",
        f"model={result.model_used}",
    ]
    if result.input_tokens or result.output_tokens:
        parts.append(f"input={result.input_tokens}")
        parts.append(f"output={result.output_tokens}")
    if result.cache_read_tokens:
        parts.append(f"cache_read={result.cache_read_tokens}")
    if result.cache_creation_tokens:
        parts.append(f"cache_create={result.cache_creation_tokens}")
    if result.cost_usd > 0:
        parts.append(f"cost=${result.cost_usd:.4f}")
    parts.append(f"duration={duration_s:.1f}s")
    if not result.success:
        parts.append(f"ERROR={result.error_message or 'unknown'}")
    if result.rate_limited:
        parts.append("RATE_LIMITED=true")

    print("    " + " ".join(parts))


class LLMProvider(ABC):
    """Abstract base class for LLM providers.

    Implementations must provide the invoke() method for making API calls.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name (e.g., 'claude', 'gemini')."""
        pass

    @property
    @abstractmethod
    def model(self) -> str:
        """Return the model identifier."""
        pass

    @abstractmethod
    def invoke(
        self,
        system_prompt: str,
        content: str,
        timeout_seconds: int = 300,
    ) -> LLMCallResult:
        """Invoke the LLM with system prompt and content.

        Args:
            system_prompt: Instructions for the model.
            content: User content to process.
            timeout_seconds: Maximum time to wait for response.

        Returns:
            LLMCallResult with response or error information.
        """
        pass


class ClaudeCLIProvider(LLMProvider):
    """Claude provider using claude -p CLI (Max subscription).

    Uses the user's logged-in Claude Code session, which works with
    Max subscription without requiring API credits.

    Supported models:
    - opus-4.5 (default for governance)
    - sonnet (faster, lower quality)
    - haiku (fastest, lowest quality)
    """

    # Model mapping from friendly names to actual model specs
    MODEL_MAP = {
        "opus-4.5": "claude-opus-4-5-20251101",
        "opus": "claude-opus-4-5-20251101",
        "sonnet": "claude-sonnet-4-20250514",
        "haiku": "claude-haiku-4-20250514",
    }

    def __init__(self, model: str = "opus-4.5"):
        """Initialize Claude CLI provider.

        Args:
            model: Model identifier (opus-4.5, sonnet, haiku).

        Raises:
            ValueError: If model is not recognized.
        """
        # Normalize model name
        model_lower = model.lower()
        if model_lower not in self.MODEL_MAP:
            valid = ", ".join(self.MODEL_MAP.keys())
            raise ValueError(f"Unknown Claude model '{model}'. Valid: {valid}")

        self._model = model_lower
        self._model_id = self.MODEL_MAP[model_lower]
        self._cli_path: Optional[str] = None

    @property
    def provider_name(self) -> str:
        return "claude"

    @property
    def model(self) -> str:
        return self._model

    def _find_cli(self) -> str:
        """Find the claude CLI executable.

        Returns:
            Path to claude executable.

        Raises:
            RuntimeError: If claude not found.
        """
        if self._cli_path:
            return self._cli_path

        # Check if claude is in PATH
        claude_path = shutil.which("claude")
        if claude_path:
            self._cli_path = claude_path
            return claude_path

        # Check common npm global install locations
        home = Path.home()
        common_locations = [
            home / "AppData" / "Roaming" / "npm" / "claude.cmd",  # Windows npm
            home / "AppData" / "Roaming" / "npm" / "claude",  # Windows npm (no ext)
            home / ".npm-global" / "bin" / "claude",  # Custom npm prefix
            Path("/usr/local/bin/claude"),  # macOS/Linux global
            home / ".local" / "bin" / "claude",  # Linux local
        ]

        for loc in common_locations:
            if loc.exists():
                self._cli_path = str(loc)
                return self._cli_path

        raise RuntimeError(
            "claude command not found. Ensure Claude Code is installed.\n"
            "Install with: npm install -g @anthropic-ai/claude-code"
        )

    def invoke(
        self,
        system_prompt: str,
        content: str,
        timeout_seconds: int = 300,
    ) -> LLMCallResult:
        """Invoke Claude via headless mode (claude -p).

        Args:
            system_prompt: System instructions for the model.
            content: User content to process.
            timeout_seconds: Maximum time to wait (default 5 minutes).

        Returns:
            LLMCallResult with response or error.
        """
        start_time = time.time()

        try:
            cli_path = self._find_cli()
        except RuntimeError as e:
            return LLMCallResult(
                success=False,
                response=None,
                raw_response=None,
                error_message=str(e),
                provider=self.provider_name,
                model_used=self._model,
                duration_ms=0,
                attempts=0,
            )

        # Build command - prompt passed via stdin
        cmd = [
            cli_path,
            "-p",
            "--output-format", "json",
            "--setting-sources", "user",  # Skip project CLAUDE.md context
            "--tools", "",  # Disable built-in tools
            "--strict-mcp-config",  # Disable MCP tools (issue #157)
            "--model", self._model_id,  # Use full model ID (e.g., claude-opus-4-5-20251101)
        ]

        if system_prompt:
            cmd.extend(["--system-prompt", system_prompt])

        try:
            result = subprocess.run(
                cmd,
                input=content,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=timeout_seconds,
            )

            duration_ms = int((time.time() - start_time) * 1000)

            if result.returncode != 0:
                error_msg = result.stderr or result.stdout or "Unknown error"
                call_result = LLMCallResult(
                    success=False,
                    response=None,
                    raw_response=result.stdout,
                    error_message=f"claude -p failed: {error_msg}",
                    provider=self.provider_name,
                    model_used=self._model,
                    duration_ms=duration_ms,
                    attempts=1,
                )
                log_llm_call(call_result)
                return call_result

            # Parse JSON response — extract usage stats (Issue #398)
            input_tokens = 0
            output_tokens = 0
            cache_read_tokens = 0
            cache_creation_tokens = 0
            cost_usd = 0.0

            try:
                response_data = json.loads(result.stdout)
                response_text = response_data.get("result", "")

                # Extract usage from claude -p JSON
                usage = response_data.get("usage", {})
                input_tokens = usage.get("input_tokens", 0)
                output_tokens = usage.get("output_tokens", 0)
                cache_read_tokens = usage.get("cache_read_input_tokens", 0)
                cache_creation_tokens = usage.get("cache_creation_input_tokens", 0)
                cost_usd = response_data.get("total_cost_usd", 0.0)

            except json.JSONDecodeError:
                # Fall back to raw stdout if not valid JSON
                response_text = result.stdout.strip()

            call_result = LLMCallResult(
                success=True,
                response=response_text,
                raw_response=result.stdout,
                error_message=None,
                provider=self.provider_name,
                model_used=self._model,
                duration_ms=duration_ms,
                attempts=1,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cache_read_tokens=cache_read_tokens,
                cache_creation_tokens=cache_creation_tokens,
                cost_usd=cost_usd,
            )
            log_llm_call(call_result)
            return call_result

        except subprocess.TimeoutExpired:
            duration_ms = int((time.time() - start_time) * 1000)
            call_result = LLMCallResult(
                success=False,
                response=None,
                raw_response=None,
                error_message=f"claude -p timed out after {timeout_seconds}s",
                provider=self.provider_name,
                model_used=self._model,
                duration_ms=duration_ms,
                attempts=1,
            )
            log_llm_call(call_result)
            return call_result
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            call_result = LLMCallResult(
                success=False,
                response=None,
                raw_response=None,
                error_message=str(e),
                provider=self.provider_name,
                model_used=self._model,
                duration_ms=duration_ms,
                attempts=1,
            )
            log_llm_call(call_result)
            return call_result


class GeminiProvider(LLMProvider):
    """Gemini provider using GeminiClient with credential rotation.

    Wraps the existing GeminiClient to provide the unified LLMProvider interface.
    Inherits all rotation and retry logic from GeminiClient.

    Supported models:
    - 2.5-pro (alias: pro) - Pro-tier governance model
    - 2.5-flash (alias: flash) - Fast Flash model
    - 3-pro-preview - Latest Pro preview
    - 3-pro - Production Pro model
    - 3-flash-preview - Latest Flash preview
    """

    # Model mapping from friendly names to actual model IDs
    MODEL_MAP = {
        "2.5-pro": "gemini-2.5-pro",
        "pro": "gemini-2.5-pro",
        "2.5-flash": "gemini-2.5-flash",
        "flash": "gemini-2.5-flash",
        "3-pro-preview": "gemini-3-pro-preview",
        "3-pro": "gemini-3-pro",
        "3-flash-preview": "gemini-3-flash-preview",
    }

    def __init__(self, model: str = "3-pro-preview"):
        """Initialize Gemini provider.

        Args:
            model: Model identifier (2.5-pro, flash, 3-pro-preview, etc.).

        Raises:
            ValueError: If model is not recognized.
        """
        # Normalize model name
        model_lower = model.lower()
        if model_lower not in self.MODEL_MAP:
            valid = ", ".join(self.MODEL_MAP.keys())
            raise ValueError(f"Unknown Gemini model '{model}'. Valid: {valid}")

        self._model = model_lower
        self._model_id = self.MODEL_MAP[model_lower]
        self._client = None

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def model(self) -> str:
        return self._model

    def _get_client(self):
        """Get or create GeminiClient instance."""
        if self._client is None:
            from assemblyzero.core.gemini_client import GeminiClient

            self._client = GeminiClient(model=self._model_id)
        return self._client

    def invoke(
        self,
        system_prompt: str,
        content: str,
        timeout_seconds: int = 300,
    ) -> LLMCallResult:
        """Invoke Gemini via GeminiClient.

        Args:
            system_prompt: System instructions for the model.
            content: User content to process.
            timeout_seconds: Maximum time to wait (not directly used - client has own timeout).

        Returns:
            LLMCallResult with response or error.
        """
        try:
            client = self._get_client()
            result = client.invoke(
                system_instruction=system_prompt,
                content=content,
            )

            # Issue #399: detect 429 from error type
            was_rate_limited = (
                result.error_type is not None
                and str(result.error_type) == "GeminiErrorType.QUOTA_EXHAUSTED"
            ) if hasattr(result, "error_type") else False

            call_result = LLMCallResult(
                success=result.success,
                response=result.response,
                raw_response=result.raw_response,
                error_message=result.error_message,
                provider=self.provider_name,
                model_used=result.model_verified or self._model,
                duration_ms=result.duration_ms,
                attempts=result.attempts,
                credential_used=result.credential_used,
                rotation_occurred=result.rotation_occurred,
                rate_limited=was_rate_limited,
            )
            log_llm_call(call_result)
            return call_result

        except Exception as e:
            # Issue #399: detect 429 in credential pool exhaustion
            is_rate_limit = "quota" in str(e).lower() or "429" in str(e)
            if is_rate_limit:
                print(f"    [LLM] RATE LIMITED: provider=gemini model={self._model} error={str(e)[:100]}")

            call_result = LLMCallResult(
                success=False,
                response=None,
                raw_response=None,
                error_message=str(e),
                provider=self.provider_name,
                model_used=self._model,
                duration_ms=0,
                attempts=0,
                rate_limited=is_rate_limit,
            )
            log_llm_call(call_result)
            return call_result


class MockProvider(LLMProvider):
    """Mock provider for testing without API calls.

    Returns configurable responses for testing workflows.
    """

    # Default responses based on model name
    DEFAULT_RESPONSES = {
        "draft": [
            "# Mock Issue Title\n\n## Summary\n\nThis is a mock draft for testing.\n\n## Requirements\n\n- Mock requirement 1\n- Mock requirement 2\n\n## Acceptance Criteria\n\n- [ ] Mock criteria met",
        ],
        "review": [
            "## Final Verdict\n\n[X] **APPROVED** - Ready for implementation\n[ ] **REVISE** - Requires changes\n[ ] **DISCUSS** - Needs clarification\n\n### Strengths\n- Well-structured\n- Clear requirements\n\n### Recommendations\n- None required for approval",
        ],
    }

    def __init__(
        self,
        model: str = "mock",
        responses: list[str] | None = None,
        fail_on_call: int | None = None,
    ):
        """Initialize mock provider.

        Args:
            model: Model identifier (for display).
            responses: List of responses to return in order. Cycles if exhausted.
            fail_on_call: If set, fail on this call number (1-indexed).
        """
        self._model = model
        # Use model-specific defaults if no responses provided
        if responses is None:
            self._responses = self.DEFAULT_RESPONSES.get(model, ["Mock response"])
        else:
            self._responses = responses
        self._fail_on_call = fail_on_call
        self._call_count = 0

    @property
    def provider_name(self) -> str:
        return "mock"

    @property
    def model(self) -> str:
        return self._model

    def invoke(
        self,
        system_prompt: str,
        content: str,
        timeout_seconds: int = 300,
    ) -> LLMCallResult:
        """Return mock response.

        Args:
            system_prompt: Ignored.
            content: Ignored.
            timeout_seconds: Ignored.

        Returns:
            LLMCallResult with mock response or error.
        """
        self._call_count += 1

        if self._fail_on_call and self._call_count == self._fail_on_call:
            return LLMCallResult(
                success=False,
                response=None,
                raw_response=None,
                error_message=f"Mock failure on call {self._call_count}",
                provider=self.provider_name,
                model_used=self._model,
                duration_ms=0,
                attempts=1,
            )

        # Cycle through responses
        response_idx = (self._call_count - 1) % len(self._responses)
        response = self._responses[response_idx]

        return LLMCallResult(
            success=True,
            response=response,
            raw_response=response,
            error_message=None,
            provider=self.provider_name,
            model_used=self._model,
            duration_ms=100,  # Simulated latency
            attempts=1,
        )


def parse_provider_spec(spec: str) -> tuple[str, str]:
    """Parse provider:model specification.

    Args:
        spec: Provider spec like "claude:opus-4.5" or "gemini:2.5-pro".

    Returns:
        Tuple of (provider_name, model_name).

    Raises:
        ValueError: If spec is malformed.
    """
    if ":" not in spec:
        raise ValueError(
            f"Invalid provider spec '{spec}'. Expected format: provider:model "
            f"(e.g., 'claude:opus-4.5', 'gemini:2.5-pro')"
        )

    parts = spec.split(":", 1)
    provider = parts[0].lower()
    model = parts[1]

    return provider, model


def get_provider(spec: str) -> LLMProvider:
    """Factory function to create LLM provider from spec.

    Args:
        spec: Provider specification like "claude:opus-4.5" or "gemini:2.5-pro".

    Returns:
        Configured LLMProvider instance.

    Raises:
        ValueError: If provider or model is not recognized.

    Examples:
        >>> drafter = get_provider("claude:opus-4.5")
        >>> reviewer = get_provider("gemini:2.5-pro")
        >>> mock = get_provider("mock:test")
    """
    provider, model = parse_provider_spec(spec)

    if provider == "claude":
        return ClaudeCLIProvider(model=model)
    elif provider == "gemini":
        return GeminiProvider(model=model)
    elif provider == "mock":
        return MockProvider(model=model)
    else:
        raise ValueError(
            f"Unknown provider '{provider}'. Supported: claude, gemini, mock"
        )
