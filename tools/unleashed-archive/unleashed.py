#!/usr/bin/env python3
"""
Unleashed Test - v3008 (Raw Console Enforcement)
- Sequence ID: 3008
- Uses msvcrt for raw Windows console input to prevent double-echoing.
- Flushes buffers to eliminate the "all over the place" cursor issue.
"""
import os
import sys
import threading
import time
import argparse
import shutil
import msvcrt # Windows-specific raw I/O 

VERSION_ID = "3008"

try:
    import winpty
except ImportError:
    sys.exit(f"[v{VERSION_ID}] FATAL: pywinpty missing.")

CLAUDE_CMD = r"C:\Users\mcwiz\AppData\Roaming\npm\claude.cmd"

class Unleashed:
    def __init__(self, cwd=None):
        self.cwd = cwd or os.getcwd()
        self.running = True

    def _reader_stdin(self, pty):
        """Captures raw keys via msvcrt to bypass local echo"""
        sys.stderr.write(f"[DEBUG v{VERSION_ID}] Stdin: RAW MODE\n")
        while self.running:
            try:
                if msvcrt.kbhit():
                    char = msvcrt.getch()
                    # Manual Ctrl+C (0x03)
                    if char == b'\x03':
                        self.running = False
                        break
                    pty.write(char.decode('utf-8', errors='ignore'))
                else:
                    time.sleep(0.01) # Prevent CPU spiking
            except Exception as e:
                break

    def _reader_pty(self, pty):
        """Reads PTY and writes to screen"""
        while self.running and pty.isalive():
            try:
                data = pty.read(1024)
                if data:
                    if isinstance(data, bytes):
                        sys.stdout.buffer.write(data)
                    else:
                        sys.stdout.write(data)
                    sys.stdout.flush()
            except Exception:
                break

    def run(self):
        sys.stderr.write(f"--- [v{VERSION_ID}] INPUT SYNC ---")
        
        try:
            c, r = shutil.get_terminal_size((120, 40))
        except: c, r = 120, 40

        # Pass environment to ensure Claude knows it has a 256color terminal [cite: 11]
        env = os.environ.copy()
        env["TERM"] = "xterm-256color"
        
        pty = winpty.PtyProcess.spawn(
            ['cmd', '/c', CLAUDE_CMD],
            dimensions=(r, c),
            cwd=self.cwd,
            env=env
        )

        t1 = threading.Thread(target=self._reader_stdin, args=(pty,), daemon=True)
        t2 = threading.Thread(target=self._reader_pty, args=(pty,), daemon=True)
        t1.start()
        t2.start()

        try:
            while self.running and pty.isalive():
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        finally:
            self.running = False
            pty.terminate()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cwd", default=None)
    args = parser.parse_args()
    Unleashed(cwd=args.cwd).run()