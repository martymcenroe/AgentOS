---
description: Real-time permission friction logger - track every permission prompt
argument-hint: "[--help] [--tail N] [--clear]"
aliases: ["/zz"]
---

# Zugzwang - Permission Friction Logger

**Aliases:** `/zz` (same as `/zugzwang`)

**If `$ARGUMENTS` contains `--help`:** Display the Help section below and STOP.

---

## Help

Usage: `/zugzwang [--help] [--tail N] [--clear]`

| Argument | Description |
|----------|-------------|
| `--help` | Show this help message and exit |
| `--tail N` | Show last N log entries (default: 10) |
| `--clear` | Clear the log file and start fresh |

**Examples:**
- `/zugzwang --help` - show this help
- `/zugzwang` or `/zz` - activate logger, show recent entries
- `/zugzwang --tail 20` - show last 20 entries
- `/zugzwang --clear` - clear log file

**What it does:**
1. Activates real-time logging of all permission-related events
2. Logs risky command patterns BEFORE execution
3. Logs blocked/denied tool calls AFTER they fail
4. Propagates logging to spawned agents

**Log location:**
`C:\Users\mcwiz\.claude\projects\C--Users-mcwiz-Projects-AgentOS\zugzwang.log`

**Why "zugzwang"?**
Chess term: a position where any move worsens your situation. Perfect metaphor for permission friction - you're stuck waiting for approval, unable to proceed.

---

## Execution

### Step 1: Determine Mode

Parse `$ARGUMENTS`:
- `--clear` flag present → Clear mode
- `--tail N` present → Show N entries (extract number)
- No flags → Default mode (activate + show last 10)

### Step 2: Log File Path

```
LOG_PATH = C:\Users\mcwiz\.claude\projects\C--Users-mcwiz-Projects-AgentOS\zugzwang.log
```

### Step 3: Execute Based on Mode

**If `--clear`:**
1. Use Write tool to create empty file at LOG_PATH
2. Output: "Zugzwang log cleared. Fresh start."
3. STOP

**If `--tail N` or default:**
1. Use Read tool to check if LOG_PATH exists
2. If file doesn't exist or is empty:
   - Output: "No friction events logged yet."
3. If file has content:
   - Read last N lines (default 10) using Read with offset
   - Display entries in formatted table

### Step 4: Activate Logging Protocol

Output to user:
```
**Zugzwang Active**

From this point forward, I will log all permission-related events to:
`C:\Users\mcwiz\.claude\projects\C--Users-mcwiz-Projects-AgentOS\zugzwang.log`

Events logged:
- PATTERN_RISKY: Commands with |, &&, ; before execution
- TOOL_BLOCKED: Tool calls blocked by hooks/permissions
- TOOL_DENIED: User denied permission prompts
- TOOL_APPROVED: User approved permission prompts

When spawning agents, logging instructions will be included automatically.
```

---

## Logging Protocol (ACTIVE FOR REMAINDER OF SESSION)

### Pre-Tool Logging (BEFORE Bash calls)

**Risky patterns that MUST be logged before execution:**
- Command contains `|` (pipe)
- Command contains `&&` (chain)
- Command contains `;` (separator)
- Command uses `head -n` or `tail -n` with flags on `.claude/` paths
- Command not in common safe allowlist

**If risky pattern detected:**
1. Get current timestamp: Use PowerShell `Get-Date -Format "yyyy-MM-ddTHH:mm:ss"`
2. Append to log file using Write tool (append mode not available - read, append, write back):

```
Read current log → Append new entry → Write back

Entry format:
TIMESTAMP | PATTERN_RISKY | agent:opus | tool:Bash | context:"COMMAND_HERE" | status:pre-execution
```

3. Then execute the command

### Post-Tool Logging (AFTER tool results)

**Scan every tool result for these indicators:**
- "blocked"
- "denied"
- "not allowed"
- "requires approval"
- "permission"
- Exit code non-zero with permission-related context

**If indicator found:**
```
TIMESTAMP | TOOL_BLOCKED | agent:opus | tool:TOOL_NAME | context:"ERROR_MSG" | status:blocked
```

### User Feedback Logging

**If user message suggests they approved/denied something:**
- Keywords: "approved", "denied", "allowed", "rejected", "clicked yes/no"

```
TIMESTAMP | TOOL_APPROVED | agent:opus | tool:unknown | context:"user indicated approval" | status:confirmed
```
or
```
TIMESTAMP | TOOL_DENIED | agent:opus | tool:unknown | context:"user indicated denial" | status:confirmed
```

---

## Spawned Agent Instructions (MANDATORY)

**When spawning ANY Task agent while zugzwang is active, APPEND this to the prompt:**

```
**ZUGZWANG LOGGING ACTIVE:**

You MUST log permission-related events to:
C:\Users\mcwiz\.claude\projects\C--Users-mcwiz-Projects-AgentOS\zugzwang.log

**Before ANY Bash command that:**
- Contains | (pipe), && (chain), or ; (separator)
- Uses flags like `head -n` or `tail -n` on .claude/ paths
- Might trigger a permission prompt

**Do this:**
1. Read the current log file content
2. Append a new line: `TIMESTAMP | PATTERN_RISKY | agent:sonnet | tool:Bash | context:"YOUR_COMMAND" | status:pre-execution`
3. Write the updated content back
4. Then execute your command

**After ANY tool result containing:**
"blocked", "denied", "not allowed", "requires approval"

**Do this:**
1. Read → Append → Write: `TIMESTAMP | TOOL_BLOCKED | agent:sonnet | tool:TOOL | context:"ERROR" | status:blocked`

Use PowerShell for timestamp: `powershell.exe -Command "Get-Date -Format 'yyyy-MM-ddTHH:mm:ss'"`
```

---

## Log Entry Format Reference

```
TIMESTAMP | EVENT_TYPE | agent:MODEL | tool:TOOL | context:"DESCRIPTION" | status:STATUS
```

| Field | Values |
|-------|--------|
| TIMESTAMP | `yyyy-MM-ddTHH:mm:ss` |
| EVENT_TYPE | `PATTERN_RISKY`, `TOOL_BLOCKED`, `TOOL_DENIED`, `TOOL_APPROVED` |
| agent | `opus`, `sonnet`, `haiku` |
| tool | `Bash`, `Edit`, `Write`, `unknown` |
| context | Brief description or command snippet |
| status | `pre-execution`, `blocked`, `denied`, `confirmed` |

**Example entries:**
```
2026-01-11T14:32:15 | PATTERN_RISKY | agent:opus | tool:Bash | context:"git status | grep modified" | status:pre-execution
2026-01-11T14:32:18 | TOOL_BLOCKED | agent:opus | tool:Bash | context:"Exit code 1: Permission denied" | status:blocked
2026-01-11T14:35:42 | TOOL_APPROVED | agent:opus | tool:unknown | context:"user clicked allow" | status:confirmed
2026-01-11T14:40:00 | PATTERN_RISKY | agent:sonnet | tool:Bash | context:"head -n 5 ~/.claude/file" | status:pre-execution
```

---

## Viewing the Log

**Manual check anytime:**
```
Read: C:\Users\mcwiz\.claude\projects\C--Users-mcwiz-Projects-AgentOS\zugzwang.log
```

**From Bash (no pipes!):**
```bash
cat /c/Users/mcwiz/.claude/projects/C--Users-mcwiz-Projects-AgentOS/zugzwang.log
```

---

## Integration with /friction

The `/friction` skill analyzes past session transcripts for patterns.
The `/zugzwang` skill captures events in real-time.

They are complementary:
- `/zugzwang` = live capture during work
- `/friction` = forensic analysis after sessions

Future enhancement: `/friction` could read zugzwang.log to correlate real-time logs with transcript analysis.

---

## Rules

- **Log BEFORE risky commands** - Don't wait for failure
- **Log AFTER any blocked result** - Capture what failed
- **Include agent type** - Critical for debugging spawned agent issues
- **Propagate to spawned agents** - Include instructions in every Task prompt
- **Append, don't overwrite** - Read → append → write pattern
