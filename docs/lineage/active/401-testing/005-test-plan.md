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
- Description: `test_read_file_with_budget_normal` | Reads file content within budget, `truncated=False` | RED

### test_t020
- Type: unit
- Requirement: 
- Mock needed: False
- Description: `test_read_file_with_budget_truncated` | Truncates large file, `truncated=True` | RED

### test_t030
- Type: unit
- Requirement: 
- Mock needed: False
- Description: `test_read_file_with_budget_binary_skip` | Returns empty content for binary files | RED

### test_t040
- Type: unit
- Requirement: 
- Mock needed: False
- Description: `test_read_file_with_budget_missing_file` | Returns empty content, no crash | RED

### test_t050
- Type: unit
- Requirement: 
- Mock needed: False
- Description: `test_read_files_within_budget_respects_total` | Stops reading when total budget exhausted | RED

### test_t055
- Type: unit
- Requirement: 
- Mock needed: False
- Description: `test_read_files_within_budget_respects_per_file` | Individual file capped at per_file_budget | RED

### test_t060
- Type: unit
- Requirement: 
- Mock needed: False
- Description: `test_parse_project_metadata_pyproject` | Extracts name, deps from pyproject.toml | RED

### test_t070
- Type: unit
- Requirement: 
- Mock needed: False
- Description: `test_parse_project_metadata_package_json` | Extracts name, deps from package.json | RED

### test_t080
- Type: unit
- Requirement: 
- Mock needed: False
- Description: `test_parse_project_metadata_missing` | Returns empty dict when no config found | RED

### test_t090
- Type: unit
- Requirement: 
- Mock needed: False
- Description: `test_scan_patterns_detects_naming` | Identifies snake_case module naming | RED

### test_t100
- Type: unit
- Requirement: 
- Mock needed: False
- Description: `test_scan_patterns_detects_typeddict` | Finds TypedDict state pattern | RED

### test_t105
- Type: unit
- Requirement: 
- Mock needed: False
- Description: `test_scan_patterns_unknown_defaults` | Returns "unknown" for undetectable fields | RED

### test_t110
- Type: unit
- Requirement: 
- Mock needed: False
- Description: `test_detect_frameworks_from_deps` | Identifies LangGraph, pytest from dependency list | RED

### test_t115
- Type: unit
- Requirement: 
- Mock needed: False
- Description: `test_detect_frameworks_from_imports` | Detects frameworks from import statements in file contents | RED

### test_t120
- Type: unit
- Requirement: 
- Mock needed: False
- Description: `test_extract_conventions_from_claude_md` | Extracts bullet-point conventions from CLAUDE.md | RED

### test_t130
- Type: unit
- Requirement: 
- Mock needed: False
- Description: `test_extract_conventions_empty` | Returns empty list for CLAUDE.md without conventions | RED

### test_t140
- Type: unit
- Requirement: 
- Mock needed: True
- Description: `test_analyze_codebase_happy_path` | Produces full CodebaseContext from mock repo | RED

### test_t145
- Type: unit
- Requirement: 
- Mock needed: False
- Description: `test_analyze_codebase_context_has_real_paths` | Generated context references real file paths and patterns from target codebase | RED

### test_t150
- Type: unit
- Requirement: 
- Mock needed: False
- Description: `test_analyze_codebase_no_repo_path` | Returns empty context, logs warning | RED

### test_t160
- Type: unit
- Requirement: 
- Mock needed: False
- Description: `test_analyze_codebase_missing_repo` | Returns empty context when repo_path doesn't exist | RED

### test_t170
- Type: unit
- Requirement: 
- Mock needed: False
- Description: `test_find_related_files_keyword_match` | Finds auth.py when issue mentions "authentication" | RED

### test_t180
- Type: unit
- Requirement: 
- Mock needed: False
- Description: `test_find_related_files_no_match` | Returns empty list for unrelated issue text | RED

### test_t185
- Type: unit
- Requirement: 
- Mock needed: False
- Description: `test_find_related_files_max_five` | Returns at most 5 results even with many matches | RED

### test_t190
- Type: unit
- Requirement: 
- Mock needed: False
- Description: `test_analyze_codebase_produces_state_key` | Node returns dict with `codebase_context` key matching CodebaseContext shape | RED

### test_t200
- Type: unit
- Requirement: 
- Mock needed: False
- Description: `test_sensitive_file_not_read_env` | `.env` file content never appears in any read result | RED

### test_t205
- Type: unit
- Requirement: 
- Mock needed: False
- Description: `test_sensitive_file_not_read_pem` | `.pem` file content never appears in any read result | RED

### test_t210
- Type: unit
- Requirement: 
- Mock needed: False
- Description: `test_select_key_files_priority_order` | CLAUDE.md before README.md before pyproject.toml | RED

### test_t220
- Type: unit
- Requirement: 
- Mock needed: False
- Description: `test_sensitive_file_exclusion` | .env, .secrets files are not read | RED

### test_t225
- Type: unit
- Requirement: 
- Mock needed: False
- Description: `test_is_sensitive_file` | Correctly identifies sensitive file patterns | RED

### test_t230
- Type: unit
- Requirement: 
- Mock needed: False
- Description: `test_symlink_outside_repo_blocked` | Symlink pointing outside repo is not read | RED

### test_010
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Read file within budget (REQ-1) | Auto | Small text file, budget=2000 | Full content, truncated=False | Content matches file, token_estimate < 2000

### test_020
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Read file exceeding budget (REQ-6) | Auto | 10KB file, budget=500 | Partial content, truncated=True | Content length ≈ 500×4 chars, truncated=True

### test_030
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Read binary file gracefully (REQ-7) | Auto | PNG file path | Empty content, no exception | Returns FileReadResult with empty content

### test_040
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Read missing file gracefully (REQ-7) | Auto | Non-existent path | Empty content, no exception | Returns FileReadResult with empty content

### test_050
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Total budget enforcement (REQ-6) | Auto | 10 files, total_budget=5000 | First N files read, rest skipped | Sum of token_estimates ≤ 5000

### test_055
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Per-file budget enforcement (REQ-6) | Auto | 1 large file, per_file_budget=500 | Single file truncated | token_estimate ≤ 500

### test_060
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Parse pyproject.toml (REQ-1) | Auto | Valid pyproject.toml | Dict with name, dependencies | Keys present, deps list non-empty

### test_070
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Parse package.json (REQ-1) | Auto | Valid package.json | Dict with name, dependencies | Keys present, deps list non-empty

### test_080
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Parse missing config (REQ-7) | Auto | Repo with no config file | Empty dict | Returns {}

### test_090
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Detect naming conventions (REQ-2) | Auto | Python files with snake_case | PatternAnalysis.naming_convention set | Contains "snake_case"

### test_100
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Detect TypedDict pattern (REQ-2) | Auto | File with TypedDict import | PatternAnalysis.state_pattern set | Contains "TypedDict"

### test_105
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Unknown pattern defaults (REQ-7) | Auto | Empty file_contents dict | All fields "unknown" | All PatternAnalysis values == "unknown"

### test_110
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Detect frameworks from deps (REQ-2) | Auto | deps=["langgraph", "pytest"] | ["LangGraph", "pytest"] | Both detected

### test_115
- Type: unit
- Requirement: 
- Mock needed: True
- Description: Detect frameworks from imports (REQ-2) | Auto | File with `from fastapi import` | ["FastAPI"] in result | FastAPI detected

### test_120
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Extract CLAUDE.md conventions (REQ-1) | Auto | CLAUDE.md with rule bullets | List of convention strings | Non-empty list, strings match rules

### test_130
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Extract empty conventions (REQ-7) | Auto | CLAUDE.md with no rules section | Empty list | Returns []

### test_140
- Type: unit
- Requirement: 
- Mock needed: True
- Description: Full analysis happy path (REQ-4) | Auto | Mock repo with all key files, issue text referencing existing modules | Complete CodebaseContext with real file paths and patterns | All fields populated; fil

### test_145
- Type: unit
- Requirement: 
- Mock needed: True
- Description: Context references real paths and patterns (REQ-4) | Auto | Mock repo with known structure + specific issue text | CodebaseContext.key_file_excerpts keys are real file paths; conventions match CLAUDE.

### test_150
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Analysis with no repo_path (REQ-7) | Auto | State with repo_path=None | Empty CodebaseContext | All fields empty/default

### test_160
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Analysis with bad repo_path (REQ-7) | Auto | State with non-existent path | Empty CodebaseContext | All fields empty/default

### test_170
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Find related files - match (REQ-3) | Auto | Issue "fix auth", repo has auth.py | [auth.py] | auth.py in results

### test_180
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Find related files - no match (REQ-3) | Auto | Issue "fix auth", repo has no auth | [] | Empty list

### test_185
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Find related files - max results (REQ-3) | Auto | Issue matching 10+ files | At most 5 paths | len(result) <= 5

### test_190
- Type: unit
- Requirement: 
- Mock needed: True
- Description: Node produces codebase_context state key (REQ-8) | Auto | Mock repo with CLAUDE.md and source files | Dict with `codebase_context` key; value is dict matching CodebaseContext shape | Return dict has k

### test_200
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Sensitive .env file never read (REQ-9) | Auto | Repo with `.env` file containing `SECRET=abc123` | `.env` not in any read results; `abc123` not in any content | No FileReadResult.path ends with `.env`

### test_205
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Sensitive .pem file never read (REQ-9) | Auto | Repo with `server.pem` file containing certificate data | `server.pem` not in any read results | No FileReadResult.path contains `server.pem`

### test_210
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Key file priority ordering (REQ-1) | Auto | Repo with CLAUDE.md + README | CLAUDE.md before README | Index of CLAUDE.md < index of README

### test_220
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Sensitive file exclusion via is_sensitive_file (REQ-9) | Auto | Repo with .env file | .env not in read results | .env path not in any FileReadResult

### test_225
- Type: unit
- Requirement: 
- Mock needed: False
- Description: is_sensitive_file detection (REQ-9) | Auto | Various sensitive paths (.env, .pem, credentials/db.yml, main.py) | True for .env, .pem, credentials/db.yml; False for main.py | Correct bool for each inpu

### test_230
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Symlink outside repo blocked (REQ-9) | Auto | Symlink to /tmp/secret.txt in repo | Empty content returned | FileReadResult.content == ""

### test_240
- Type: unit
- Requirement: 
- Mock needed: True
- Description: Cross-repo analysis via repo_path (REQ-5) | Auto | State with repo_path pointing to a second mock repo in fixtures | CodebaseContext populated from second repo's files | key_file_excerpts contain cont

