# Extracted Test Plan

## Scenarios

### test_id
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Test Description | Expected Behavior | Status

### test_t010
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Load approved LLD | Parses LLD and extracts files list | RED

### test_t020
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Reject unapproved LLD | Raises error for PENDING status | RED

### test_t030
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Analyze codebase extracts excerpts | Returns dict of file→excerpt | RED

### test_t040
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Generate spec includes all sections | Spec has concrete examples | RED

### test_t050
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Validate completeness catches missing excerpts | Returns BLOCKED | RED

### test_t060
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Validate completeness passes complete spec | Returns PASSED | RED

### test_t070
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Review spec routing on APPROVED | Routes to N6 | RED

### test_t080
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Review spec routing on REVISE | Routes to N2, increments iteration | RED

### test_t090
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Finalize writes spec file | File exists at expected path | RED

### test_t100
- Type: unit
- Requirement: 
- Mock needed: False
- Description: CLI runs full workflow | Produces spec file | RED

### test_010
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Happy path - simple LLD | Auto | `tests/fixtures/lld_approved_simple.md` | Spec at `docs/lld/drafts/spec-999.md` | File exists, contains excerpts

### test_020
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Complex LLD with many files | Auto | `tests/fixtures/lld_approved_complex.md` | Complete spec | All 10+ files have excerpts

### test_030
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Unapproved LLD rejection | Auto | `tests/fixtures/lld_not_approved.md` | Error raised | Workflow aborts before N1

### test_040
- Type: unit
- Requirement: 
- Mock needed: False
- Description: File not found in codebase | Auto | LLD with non-existent file | Graceful error | Clear message about missing file

### test_050
- Type: unit
- Requirement: 
- Mock needed: True
- Description: Incomplete spec regeneration | Auto | Mock Claude returns incomplete | N3 → N2 retry | Second attempt improves

### test_060
- Type: unit
- Requirement: 
- Mock needed: True
- Description: Max iterations exceeded | Auto | Mock always returns incomplete | Workflow aborts | Error after 3 iterations

### test_070
- Type: unit
- Requirement: 
- Mock needed: True
- Description: Gemini REVISE verdict | Auto | Mock Gemini returns REVISE | Regenerate with feedback | Feedback in next N2 prompt

### test_080
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Pattern reference validation | Auto | Spec references existing pattern | Check passes | Pattern at file:line exists

### test_090
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Invalid pattern reference | Auto | Spec references non-existent line | Check fails | Completeness blocked

### test_100
- Type: e2e
- Requirement: 
- Mock needed: False
- Description: CLI end-to-end | Auto | Valid issue number | Spec file created | Exit code 0

