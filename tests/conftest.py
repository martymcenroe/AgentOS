"""Pytest configuration for AgentOS tests.

This file adds the project root to sys.path so that the agentos package
can be imported in tests without requiring package installation.
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
