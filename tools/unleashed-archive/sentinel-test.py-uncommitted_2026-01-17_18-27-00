#!/usr/bin/env python3
"""
Sentinel Test - Debug/Verification Runner
Run this via: sentinel-test
"""
import sys
import os
import re
import time
import threading
import queue
from dotenv import load_dotenv

try:
    import winpty
    import msvcrt
    from colorama import init, Fore, Style
    from litellm import completion
except ImportError:
    print("Missing deps. Run: poetry add pywinpty colorama litellm python-dotenv")
    sys.exit(1)

load_dotenv()
init(autoreset=True)

VERSION = "2.0.2-THREADED"
TRIGGER_REGEX = re.compile(r"Allow this command to run\?", re.IGNORECASE)

def debug_log(msg):
    ts = time.strftime("%H:%M:%S")
    sys.stderr.write(f"{Fore.MAGENTA}[DEBUG {ts}] {msg}{Style.RESET_ALL}\n")

# --- THE FIX: THREADED READER (Borrowed from Unleashed) ---
class PtyReader:
    """Reads from PTY in a background thread to prevent blocking hangs."""
    def __init__(self, pty):
        self.pty = pty
        self.queue = queue.Queue()
        self.running = True
        self.thread = threading.Thread(target=self._reader_thread, daemon=True)
        self.thread.start()

    def _reader_thread(self):
        while self.running and self.pty.isalive():
            try:
                # This blocks, but it's in a thread so main loop is safe
                chunk = self.pty.read(1024)
                if chunk:
                    self.queue.put(chunk)
            except EOFError:
                break
            except Exception:
                break

    def read_nowait(self):
        """Non-blocking read for the main loop."""
        data = ""
        while not self.queue.empty():
            try:
                data += self.queue.get_nowait()
            except queue.Empty:
                break
        return data

class SentinelTest:
    def __init__(self):
        self.output_buffer = ""
        self.running = True
        self.evaluating = False
        
        # 1. ENV ISOLATION (Fixes API Key Conflict)
        self.clean_env = os.environ.copy()
        if "ANTHROPIC_API_KEY" in self.clean_env:
            debug_log("Stripping ANTHROPIC_API_KEY from child env")
            del self.clean_env["ANTHROPIC_API_KEY"]
        if "SystemRoot" not in self.clean_env:
            self.clean_env["SystemRoot"] = "C:\\Windows"

        # 2. SPAWN PTY
        try:
            r, c = os.get_terminal_size().lines, os.get_terminal_size().columns
        except:
            r, c = 24, 80

        debug_log(f"Spawning claude via winpty...")
        self.pty = winpty.PtyProcess.spawn(
            ['claude'], 
            dimensions=(r, c),
            cwd=os.getcwd(),
            env=self.clean_env
        )
        
        # 3. START READ THREAD (Fixes the Hang)
        self.reader = PtyReader(self.pty)
        debug_log("PtyReader thread started.")

    def _ask_haiku(self, context):
        debug_log("Asking Haiku (Mock check)...")
        # For test, we assume SAFE to verify flow
        return True

    def _input_loop(self):
        while self.running:
            if msvcrt.kbhit():
                char = msvcrt.getwch()
                if self.pty.isalive():
                    self.pty.write(char)
            time.sleep(0.005)

    def run(self):
        print(f"{Fore.YELLOW}[Sentinel TEST v{VERSION}] Active.{Style.RESET_ALL}")
        threading.Thread(target=self._input_loop, daemon=True).start()

        try:
            while self.running and self.pty.isalive():
                # NON-BLOCKING READ
                data = self.reader.read_nowait()
                
                if data:
                    sys.stdout.write(data)
                    sys.stdout.flush()

                    self.output_buffer += data
                    if len(self.output_buffer) > 2000:
                        self.output_buffer = self.output_buffer[-2000:]

                    # Trigger Check
                    if not self.evaluating and TRIGGER_REGEX.search(data):
                        self.evaluating = True
                        debug_log("Trigger Regex Matched!")
                        
                        # Test Logic: Wait 1s then Approve
                        time.sleep(1.0)
                        debug_log("TEST: Auto-approving...")
                        self.pty.write("y\r")
                        
                        self.evaluating = False
                
                # Sleep briefly to yield CPU
                time.sleep(0.01)

        except KeyboardInterrupt:
            debug_log("Keyboard Interrupt.")
        finally:
            self.running = False
            self.reader.running = False

if __name__ == "__main__":
    SentinelTest().run()
    