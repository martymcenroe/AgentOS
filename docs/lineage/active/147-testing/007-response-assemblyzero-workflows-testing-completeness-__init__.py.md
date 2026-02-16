```python
"""Completeness analysis for implementation verification.

Issue #147: Implementation Completeness Gate (Anti-Stub Detection)
Related: #181 (Implementation Report), #335 (N2.5 precedent)

This package provides two-layer completeness analysis:
- Layer 1: AST-based deterministic analysis (fast, free)
- Layer 2: Gemini semantic review materials preparation (orchestrator-controlled)

Modules:
- ast_analyzer: Layer 1 AST-based analysis functions
- report_generator: Implementation verification report generation
"""

from assemblyzero.workflows.testing.completeness.ast_analyzer import (
    analyze_dead_cli_flags,
    analyze_docstring_only_functions,
    analyze_empty_branches,
    analyze_trivial_assertions,
    analyze_unused_imports,
    run_ast_analysis,
)
from assemblyzero.workflows.testing.completeness.report_generator import (
    extract_lld_requirements,
    generate_implementation_report,
    prepare_review_materials,
)

__all__ = [
    "analyze_dead_cli_flags",
    "analyze_empty_branches",
    "analyze_docstring_only_functions",
    "analyze_trivial_assertions",
    "analyze_unused_imports",
    "run_ast_analysis",
    "extract_lld_requirements",
    "generate_implementation_report",
    "prepare_review_materials",
]
```
