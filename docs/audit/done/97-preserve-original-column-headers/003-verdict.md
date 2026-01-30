# Issue Review: Preserve Original Column Headers in CSV Output

## Identity Confirmation
I am Gemini 3 Pro, acting as Senior Technical Product Manager & Governance Lead.

## Pre-Flight Gate
PASSED

## Review Summary
The issue is structurally sound with clear User Stories and Acceptance Criteria. However, it fails Tier 1 checks regarding Security (CSV Injection risks due to "No Sanitization" requirement) and Legal (Data Residency explicit statement). These must be addressed before the issue is actionable.

## Tier 1: BLOCKING Issues

### Security
- [ ] **CSV Injection / Formula Injection Risk:** The requirement states "No normalization or sanitization applied to header text." While protecting against snake_case conversion is the goal, strictly applying *no* sanitization opens the door to CSV Injection (e.g., headers starting with `=`, `@`, `+`, `-`). If a PDF header contains these characters, opening the resulting CSV in Excel could execute code.
    *   **Recommendation:** Update requirements to explicitly state: "Preserve text exactly, BUT escape leading formula characters (e.g., prepend `'`) to prevent CSV injection vulnerabilities."

### Safety
- [ ] No issues found.

### Cost
- [ ] No issues found.

### Legal
- [ ] **Privacy & Data Residency:** The draft implies local processing of `W20552.pdf` but does not explicitly mandate the processing environment.
    *   **Recommendation:** Explicitly add a requirement or context statement: "Data processing must occur Local-Only; no external API transmission of PDF contents."

## Tier 2: HIGH PRIORITY Issues

### Quality
- [ ] **Ambiguity in "Exact" Matching:** The requirement "CSV headers must use exact text... Original whitespace" conflicts with standard CSV formatting rules if the original text contains newlines or delimiters.
    *   **Recommendation:** Clarify in Requirements: "Standard CSV escaping (quoting) must be applied for headers containing delimiters (commas) or newlines, handled via standard library `csv.QUOTE_MINIMAL` or similar."

### Architecture
- [ ] **Dependency State:** The issue lists Issue #004 as a dependency.
    *   **Recommendation:** Verify #004 is in "Done" state. If not, this issue cannot be started.

## Tier 3: SUGGESTIONS
- **Taxonomy:** Add labels: `feature`, `data-integrity`, `priority:medium`.
- **Effort Estimate:** Add T-shirt size (Estimate: S/M).

## Questions for Orchestrator
1. Does the "No Sanitization" requirement extend to leading characters that trigger formulas in Excel (`=`, `@`, `+`, `-`), or can we sanitize those for security?

## Verdict
[ ] **APPROVED** - Ready to enter backlog
[x] **REVISE** - Fix Tier 1/2 issues first
[ ] **DISCUSS** - Needs Orchestrator decision