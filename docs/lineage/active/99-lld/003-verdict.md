# LLD Review: 199-Feature: Schema-driven project structure

## Identity Confirmation
I am Gemini 3 Pro, acting as Senior Software Architect & AI Governance Lead.

## Pre-Flight Gate
PASSED

## Review Summary
The proposed design correctly identifies the need for a configuration-driven approach to project structure, using a JSON schema as the single source of truth. The architecture is sound and follows the standard pattern for this type of refactor. However, the Test Plan (Section 10) relies exclusively on synthetic fixtures, failing to validate that the *actual production schema file* meets the specific business requirements defined in Section 3.

## Open Questions Resolved
- [x] ~~Should the schema include file templates inline or reference external template files?~~ **RESOLVED: Reference external files.** Inline templates in JSON are difficult to maintain (no multiline string support, escaping issues) and bloat the schema. Store templates in a dedicated `templates/` directory or similar.
- [x] ~~Should schema validation include content validation (e.g., CLAUDE.md must contain certain sections)?~~ **RESOLVED: No.** Limit this tool to *structural* validation (existence of files/directories). Content validation adds significant complexity and belongs in a separate linter or specific test suite (e.g., `test_documentation.py`).

## Requirement Coverage Analysis (MANDATORY)

**Section 3 Requirements:**
| # | Requirement | Test(s) | Status |
|---|-------------|---------|--------|
| 1 | `docs/standards/0009-structure-schema.json` exists and defines complete project structure | - | **GAP** |
| 2 | `new-repo-setup.py` reads structure from schema instead of hardcoded lists | T020, T040 | ✓ Covered |
| 3 | `new-repo-setup.py --audit` validates against schema definitions | T080, T090, T100 | ✓ Covered |
| 4 | Standard 0009 references schema as authoritative source | - | **GAP** |
| 5 | Schema includes `docs/lineage/` structure with `active/` and `done/` subdirectories | - | **GAP** |
| 6 | No hardcoded directory lists remain in new-repo-setup.py | T020 (Missing file exception proves dependency) | ✓ Covered |

**Coverage Calculation:** 3 requirements covered / 6 total = **50%**

**Verdict:** **BLOCK**

**Missing Test Scenarios:**
- **For Req 1 & 5:** Add `test_production_schema_integrity`: Load the actual `docs/standards/0009-structure-schema.json` file (not a fixture) and assert it is valid JSON, contains required keys, and specifically contains the `docs/lineage` -> `children` -> `active` / `done` structure.
- **For Req 4:** Add `test_standard_references_schema`: Read `docs/standards/0009-canonical-project-structure.md` and assert it contains a link or reference to the JSON schema file.

## Tier 1: BLOCKING Issues
No blocking issues found in Cost, Safety, Security, or Legal categories. LLD is approved on these fronts.

### Cost
- [ ] No issues found.

### Safety
- [ ] No issues found.

### Security
- [ ] No issues found.

### Legal
- [ ] No issues found.

## Tier 2: HIGH PRIORITY Issues

### Architecture
- [ ] No issues found.

### Observability
- [ ] No issues found.

### Quality
- [ ] **Requirement Coverage:** Coverage is 50% (< 95%). The test plan focuses on testing the *engine* (loading/flattening logic) using fixtures but neglects to test the *configuration* (the actual schema file) against the business requirements. See "Missing Test Scenarios" above.

## Tier 3: SUGGESTIONS
- **Recursion Limit:** While Python has a recursion limit, explicitly bounding the `flatten_directories` recursion (e.g., max depth 10) prevents potential stack overflows if the schema structure is malformed or circular (though unlikely in JSON).
- **Schema Validation:** Consider adding a meta-schema (JSON Schema Draft 7) to validate the structure schema itself, ensuring `required` is a boolean, `children` is a dict, etc.

## Questions for Orchestrator
1. None.

## Verdict
[ ] **APPROVED** - Ready for implementation
[x] **REVISE** - Fix Tier 1/2 issues first
[ ] **DISCUSS** - Needs Orchestrator decision