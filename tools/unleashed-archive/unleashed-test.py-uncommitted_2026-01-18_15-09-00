#!/usr/bin/env python3
"""
Unleashed Test - v3026 (Latin-1 Bypass)
- Sequence ID: 3026
- PERMANENT: Forensic logging to stderr.
- PERMANENT: Versioning and Debug markers.
- FIXED: Uses 'latin-1' to satisfy WinPTY's string requirement for raw bytes.
"""
import os
import sys
import threading
import time
import argparse
import shutil
import msvcrt

VERSION_ID = "3026"

try:
    import winpty
except ImportError:
    sys.stderr.write(f"[v{VERSION_ID}] FATAL: pywinpty missing.\n")
    sys.stderr.flush()
    sys.exit(1)

CLAUDE_CMD = r"C:\Users\mcwiz\AppData\Roaming\npm\claude.cmd"
FOOTER_PATTERN = b'Esc to cancel'

class Unleashed:
    def __init__(self, cwd=None):
        self.cwd = cwd or os.getcwd()
        self.running = True
        self.in_countdown = False
        self.overlap_buffer = b""

    def _reader_stdin(self, pty):
        sys.stderr.write(f"[DEBUG v{VERSION_ID}] Thread-Stdin: ONLINE\n")
        sys.stderr.flush()
        while self.running:
            try:
                char = msvcrt.getch()
                
                if char == b'\x03': # Ctrl+C
                    sys.stderr.write(f"[DEBUG v{VERSION_ID}] User Interrupted (Ctrl+C).\n")
                    sys.stderr.flush()
                    self.running = False
                    break
                
                if char in (b'\x00', b'\xe0'):
                    next_char = msvcrt.getch()
                    # FIX: Decode the raw bytes using latin-1.
                    # This maps 0xe0 0x50 to string characters that PyString accepts
                    # while preserving the exact bit-pattern for the PTY.
                    full_seq = (char + next_char).decode('latin-1')
                    pty.write(full_seq)
                else:
                    # For normal text, utf-8 is safe
                    pty.write(char.decode('utf-8', errors='ignore'))
                    
            except Exception as e:
                sys.stderr.write(f"[DEBUG v{VERSION_ID}] Stdin Error: {e}\n")
                sys.stderr.flush()
                break

    def _reader_pty(self, pty):
        sys.stderr.write(f"[DEBUG v{VERSION_ID}] Thread-PTY: ONLINE\n")
        sys.stderr.flush()
        while self.running and pty.isalive():
            try:
                data = pty.read(8192)
                if data:
                    if isinstance(data, str):
                        raw_bytes = data.encode('utf-8', errors='ignore')
                        sys.stdout.write(data)
                    else:
                        raw_bytes = data
                        sys.stdout.buffer.write(data)
                    
                    sys.stdout.flush()
                    time.sleep(0.002)

                    search_chunk = self.overlap_buffer + raw_bytes
                    if not self.in_countdown and FOOTER_PATTERN in search_chunk:
                        self.do_approval(pty)
                    
                    self.overlap_buffer = raw_bytes[-32:]
            except Exception as e:
                sys.stderr.write(f"[DEBUG v{VERSION_ID}] PTY Error: {e}\n")
                sys.stderr.flush()
                break

    def do_approval(self, pty):
        self.in_countdown = True
        self.overlap_buffer = b""
        sys.stderr.write("\n\033[1;33m[Unleashed] Approving in 0.5s...\033[0m\n")
        sys.stderr.flush()
        time.sleep(0.5)
        pty.write('\r')
        self.in_countdown = False

    def run(self):
        sys.stderr.write(f"--- [v{VERSION_ID}] FORENSIC SESSION START ---\n")
        sys.stderr.write(f"[DEBUG] Python: {sys.version.split()[0]}\n")
        sys.stderr.write(f"[DEBUG] CWD: {self.cwd}\n")
        sys.stderr.flush()
        
        try:
            c, r = shutil.get_terminal_size((120, 40))
        except: c, r = 120, 40

        env = os.environ.copy()
        env["TERM"] = "xterm-256color"
        
        try:
            pty = winpty.PtyProcess.spawn(
                ['cmd', '/c', CLAUDE_CMD],
                dimensions=(r, c),
                cwd=self.cwd,
                env=env
            )
            sys.stderr.write(f"[DEBUG] Spawn SUCCESS. PID: {pty.pid}\n")
            sys.stderr.flush()
        except Exception as e:
            sys.stderr.write(f"[DEBUG] Spawn FAILED: {e}\n")
            sys.stderr.flush()
            return

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
            sys.stderr.write(f"--- [v{VERSION_ID}] SESSION CLOSED ---\n")
            sys.stderr.flush()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cwd", default=None)
    args = parser.parse_args()
    Unleashed(cwd=args.cwd).run()