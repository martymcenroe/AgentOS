#!/usr/bin/env python3
"""
Unleashed Danger - NO SAFETY CHECKS
FIXED: Environment Isolation
"""
import argparse
import os
import sys
import threading
import time
import queue
try: import winpty
except: sys.exit(1)
try: import msvcrt
except: pass

VERSION = "1.4.2-DANGER-FIXED"

class PtyReader:
    def __init__(self, pty):
        self.pty = pty; self.queue = queue.Queue(); self.running = True
        threading.Thread(target=self._run, daemon=True).start()
    def _run(self):
        while self.running and self.pty.isalive():
            try: 
                d = self.pty.read(4096)
                if d: self.queue.put(d)
            except: break
    def read(self):
        r = ""
        while not self.queue.empty(): r += self.queue.get_nowait()
        return r

class UnleashedDanger:
    def __init__(self, cwd=None):
        self.cwd = cwd or os.getcwd()
        # --- FIX ENV ---
        self.clean_env = os.environ.copy()
        if "ANTHROPIC_API_KEY" in self.clean_env: del self.clean_env["ANTHROPIC_API_KEY"]
        if "SystemRoot" not in self.clean_env: self.clean_env["SystemRoot"] = "C:\\Windows"

    def run(self):
        print(f"Unleashed DANGER v{VERSION}")
        c, r = 80, 24
        try: c, r = os.get_terminal_size().columns, os.get_terminal_size().lines
        except: pass

        pty = winpty.PtyProcess.spawn(['claude'], dimensions=(r, c), cwd=self.cwd, env=self.clean_env)
        reader = PtyReader(pty)

        try:
            while pty.isalive():
                out = reader.read()
                if out: 
                    sys.stdout.write(out); sys.stdout.flush()
                    if "Allow this command to run?" in out:
                        # INSTANT APPROVAL
                        pty.write('\r')
                
                # Passthrough input
                if msvcrt.kbhit(): pty.write(msvcrt.getwch())
                time.sleep(0.01)
        except KeyboardInterrupt: pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cwd", type=str)
    args, _ = parser.parse_known_args()
    UnleashedDanger(cwd=args.cwd).run()