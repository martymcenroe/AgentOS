# File: src/agentos/workflow/checkpoint.py

```python
"""Checkpoint database path resolution for workflow persistence.

This module provides functions to determine the location of the workflow
checkpoint database, with support for per-repo isolation and environment
variable overrides.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def get_repo_root() -> Path | None:
    """Get the root directory of the current git repository.
    
    Returns:
        Path to the repository root, or None if not in a git repository.
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return Path(result.stdout.strip())
        return None
    except (FileNotFoundError, OSError):
        # git command not found or other OS error
        return None


def get_checkpoint_db_path() -> Path:
    """Determine the checkpoint database path.
    
    Priority:
    1. AGENTOS_WORKFLOW_DB environment variable (if set and non-empty)
    2. Per-repo: {repo_root}/.agentos/issue_workflow.db
    3. Fail closed with descriptive error if outside git repo
    
    Returns:
        Path to the checkpoint database file.
    
    Raises:
        SystemExit: If not in a git repo and no env var set (fail closed).
    """
    # Check environment variable first
    env_path = os.environ.get("AGENTOS_WORKFLOW_DB", "")
    
    if env_path:  # Non-empty string
        # Expand ~ to home directory
        expanded_path = Path(env_path).expanduser()
        # Ensure parent directory exists
        expanded_path.parent.mkdir(parents=True, exist_ok=True)
        return expanded_path
    
    # Try per-repo path
    repo_root = get_repo_root()
    
    if repo_root is None:
        # Fail closed - not in a git repo and no env var
        print(
            "Error: Not in a git repository and AGENTOS_WORKFLOW_DB not set.\n"
            "Either run from within a git repository, or set the\n"
            "AGENTOS_WORKFLOW_DB environment variable to specify a database path.",
            file=sys.stderr,
        )
        sys.exit(1)
    
    # Create .agentos directory if needed
    agentos_dir = repo_root / ".agentos"
    agentos_dir.mkdir(mode=0o755, parents=True, exist_ok=True)
    
    return agentos_dir / "issue_workflow.db"
```