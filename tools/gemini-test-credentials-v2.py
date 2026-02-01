#!/usr/bin/env python3
"""
gemini-test-credentials-v2.py - Test all Gemini credentials using the new google-genai SDK.

This script uses the modern SDK (google-genai) to verify credentials
and demonstrates the timeout mechanism to prevent hanging.

Usage:
    python tools/gemini-test-credentials-v2.py
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import Optional, Tuple

try:
    from google import genai
    from google.genai import errors, types
except ImportError:
    print("ERROR: google-genai SDK not found.")
    print("Please run: poetry add google-genai")
    sys.exit(1)

# Configuration
CREDENTIALS_FILE = Path.home() / ".agentos" / "gemini-credentials.json"
TEST_PROMPT = "Say hello in exactly 3 words."
TEST_MODEL = "gemini-2.0-flash"  # Fast model for testing
TIMEOUT_MS = 60000  # Explicit timeout in MILLISECONDS

def test_api_key(name: str, key: str) -> Tuple[bool, str]:
    """Test an API key credential using the new SDK."""
    try:
        client = genai.Client(api_key=key)
        
        # Call with explicit timeout in MILLISECONDS
        response = client.models.generate_content(
            model=TEST_MODEL,
            contents=TEST_PROMPT,
            config=types.GenerateContentConfig(
                http_options=types.HttpOptions(timeout=TIMEOUT_MS)
            )
        )

        if response.text:
            preview = response.text.strip()[:50]
            return True, f"OK - Response: {preview}"
        else:
            return False, "ERROR: Empty response"

    except errors.ClientError as e:
        error_msg = str(e)
        if "API_KEY_INVALID" in error_msg or "403" in error_msg:
            return False, "INVALID KEY / PERMISSION DENIED"
        elif "429" in error_msg or "QUOTA_EXHAUSTED" in error_msg:
            return False, "RATE LIMITED (429) / QUOTA EXHAUSTED"
        else:
            return False, f"CLIENT ERROR: {error_msg[:100]}"
    except errors.APIError as e:
        return False, f"API ERROR: {str(e)[:100]}"
    except Exception as e:
        if "timeout" in str(e).lower():
            return False, f"TIMEOUT ({TIMEOUT_SECONDS}s)"
        return False, f"EXCEPTION: {type(e).__name__}: {str(e)[:100]}"

def main():
    print("=" * 60)
    print("GEMINI CREDENTIAL TEST V2 (google-genai SDK)")
    print(f"Testing with model: {TEST_MODEL}")
    print(f"Prompt: \"{TEST_PROMPT}\"")
    print(f"Timeout: {TIMEOUT_MS}ms")
    print("=" * 60)
    print()

    # Load credentials
    if not CREDENTIALS_FILE.exists():
        print(f"ERROR: Credentials file not found: {CREDENTIALS_FILE}")
        sys.exit(1)

    try:
        with open(CREDENTIALS_FILE, encoding="utf-8") as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in credentials file: {e}")
        sys.exit(1)

    credentials = config.get("credentials", [])
    if not credentials:
        print("No credentials found in config file.")
        sys.exit(1)

    results = []

    for cred in credentials:
        name = cred.get("name", "unnamed")
        cred_type = cred.get("type", "unknown")
        enabled = cred.get("enabled", False)
        account = cred.get("account-name", "")

        status_str = "ENABLED" if enabled else "disabled"
        account_str = f" ({account})" if account else ""

        print(f"Testing: {name}{account_str} [{cred_type}] [{status_str}]")
        print("-" * 50)

        if cred_type == "api_key":
            key = cred.get("key", "")
            if not key:
                success, message = False, "NO KEY CONFIGURED"
            else:
                success, message = test_api_key(name, key)
        elif cred_type == "oauth":
            # OAuth is handled differently in the new SDK; 
            # for this tool, we'll focus on API Keys first.
            success, message = False, "OAuth test not implemented in v2 yet"
        else:
            success, message = False, f"UNKNOWN TYPE: {cred_type}"

        status_icon = "PASS" if success else "FAIL"
        print(f"  {status_icon} {message}")
        print()

        results.append((name, enabled, success, message))

    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    working = [r for r in results if r[2]]
    enabled_working = [r for r in working if r[1]]

    print(f"Total credentials: {len(results)}")
    print(f"Working: {len(working)}")
    print(f"Working + Enabled: {len(enabled_working)}")
    print()

    if not enabled_working:
        print("WARNING: No working enabled credentials found.")
    else:
        print("All good! The new SDK successfully communicated with Gemini.")

if __name__ == "__main__":
    main()
