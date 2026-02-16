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
- Description: test_detect_dead_cli_flags | Returns issue for unused argparse arg | RED

### test_t020
- Type: unit
- Requirement: 
- Mock needed: False
- Description: test_detect_empty_branch_pass | Returns issue for `if x: pass` | RED

### test_t030
- Type: unit
- Requirement: 
- Mock needed: False
- Description: test_detect_empty_branch_return_none | Returns issue for `if x: return None` | RED

### test_t040
- Type: unit
- Requirement: 
- Mock needed: False
- Description: test_detect_docstring_only_function | Returns issue for func with docstring+pass | RED

### test_t050
- Type: unit
- Requirement: 
- Mock needed: False
- Description: test_detect_trivial_assertion | Returns issue for `assert x is not None` only | RED

### test_t060
- Type: unit
- Requirement: 
- Mock needed: False
- Description: test_detect_unused_import | Returns issue for import not used in functions | RED

### test_t070
- Type: unit
- Requirement: 
- Mock needed: False
- Description: test_valid_code_no_issues | Returns empty issues list for clean code | RED

### test_t080
- Type: unit
- Requirement: 
- Mock needed: False
- Description: test_completeness_gate_block_routing | BLOCK verdict routes to N4 | RED

### test_t090
- Type: unit
- Requirement: 
- Mock needed: False
- Description: test_completeness_gate_pass_routing | PASS verdict routes to N5 | RED

### test_t100
- Type: unit
- Requirement: 
- Mock needed: False
- Description: test_max_iterations_ends | BLOCK at max iterations (3) routes to end | RED

### test_t110
- Type: unit
- Requirement: 
- Mock needed: False
- Description: test_report_generation | Report file created with correct structure | RED

### test_t120
- Type: unit
- Requirement: 
- Mock needed: False
- Description: test_lld_requirement_extraction | Requirements parsed from Section 3 | RED

### test_t130
- Type: unit
- Requirement: 
- Mock needed: False
- Description: test_prepare_review_materials | ReviewMaterials correctly populated with LLD requirements and code snippets | RED

### test_010
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Dead CLI flag detection | Auto | Code with `add_argument('--foo')` unused | CompletenessIssue with category=DEAD_CLI_FLAG | Issue returned with correct file/line

### test_020
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Empty branch (pass) detection | Auto | Code with `if x: pass` | CompletenessIssue with category=EMPTY_BRANCH | Issue identifies branch location

### test_030
- Type: unit
- Requirement: 
- Mock needed: True
- Description: Empty branch (return None) detection | Auto | Code with `if mock: return None` | CompletenessIssue with category=EMPTY_BRANCH | Issue identifies branch location

### test_040
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Docstring-only function detection | Auto | `def foo(): """Doc.""" pass` | CompletenessIssue with category=DOCSTRING_ONLY | Issue identifies function

### test_050
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Trivial assertion detection | Auto | Test with only `assert result is not None` | CompletenessIssue with category=TRIVIAL_ASSERTION | Issue warns about assertion quality

### test_060
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Unused import detection | Auto | `import os` with no usage | CompletenessIssue with category=UNUSED_IMPORT | Issue identifies import

### test_070
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Valid implementation (negative) | Auto | Complete implementation code | Empty issues list | No false positives

### test_080
- Type: unit
- Requirement: 
- Mock needed: False
- Description: BLOCK routes to N4 | Auto | State with verdict='BLOCK', iter<3 | Route returns 'N4_implement_code' | Correct routing

### test_090
- Type: unit
- Requirement: 
- Mock needed: False
- Description: PASS routes to N5 | Auto | State with verdict='PASS' | Route returns 'N5_verify_green' | Correct routing

### test_100
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Max iterations ends workflow | Auto | State with verdict='BLOCK', iter>=3 | Route returns 'end' | Prevents infinite loop

### test_110
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Report file generation | Auto | Issue #999, results | File at docs/reports/active/999-implementation-report.md | File exists with correct structure

### test_120
- Type: unit
- Requirement: 
- Mock needed: False
- Description: LLD requirement parsing | Auto | LLD with Section 3 requirements | List of (id, text) tuples | All requirements extracted

### test_130
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Review materials preparation | Auto | LLD path + implementation files | ReviewMaterials with requirements and code snippets | Materials correctly formatted for orchestrator

