"""Tests for gate_log utility — Issue #372.

Verifies per-second timestamps on TDD workflow gate output.
"""

import re

from assemblyzero.workflows.testing.audit import gate_log


class TestGateLog:
    """Tests for gate_log() timestamp formatting."""

    def test_output_has_timestamp(self, capsys):
        """gate_log prepends [HH:MM:SS] timestamp."""
        gate_log("[N4] Test message")
        captured = capsys.readouterr()
        # Should match [HH:MM:SS] pattern
        assert re.search(r"\[\d{2}:\d{2}:\d{2}\]", captured.out)

    def test_message_preserved(self, capsys):
        """Original message appears after timestamp."""
        gate_log("[N0] Loading LLD...")
        captured = capsys.readouterr()
        assert "[N0] Loading LLD..." in captured.out

    def test_format_is_timestamp_space_message(self, capsys):
        """Output format is exactly [HH:MM:SS] message."""
        gate_log("[N2] Scaffold")
        captured = capsys.readouterr()
        line = captured.out.strip()
        assert re.match(r"^\[\d{2}:\d{2}:\d{2}\] \[N2\] Scaffold$", line)

    def test_fstring_message_works(self, capsys):
        """F-string messages work correctly."""
        iteration = 3
        gate_log(f"[N4] Implementing (iteration {iteration})...")
        captured = capsys.readouterr()
        assert "(iteration 3)" in captured.out
