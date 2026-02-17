"""Implementation Spec Workflow package.

Issue #304: Implementation Readiness Review Workflow (LLD → Implementation Spec)

This package provides a workflow that transforms approved LLDs into
Implementation Specs with enough concrete detail for autonomous AI
implementation.

Key components:
- state: ImplementationSpecState TypedDict and supporting types
- graph: LangGraph workflow definition with conditional routing
- nodes/: Individual node implementations (N0-N6)

Workflow steps:
1. N0: Load approved LLD and parse files list
2. N1: Analyze codebase, extract current state excerpts
3. N2: Generate Implementation Spec draft (Claude)
4. N3: Validate mechanical completeness
5. N4: Optional human review gate
6. N5: Gemini readiness review
7. N6: Finalize and write spec to docs/lld/drafts/
"""

from assemblyzero.workflows.implementation_spec.graph import (
    create_implementation_spec_graph,
    route_after_review,
    route_after_validation,
)
from assemblyzero.workflows.implementation_spec.state import (
    CompletenessCheck,
    FileToModify,
    ImplementationSpecState,
    PatternRef,
)

__all__ = [
    "ImplementationSpecState",
    "FileToModify",
    "PatternRef",
    "CompletenessCheck",
    "create_implementation_spec_graph",
    "route_after_validation",
    "route_after_review",
]