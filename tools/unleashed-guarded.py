#!/usr/bin/env python3
"""
Unleashed Guarded v2 - Instant Approval & Audit Logging.
"""
import os
import sys
import threading
import time
import queue
import re
import argparse
import datetime
from collections import deque

# Check dependencies
try:
    import winpty
    import msvcrt
    from anthropic import Anthropic
except ImportError:
    sys.exit("Error: Missing dependencies. Run 'poetry add anthropic pywinpty' in AgentOS.")

# --- CONFIGURATION ---
FOOTER_PATTERN = re.compile(r'Esc to cancel[-·–—\s]+Tab to add additional instructions', re.IGNORECASE)
MAX_CONTEXT_CHARS = 4000
ANSI_ESCAPE = re.compile(r'\x1b\[[0-9;]*m')

class RollingBuffer:
    def __init__(self, maxlen=4000):
        self.maxlen = maxlen
        self.buffer = deque()
        self.current_len = 0

    def append(self, text):
        clean_text = ANSI_ESCAPE.sub('', text)
        self.buffer.append(clean_text)
        self.current_len += len(clean_text)
        while self.current_len > self.maxlen and self.buffer:
            removed = self.buffer.popleft()
            self.current_len -= len(removed)

    def get_context(self):
        return "".join(self.buffer)

class UnleashedGuarded:
    def __init__(self, target_cwd=None):
        self.running = True
        self.in_check = False
        self.cwd = target_cwd if target_cwd else os.getcwd()
        self.output_buffer = RollingBuffer(maxlen=MAX_CONTEXT_CHARS)
        
        # Setup Logging (Absolute path to avoid CWD confusion)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir) # Go up from /tools
        self.log_dir = os.path.join(project_root, "logs")
        self.log_file = os.path.join(self.log_dir, "sentinel-audit.log")
        
        # Ensure log directory exists
        os.makedirs(self.log_dir, exist_ok=True)

        # Load Keys
        self.sentinel_key = os.environ.get("AGENTOS_SENTINEL_KEY")
        if not self.sentinel_key:
            sys.exit("Error: AGENTOS_SENTINEL_KEY not found in environment.")

        # Clean Environment
        self.clean_env = os.environ.copy()
        if "ANTHROPIC_API_KEY" in self.clean_env:
            del self.clean_env["ANTHROPIC_API_KEY"]
        if "SystemRoot" not in self.clean_env:
            self.clean_env["SystemRoot"] = "C:\\Windows"

    def _read_loop(self, pty, q):
        while self.running and pty.isalive():
            try:
                d = pty.read(1024)
                if d: q.put(d)
            except: break

    def _input_loop(self, pty):
        while self.running:
            if msvcrt.kbhit():
                try: pty.write(msvcrt.getwch())
                except: pass
            time.sleep(0.01)

    def log_audit(self, verdict, reason, context_snippet):
        """Writes event to the audit log."""
        timestamp = datetime.datetime.now().isoformat()
        entry = (
            f"[{timestamp}] VERDICT: {verdict}\n"
            f"  Reason: {reason}\n"
            f"  CWD: {self.cwd}\n"
            f"  Context (First 100 chars): {context_snippet[:100].replace(chr(10), ' ')}...\n"
            f"--------------------------------------------------\n"
        )
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(entry)
        except Exception as e:
            # Never crash the UI for a log error, just print to stderr
            sys.stderr.write(f"\r[LOG ERROR] Could not write to audit log: {e}\n")

    def check_safety(self, context_str):
        client = Anthropic(api_key=self.sentinel_key)
        
        system_prompt = (
            "You are a safety guard for an autonomous coding agent. "
            "Review the terminal output provided. "
            "1. Identify the action (e.g., 'rm -rf', 'git push', 'edit main.py'). "
            "2. ASSESS RISK: "
            "   - BLOCK: System destruction, huge downloads, exfiltrating secrets, 'find /dev/null'. "
            "   - ALLOW: Coding, editing, testing, git operations. "
            "Output exactly 'ALLOW' or 'BLOCK: <reason>'."
        )

        user_message = f"Working Directory: {self.cwd}\n\nTERMINAL OUTPUT CONTEXT:\n{context_str}"

        try:
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=150,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}]
            )
            return response.content[0].text.strip()
        except Exception as e:
            return f"BLOCK: API Error ({str(e)})"

    def run(self):
        try:
            c, r = os.get_terminal_size().columns, os.get_terminal_size().lines
        except: c, r = 120, 40

        pty = winpty.PtyProcess.spawn(
            ['claude'], dimensions=(r, c), cwd=self.cwd, env=self.clean_env
        )

        q = queue.Queue()
        threading.Thread(target=self._read_loop, args=(pty, q), daemon=True).start()
        threading.Thread(target=self._input_loop, args=(pty,), daemon=True).start()

        try:
            while pty.isalive():
                try:
                    chunk = q.get_nowait()
                    sys.stdout.write(chunk)
                    sys.stdout.flush()
                    self.output_buffer.append(chunk)

                    clean = ANSI_ESCAPE.sub('', chunk)
                    if not self.in_check and FOOTER_PATTERN.search(clean):
                        self.trigger_guard(pty)
                        
                except queue.Empty:
                    time.sleep(0.01)
        except KeyboardInterrupt:
            pass
        finally:
            self.running = False

    def trigger_guard(self, pty):
        self.in_check = True
        
        # Non-blocking status indicator
        sys.stdout.write(f"\n\x1b[33m[Sentinel] 🛡️ Scanning...\x1b[0m")
        sys.stdout.flush()

        context = self.output_buffer.get_context()
        verdict_raw = self.check_safety(context)
        
        # Parse Verdict
        if verdict_raw.startswith("ALLOW"):
            verdict = "ALLOW"
            reason = "Safe"
        else:
            verdict = "BLOCK"
            reason = verdict_raw.replace("BLOCK:", "").strip()

        # Log it
        self.log_audit(verdict, reason, context)

        # Clear status line
        sys.stdout.write("\r" + " " * 40 + "\r")

        if verdict == "ALLOW":
            # ZERO TIMER: Instant approval
            sys.stdout.write(f"\x1b[32m[Sentinel] ✓ Auto-Approved.\x1b[0m\n")
            pty.write('\r')
            self.in_check = False
        else:
            # BLOCKED: Manual Control
            sys.stdout.write(f"\n\x1b[91m[Sentinel] 🛑 BLOCKED: {reason}\x1b[0m\n")
            sys.stdout.write(f"\x1b[93mPress ENTER to override, or ESC to cancel.\x1b[0m\n")
            sys.stdout.flush()
            self.in_check = False 
            time.sleep(1) 

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cwd", help="Target directory")
    args = parser.parse_args()
    UnleashedGuarded(target_cwd=args.cwd).run()