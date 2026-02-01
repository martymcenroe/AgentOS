"""Unified Governance Workflow package.

Issue #101: Unified Governance Workflow

This package provides a unified workflow for both:
- Issue creation (from briefs/ideation notes)
- LLD creation (from GitHub issues)

Key components:
- config: WorkflowConfig dataclass and presets
- state: GovernanceWorkflowState TypedDict
- audit: Unified audit trail utilities
- graph: Parameterized StateGraph
- nodes/: Individual node implementations
"""

from agentos.workflows.governance.config import (
    GateConfig,
    WorkflowConfig,
    create_issue_config,
    create_lld_config,
)
from agentos.workflows.governance.graph import create_governance_graph
from agentos.workflows.governance.state import (
    GovernanceWorkflowState,
    HumanDecision,
    WorkflowType,
    create_initial_state,
)

__all__ = [
    "WorkflowConfig",
    "GateConfig",
    "GovernanceWorkflowState",
    "HumanDecision",
    "WorkflowType",
    "create_issue_config",
    "create_lld_config",
    "create_governance_graph",
    "create_initial_state",
]
