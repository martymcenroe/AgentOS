The file has been written at `C:\Users\mcwiz\Projects\AssemblyZero-304\docs\standards\0701-implementation-spec-template.md`.

The template includes:

- **Metadata header** following the project's standard format (0010 pattern)
- **10 required sections** matching what N3 (`validate_completeness`) checks: Summary, Files to Implement, Current State Analysis, Data Structures, Function Specifications, Change Instructions, Pattern References, Dependencies & Imports, Test Guidance, and Implementation Checklist
- **Completeness Checks table** documenting exactly what N3 validates and the minimum thresholds
- **Anti-Patterns table** showing common failures that cause N3/N5 rejection
- **Section Requirements Summary** with which sections are N3-checked
- **Cross-references** to related standards (0702, 0010, 0007, 0001)

The template is designed so `generate_spec.py` loads it via `load_template(SPEC_TEMPLATE_PATH)` and passes it to Claude as the structure to follow, while `validate_completeness.py` mechanically verifies the output against the documented checks.

What do you want to work on next?
