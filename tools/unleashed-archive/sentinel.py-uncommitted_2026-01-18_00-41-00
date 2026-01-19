#!/usr/bin/env python3
"""
Sentinel - AI Permission Gate (Haiku)
SAFE VERSION: Avoids terminal capturing to prevent Git Bash deadlocks.
"""
import os
import sys
import subprocess
import asyncio
import argparse

# Check for the library gracefully
try:
    from anthropic import AsyncAnthropic
except ImportError:
    sys.exit("CRITICAL ERROR: 'anthropic' library missing. Run 'poetry add anthropic' in AgentOS.")

# ANSI Colors for visibility
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RESET = '\033[0m'

async def check_safety(command_args, context_cwd):
    # 1. Load the Dedicated Sentinel Key
    api_key = os.environ.get("AGENTOS_SENTINEL_KEY")
    
    if not api_key:
        print(f"{RED}[SENTINEL] ERROR: AGENTOS_SENTINEL_KEY is missing.{RESET}")
        print("Check ~/.agentos_secrets and your .bash_profile.")
        return False

    # 2. Reconstruct the command string for the AI
    command_str = " ".join(command_args)

    # 3. Initialize Haiku
    client = AsyncAnthropic(api_key=api_key)

    # 4. The Security Prompt
    system_prompt = (
        "You are Sentinel, a security gatekeeper for a Windows/Git Bash environment. "
        "Analyze the user's command for danger (deletion, sensitive data exfiltration, system modification). "
        "Context: User is a Professional Engineer. "
        "If the command is safe/standard (e.g., git status, ls, cat, standard python), reply exactly 'ALLOW'. "
        "If unsafe (e.g., rm -rf /, uploading secrets, formatting drives), reply 'BLOCK: <reason>'."
    )

    user_message = f"Working Directory: {context_cwd}\nCommand: {command_str}"

    try:
        # Print scanning message to stderr so it doesn't pollute pipes
        sys.stderr.write(f"{YELLOW}[SENTINEL] Scanning: {command_str}...{RESET}\r")
        sys.stderr.flush()
        
        response = await client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=100,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )

        verdict = response.content[0].text.strip()

        # Clear the "Scanning" line
        sys.stderr.write(" " * 60 + "\r")

        if verdict == "ALLOW":
            # Silent success - let the command run
            return True
        else:
            print(f"{RED}[SENTINEL] ✕ BLOCKED: {verdict}{RESET}")
            return False

    except Exception as e:
        print(f"\n{RED}[SENTINEL] API ERROR: {e}{RESET}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    if not args.command:
        print("Usage: sentinel <command> [args...]")
        sys.exit(1)

    # 1. Run the AI Check
    is_safe = asyncio.run(check_safety(args.command, os.getcwd()))

    # 2. Execute or Abort
    if is_safe:
        try:
            # SAFETY: We use subprocess.run with no piping. 
            # This allows the child command (like git or ls) to own the terminal.
            # This prevents the "Freezing" behavior seen with PTY wrappers.
            result = subprocess.run(args.command)
            sys.exit(result.returncode)
        except FileNotFoundError:
            print(f"{RED}Error: Command not found: {args.command[0]}{RESET}")
            sys.exit(127)
        except KeyboardInterrupt:
            sys.exit(130)
    else:
        sys.exit(1)