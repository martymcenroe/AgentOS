# 0603 Unleashed - Auto-Approval PTY Wrapper

**Tool:** `tools/unleashed.py`
**Bash Wrapper:** `tools/unleashed`
**Issue:** [#10](https://github.com/martymcenroe/AgentOS/issues/10)

---

## Overview

Unleashed is a PTY wrapper that eliminates permission friction by auto-approving Claude Code permission prompts after a 10-second countdown, giving users a window to cancel.

**Use case:** Unattended or low-friction Claude sessions where you trust the operations but want a safety window.

---

## Quick Start

### CLI Usage

```bash
# Add to PATH (add to ~/.bashrc for persistence)
export PATH="/c/Users/mcwiz/Projects/AgentOS/tools:$PATH"

# Run unleashed instead of claude
unleashed

# Test detection without injection
unleashed --dry-run

# Custom countdown delay
unleashed --delay 5
UNLEASHED_DELAY=5 unleashed
```

### From Poetry

```bash
poetry run --directory /c/Users/mcwiz/Projects/AgentOS python tools/unleashed.py
poetry run --directory /c/Users/mcwiz/Projects/AgentOS python tools/unleashed.py --dry-run
```

---

## How It Works

### Detection

Unleashed detects permission prompts by looking for Claude Code's footer pattern:

```
Esc to cancel · Tab to add additional instructions
```

The regex handles Unicode variations in the separator:
- `·` (U+00B7 middle dot)
- `–` (U+2013 en-dash)
- `—` (U+2014 em-dash)
- `-` (ASCII hyphen)

### Countdown Sequence

1. Footer detected in PTY output
2. Screen state captured (for audit logging)
3. Countdown overlay displayed (top of screen)
4. 10-second countdown (configurable)
5. If user presses printable key → cancelled, key passed to Claude
6. If countdown completes → Enter injected, prompt approved

### Overlay

The countdown overlay uses ANSI cursor save/restore sequences to avoid corrupting Claude's TUI:

```
[UNLEASHED] Auto-approving in 8s... (Press any key to cancel)
```

---

## Options

| Option | Description |
|--------|-------------|
| `--dry-run` | Test detection without injecting Enter |
| `--delay N` | Countdown delay in seconds (default: 10) |
| `--help` | Show help message |

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `UNLEASHED_DELAY` | Countdown delay in seconds | 10 |

---

## Logging

All sessions are logged to `logs/`:

### Raw Log (`unleashed_TIMESTAMP.log`)

Full raw byte stream from Claude's PTY output. Useful for debugging.

**Warning:** Raw logs can be large for long sessions. Consider periodic cleanup.

### Event Log (`unleashed_events_TIMESTAMP.jsonl`)

Structured JSONL events:

```jsonl
{"ts": "2026-01-14T12:00:00Z", "event": "START", "delay": 10, "dry_run": false}
{"ts": "2026-01-14T12:00:05Z", "event": "FOOTER_DETECTED"}
{"ts": "2026-01-14T12:00:05Z", "event": "SCREEN_CAPTURED", "context_length": 1500}
{"ts": "2026-01-14T12:00:05Z", "event": "COUNTDOWN_START", "delay": 10}
{"ts": "2026-01-14T12:00:15Z", "event": "AUTO_APPROVED", "context": "...first 500 chars..."}
{"ts": "2026-01-14T12:00:30Z", "event": "CHILD_EXITED", "exit_code": 0}
{"ts": "2026-01-14T12:00:30Z", "event": "END"}
```

**Event Types:**
- `START` - Session started
- `FOOTER_DETECTED` - Permission prompt detected
- `SCREEN_CAPTURED` - Screen context saved
- `COUNTDOWN_START` - Countdown began
- `AUTO_APPROVED` - Prompt auto-approved (includes context)
- `AUTO_APPROVED_DRY_RUN` - Would have approved (dry-run mode)
- `CANCELLED_BY_USER` - User pressed key to cancel
- `INTERRUPTED` - Session interrupted (Ctrl+C)
- `CHILD_EXITED` - Claude process exited
- `ERROR` - Error occurred
- `END` - Session ended

---

## Security Considerations

### This is NOT a Security Tool

Unleashed auto-approves ALL permission prompts. It does not:
- Inspect or filter commands
- Distinguish "safe" from "dangerous" operations
- Provide any sandboxing

### Mitigations

1. **10-second delay** - Visual review window before auto-action
2. **Screen capture** - User sees WHAT is being approved
3. **Cancel capability** - Any printable key aborts countdown
4. **Full logging** - Audit trail of all auto-approvals

### When to Use

- Unattended batch operations
- Trusted development workflows
- When you trust the agent's judgment
- When permission prompts are friction, not protection

### When NOT to Use

- Working with untrusted code
- Operations affecting production systems
- When you need to review each action
- When running commands from untrusted sources

---

## Troubleshooting

### "pywinpty not installed"

```bash
poetry add pywinpty
```

### Countdown doesn't trigger

1. Check if the footer pattern is visible in Claude's output
2. Run with `--dry-run` to test detection
3. Check raw log for the footer text

### TUI corruption

If the display looks corrupted:
1. Press Ctrl+L to redraw Claude's screen
2. Try a larger terminal window
3. Check terminal emulator compatibility with ANSI sequences

### Input not working

Unleashed uses `msvcrt` on Windows for keyboard input. If keys aren't registering:
1. Ensure running in a proper terminal (Git Bash, Windows Terminal)
2. Not running in a non-interactive shell

---

## Architecture

```
┌─────────────────┐
│   User Input    │
│   (keyboard)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│  InputReader    │────▶│   Unleashed     │
│  (background)   │     │   (main loop)   │
└─────────────────┘     └────────┬────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   PTY Process   │     │  Footer Check   │     │   Event Logger  │
│   (winpty)      │     │  (regex match)  │     │   (JSONL)       │
└────────┬────────┘     └────────┬────────┘     └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│   PtyReader     │     │ CountdownOverlay│
│   (background)  │     │ (ANSI escape)   │
└────────┬────────┘     └─────────────────┘
         │
         ▼
┌─────────────────┐
│   stdout        │
│   (display)     │
└─────────────────┘
```

---

## Dependencies

- `pywinpty` - PTY handling for Windows (already in pyproject.toml)
- Python 3.8+
- Git Bash or compatible terminal

---

## Future Enhancements (Out of Scope)

- Command blacklist/whitelist filtering
- Cross-platform Unix pty support
- Log rotation/size capping
- Integration with `.claude/settings.json`
- Configuration file for settings
