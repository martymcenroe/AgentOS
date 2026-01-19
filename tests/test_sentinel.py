#!/usr/bin/env python3
"""
Tests for Sentinel.py - AI-Gated Permission Controller

Uses mocks for winpty and litellm to avoid real process spawning and API calls.
"""

import json
import sys
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'tools'))

# Mock winpty and msvcrt before importing sentinel
mock_winpty_module = MagicMock()
mock_winpty_module.PtyProcess = MagicMock()
mock_msvcrt_module = MagicMock()
mock_msvcrt_module.kbhit.return_value = False
mock_msvcrt_module.getwch.return_value = ''

# Apply mocks before import
sys.modules['winpty'] = mock_winpty_module
sys.modules['msvcrt'] = mock_msvcrt_module

# Now import sentinel
from sentinel import (
    load_forbidden_paths,
    strip_ansi,
    Sentinel,
    PROMPT_REGEX,
    BUFFER_SIZE,
    DEFAULT_FORBIDDEN,
)


class TestLoadForbiddenPaths:
    """Tests for load_forbidden_paths function."""

    def test_load_defaults_when_no_settings(self, tmp_path):
        """Verify default forbidden paths are returned when no settings file exists."""
        with patch('sentinel.Path.home', return_value=tmp_path):
            with patch('sentinel.Path.cwd', return_value=tmp_path):
                paths = load_forbidden_paths()

                # All defaults should be present
                for default in DEFAULT_FORBIDDEN:
                    assert default in paths

    def test_load_context_from_settings(self, tmp_path):
        """Create temp settings.local.json, verify paths loaded."""
        settings = {
            "permissions": {"deny": ["CustomPath1", "SecretFolder"]},
            "ignorePatterns": ["CustomPath2", "*.secret"]
        }

        # Create settings file
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir(parents=True)
        settings_file = claude_dir / "settings.local.json"
        settings_file.write_text(json.dumps(settings))

        with patch('sentinel.Path.home', return_value=tmp_path):
            with patch('sentinel.Path.cwd', return_value=tmp_path):
                paths = load_forbidden_paths()

                # Custom paths should be present
                assert "CustomPath1" in paths
                assert "CustomPath2" in paths
                assert "SecretFolder" in paths
                assert "*.secret" in paths

                # Defaults should still be present
                assert "OneDrive" in paths
                assert "AppData" in paths

    def test_deduplication(self, tmp_path):
        """Verify duplicate paths are removed."""
        settings = {
            "permissions": {"deny": ["OneDrive", "OneDrive"]},  # Duplicate of default
            "ignorePatterns": ["AppData"]  # Duplicate of default
        }

        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir(parents=True)
        settings_file = claude_dir / "settings.local.json"
        settings_file.write_text(json.dumps(settings))

        with patch('sentinel.Path.home', return_value=tmp_path):
            with patch('sentinel.Path.cwd', return_value=tmp_path):
                paths = load_forbidden_paths()

                # Count occurrences - should be exactly 1 each
                assert paths.count("OneDrive") == 1
                assert paths.count("AppData") == 1

    def test_malformed_json_handled(self, tmp_path):
        """Verify malformed JSON doesn't crash, returns defaults."""
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir(parents=True)
        settings_file = claude_dir / "settings.local.json"
        settings_file.write_text("{ invalid json }")

        with patch('sentinel.Path.home', return_value=tmp_path):
            with patch('sentinel.Path.cwd', return_value=tmp_path):
                paths = load_forbidden_paths()

                # Should still have defaults
                assert "OneDrive" in paths


class TestAskHaiku:
    """Tests for the _ask_haiku method."""

    def test_ask_haiku_safe(self):
        """Mock litellm returns SAFE -> True."""
        with patch('sentinel.litellm.completion') as mock_llm:
            mock_response = Mock()
            mock_response.choices = [Mock(message=Mock(content="SAFE"))]
            mock_llm.return_value = mock_response

            s = Sentinel()
            s.forbidden = ["OneDrive"]

            result = s._ask_haiku("ls /tmp")
            assert result is True
            mock_llm.assert_called_once()

    def test_ask_haiku_unsafe(self):
        """Mock litellm returns UNSAFE -> False."""
        with patch('sentinel.litellm.completion') as mock_llm:
            mock_response = Mock()
            mock_response.choices = [Mock(message=Mock(content="UNSAFE - touches forbidden path"))]
            mock_llm.return_value = mock_response

            s = Sentinel()
            s.forbidden = ["OneDrive"]

            result = s._ask_haiku("rm -rf /")
            assert result is False

    def test_ask_haiku_api_failure(self):
        """Mock litellm raises exception -> False (fail closed)."""
        with patch('sentinel.litellm.completion') as mock_llm:
            mock_llm.side_effect = Exception("API Error - quota exhausted")

            s = Sentinel()
            s.forbidden = ["OneDrive"]

            result = s._ask_haiku("any command")
            assert result is False  # Fail closed

    def test_ask_haiku_safe_lowercase(self):
        """Mock litellm returns 'safe' lowercase -> True."""
        with patch('sentinel.litellm.completion') as mock_llm:
            mock_response = Mock()
            mock_response.choices = [Mock(message=Mock(content="safe"))]
            mock_llm.return_value = mock_response

            s = Sentinel()
            s.forbidden = ["OneDrive"]

            result = s._ask_haiku("git status")
            assert result is True


class TestTriggerDetection:
    """Tests for permission prompt detection."""

    def test_prompt_regex_matches(self):
        """Verify the regex matches the Claude permission prompt."""
        # Should match
        assert PROMPT_REGEX.search("Allow this command to run?")
        assert PROMPT_REGEX.search("  Allow this command to run?  ")
        assert PROMPT_REGEX.search("Some text before Allow this command to run? and after")

        # Should not match
        assert not PROMPT_REGEX.search("Allow this to run")
        assert not PROMPT_REGEX.search("command to run?")

    def test_trigger_detection(self):
        """Feed prompt text, verify evaluating flag triggers."""
        s = Sentinel()
        s.evaluating = False
        s._ask_haiku = Mock(return_value=True)  # Mock to avoid API call
        s.pty = Mock()

        # Simulate output containing the trigger
        chunk = "Some output\nAllow this command to run?\n"
        s._process_output(chunk)

        # Should reset after _evaluate()
        assert s.evaluating is False
        # Haiku was consulted
        s._ask_haiku.assert_called_once()

    def test_no_double_evaluation(self):
        """Verify evaluating flag prevents re-entry."""
        s = Sentinel()
        s.evaluating = True  # Already evaluating
        s._ask_haiku = Mock()
        s.pty = Mock()

        # Simulate output containing the trigger
        chunk = "Allow this command to run?\n"
        s._process_output(chunk)

        # Should NOT call _ask_haiku since already evaluating
        s._ask_haiku.assert_not_called()


class TestStripAnsi:
    """Tests for ANSI escape code stripping."""

    def test_strip_ansi_codes(self):
        """Verify ANSI codes are removed."""
        # Text with color codes
        colored = "\x1b[32mGreen text\x1b[0m and \x1b[31mred text\x1b[0m"
        assert strip_ansi(colored) == "Green text and red text"

        # Text with cursor movement
        cursor = "\x1b[2J\x1b[HHello"
        assert strip_ansi(cursor) == "Hello"

        # Plain text unchanged
        plain = "No escape codes here"
        assert strip_ansi(plain) == plain

    def test_strip_bold_and_underline(self):
        """Verify bold and underline codes are removed."""
        bold = "\x1b[1mBold\x1b[0m"
        assert strip_ansi(bold) == "Bold"

        underline = "\x1b[4mUnderline\x1b[0m"
        assert strip_ansi(underline) == "Underline"


class TestBufferManagement:
    """Tests for rolling buffer behavior."""

    def test_buffer_truncation(self):
        """Verify buffer is truncated to BUFFER_SIZE."""
        s = Sentinel()
        s.pty = Mock()
        s._ask_haiku = Mock(return_value=True)

        # Feed more than BUFFER_SIZE characters
        large_chunk = "x" * (BUFFER_SIZE + 500)
        s._process_output(large_chunk)

        # Buffer should be truncated to BUFFER_SIZE
        assert len(s.buffer) == BUFFER_SIZE

    def test_buffer_accumulation(self):
        """Verify buffer accumulates across calls."""
        s = Sentinel()
        s.pty = Mock()

        # Feed multiple small chunks
        s._process_output("Hello ")
        s._process_output("World!")

        assert "Hello World!" in s.buffer

    def test_buffer_rolling(self):
        """Verify old content is dropped when buffer is full."""
        s = Sentinel()
        s.pty = Mock()

        # Fill buffer with 'a's
        s.buffer = "a" * BUFFER_SIZE

        # Add 'b's - should push out 'a's
        s._process_output("b" * 100)

        # Buffer should end with 'b's
        assert s.buffer.endswith("b" * 100)
        # And start with 'a's (remaining after truncation)
        assert s.buffer.startswith("a")
        assert len(s.buffer) == BUFFER_SIZE


class TestSentinelInit:
    """Tests for Sentinel initialization."""

    def test_init_defaults(self):
        """Verify Sentinel initializes with correct defaults."""
        s = Sentinel()

        assert s.buffer == ""
        assert s.evaluating is False
        assert s.pty is None
        assert isinstance(s.forbidden, list)
        assert len(s.forbidden) >= len(DEFAULT_FORBIDDEN)
